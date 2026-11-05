"""Make a scratch copy of the CC3D project for a seed-200, 3k-MCS smoke twin (Gate B').

The twin pattern used in every B' phase (lab-notebook 2026-10-31 .. 11-02): a copy of
model/cc3d/subepithelial_fibrosis_draft/ with <Steps>3001</Steps> and <RandomSeed>200</RandomSeed>
in the XML, the ParameterScan line removed from the .cc3d, and the named parameters.py switches
rewritten. Run it headless, alone, from the repo root:
    conda run -n cc3d_490 --no-capture-output python -m cc3d.run_script         -i <dest>/subepithelial_fibrosis_draft.cc3d -o <out_dir> > <log> 2>&1
then compare against results/cc3d/bprime-ref-3k-seed200/ with compare_replicates.py (--key
rng_seed) and compare_run_logs.py.

Usage: python model/cc3d/tools/make_smoke_twin.py <repo_root> <dest_dir> SWITCH=True SWITCH=False ...
       (SWITCH is any `NAME = True|False|<int>` line in parameters.py, e.g. P_FIELD_ENABLED=True
        MMP_FIELD_ENABLED=True C_MMP_DECAY_ENABLED=False C_MMP_DECAY_PERIOD_MCS=10)
The copy leaves out __pycache__ and _settings.sqlite. <dest_dir> is removed first if it exists;
keep it outside the project (a scratch directory), never under model/cc3d/.
"""
import re
import shutil
import sys
from pathlib import Path

repo = Path(sys.argv[1])
dest = Path(sys.argv[2])
settings = dict(arg.split("=", 1) for arg in sys.argv[3:])

src = repo / "model" / "cc3d" / "subepithelial_fibrosis_draft"
if dest.exists():
    shutil.rmtree(dest)
shutil.copytree(src, dest, ignore=shutil.ignore_patterns("__pycache__", "_settings.sqlite"))

xml_path = dest / "Simulation" / "Subepithelial_Fibrosis.xml"
xml = xml_path.read_text(encoding="ascii")
xml, n_steps = re.subn(r"<Steps>\d+</Steps>", "<Steps>3001</Steps>", xml)
assert n_steps == 1, n_steps
assert "<RandomSeed>" not in xml
xml = xml.replace("<Steps>3001</Steps>", "<Steps>3001</Steps>\n        <RandomSeed>200</RandomSeed>", 1)
xml_path.write_text(xml, encoding="ascii")

cc3d_path = dest / "subepithelial_fibrosis_draft.cc3d"
lines = [ln for ln in cc3d_path.read_text(encoding="ascii").splitlines(keepends=True)
         if "ParameterScan" not in ln]
cc3d_path.write_text("".join(lines), encoding="ascii")

par_path = dest / "Simulation" / "parameters.py"
par = par_path.read_text(encoding="ascii")
for name, value in settings.items():
    pattern = re.compile(r"^(%s\s*=\s*)(True|False|\d+)(\b)" % re.escape(name), re.M)
    par, n = pattern.subn(lambda m: m.group(1) + value + m.group(3), par)
    assert n == 1, (name, n)
par_path.write_text(par, encoding="ascii")

print("twin at", dest, "with", settings)
for name in ("P_FIELD_ENABLED", "P_GATES_REPAIR", "P_DRIVES_PROLIFERATION", "MMP_FIELD_ENABLED",
             "ECM_CELLS_ENABLED", "C_MMP_DECAY_ENABLED", "C_MMP_DECAY_PERIOD_MCS"):
    m = re.search(r"^%s\s*=\s*(\S+)" % name, par, re.M)
    print("  ", name, "=", m.group(1) if m else "?")
