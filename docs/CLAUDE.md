# Fluent Python study: context for Claude

This file records how the Fluent Python study sessions work, so a new session can pick up where the last one stopped. It adds to the global `CLAUDE.md` (in `configs/claude/`).

## Goal

- Preparing for an **IMC Trading internship** in **strategy reliability engineering**: building automation tools (health checks, monitoring, alerting, retries, log processing, running checks across many machines).
- The book is *Fluent Python*, 2nd edition, by Luciano Ramalho. The local PDF is `/Users/michaelwsd/Other/Books/fluent-python.pdf`.
- **PDF page = book page + 30.**
- The roadmap (chapters, pages, key ideas) is in [`fluent-python/README.md`](../fluent-python/README.md).

## How each chapter is taught

1. **Setup:** create `fluent-python/chNN/` with the following:
   - a runnable demo of the book's main examples (for example `inheritance_demo.py`);
   - `exercises_chNN.py`: stubs that raise `NotImplementedError`, each with a comment block that explains the task and shows example input and output;
   - `test_chNN.py`: pytest tests for the exercises, including source or structure checks when the exercise is about *how* to write the code (for example "uses `super().__init__(`").

   Before handing over, check three things:
   - a reference solution (kept in the scratchpad, not in the repo) passes every test;
   - the stubs fail;
   - `ruff check` and `ruff format` are clean.

   Tell the user the run commands and list the sections.
2. **Walk through the sections one at a time.** The user says "next" to move on. For each section:
   - explain plainly, step by step, assuming no prior knowledge of the topic;
   - **run every example** (python or mypy) before showing its output, and say that it was run;
   - link the section to its exercise and give the `-k` command;
   - end with a short summary and "Say next for Section N".
3. **Exercises:** the user writes the code; Claude answers questions about it without giving away the full solution unless asked.
4. **Review and quiz:** code review, then a short quiz in the user's own words.

The user often asks follow-up questions that start with "so basically...". Confirm what is right, and correct the part that isn't, with a small runnable example.

### Commands

Run them from `fluent-python/`. Clear `VIRTUAL_ENV` first, so uv uses the project's environment:

```bash
VIRTUAL_ENV= uv run python ch14/inheritance_demo.py
VIRTUAL_ENV= uv run pytest ch14 -v -k stack
VIRTUAL_ENV= uv run mypy some_file.py
VIRTUAL_ENV= uv run ruff check . && VIRTUAL_ENV= uv run ruff format --check .
```

## Progress (as of 2026-11-20)

| Chapter | Sections | Exercises | Notes PDF | Quiz |
|---|---|---|---|---|
| 1 Data Model | done | pass | done | done |
| 2 Sequences | done | **2 tests still fail**: `test_run_go`, `test_parse_trade_full_width_columns` | done | done |
| 3 Dicts and Sets | done | pass | done | done |
| 6 References | done | pass | done | done |
| 7 Functions | done | pass | done | done |
| 8 Type Hints | done | pass (18/18) | done (pages 16-18) | **skipped** |
| 14 Inheritance | done (all 6 sections) | **not started** (15 of 16 tests fail on the stubs) | done (pages 19-20) | not done |

**Next steps:**
1. The user does the Ch 14 exercises, then a Ch 14 review and quiz. A Ch 8 quiz is still open if wanted.
2. Optionally, fix the 2 failing Ch 2 tests.
3. Extension chapters, in this order, chosen for the reliability-engineering role:
   - **Ch 9** (decorators: retry and timing wrappers);
   - **Ch 18** (context managers, `try`/`else`/`finally`);
   - **Ch 20** (concurrent executors: parallel checks), with **Ch 19** as background;
   - **Ch 17** (generators for log pipelines);
   - **Ch 5** (data classes);
   - Ch 13 only if time allows.

   This differs from the extension list in `fluent-python/README.md` (5, 13, 17, 18). Update the README when starting them.
4. After the book: a small project, a CLI health-check tool, using `logging`, `subprocess`, `argparse`, `pathlib`, `ThreadPoolExecutor` and `pytest` + `unittest.mock`. It ties together decorators, context managers and executors.

## Notes PDF

- **Output:** `docs/fluent-python-notes.pdf`.
- **Source:** `docs/src/fluent-python-notes.html`. Edit the source, never the PDF.
- Add to the PDF **only when the user asks**. A chapter's section list in the contents (`.ci` line on the cover) is updated with it.

### Build and check

From `docs/`:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --no-pdf-header-footer --print-to-pdf=fluent-python-notes.pdf src/fluent-python-notes.html
pdfinfo fluent-python-notes.pdf | grep Pages
pdftoppm -f 19 -l 20 -r 80 -png fluent-python-notes.pdf <scratchpad>/page   # then view the images
```

**Always render and look at every changed page before reporting.** Check for:
- wrapped code lines;
- sections split across pages;
- overflow onto an extra page.

### HTML structure

- **Chapter:** `<section class="ch chNN">` holds the chapter. Its first `<div class="sec">` contains the `h2`, the `.meta` line, the `.lead` box and the first `h3`. Add `.chNN` to the `.ch8 ...` CSS selector lists so the chapter gets the same spacing.
- **Section:** `<div class="sec">` contains one `h3` and its rows. Use `class="sec pb"` to force a section onto a new page.
- **Row:** `<div class="two keep">` is two equal columns: **text on the left, code on the right**. Use `<div class="stack">` to put several `<pre>` blocks in one column.
- **Code:** `<pre>`. Comments go in `<span class="c">`. Escape `<`, `>` and `&`.

### Writing rules (from user feedback)

- Be concise. Give each idea an example, and put **each standalone example in its own code block**.
- **The wording must match the example exactly**: the text names what the code shows, and the code shows only what the text claims. Each example illustrates one point only, with nothing extra.
- Titles are in book-style Title Case, with type and module names in `<code>`.
- Never use the em dash (U+2014); use "-" or rephrase.
- **Lines that are too long:** shorten or split the comment rather than letting the line wrap. At the usual zoom, about 46 characters fit in the code column.

### Layout rules

These are also saved in auto-memory (`pdf-notes-layout`).

1. Every chapter starts on a new page.
2. Sections are never split across pages.
3. Spacing is uniform, set in CSS only; never add spacing inline.
4. Fill spare room with a per-page `style="zoom:N"` on that page's sections:
   - capped at about 1.15-1.18;
   - only as far as the page still fits and no code line wraps;
   - find the value by rebuilding and checking the page count.

   The last page of a chapter may stay partly empty.

## Repo housekeeping

- Commit only when the user asks. No co-author lines.
- Run `git status` before committing. The docs HTML and PDF change together, so commit them together.
