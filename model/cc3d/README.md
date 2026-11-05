# CC3D Model

CompuCell3D spatial model for macrophage polarization (M1/M2) in a virtual tissue.

> For the step-by-step working routine (GUI development → commit → parameter scan) that keeps
> every run under version control, see [`WORKFLOW.md`](WORKFLOW.md).

## Environment setup

Requires a CompuCell3D conda environment. **The env name is not consistent across
machines** — it's `cc3d` on some, `cc3d_490` on others. Check what's already there before
creating a new one:

```
conda env list
conda run -n <candidate-name> python -c "import cc3d; print(cc3d.__version__)"
```

If none exists (or the candidate prints an ImportError — this has happened when `python=3.12`
failed to pin and the env solved to a newer, CC3D-incompatible Python instead), create one.
Pin the Python version explicitly and verify it took before installing CC3D:

```
conda create -n cc3d -c conda-forge python=3.12
conda activate cc3d
python --version   # must print 3.12.x — if not, stop and recreate rather than installing on top
$env:PYTHONIOENCODING = "utf-8"   # Windows PowerShell; use `set` in cmd.exe
mamba install -c conda-forge -c compucell3d compucell3d=4.10.0
```

Verify: `python -c "import cc3d; print(cc3d.__version__)"`

## Headless run walkthrough

1. **Open Git Bash** (search "Git Bash" in the Start menu).

2. **Navigate to the repo root:**
   ```
   cd ~/research/toxicology-virtual-tissue
   ```

3. **Activate the CC3D environment** (name varies by machine — see "Environment setup" above):
   ```
   conda activate cc3d
   ```
   Your prompt should change to show the env name at the start.

4. **Run the model:**
   ```
   python -m cc3d.run_script -i model/cc3d/M1_M2_antimony/M1_M2_antimony.cc3d
   ```
   The simulation runs and prints a performance report when done (~3.5 minutes).
   You will see a few warnings about `PlayerSizes` and `MCSConversionFactor` — these are
   harmless and can be ignored for now.

5. **When it finishes** you'll see something like:
   ```
   TOTAL RUNTIME 3 m : 37 s : 429 ms = 217.429 s
   ```

**Optional flags:**
```
# Save output frames to a folder
python -m cc3d.run_script -i model/cc3d/M1_M2_antimony/M1_M2_antimony.cc3d \
    --output-dir results/cc3d/run1

# See all options
python -m cc3d.run_script --help
```

## Other launch modes

```
conda activate cc3d   # or whatever this machine's CC3D env is named — see Environment setup

# GUI Player (interactive)
python -m cc3d.player5

# Editor (Twedit++)
python -m cc3d.twedit5
```

If the Player crashes after moving windows/monitors, delete `Simulation/_settings.sqlite`.

## Notes

- CC3D 4.7.0 (listed on the official install page) cannot be installed on Windows because
  it requires `vs2015_win-64`, which no longer exists in conda-forge. Use 4.10.0.
- Keep this environment separate from `tox-ode`; mixing them can break libRoadRunner.
