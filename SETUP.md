# SETUP — Git + GitHub research workflow (beginner-friendly)

A one-time setup and a daily routine for maintaining this project (and future ones) as a
git repository, synced across your home and work laptops via GitHub. Commands are shown for
**Git Bash** (the Unix-style shell that ships with Git for Windows) — it matches the shell
skills you've been learning.

> **The golden rule:** your git repos live **outside Google Drive** (Drive's sync corrupts
> git). GitHub — not Drive — keeps your two laptops in sync.

---

## Part 0 — The mental model (2 min)

```
your laptop  ──push──▶  GitHub (private, the source of truth)  ──pull──▶  other laptop
```
- You edit files locally, take **snapshots** (`commit`), and **upload** them (`push`).
- On the other laptop you **download** the latest (`pull`) before working.
- One **repository = one project**. Each is an independent folder with its own history.

---

## Part 1 — One-time install (do once per laptop)

1. **Git for Windows** — https://git-scm.com/download/win (includes Git Bash). Accept defaults.
2. **Tell git who you are** (open Git Bash):
   ```bash
   git config --global user.name  "Marcella Torres"
   git config --global user.email "you@example.com"
   git config --global init.defaultBranch main
   ```
3. **Miniconda** (for Python/CC3D environments) — https://docs.conda.io/en/latest/miniconda.html
4. **A GitHub account** — https://github.com (use your email above). Optional but recommended:
   the **GitHub CLI** `gh` (https://cli.github.com) — it makes creating repos a one-liner.
5. Optional: **VS Code** — a friendly editor with built-in git buttons.

---

## Part 2 — Create your research home and place this repo

Pick a folder **not** inside `H:\My Drive`. A local path like `C:\Users\<user>\research` is ideal.

```bash
mkdir -p /c/Users/<user>/research
# Unzip toxicology-virtual-tissue.zip so the folder lands here:
#   C:\Users\<user>\research\toxicology-virtual-tissue
cd /c/Users/<user>/research/toxicology-virtual-tissue
```

---

## Part 3 — Make it a git repo and take the first snapshot

```bash
git init
git add -A
git commit -m "initial project scaffold and Summer 2025 context"
```
That's your first commit — a permanent, timestamped snapshot.

---

## Part 4 — Put it on GitHub (private)

**Option A — GitHub CLI (easiest):**
```bash
gh auth login                       # once per laptop; follow the prompts
gh repo create toxicology-virtual-tissue --private --source=. --push
```

**Option B — GitHub website:**
1. github.com → **New repository** → name `toxicology-virtual-tissue` → **Private** → *don't* add a README → Create.
2. Copy the URL it shows, then:
   ```bash
   git remote add origin https://github.com/<your-username>/toxicology-virtual-tissue.git
   git push -u origin main
   ```

Your project is now backed up and shareable (privately).

---

## Part 5 — Your other laptop (do once there)

After installing Git (Part 1) on the second laptop:
```bash
mkdir -p /c/Users/<user>/research && cd /c/Users/<user>/research
git clone https://github.com/<your-username>/toxicology-virtual-tissue.git
cd toxicology-virtual-tissue
```
Now both laptops have the repo. Keep them in sync with the daily loop below.

---

## Part 6 — The daily loop (this becomes muscle memory)

```bash
cd /c/Users/<user>/research/toxicology-virtual-tissue
git pull                 # 1. START of session: get the latest

#    ... do your work; Claude Code can help edit code, run CC3D, write the notebook entry ...

git add -A               # 2. stage everything you changed
git commit -m "describe what changed and why"
git push                 # 3. END of session: upload
```
**Pull before you start, push before you stop.** Never work on both laptops at once without
pushing/pulling in between (that causes merge conflicts).

Each work session, also add/update a dated entry in `lab-notebook/YYYY/` (copy
`lab-notebook/TEMPLATE.md`). That is your version-controlled lab notebook.

---

## Part 7 — Bring in the existing code and data

1. **CC3D prototype:** copy `H:\My Drive\Math Modeling in Toxicology\Old CC3D M1 to M2 files\`
   into `model/cc3d/`, then commit.
2. **ODE notebooks:** copy the `.ipynb` files from `Math Modeling in Toxicology\` into
   `model/ode/`. **Clear each notebook's outputs first** (Jupyter: Kernel → Restart & Clear
   Output), then commit — this keeps the repo small and diffs readable.
3. **Literature:** in Zotero, select your project items → right-click → Export → **BibTeX** →
   save into `literature/references.bib`. Keep the PDFs in Zotero; don't commit them.
4. **Large raw data** (big datasets, CC3D output dumps): leave in a Drive/university data
   folder or keep locally; it's gitignored. If you must version large files, ask about
   **Git LFS**.

---

## Part 8 — Start a NEW project from this template

This repo is designed to be your template. Two easy ways to reuse it:

- **GitHub template repo:** on GitHub, open this repo → Settings → check **Template repository**.
  Then for any new project: **Use this template** → new repo → `git clone` it. One click, same
  structure every time.
- **Or copy locally:** duplicate the folder, delete `.git/` and the `docs/`/`lab-notebook`
  contents, then `git init` again.

Keep every project under `C:\Users\<user>\research\<project-name>`, one repo each. Optionally
keep a tiny `research-index` repo (or a note) listing each project and its GitHub URL.

---

## Part 9 — Git cheat sheet

| Goal | Command |
|---|---|
| See what changed | `git status` |
| See line-level changes | `git diff` |
| Stage everything | `git add -A` |
| Snapshot with a message | `git commit -m "message"` |
| Upload to GitHub | `git push` |
| Download latest | `git pull` |
| View history | `git log --oneline` |
| Undo unstaged changes to a file | `git checkout -- <file>` |

---

## Troubleshooting

- **"Should I put the repo in H:\My Drive?"** No. Google Drive and git corrupt each other.
  Repos live in `C:\Users\<user>\research`; GitHub is the sync.
- **Accidentally committed a huge/secret file?** Add it to `.gitignore`, then
  `git rm --cached <file>` and commit. (Ask for help if it's already pushed — history rewrites
  are fiddly.)
- **Merge conflict after editing on both laptops?** `git status` lists the conflicted files;
  open them, keep the correct lines, `git add` them, then `git commit`. Prevent it by always
  pulling before you start and pushing before you stop.
