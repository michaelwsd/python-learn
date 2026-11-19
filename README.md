# Python Prep

Preparation notes and practice projects on modern Python tooling, Kubernetes and core Python.

## Contents

| Folder | What's inside |
|---|---|
| [`uv/`](uv/) | Guide to the [uv](https://docs.astral.sh/uv/) package manager, plus **`pinger`**, a small CLI that checks URLs and exits 0 (healthy) or 1 (unhealthy) |
| [`k8s/`](k8s/) | Hands-on Kubernetes guide using minikube: Deployments, Services, scaling, rolling updates, YAML manifests, and running `pinger` as a Job/CronJob |
| [`fluent-python/`](fluent-python/) | Working through *Fluent Python* (2nd ed.): a demo, exercises and pytest tests per chapter. Roadmap in [`fluent-python/README.md`](fluent-python/README.md) |
| [`docs/`](docs/) | Study notes as PDFs: [`imc-notes.pdf`](docs/imc-notes.pdf), [`fluent-python-notes.pdf`](docs/fluent-python-notes.pdf) (chapter-by-chapter notes) and [`k8s-layers.pdf`](docs/k8s-layers.pdf) (how Kubernetes fits together). HTML sources in [`docs/src/`](docs/src/) |
| [`python-basics/`](python-basics/) | Jupyter notebooks from a Python fundamentals course, with my exercise work |
| [`configs/`](configs/) | My global `CLAUDE.md` and VS Code settings, keybindings and extension list |

## Quick start

```bash
# pinger (needs uv)
cd uv/pinger
uv sync
uv run pinger https://example.com
uv run pytest

# Kubernetes labs (needs Docker + minikube)
minikube start
# then follow k8s/README.md

# Fluent Python exercises (needs uv)
cd fluent-python
uv run python ch07/functions_demo.py   # run a chapter's demo
uv run pytest ch07 -v                  # check a chapter's exercises
```
