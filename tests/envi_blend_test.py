"""EnVi end-to-end test with a real .blend file.

    blender -b <copy of tests/data/simple_cube.blend> --python-exit-code 1 \
        --python tests/envi_blend_test.py -- --report envi-report.json

Opens the file (it must be in a writable directory, VI-Suite writes next to it), then:
1. EnVi Geometry node  -> node.engexport (geometry export)
2. EnVi Context node   -> node.encon     (IDF export)
3. EnergyPlus run per frame, with the same command line as node.ensim
   (node.ensim itself is a modal operator and cannot run in background mode)
4. Checks: operators finished, in<frame>.idf written, EnergyPlus completed
   without severe errors, .err and .eso written.
"""

import argparse
import glob
import importlib
import json
import os
import shutil
import subprocess
import tempfile
import sys
import traceback
from types import SimpleNamespace

import addon_utils
import bpy

EXT_ID = "vi_suite_HBC"
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
results = []


def record(name, ok, detail="", fatal=True):
    status = "PASS" if ok else ("FAIL" if fatal else "INFO")
    results.append({"check": name, "status": status, "detail": str(detail)})
    print(f"[{status}] {name}: {detail}", flush=True)
    return ok


def find_module():
    for mod in addon_utils.modules(refresh=False):
        if mod.__name__.split(".")[-1] == EXT_ID:
            return mod.__name__
    return None


def node_of(tree, idname):
    for n in tree.nodes:
        if n.bl_idname == idname:
            return n
    return None


def add_execute(modname, *class_names):
    """The EnVi export operators only define invoke(), which cannot be called in
    background mode. Re-register them for this test run with an execute() that
    calls invoke() (they do not use the event)."""
    ops = sys.modules[f"{modname}.vi_operators"]
    for cn in class_names:
        cls = getattr(ops, cn)
        if "execute" not in cls.__dict__:
            bpy.utils.unregister_class(cls)
            cls.execute = lambda self, context: self.invoke(context, None)
            bpy.utils.register_class(cls)


def set_weather(modname, loc, weather):
    """Point the location node to a weather file available on this machine."""
    if os.path.isfile(loc.weather):
        return record("weather file", True, loc.weather)

    record("weather file from .blend not found, using copy", True, f"{loc.weather} -> {weather}", fatal=False)
    # The weather enum is stored as an index, so give the add-on a folder that
    # contains only the chosen file.
    wdir = tempfile.mkdtemp(prefix="vi_weather_")
    weather = shutil.copy(weather, wdir)
    prefs = bpy.context.preferences.addons[modname].preferences
    prefs.epweath = wdir
    # updatelatlong() rebuilds the weather list; it expects a node editor context
    fake = SimpleNamespace(space_data=SimpleNamespace(edit_tree=None), scene=bpy.context.scene)
    try:
        loc.updatelatlong(fake)
    except Exception:
        traceback.print_exc()
        loc['entries'] = [(weather, os.path.basename(weather), 'Weather Location')]
    if loc.weather != weather:
        try:
            loc.weather = weather
        except Exception as e:
            print("setting weather:", e)
    if loc.weather != weather:
        return record("weather file", False, f"location node uses {loc.weather}, expected {weather}")
    return record("weather file", os.path.isfile(loc.weather), loc.weather)


def run_op(label, op, node):
    try:
        with bpy.context.temp_override(node=node):
            res = op('EXEC_DEFAULT')
        return record(label, 'FINISHED' in res, res)
    except Exception:
        return record(label, False, traceback.format_exc()[-2000:])


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", default="envi-report.json")
    ap.add_argument("--weather", default="", help="EPW to use if the one in the .blend is not found")
    args = ap.parse_args(argv)

    record("blend file", bool(bpy.data.filepath), bpy.data.filepath)

    modname = find_module()
    if not record("add-on enabled", modname in bpy.context.preferences.addons, modname):
        return

    vi_func = importlib.import_module(f"{modname}.vi_func")
    trees = [ng for ng in bpy.data.node_groups if ng.bl_idname == 'ViN']
    if not record("VI-Suite node tree", bool(trees), [t.name for t in trees]):
        return

    tree = trees[0]
    geo, con, sim = (node_of(tree, i) for i in ('No_En_Geo', 'No_En_Con', 'No_En_Sim'))
    if not record("EnVi Geometry/Context/Simulation nodes", all((geo, con, sim)),
                  [getattr(n, 'name', None) for n in (geo, con, sim)]):
        return

    loc = con.inputs['Location in'].links[0].from_node if con.inputs['Location in'].links else None
    if not record("location node", loc is not None, getattr(loc, 'name', '')):
        return

    addon_dir = os.path.dirname(sys.modules[modname].__file__)
    # Weather file: --weather, else the file with the same name as in the .blend
    # from tests/data, else a weather file bundled with the add-on.
    same_name = os.path.join(DATA, os.path.basename(loc.weather.replace("\\", "/")))
    weather = args.weather or (same_name if os.path.isfile(same_name) else
                               os.path.join(addon_dir, "EPFiles", "Weather", "GBR_Birmingham.035340_IWEC.epw"))
    if not set_weather(modname, loc, os.path.abspath(weather)):
        return

    add_execute(modname, "NODE_OT_En_Geo", "NODE_OT_En_Con")

    if not run_op("geometry export (node.engexport)", bpy.ops.node.engexport, geo):
        return
    if not run_op("IDF export (node.encon)", bpy.ops.node.encon, con):
        return

    svp = bpy.context.scene.vi_params
    newdir = svp['viparams']['newdir']
    fs, fe = svp['enparams']['fs'], svp['enparams']['fe']
    frames = range(fs, fe + 1)
    idfs = [os.path.join(newdir, f"in{f}.idf") for f in frames]
    if not record("IDF written", all(os.path.isfile(i) for i in idfs), idfs):
        return

    expand = "-x" if svp['viparams'].get('hvactemplate') else ""
    resname = sim.resname or 'eplus'
    env = vi_func.ep_env()

    for f in frames:
        # same command line as NODE_OT_En_Sim
        cmd = "energyplus {0} -w in{1}.epw -p {2}{1} in{1}.idf".format(expand, f, resname).split()
        r = subprocess.run(cmd, cwd=newdir, env=env, capture_output=True, text=True, timeout=1800)
        errf = os.path.join(newdir, f"{resname}{f}out.err")
        esof = os.path.join(newdir, f"{resname}{f}out.eso")
        err = open(errf).read() if os.path.isfile(errf) else ""
        summary = next((l.strip() for l in err.splitlines() if "EnergyPlus Completed Successfully" in l
                        or "EnergyPlus Terminated" in l), "")
        ok = (r.returncode == 0 and "EnergyPlus Completed Successfully" in err
              and "0 Severe Errors" in summary and os.path.isfile(esof))
        severe = [l for l in err.splitlines() if "** Severe" in l or "**  Fatal" in l][:20]
        record(f"EnergyPlus frame {f}", ok,
               f"cmd: {' '.join(cmd)} | rc={r.returncode} | err {'written' if err else 'MISSING'} | "
               f"eso {'written' if os.path.isfile(esof) else 'MISSING'} | {summary}"
               + ("" if ok else "\n" + "\n".join(severe or [(r.stderr or r.stdout)[-2000:]])))

    record("output files", True, sorted(os.path.basename(p) for p in glob.glob(os.path.join(newdir, f"{resname}*"))), fatal=False)


try:
    main()
except Exception:
    record("unexpected error", False, traceback.format_exc())

_argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
_report = _argv[_argv.index("--report") + 1] if "--report" in _argv else "envi-report.json"
with open(_report, "w") as fh:
    json.dump(results, fh, indent=2)

_failed = [r for r in results if r["status"] == "FAIL"]
print(f"\n{len(results)} checks, {len(_failed)} failed", flush=True)
if _failed:
    raise SystemExit(1)
