# python-learn

My preparation notes and practice projects for a Strategy Reliability Engineering internship: modern Python tooling, Kubernetes and core Python.

## Contents

| Folder | What's inside |
|---|---|
| [`uv/`](uv/) | Guide to the [uv](https://docs.astral.sh/uv/) package manager, plus **`pinger`**, a small CLI that checks URLs and exits 0 (healthy) or 1 (unhealthy) |
| [`k8s/`](k8s/) | Hands-on Kubernetes guide using minikube: Deployments, Services, scaling, rolling updates, YAML manifests, and running `pinger` as a Job/CronJob |
| [`docs/`](docs/) | Study notes ([`imc-notes.pdf`](docs/imc-notes.pdf)) and an interactive explainer of how Kubernetes fits together ([`k8s-layers.html`](docs/k8s-layers.html)) |
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
```
