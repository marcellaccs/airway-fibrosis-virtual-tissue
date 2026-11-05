# CC3D session workflow (GUI development → version control → parameter scan)

The routine for a working session that uses the GUI (Twedit to edit, Player to visualize)
before running headless parameter scans. It exists to prevent two record-keeping failures:

- **Outputs landing outside version control.** With no output dir, CC3D writes a timestamped
  `<project>_cc3d_<date>_<hash>/` folder into the *current working directory*. Launch a tool
  from your home dir and the dump lands there, untracked and unrecorded.
- **Work created outside the repo.** Twedit's *New Simulation* wizard defaults to CC3D's scratch
  folder, so a model started there is never in git.

Both are avoided by the same discipline: **launch everything from the repo root, and edit/create
only under `model/cc3d/…`.**

Prereqs: repo at `C:\Users\<user>\research\toxicology-virtual-tissue`; the `cc3d` conda env
installed (see [`README.md`](README.md)). Commands are for **Git Bash**.

## Steps

1. **Open Git Bash and go to the repo root — never launch CC3D from your home dir.**
   ```bash
   cd /c/Users/<user>/research/toxicology-virtual-tissue
   pwd    # confirm you are in the repo
   ```
   Every CC3D tool inherits this as its working directory, so any bare output dump lands
   *inside* the repo where `.gitignore` catches it.

2. **Pull the latest and activate the environment.**
   ```bash
   git pull
   conda activate cc3d          # prompt should show (cc3d)
   ```

3. **(First run of the day) record the CC3D version** for the lab-notebook entry.
   ```bash
   python -c "import cc3d; print(cc3d.__version__)"
   ```

4. **Edit in Twedit — the repo's copy only.**
   ```bash
   cc3d-twedit5 &               # '&' frees the shell; or: python -m cc3d.twedit5 &
   ```
   In Twedit: **CC3D Project → Open CC3D Project** →
   `model/cc3d/M1_M2_antimony/M1_M2_antimony.cc3d`. Twedit saves `.py`/`.xml` in place.

   **Starting a genuinely new model?** Use the wizard, but send it into the repo — don't create
   folders by hand:
   - **CC3D Project → New CC3D Project…** opens the *CompuCell3D Simulation Wizard*.
   - On the first page set **Simulation Name** (e.g. `airway_fibrosis_v1`), **Simulation Type**
     `Python+XML`, and — the field that matters — **Simulation Directory**: click **Browse…**
     and choose `model/cc3d`. The wizard then creates `model/cc3d/<Simulation Name>/` containing
     `<name>.cc3d` and a `Simulation/` folder (`<name>.py`, `<name>.xml`,
     `<name>Steppables.py`), so it is version-controlled from birth.
   - **Check the Simulation Directory every time.** It defaults to *wherever you last made a
     project* (Twedit's `RecentNewProjectDir`), not this repo — so one project made in CC3D's
     scratch/examples folder makes every later one default there and land outside git. Browse
     back to `model/cc3d` before finishing.

5. **Visualize and iterate in the Player, on the same repo project.**
   ```bash
   cc3d-player5 -i model/cc3d/M1_M2_antimony/M1_M2_antimony.cc3d &
   # or: python -m cc3d.player5 -i model/cc3d/M1_M2_antimony/M1_M2_antimony.cc3d &
   ```
   Loop: edit in Twedit → save → re-open in the Player → run/step to check behavior.
   - Player run output goes to a `*_cc3d_<timestamp>/` folder in the CWD (the repo root, from
     step 1). That is gitignored — do not commit it.
   - If a plot window won't open or the layout is broken, close the Player and delete
     `model/cc3d/M1_M2_antimony/Simulation/_settings.sqlite` (disposable, gitignored Player
     state), then relaunch.

6. **Commit the model once the GUI behaves — before scanning.**
   ```bash
   git status   # expect only .py/.xml/.cc3d under model/cc3d/… —
                # NOT any *_cc3d_* dump or _settings.sqlite. If those appear, stop:
                # .gitignore isn't catching them.
   git add model/cc3d/M1_M2_antimony
   git commit -m "<imperative description + why>"
   ```
   This snapshots the exact model that produced your GUI results, before scanning changes it.

7. **Run the headless parameter scan / batch, output into gitignored `results/`.**
   ```bash
   python -m cc3d.run_script \
       -i model/cc3d/M1_M2_antimony/M1_M2_antimony.cc3d \
       --output-dir results/cc3d/<run-name>
   # python -m cc3d.run_script --help  for all flags
   ```
   `results/` is gitignored, so large outputs never enter git; because you committed in step 6,
   every figure traces back to a commit.

8. **Close out — lab notebook + push.**
   - Copy `lab-notebook/TEMPLATE.md` → `lab-notebook/2026/YYYY-MM-DD.md`; record what changed,
     the CC3D version, commands run, and where outputs landed.
   ```bash
   git add -A
   git commit -m "<what changed and why>"
   git push
   ```
   Pull before you start, push before you stop (see [`../../SETUP.md`](../../SETUP.md) Part 6).

## Quick rules

- Launch every CC3D tool from the **repo root**, never your home dir.
- Edit or create only under `model/cc3d/…`; never the *New Simulation* default path.
- Code (`.py`/`.xml`/`.cc3d`) is committed; outputs (`*_cc3d_*/`, `results/`, `_settings.sqlite`)
  are gitignored.
- Commit the model **before** you scan.
