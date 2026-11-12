"""Smoke test for the installed VI-Suite HBC extension.

Run inside Blender after "blender --command extension install-file ...":

    blender -b --python-exit-code 1 --python tests/smoke_test.py -- --report smoke-report.json

Checks (FAIL = test fails, INFO = only reported):
- the add-on can be enabled
- the bundled Python packages can be imported
- the bundled EnergyPlus starts (via vi_func.ep_check / ep_env)
- a minimal EnergyPlus simulation (tests/data/mini.idf) completes
- ExpandObjects and Radiance (rtrace) start
"""

import argparse
import importlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import traceback

import addon_utils
import bpy

EXT_ID = "vi_suite_HBC"
HERE = os.path.dirname(os.path.abspath(__file__))
IMPORTS = [
    "numpy", "scipy", "matplotlib", "matplotlib.pyplot", "PySide6", "PySide6.QtWidgets",
    "shiboken6", "netgen", "ngsolve", "pyroomacoustics", "psutil", "PIL",
]

results = []


def record(name, ok, detail="", fatal=True):
    status = "PASS" if ok else ("FAIL" if fatal else "INFO")
    results.append({"check": name, "status": status, "detail": str(detail)})
    print(f"[{status}] {name}: {detail}", flush=True)
    return ok


def run(cmd, **kw):
    kw.setdefault("capture_output", True)
    kw.setdefault("text", True)
    kw.setdefault("timeout", 300)
    return subprocess.run(cmd, **kw)


def find_module():
    for mod in addon_utils.modules(refresh=True):
        if mod.__name__.split(".")[-1] == EXT_ID:
            return mod.__name__
    return None


def check_enable():
    modname = find_module()
    if not record("extension installed", modname is not None, modname or "module not found"):
        return None

    errors = []
    addon_utils.enable(modname, default_set=True, handle_error=lambda e: errors.append(traceback.format_exc()))
    ok = modname in bpy.context.preferences.addons and not errors
    record("add-on enabled", ok, "".join(errors)[-2000:] or modname)
    return modname if ok else None


def check_imports():
    for name in IMPORTS:
        try:
            m = importlib.import_module(name)
            record(f"import {name}", True, getattr(m, "__version__", ""))
        except Exception as e:
            record(f"import {name}", False, f"{type(e).__name__}: {e}")


def check_energyplus(modname, addon_dir):
    vi_func = importlib.import_module(f"{modname}.vi_func")
    ep_dir = os.path.join(addon_dir, "EPFiles", sys.platform)
    ep_exe = shutil.which("energyplus")
    record("energyplus on PATH", ep_exe is not None, ep_exe or os.environ.get("PATH", ""))
    if not ep_exe:
        return

    if sys.platform == "darwin":
        lib = os.path.join(ep_dir, "libenergyplusapi.25.1.0.dylib")
        record("libenergyplusapi.25.1.0.dylib present", os.path.isfile(lib), lib)

        r = run(["otool", "-l", os.path.realpath(ep_exe)])
        rpaths = [l.split()[1] for l in r.stdout.splitlines() if l.strip().startswith("path ")]
        record("energyplus LC_RPATH", True, rpaths, fatal=False)

        # CI marks the installed program folders as quarantined (like a browser
        # download unpacked with Finder); the add-on must remove the flag on load.
        for exe in (os.path.realpath(ep_exe), shutil.which("rtrace") or ""):
            if exe:
                r = run(["xattr", "-l", exe])
                record(f"no quarantine flag on {os.path.basename(exe)}", "com.apple.quarantine" not in r.stdout,
                       r.stdout.strip() or "none")

        r = run(["energyplus", "--version"])
        # The bundled binary must have @executable_path as rpath (fix B). If this fails
        # after a merge from master, run build_scripts/fix_energyplus_rpath_macos.sh on a Mac.
        record("energyplus --version WITHOUT ep_env (rpath fix B)",
               r.returncode == 0, f"rc={r.returncode} {(r.stderr or r.stdout).strip()[:500]}")

    ok, msg = vi_func.ep_check()
    record("ep_check (energyplus --version with ep_env)", ok, msg)
    if not ok:
        return

    epw = os.path.join(addon_dir, "EPFiles", "Weather", "GBR_Birmingham.035340_IWEC.epw")
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copy(os.path.join(HERE, "data", "mini.idf"), os.path.join(tmp, "in.idf"))
        r = run(["energyplus", "-w", epw, "-p", "results0", "in.idf"], cwd=tmp, env=vi_func.ep_env())
        errfile = os.path.join(tmp, "results0out.err")
        err = open(errfile).read() if os.path.isfile(errfile) else ""
        done = r.returncode == 0 and "EnergyPlus Completed Successfully" in err
        record("EnergyPlus mini simulation", done,
               f"rc={r.returncode}, err file {'written' if err else 'MISSING'}, "
               f"eso {'written' if os.path.isfile(os.path.join(tmp, 'results0out.eso')) else 'MISSING'}"
               + ("" if done else "\n" + (err or r.stderr or r.stdout)[-2000:]))

        r = run(["ExpandObjects"], cwd=tmp)
        record("ExpandObjects starts", r.returncode == 0, f"rc={r.returncode} {(r.stderr or r.stdout).strip()[:300]}")


def check_radiance():
    exe = shutil.which("rtrace")
    if not record("rtrace on PATH", exe is not None, exe or ""):
        return
    r = run(["rtrace", "-version"])
    record("rtrace -version", r.returncode == 0, (r.stdout or r.stderr).strip()[:300])


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", default="smoke-report.json")
    args = ap.parse_args(argv)

    record("blender", True, f"{bpy.app.version_string}, Python {sys.version.split()[0]}, {sys.platform}", fatal=False)

    try:
        modname = check_enable()
        check_imports()
        if modname:
            addon_dir = os.path.dirname(sys.modules[modname].__file__)
            check_energyplus(modname, addon_dir)
            check_radiance()
    except Exception:
        record("unexpected error", False, traceback.format_exc())

    with open(args.report, "w") as f:
        json.dump(results, f, indent=2)

    failed = [r for r in results if r["status"] == "FAIL"]
    print(f"\n{len(results)} checks, {len(failed)} failed", flush=True)
    if failed:
        raise SystemExit(1)


main()
