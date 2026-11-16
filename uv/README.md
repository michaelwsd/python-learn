# Module 1 - uv

Goal: understand how Python projects, environments and dependencies work, and be fluent with uv, the tool that manages them.

How this guide is organised:

- **Part A - Background.** The problems uv solves and the words you will keep seeing (package, PyPI, virtual environment, lockfile, wheel...). Read this first, it makes everything else obvious.
- **Part B - Anatomy of a uv project.** Every file uv creates, line by line.
- **Part C - Command reference.** Every command and flag used in this module, explained.
- **Part D - Hands-on lab.** You build `pinger`, a small health-check CLI an SRE might write. Each step says what to run, what happens, and why.
- **Part E - Checkpoint questions**, with answers hidden at the end.

Written against **uv 0.13.7** (check yours with `uv --version`). Official docs: https://docs.astral.sh/uv/

---

# Part A - Background

## A1. The problem

When you write `import httpx`, Python has to find the `httpx` code somewhere on disk. Three questions decide whether your code works:

1. **Which Python?** 3.12 and 3.14 behave differently. Your laptop, your teammate's laptop and the production server may each have a different one.
2. **Which packages are installed, and where?** If every project installs into one shared place, project A needing `httpx 0.27` and project B needing `httpx 0.28` will clash.
3. **Which exact versions?** "httpx" today is not the same code as "httpx" in six months. Neither are its own dependencies.

If any of these differ between your machine and production, you get the classic "works on my machine" bug. In a trading firm that can mean a strategy failing at market open. uv exists to make all three answers explicit, automatic and reproducible.

## A2. Vocabulary

**Package** - a bundle of Python code you can install, e.g. `httpx`, `pytest`, `numpy`.

**PyPI** (Python Package Index, https://pypi.org) - the public server packages are downloaded from. Companies like IMC often run an internal mirror too.

**Dependency** - a package your code needs. **Transitive dependency** - a package your dependency needs. `httpx` needs `httpcore`, `anyio`, `certifi`, `idna`... You never asked for those, but you need them.

**Dependency resolution** - finding one version of every package (direct and transitive) that satisfies all the constraints at once. This is a hard search problem. uv's resolver is a big part of why it is fast.

**Version specifier** - a rule for acceptable versions:

| Specifier | Meaning |
|---|---|
| `httpx` | any version |
| `httpx==0.28.1` | exactly 0.28.1 |
| `httpx>=0.28` | 0.28 or newer |
| `httpx>=0.28,<0.29` | at least 0.28, below 0.29 |
| `httpx~=0.28.1` | "compatible release": >=0.28.1 and <0.29 |

Versions usually follow **MAJOR.MINOR.PATCH**. A major bump may break your code. Minor adds features. Patch fixes bugs.

**Virtual environment (venv)** - a folder (here `.venv/`) holding its own Python link and its own `site-packages` directory, where installed packages live. Each project gets its own, so projects can't clash. "Activating" a venv just puts `.venv/bin` first on your `PATH`, so typing `python` finds the venv's Python. With uv you rarely activate, because `uv run` uses the venv for you.

**Lockfile** - a file recording the **exact** version (plus a checksum hash) of every package, including transitive ones, that the resolver picked. Anyone installing from the lockfile gets the identical set. The hash also guarantees the download hasn't been tampered with.

**Build / wheel / sdist** - to install your own project as a package, it gets "built" into:
- a **wheel** (`.whl`): a ready-to-install zip. Installing it is just unzipping.
- an **sdist** (source distribution, `.tar.gz`): the raw source, built on the target machine.

**Build backend** - the tool that does the building. uv ships its own, `uv_build`. Others exist (hatchling, setuptools...).

**Entry point / console script** - a declaration like `pinger = "pinger:main"`. When the package is installed, a small executable called `pinger` is created that imports module `pinger` and calls its `main()` function. That's how `uv run pinger` works.

**TOML** - the config file format used by `pyproject.toml` and `uv.lock`. `[section]` starts a table, `key = value` sets a value, `[[name]]` is one item in a list of tables.

## A3. What uv replaces

Before uv, Python needed a pile of separate tools. uv does all of their jobs, 10-100x faster:

| Job | Old tool(s) | uv |
|---|---|---|
| Install Python versions | pyenv, python.org installers | `uv python install` |
| Create a venv | `python -m venv` | automatic (or `uv venv`) |
| Install packages | pip | `uv add` / `uv sync` |
| Lock versions | pip-tools, poetry, `pip freeze` | `uv lock` |
| Run CLI tools in isolation | pipx | `uvx`, `uv tool install` |
| Build and publish | build, twine | `uv build`, `uv publish` |

Conda (which you had via Anaconda) is a different ecosystem with its own package format. You don't need it for this work.

---

# Part B - Anatomy of a uv project

After `uv init pinger`, `uv add httpx` and `uv add --dev pytest`, the project looks like this:

```
pinger/
├── .git/               # git repository (uv init runs `git init` for you)
├── .gitignore          # tells git to ignore .venv, __pycache__, dist/...
├── .python-version     # which Python to use
├── README.md           # project description (referenced by pyproject.toml)
├── pyproject.toml      # project definition: what you WANT
├── uv.lock             # exact resolved versions: what you GOT
├── .venv/              # the installed environment (disposable)
└── src/
    └── pinger/
        └── __init__.py # your code
```

## B1. `pyproject.toml` - the project definition

This is the standard Python project file (defined by PEPs 518, 621 and 735, so other tools read it too). You edit it, or `uv add` / `uv remove` edit it for you.

```toml
[project]                                   # standard metadata about your project
name = "pinger"                             # package name (what `pip install` would use)
version = "0.1.0"                           # your project's own version
description = "Add your description here"  # one-line summary
readme = "README.md"                        # this file MUST exist, or building fails
authors = [
    { name = "michaelwsd", email = "michaelwsd@icloud.com" }
]
requires-python = ">=3.12"                  # Python versions your project supports
dependencies = [                            # runtime dependencies: needed to RUN the code
    "httpx>=0.28.1",                        #   added by `uv add httpx`
]

[project.scripts]                           # console scripts / entry points
pinger = "pinger:main"                      # command `pinger` -> module `pinger`, function `main`

[build-system]                              # HOW to build this project into a wheel
requires = ["uv_build>=0.13.7,<0.14.0"]     # the build tool to download
build-backend = "uv_build"                  # the Python object that does the build

[dependency-groups]                         # dependencies for DEVELOPING, not running
dev = [                                     # `uv add --dev X` puts X here
    "pytest>=9.2.0",
    "ruff>=0.14.0",
]

# [tool.uv]                                 # optional uv-specific settings go here
```

Things to notice:

- `uv add httpx` writes a **lower bound** (`>=0.28.1`, the version it just installed), not an exact pin. The exact pin lives in `uv.lock`. This split is deliberate: `pyproject.toml` states what is *acceptable*, `uv.lock` records what was *chosen*.
- **`dependencies` vs `[dependency-groups] dev`**: runtime deps ship with your package. Dev deps (test runners, linters) are only for people working on the code. If someone installs your tool, they don't get pytest.
- **`requires-python`** is a promise about compatibility. uv refuses to use a Python outside this range, and resolves dependencies so they work on *every* version in the range.
- **`[build-system]`** is only present for packaged projects (see `--package` in Part C). Its presence means "this project is installable", so `uv run` builds and installs it into `.venv`. That's why a missing `README.md` broke `uv run pinger` earlier: the build reads the readme.

## B2. `uv.lock` - the lockfile

Generated by uv. **Commit it to git. Never edit it by hand.** A trimmed entry:

```toml
version = 1
revision = 5                         # lockfile format version (internal to uv)
requires-python = ">=3.12"           # copied from pyproject.toml

[[package]]                          # one block per package in the whole tree
name = "httpx"
version = "0.28.1"                   # the EXACT version chosen
source = { registry = "https://pypi.org/simple" }   # where it came from
dependencies = [                     # what it depends on (transitive deps)
    { name = "anyio" },
    { name = "certifi" },
    { name = "httpcore" },
    { name = "idna" },
]
sdist = { url = "https://files.pythonhosted.org/...httpx-0.28.1.tar.gz",
          hash = "sha256:75e98c...", size = 141406 }
wheels = [
    { url = "https://files.pythonhosted.org/...httpx-0.28.1-py3-none-any.whl",
      hash = "sha256:d90983...", size = 73517 },
]
```

- It includes **every** package (`anyio`, `idna`...), not just the ones you added.
- `hash` is a SHA-256 checksum. If the downloaded file doesn't match, uv refuses to install it.
- It's **universal**: it records choices for macOS, Linux and Windows at once. Your Mac and IMC's Linux servers install the same versions from the same file.

## B3. `.python-version`

One line, e.g. `3.12`. It tells uv which interpreter to build `.venv` with. If you don't have that Python, uv downloads it automatically. Commit it. Change it with `uv python pin`.

Not the same as `requires-python`: `.python-version` is *the one version this checkout uses*, `requires-python` is *the range the project supports*. The pin must fall inside the range.

## B4. `.venv/`

```
.venv/
├── bin/
│   ├── python -> (link to the real interpreter)
│   ├── pinger      # console script generated from [project.scripts]
│   ├── pytest      # console scripts of installed packages
│   └── activate    # script used by `source .venv/bin/activate`
├── lib/python3.12/site-packages/   # where installed packages actually live
└── pyvenv.cfg      # records which interpreter this venv was built from
```

Fully disposable: `rm -rf .venv` then `uv sync` rebuilds it identically from `uv.lock`. Never commit it. uv's `.gitignore` already excludes it.

## B5. `src/pinger/__init__.py` - the src layout

Your code lives in `src/<package_name>/`. A folder containing `__init__.py` is a Python **package**. The `src/` folder stops you accidentally importing the local folder instead of the installed package, so tests run against what users actually get.

## B6. Where uv keeps things outside your project

- **Cache** (`uv cache dir`, usually `~/.cache/uv`): every downloaded package, stored once and shared. Installing into a new venv just links files from the cache, which is why it's near-instant.
- **Managed Pythons** (`uv python dir`): interpreters downloaded by `uv python install`.
- **Tools** (`uv tool dir`): isolated envs for `uv tool install`. Their executables go in `~/.local/bin`.

---

# Part C - Command reference

## C1. Projects

| Command | What it does |
|---|---|
| `uv init <name>` | Create a new project folder with `pyproject.toml`, `.python-version`, `README.md`, `.gitignore`, `src/`, and a git repo. Without `<name>`, initialises the current directory. |
| `uv add <pkg>` | Add a dependency: edit `pyproject.toml`, re-resolve, update `uv.lock`, install into `.venv`. All in one step. |
| `uv remove <pkg>` | The reverse: remove from `pyproject.toml`, re-lock, uninstall. |
| `uv lock` | Resolve dependencies and write `uv.lock`, without installing anything. |
| `uv sync` | Make `.venv` exactly match `uv.lock`: install missing packages **and remove extra ones**. Creates `.venv` if needed. |
| `uv run <cmd>` | Lock if needed, sync if needed, then run `<cmd>` inside the project's venv. |
| `uv tree` | Print the dependency tree, showing which package pulled in which. |
| `uv build` | Build a wheel and sdist into `dist/`. |
| `uv version` | Show (or with `--bump minor` etc., change) the project version. |

Flags used in this module:

| Flag | On | Meaning |
|---|---|---|
| `--package` | `uv init` | Make an installable package: `src/` layout + `[build-system]` + `[project.scripts]`. In uv 0.13 this is already the default for `uv init` (and for `--app`). |
| `--no-package` | `uv init` | Flat layout: a top-level `main.py`, no `[build-system]`, no console script, no build step. Run with `uv run main.py`. Good for scripts that will never be installed. |
| `--app` | `uv init` | An application (the default). In uv 0.13 it gets the same packaged `src/` layout as `--package`. |
| `--lib` | `uv init` | A library meant to be imported by other code (adds a `py.typed` marker, no console script). |
| `--bare` | `uv init` | Only create `pyproject.toml`, nothing else. |
| `--python 3.12` / `-p` | most commands | Use this Python version. |
| `--dev` | `uv add` / `uv remove` | Put the package in the `dev` dependency group instead of `dependencies`. |
| `--group <name>` | `uv add` | Put it in a custom group, e.g. `--group lint`. |
| `--upgrade-package <pkg>` / `-P` | `uv lock`, `uv add`, `uv sync` | Allow this one package to move to a newer version, keep everything else as locked. |
| `--upgrade` / `-U` | `uv lock` | Allow **all** packages to upgrade. |
| `--locked` | `uv sync`, `uv run` | Fail if `uv.lock` is out of date with `pyproject.toml` instead of updating it. Use in CI. |
| `--frozen` | `uv sync`, `uv run` | Use `uv.lock` as-is without even checking it. |
| `--no-dev` | `uv sync`, `uv run` | Skip dev dependencies (what you'd do in a production image). |
| `--with <pkg>` | `uv run` | Temporarily add a package for this one run only. |
| `--no-project` | `uv run` | Ignore the surrounding project, don't install it. |
| `--` | `uv run` | Everything after `--` goes to your command, not to uv. `uv run -- pinger --help` passes `--help` to pinger. |

## C2. Single-file scripts

| Command | What it does |
|---|---|
| `uv init --script file.py` | Create a script with an empty inline metadata block. |
| `uv add --script file.py <pkg>` | Add a dependency to the script's inline metadata. |
| `uv run file.py` | Run it in a cached, throwaway environment built from its metadata. |
| `uv lock --script file.py` | Create `file.py.lock` for full reproducibility. |

**Inline script metadata** (PEP 723) is a special comment block at the top of a script, so a single `.py` file declares its own dependencies:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "rich",
# ]
# ///
```

**Shebang** - a first line like `#!/usr/bin/env -S uv run --script` tells the OS which program runs the file, so after `chmod +x file.py` you can run it with `./file.py`. (`env -S` lets the line contain several words.)

## C3. Python versions

| Command | What it does |
|---|---|
| `uv python list` | Show available and installed Pythons. Add `--only-installed` to filter. |
| `uv python install 3.12` | Download a Python build managed by uv. |
| `uv python pin 3.12` | Write `3.12` to `.python-version`. |
| `uv python find` | Print the path of the Python uv would use here. |

## C4. Tools (CLI apps you use, not import)

| Command | What it does |
|---|---|
| `uvx <tool>` | Short for `uv tool run`. Run a tool in a temporary isolated env. Nothing installed permanently. |
| `uvx --from <pkg> <cmd>` | When the package name differs from the command, e.g. package `httpie` provides command `http`. |
| `uvx <tool>@<version>` | Run a specific exact version, e.g. `ruff@0.6.0`, or `@latest`. |
| `uv tool install <tool>` | Install permanently into its own isolated env, put its command on your `PATH` (`~/.local/bin`). |
| `uv tool list` / `upgrade` / `uninstall` | Manage installed tools. |

How to choose:

- **`uvx ruff`** - one-off or occasional use.
- **`uv tool install ruff`** - you use it every day, in every project.
- **`uv add --dev ruff`** - the project depends on it: everyone on the team (and CI) must use the **same version**, recorded in `uv.lock`. Use this for anything that touches your project's code (pytest, ruff, mypy).

## C5. Housekeeping

| Command | What it does |
|---|---|
| `uv self update` | Upgrade uv itself. |
| `uv cache dir` / `uv cache clean` | Show / wipe the download cache. |
| `uv pip ...` | pip-compatible interface (`uv pip install`, `uv pip list`...). For legacy workflows. Prefer `uv add` in projects. |

---

# Part D - Hands-on lab: build `pinger`

Time: ~2 hours. Type every command yourself. After each step, look at what changed on disk: that's how the model in Parts A and B becomes real.

## D0. Environment hygiene

```bash
uv --version
echo $VIRTUAL_ENV      # should print nothing
which python3          # ideally /opt/homebrew/bin/python3
```

If `VIRTUAL_ENV` prints a path, run `deactivate`. A stale activated venv doesn't break uv (it warns and ignores it), but it confuses *you* about which `python` you're getting.

## D1. Create the project

You already have `pinger/`. To redo it from scratch for practice:

```bash
cd ~/Developer/python-learn/uv
rm -rf pinger
uv init pinger
cd pinger
```

**What happened:** uv created the files from Part B (except `.venv` and `uv.lock`, which appear on first use) and ran `git init`. `.python-version` holds the Python uv found, and `requires-python` is set to match.

Explore:

```bash
ls -a
cat pyproject.toml
cat .python-version
cat src/pinger/__init__.py
git status
```

Now run it:

```bash
uv run pinger
ls -a
```

**What happened**, in order:
1. uv read `pyproject.toml` and saw no `uv.lock`, so it **resolved** dependencies (none yet) and wrote `uv.lock`.
2. It saw no `.venv`, so it **created** one using the Python from `.python-version`.
3. Because there's a `[build-system]`, it **built and installed your project** into `.venv`. That generated the `.venv/bin/pinger` executable from `[project.scripts]`.
4. It **ran** `.venv/bin/pinger`, which called `pinger.main()`.

Confirm step 3 yourself:

```bash
cat .venv/bin/pinger     # a tiny Python script that imports pinger and calls main()
```

## D2. Add dependencies

```bash
uv add httpx
```

Then look at the three places that changed:

```bash
cat pyproject.toml       # "httpx>=0.28.1" appeared under dependencies
grep -A3 'name = "httpx"' uv.lock    # exact version + source
ls .venv/lib/python*/site-packages/  # httpx AND its dependencies are installed
```

Add development tools:

```bash
uv add --dev pytest ruff
cat pyproject.toml       # new [dependency-groups] dev section
uv tree                  # see who depends on what
```

**Try it - upgrades and pins:**

```bash
uv add 'httpx==0.27.0'   # pin an older exact version (quotes stop the shell treating = and < specially)
uv tree | head -5        # httpx 0.27.0
uv add 'httpx>=0.28'     # relax the constraint again
uv lock --upgrade-package httpx   # let just httpx move to the newest allowed version
uv tree | head -5
```

Watch `git diff uv.lock` between steps to see how the lock changes.

## D3. Write the tool

Replace the contents of `src/pinger/__init__.py` with a CLI that:

1. Accepts one or more URLs as arguments. Use `argparse` from the standard library.
2. Sends a GET request to each with a 2 second timeout using `httpx.get(url, timeout=2)`.
3. Prints one line per URL: status code and latency in milliseconds (`time.perf_counter()`), or the error message if it failed.
4. Exits with code `0` if every URL returned 2xx, `1` otherwise. Use `sys.exit(code)` or return the code from `main` and call `raise SystemExit(main())`.

Why exit codes matter: they're how machines read your tool's result. Shell scripts (`pinger ... && deploy`), CI pipelines, cron alerts and Kubernetes health probes (Module 2) all look only at the exit code: 0 = success, anything else = failure.

Test it:

```bash
uv run pinger https://docs.astral.sh https://httpbin.org/status/503 https://does-not-exist.invalid
echo $?                  # prints the exit code of the last command: should be 1
uv run pinger https://docs.astral.sh
echo $?                  # should be 0
```

Stretch goal: check all URLs **concurrently** with `httpx.AsyncClient` and `asyncio.gather`. Time both versions with `time uv run pinger ...` across 5+ URLs.

## D4. Lint, format and test

**ruff** is a linter (finds bugs and bad style) and formatter (rewrites your code into a consistent style). **pytest** runs tests.

```bash
uv run ruff check .      # report problems
uv run ruff check . --fix  # auto-fix what it can
uv run ruff format .     # reformat files
```

Write a test. Pull the "is this status code healthy?" logic into its own small function (no network involved), so it's easy to test:

```bash
mkdir tests
# create tests/test_pinger.py with e.g.:
#   from pinger import is_healthy
#   def test_200_is_healthy(): assert is_healthy(200)
#   def test_503_is_not():     assert not is_healthy(503)
uv run pytest -q         # -q = quiet output
```

`uv run pytest` works because pytest is in your dev group (so it's in `.venv`) and your project is installed in `.venv` (so `from pinger import ...` works).

## D5. Python versions

```bash
uv python list --only-installed
uv python install 3.13
uv python pin 3.13       # rewrites .python-version
cat .python-version
uv run python --version  # uv rebuilds .venv with 3.13 automatically
```

Now try a version **outside** `requires-python`. If yours says `>=3.12`:

```bash
uv python pin 3.11       # uv refuses: 3.11 doesn't satisfy requires-python
```

Pin back to your original version afterwards. Lesson: `.python-version` must sit inside `requires-python`.

## D6. Reproducibility drill (the most important step)

Pretend you're a teammate who just ran `git clone` on your repo. They have `pyproject.toml`, `uv.lock` and `.python-version`, but no `.venv`:

```bash
rm -rf .venv
uv sync --locked
uv run pinger https://docs.astral.sh
```

`uv sync --locked` rebuilt the identical environment from the lockfile, and would have failed loudly if the lock didn't match `pyproject.toml`.

Now break it on purpose. Open `pyproject.toml` and **by hand** add `"rich"` to `dependencies` (don't use `uv add`). Then:

```bash
uv sync --locked         # error: the lockfile needs to be updated
uv lock                  # re-resolve, rich now in uv.lock
uv sync --locked         # works
```

This is exactly the check a CI pipeline runs. Remove `rich` again with `uv remove rich`.

Also notice what `uv sync` does with extras:

```bash
uv run --with cowsay python -c "print('hi')"   # temporary extra, not saved anywhere
uv pip install --python .venv cowsay   # sneak a package into .venv behind uv's back
uv sync                  # "- cowsay": sync makes .venv EXACTLY match the lock
```

Careful: unlike `uv add`/`uv sync`/`uv run`, the `uv pip` commands install into whatever venv is **activated** (`$VIRTUAL_ENV`) if there is one, not the project's `.venv`. That's why `--python .venv` is spelled out above. One more reason to keep stale venvs deactivated.

## D7. Single-file scripts

SREs write lots of one-off scripts. Inline metadata lets a single file carry its own dependencies, no project needed.

```bash
cd ~/Developer/python-learn/uv
uv init --script check_disk.py --python 3.12
cat check_disk.py        # see the `# /// script` block
uv add --script check_disk.py rich
cat check_disk.py        # rich added to the block
```

Write the script: use `shutil.disk_usage("/")` to get total, used and free bytes, and print them in a `rich` table (`from rich.table import Table`, `from rich.console import Console`). Show the usage percentage in red if over 80%.

```bash
uv run check_disk.py
```

Make it run like a normal executable:

```bash
# make the first line of check_disk.py exactly:
#   #!/usr/bin/env -S uv run --script
chmod +x check_disk.py   # mark the file as executable
./check_disk.py
```

## D8. Tools

```bash
uvx pycowsay "hello IMC"                       # downloads, runs, leaves nothing installed
uvx --from httpie http GET https://httpbin.org/get   # package httpie, command http
uvx ruff@latest --version
uv tool install ruff                           # permanent install
uv tool list
which ruff                                     # ~/.local/bin/ruff
```

## D9. Build and install your package

```bash
cd ~/Developer/python-learn/uv/pinger
uv build
ls dist/                 # pinger-0.1.0-py3-none-any.whl and pinger-0.1.0.tar.gz
```

The wheel filename has a meaning: `name-version-pythontag-abitag-platformtag`. `py3-none-any` means "any Python 3, no compiled code, any OS".

Install your own tool globally, then run it from anywhere:

```bash
uv tool install dist/pinger-0.1.0-py3-none-any.whl
cd ~
pinger https://docs.astral.sh
uv tool uninstall pinger
```

---

# Part E - Checkpoint

You're ready for Module 2 (Kubernetes) when you can answer these without looking:

1. In `pyproject.toml`, where does the `pinger` command come from, and what exactly does it call?
2. What's in `uv.lock` that isn't in `pyproject.toml`, and why have both?
3. Why does `uv add httpx` write `>=0.28.1` in `pyproject.toml` rather than `==0.28.1`?
4. Why use `uv run pytest` rather than `uvx pytest` in a project?
5. What's the difference between `.python-version` and `requires-python`?
6. In CI, why would you want `uv sync --locked` to *fail* instead of quietly updating the lockfile?
7. You email `check_disk.py` to a colleague who has uv but nothing else. What do they run?
8. When do you use `uvx ruff` vs `uv tool install ruff` vs `uv add --dev ruff`?
9. Why did `uv run pinger` fail when `README.md` was missing, and why wouldn't a `--no-package` project hit that error?
10. What's the difference between `uv sync` and `uv run --with`?

When you're done, say "quiz me on uv" for a harder follow-up round.

<details>
<summary>Answers (try first!)</summary>

1. `[project.scripts]` has `pinger = "pinger:main"`. When the project is installed into `.venv`, uv generates `.venv/bin/pinger`, which imports module `pinger` and calls `main()`.
2. The exact version of **every** package, including transitive ones, plus source URLs and SHA-256 hashes. `pyproject.toml` states what's acceptable (human intent, kept loose so upgrades are easy). `uv.lock` records what was chosen (machine output, exact, so installs are reproducible).
3. A lower bound says "I need at least the version I tested with" while still allowing future bug-fix upgrades. Exact reproducibility is the lockfile's job, so `pyproject.toml` doesn't need to over-constrain. Over-constraining also causes resolution conflicts when other packages depend on yours.
4. `uvx` runs the tool in a separate isolated env that doesn't contain your project or its dependencies, so imports of your code fail. Its version also isn't recorded in `uv.lock`. `uv run pytest` uses the project's `.venv` with the locked pytest version.
5. `requires-python` is the range of versions the project supports (affects resolution and is published with the package). `.python-version` is the one version this checkout's `.venv` uses. The pin must be within the range.
6. A mismatch means someone changed `pyproject.toml` without re-locking. Silently re-locking in CI would test a different set of packages than anyone reviewed or committed. Failing forces the lock change to go through review, so CI and production run exactly what's in git.
7. `uv run check_disk.py` (or `./check_disk.py` if it has the shebang and is executable). uv reads the inline metadata, installs the right Python and `rich` into a cached env, and runs it.
8. `uvx`: occasional one-off use, nothing installed. `uv tool install`: a tool you personally use everywhere, on your `PATH`. `uv add --dev`: the project depends on it, so the whole team and CI share one locked version.
9. The project has a `[build-system]`, so `uv run` builds and installs it, and the build reads the `readme` file named in `pyproject.toml`. A `--no-package` project has no build step: uv only installs its dependencies and never builds the project itself.
10. `uv sync` makes `.venv` exactly match `uv.lock` (permanent, removes extras). `uv run --with X` adds `X` temporarily for that one command only, without touching `pyproject.toml`, `uv.lock` or `.venv`.

</details>
