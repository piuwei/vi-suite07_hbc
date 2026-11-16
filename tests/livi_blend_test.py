"""LiVi end-to-end test with a real .blend file.

    blender -b <copy of tests/data/simple_cube_livi.blend> --python-exit-code 1 \
        --python tests/livi_blend_test.py -- --report livi-report.json

Opens the file (it must be in a writable directory, VI-Suite writes next to it), then:
1. LiVi Geometry node   -> node.ligexport (geometry and sensor points)
2. LiVi Context node    -> node.liexport  (sky / context export)
3. LiVi Simulation node -> node.livicalc  (Radiance calculation)
   node.livicalc calculates in invoke() and only post-processes the results in a
   modal handler, which does not run in background mode; the test calls the same
   post-processing (simnode.postsim) right after the calculation.
4. Checks: operators finished, all sensor points calculated, illuminance on the
   measurement grid within a plausible range around a reference value.

Radiance calculates the indirect light with random sampling, so the results vary
by a few percent between runs; the reference check uses a generous tolerance.
"""

import argparse
import json
import os
import shutil
import sys
import tempfile
import traceback
from types import SimpleNamespace

import addon_utils
import bpy

EXT_ID = "vi_suite_HBC"
WEATHER_EPW = "GBR_London.Gatwick.037760_IWEC.epw"  # bundled with the add-on, used by the .blend
SENSOR_OBJECT = "Grid"                               # measurement grid (sensor material) in the .blend
SENSOR_POINTS = 25                                   # 5 x 5 faces
# Average illuminance on the grid for simple_cube_livi.blend (Basic context, 1 Jan 12:00),
# measured with Blender 5.3.0: about 740 lx. Update when the .blend changes.
REFERENCE_AVG_LUX = 740.0
TOLERANCE = 0.3                                      # +-30 %

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
    return next((n for n in tree.nodes if n.bl_idname == idname), None)


def add_execute(modname):
    """Make the LiVi operators callable in background mode (re-registered for this run only).

    - NODE_OT_Li_Con only defines invoke(); it does not use the event.
    - NODE_OT_Li_Sim calculates in invoke(), then adds a modal handler that runs
      simnode.postsim(). Background mode has no event loop, so postsim is called here.
      The operator still returns invoke()'s result (RUNNING_MODAL); returning anything
      else while the handler is registered crashes Blender on exit.
    """
    ops = sys.modules[f"{modname}.vi_operators"]

    def con_execute(self, context):
        return self.invoke(context, None)

    def sim_execute(self, context):
        res = self.invoke(context, None)
        if getattr(self, "reslists", None):
            self.simnode.postsim(self.reslists)
        return res

    for cls, func in ((ops.NODE_OT_Li_Con, con_execute), (ops.NODE_OT_Li_Sim, sim_execute)):
        bpy.utils.unregister_class(cls)
        cls.execute = func
        bpy.utils.register_class(cls)


def set_weather(modname, loc, weather):
    """Point the location node to the bundled weather file (the .blend stores an absolute path)."""
    if os.path.isfile(loc.weather) and os.path.basename(loc.weather) == os.path.basename(weather):
        return record("weather file", True, loc.weather)

    record("weather file from .blend replaced", True, f"{loc.weather} -> {weather}", fatal=False)
    # The weather enum is stored as an index, so give the add-on a folder with only this file.
    wdir = tempfile.mkdtemp(prefix="vi_weather_")
    weather = shutil.copy(weather, wdir)
    bpy.context.preferences.addons[modname].preferences.epweath = wdir
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
    return record("weather file", loc.weather == weather and os.path.isfile(weather), loc.weather)


def run_op(label, op, node):
    try:
        with bpy.context.temp_override(node=node):
            res = op('EXEC_DEFAULT')
        return record(label, bool({'FINISHED', 'RUNNING_MODAL'} & set(res)), res)
    except Exception:
        return record(label, False, traceback.format_exc()[-2000:])


def main():
    record("blend file", bool(bpy.data.filepath), bpy.data.filepath)

    modname = find_module()
    if not record("add-on enabled", modname in bpy.context.preferences.addons, modname):
        return

    trees = [ng for ng in bpy.data.node_groups if ng.bl_idname == 'ViN']
    if not record("VI-Suite node tree", bool(trees), [t.name for t in trees]):
        return
    tree = trees[0]
    geo, con, sim = (node_of(tree, i) for i in ('No_Li_Geo', 'No_Li_Con', 'No_Li_Sim'))
    if not record("LiVi Geometry/Context/Simulation nodes", all((geo, con, sim)),
                  [getattr(n, 'name', None) for n in (geo, con, sim)]):
        return

    loc = con.inputs['Location in'].links[0].from_node if con.inputs['Location in'].links else None
    if loc:
        addon_dir = os.path.dirname(sys.modules[modname].__file__)
        set_weather(modname, loc, os.path.join(addon_dir, "EPFiles", "Weather", WEATHER_EPW))

    grid = bpy.data.objects.get(SENSOR_OBJECT)
    if not record("measurement grid with sensor material", grid is not None and any(
            m and m.vi_params.mattype == '1' for m in grid.data.materials), SENSOR_OBJECT):
        return

    add_execute(modname)
    if not run_op("geometry export (node.ligexport)", bpy.ops.node.ligexport, geo):
        return
    if not run_op("context export (node.liexport)", bpy.ops.node.liexport, con):
        return

    gvp = grid.vi_params
    npoints = gvp.get('rtpnum')
    record("sensor points exported", npoints == SENSOR_POINTS, f"{npoints} (expected {SENSOR_POINTS})")

    if not run_op("Radiance simulation (node.livicalc)", bpy.ops.node.livicalc, sim):
        return

    frame = bpy.context.scene.frame_current
    key = f"illu{frame}"
    try:
        lmin, lave, lmax = (float(gvp[k][key]) for k in ('omin', 'oave', 'omax'))
    except Exception as e:
        record("illuminance results", False, f"no '{key}' results on {SENSOR_OBJECT}: {e}")
        return

    record("illuminance results", 0 < lmin <= lave <= lmax,
           f"min {lmin:.0f} lx, average {lave:.0f} lx, max {lmax:.0f} lx")
    lo, hi = REFERENCE_AVG_LUX * (1 - TOLERANCE), REFERENCE_AVG_LUX * (1 + TOLERANCE)
    record("average illuminance near reference", lo <= lave <= hi,
           f"{lave:.0f} lx, expected {REFERENCE_AVG_LUX:.0f} lx +-{TOLERANCE:.0%} ({lo:.0f}-{hi:.0f} lx)")


try:
    main()
except Exception:
    record("unexpected error", False, traceback.format_exc())

_argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
_ap = argparse.ArgumentParser()
_ap.add_argument("--report", default="livi-report.json")
_args = _ap.parse_args(_argv)
with open(_args.report, "w") as fh:
    json.dump(results, fh, indent=2)

_failed = [r for r in results if r["status"] == "FAIL"]
print(f"\n{len(results)} checks, {len(_failed)} failed", flush=True)
if _failed:
    raise SystemExit(1)
