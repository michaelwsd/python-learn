# Module 2 - Kubernetes

Goal: understand what Kubernetes is, why IMC runs its systems on it, and be comfortable using `kubectl` to deploy, inspect, scale, update, debug and roll back applications. At the end you package **your own `pinger`** into a container and run it inside the cluster.

How this guide is organised:

- **Part A - Background.** The problem Kubernetes solves and the core vocabulary. Read this first.
- **Part B - Setup on your Mac.** Already done once for you; how to start and stop the cluster.
- **Part C - The official tutorial, explained.** The six modules of https://kubernetes.io/docs/tutorials/kubernetes-basics/, with every command explained and **fixed for Apple Silicon Macs** where the tutorial's commands don't work.
- **Part D - Imperative vs declarative: YAML manifests.** How real teams actually use Kubernetes.
- **Part E - Project: run `pinger` in the cluster.** Containerise it, run it as a Job and a CronJob, watch Kubernetes react to its exit codes.
- **Part F - Debugging cheat sheet** for when things go wrong (they will, that's your job).
- **Part G - Command reference and checkpoint questions.**

Everything here was tested on your machine: minikube v1.39, Kubernetes v1.37, kubectl v1.37, Docker Desktop, arm64.

---

# Part A - Background

## A1. The problem

You have a program (say, a trading strategy service). To run it in production you need to answer:

- **Where does it run?** Which of the 200 servers has free CPU and memory?
- **What if it crashes?** Someone has to notice and restart it, at 3am.
- **What if the server dies?** Someone has to start it somewhere else.
- **How do others reach it?** If it moves servers, its IP address changes.
- **How do we run more copies** when load goes up, and spread traffic between them?
- **How do we ship a new version** without downtime, and roll back if it's broken?

Doing this by hand (SSH into servers, start processes, edit config files) doesn't scale and is error-prone. **Kubernetes (k8s)** automates all of it. You tell it *what* you want running; it figures out *where* and *how*, and keeps it that way.

## A2. Containers first

Kubernetes runs **containers**, so you need that concept first.

- A **container image** is a packaged, read-only snapshot of an application plus *everything it needs*: the OS libraries, Python, your dependencies, your code. Built from a recipe file called a `Dockerfile`.
- A **container** is a running instance of an image: an isolated process with its own filesystem, network and process list, sharing the host's kernel.
- A **registry** is a server that stores images (Docker Hub, `gcr.io`, `ghcr.io`, or a company's private registry). Image names look like `registry/name:tag`, e.g. `gcr.io/google-samples/kubernetes-bootcamp:v1`. The **tag** (`v1`) is the version.

Why containers? It's the same idea as `uv.lock` in Module 1, taken further: the lockfile pins your Python packages; an image pins **everything**, down to the OS. The image you test is byte-for-byte the image that runs in production.

Containers vs virtual machines: a VM emulates a whole computer with its own kernel (heavy, slow to boot). A container is just an isolated process on the existing kernel (light, starts in milliseconds).

## A3. The core idea: desired state and reconciliation

This is the single most important concept in Kubernetes.

You don't tell Kubernetes "start 3 copies of my app" (a command, done once). You tell it "**there should be** 3 copies of my app" (a desired state, stored permanently). Then **controllers** run a loop forever:

```
loop:
    observe actual state      (2 copies running)
    compare to desired state  (3 wanted)
    act to close the gap      (start 1 more)
```

This is called **reconciliation**. It's why Kubernetes is *self-healing*: if a container crashes or a server dies, actual state drifts from desired state, and a controller fixes it without anyone being paged. You'll see this happen in Part C.

## A4. Architecture of a cluster

A **cluster** is a set of machines running Kubernetes. Two kinds of parts:

```
┌─────────────────────── Control plane (the brain) ───────────────────────┐
│  kube-apiserver      the front door: every command goes through its API  │
│  etcd                database storing the desired state of everything    │
│  kube-scheduler      decides which node each new Pod should run on       │
│  controller-manager  runs the reconciliation loops (Deployments, Jobs...)│
└──────────────────────────────────────────────────────────────────────────┘
                 ▲ API calls                 │ instructions
                 │                           ▼
┌──── Node 1 (a worker machine) ────┐   ┌──── Node 2 ────┐   ...
│  kubelet         agent: starts/stops containers as told,  │
│                  reports health back to the control plane │
│  container runtime (containerd)   actually runs containers│
│  kube-proxy      network rules so Services reach Pods     │
│  [Pod] [Pod] [Pod]                                        │
└───────────────────────────────────┘
```

- **Node**: a machine (physical or VM) that runs your workloads.
- **kubectl** ("kube-control"): the command-line client. It just sends HTTP requests to the API server. Everything you do with kubectl, a script or a tool could do through the same API, which is how SRE automation works.
- **minikube**: a tool that runs a whole single-node cluster on your laptop (control plane and worker in one) for learning. On your Mac it runs inside a Docker container.

## A5. The objects you'll use

Everything in Kubernetes is an **object** (also called a resource) stored in etcd, with a `kind`, a `name`, a `spec` (desired state) and a `status` (actual state).

| Object | What it is | Analogy |
|---|---|---|
| **Pod** | The smallest unit: one or more containers that run together on one node, sharing an IP address and storage. Usually one container per Pod. Pods are **disposable**: they get created and destroyed, never repaired. | one running instance |
| **ReplicaSet** | Keeps N identical Pods running. You rarely touch it directly. | "always have 3 of these" |
| **Deployment** | Manages ReplicaSets to give you scaling, **rolling updates** and **rollbacks**. This is what you create for a long-running app. | the app's manager |
| **Service** | A **stable name and IP** in front of a changing set of Pods, with load balancing. Pods come and go; the Service address stays. | a phone number that forwards to whoever's on shift |
| **Label** | A `key=value` tag on any object, e.g. `app=kubernetes-bootcamp`. | sticky note |
| **Selector** | A query over labels, e.g. "all Pods with `app=kubernetes-bootcamp`". This is how a Deployment knows its Pods and a Service knows where to send traffic. | search filter |
| **Namespace** | A folder that groups objects, e.g. `default`, `kube-system`, or `trading-prod`. | directory |
| **Job** | Runs Pods **to completion** (exit 0), retrying on failure. | a batch task |
| **CronJob** | Creates a Job on a schedule. | `cron` |

How they relate:

```
Deployment ──creates/updates──► ReplicaSet ──keeps N of──► Pod, Pod, Pod
                                                            ▲   ▲   ▲
Service ──selects by label app=myapp──────────────────────┘───┘───┘
```

---

# Part B - Setup on your Mac

Already done in this session:

- `brew install minikube` (also installed a matching `kubectl` v1.37 at `/opt/homebrew/bin/kubectl`)
- Docker Desktop started
- `minikube start` run once, which downloaded everything (~500 MB)

**Daily use:**

```bash
open -a Docker              # Docker Desktop must be running first (whale icon in the menu bar)
minikube start              # start the cluster (fast after the first time)
minikube status             # host / kubelet / apiserver should say Running
kubectl get nodes           # one node called "minikube", STATUS Ready
...
minikube stop               # stop it when done: frees CPU and memory
minikube delete             # nuke the cluster entirely (to start fresh)
```

Three Mac-specific things to know, all verified:

1. **Old kubectl.** There's an older kubectl v1.34 at `/usr/local/bin/kubectl` (from Docker Desktop). The Homebrew v1.37 comes first on your `PATH`, so it wins. Check with `kubectl version` (client and server should both say v1.37). kubectl is only supported within one minor version of the cluster.
2. **The tutorial's sample image is Intel-only (amd64).** Your Mac is Apple Silicon (arm64). It still works, through emulation, but each Pod takes ~10 seconds to start. Be patient after creating or updating a Deployment.
3. **You can't reach the cluster's IP directly.** The tutorial uses `curl $(minikube ip):$NODE_PORT`. On a Mac with the Docker driver this **times out**, because the cluster lives inside a Docker VM. Use `kubectl port-forward` or `minikube service --url` instead (shown in Part C).

---

# Part C - The official tutorial, explained

Follow along in your terminal. Read the official page for each module alongside, but use the commands here: they're verified and fixed for your Mac.

## C1. Module 1 - Create a cluster

```bash
minikube start
minikube status
kubectl version
kubectl get nodes
kubectl cluster-info
```

- `minikube status` shows the parts from A4: `host` (the minikube container), `kubelet`, `apiserver`.
- `kubectl version` shows two versions: **Client** (kubectl on your Mac) and **Server** (the API server in the cluster). kubectl talking to the server proves the connection works.
- `kubectl get nodes` lists worker machines. You have one, `minikube`, with `ROLES control-plane` because it's also the control plane.

How does kubectl know where the cluster is? `minikube start` wrote connection details to `~/.kube/config` (a "kubeconfig"). See it with `kubectl config view` and `kubectl config current-context`. At IMC you'll have several contexts (dev, staging, prod clusters) and switching between them with `kubectl config use-context` is a daily thing. **Always check which context you're on before running anything destructive.**

## C2. Module 2 - Deploy an app

```bash
kubectl create deployment kubernetes-bootcamp --image=gcr.io/google-samples/kubernetes-bootcamp:v1
kubectl get deployments
kubectl get pods
```

**What happened behind the scenes:**
1. kubectl sent "create a Deployment named `kubernetes-bootcamp` running this image" to the API server, which stored it in etcd.
2. The Deployment controller created a ReplicaSet, which created a Pod (desired: 1 replica).
3. The scheduler picked a node for the Pod (only one choice here).
4. The kubelet on that node told containerd to pull the image and start the container.

Watch the Pod go through `ContainerCreating` to `Running`:

```bash
kubectl get pods --watch     # Ctrl+C to stop watching
```

`kubectl get deployments` columns:
- `READY 1/1`: ready replicas / desired replicas
- `UP-TO-DATE`: replicas running the latest version of the spec
- `AVAILABLE`: replicas available to users

**Reaching the Pod.** Pods live on a private network inside the cluster. The tutorial reaches it through `kubectl proxy`, which opens a tunnel from your Mac to the API server:

```bash
# terminal 2 (leave running):
kubectl proxy

# terminal 1:
curl http://localhost:8001/version        # talking to the API server directly
export POD_NAME=$(kubectl get pods -l app=kubernetes-bootcamp -o jsonpath='{.items[0].metadata.name}')
echo "Name of the Pod: $POD_NAME"
curl http://localhost:8001/api/v1/namespaces/default/pods/$POD_NAME:8080/proxy/
```

Expected: `Hello Kubernetes bootcamp! | Running on: kubernetes-bootcamp-... | v=1`

Notes:
- `curl localhost:8001/version` shows the API server is just an HTTP API. kubectl is a client for it.
- I changed the tutorial's `POD_NAME` command. The tutorial's go-template prints **every** Pod name, which breaks as soon as you have more than one Pod (Module 5). `-l app=kubernetes-bootcamp` selects by label, `-o jsonpath='{.items[0].metadata.name}'` extracts just the first name.
- `-o jsonpath=...` is how you extract fields from kubectl output in scripts. Try `kubectl get pod $POD_NAME -o yaml` to see every field you could extract.

## C3. Module 3 - Explore your app

The four commands you'll use most in your job:

```bash
kubectl get pods                    # list: name, status, restarts, age
kubectl describe pod $POD_NAME      # details + EVENTS (the most useful debugging output)
kubectl logs $POD_NAME              # the container's stdout/stderr
kubectl exec $POD_NAME -- env       # run a command inside the container
```

`kubectl describe` is your first stop when something is wrong. Scroll to the bottom: **Events** shows what Kubernetes did and what went wrong (`Scheduled`, `Pulling`, `Pulled`, `Created`, `Started`, or errors like `Failed to pull image`).

`kubectl logs` shows what the app printed. Every `print()` in your Python service ends up here. Useful flags: `-f` (follow live, like `tail -f`), `--previous` (logs from the last crashed container), `--tail=50`.

Get a shell inside the container:

```bash
kubectl exec -ti $POD_NAME -- bash
# now you're INSIDE the container:
cat server.js                 # the app's source code
curl http://localhost:8080    # call the app from inside
exit
```

- `--` separates kubectl's own arguments from the command to run in the container (same as `uv run -- ...` in Module 1).
- `-t` gives you a terminal, `-i` keeps input open: together, an interactive shell.
- Note: many production images are minimal and have no `bash` or `curl`. Then use `sh`, or `kubectl debug` to attach a debugging container.

## C4. Module 4 - Expose your app with a Service

Pods are mortal: when one is replaced, the new one has a **different IP**. Something talking to Pod IPs directly would break constantly. A **Service** gives a stable address and load-balances over whichever Pods currently match its selector.

```bash
kubectl get services                    # "kubernetes" is the API server's own Service
kubectl expose deployment/kubernetes-bootcamp --type=NodePort --port 8080
kubectl get services
kubectl describe service/kubernetes-bootcamp
```

In the `describe` output, look at:
- `Selector: app=kubernetes-bootcamp`: which Pods this Service sends traffic to.
- `Endpoints: 10.244.0.3:8080`: the current Pod IPs behind it. This list updates automatically as Pods come and go.
- `NodePort: 30096/TCP` (yours will differ): a port opened on every node.

**Service types:**

| Type | Reachable from | Use |
|---|---|---|
| `ClusterIP` (default) | inside the cluster only | service-to-service traffic: most Services |
| `NodePort` | `<any node IP>:<30000-32767>` | simple external access, dev/test |
| `LoadBalancer` | an external IP from a cloud load balancer | production external access on cloud |
| `ExternalName` | n/a, it's a DNS alias to an outside name | pointing at external services |

**Reaching it from your Mac.** The tutorial's `curl http://$(minikube ip):$NODE_PORT` **times out** on Mac (verified). Use either:

```bash
# Option 1: port-forward (works with any cluster, the one you'll use at work)
kubectl port-forward service/kubernetes-bootcamp 8080:8080   # leave running
curl http://localhost:8080                                    # in another terminal

# Option 2: minikube's helper
minikube service kubernetes-bootcamp --url    # prints e.g. http://127.0.0.1:58148, leave running
curl http://127.0.0.1:58148                   # use the URL it printed
```

`port-forward LOCAL:REMOTE` tunnels your Mac's port 8080 to the Service's port 8080 through the API server. It's the standard way to poke at something inside a cluster.

**Labels and selectors:**

```bash
kubectl describe deployment                         # see Labels and Selector
kubectl get pods -l app=kubernetes-bootcamp         # -l = filter by label
kubectl get services -l app=kubernetes-bootcamp
kubectl label pods $POD_NAME version=v1             # add a label to a running Pod
kubectl get pods --show-labels
kubectl get pods -l version=v1
```

Labels are just metadata. `version=v1` doesn't pin or change anything; it only makes the Pod findable by that label. Their power is that selectors (Deployments, Services, `-l` queries) are built on them.

**Delete the Service and prove the app is still there:**

```bash
kubectl delete service -l app=kubernetes-bootcamp
kubectl get services                                         # gone
kubectl exec -ti $POD_NAME -- curl http://localhost:8080     # app still runs inside the cluster
```

The Service and the Pods are independent objects. Deleting the Service removed the *way in*, not the app.

## C5. Module 5 - Scale your app

```bash
kubectl get rs                                   # the ReplicaSet the Deployment created
kubectl scale deployment/kubernetes-bootcamp --replicas=4
kubectl get deployments
kubectl get pods -o wide                         # -o wide adds IP and NODE columns
```

You now have 4 Pods, each with its own IP. The ReplicaSet's name is `<deployment>-<hash>`, and each Pod's name is `<replicaset>-<random>`. That's how you can tell which ReplicaSet (and so which version) a Pod belongs to.

**See the self-healing loop from A3 in action:**

```bash
kubectl delete pod $POD_NAME     # kill one Pod
kubectl get pods                 # a NEW Pod is already being created to replace it
```

You deleted a Pod, actual state (3) no longer matched desired state (4), so the ReplicaSet controller created a new one. Nobody had to do anything. This is why you "never repair Pods": you delete them and let the controller replace them.

**Load balancing across Pods.** Expose it again (the tutorial says to use `LoadBalancer`, but that needs `minikube tunnel` on minikube; NodePort plus port-forward is simpler and teaches the same thing):

```bash
kubectl expose deployment/kubernetes-bootcamp --type=NodePort --port 8080
kubectl describe service/kubernetes-bootcamp     # Endpoints now lists 4 IPs
```

To see different Pods answer, call the Service from **inside** the cluster (port-forward pins you to one Pod, so it won't show balancing):

```bash
kubectl run tmp --rm -ti --image=curlimages/curl --restart=Never -- \
  sh -c 'for i in 1 2 3 4 5 6 7 8; do curl -s kubernetes-bootcamp:8080; echo; done'
```

- `kubectl run ... --rm -ti --restart=Never` starts a throwaway Pod, attaches to it, and deletes it on exit.
- `kubernetes-bootcamp:8080`: inside the cluster, **a Service's name is a DNS hostname**. That's how services find each other.
- You'll see different Pod names in `Running on: ...`. Distribution isn't strict round-robin, just spread out.

Scale down:

```bash
kubectl scale deployment/kubernetes-bootcamp --replicas=2
kubectl get pods            # two Pods go to Terminating
```

## C6. Module 6 - Rolling update and rollback

Upgrade the app to v2 with zero downtime:

```bash
kubectl set image deployment/kubernetes-bootcamp kubernetes-bootcamp=docker.io/jocatalin/kubernetes-bootcamp:v2
kubectl rollout status deployment/kubernetes-bootcamp     # watch it progress
kubectl get rs                                            # OLD ReplicaSet scaled to 0, NEW one has the Pods
kubectl get pods
```

`set image <deployment> <container-name>=<new-image>`: the container is named after the deployment because `create deployment` named it that way.

**What a rolling update does:** the Deployment creates a **new ReplicaSet** with the new image and gradually shifts Pods from old to new: start some new Pods, wait until they're ready, stop some old ones, repeat. Users always have running Pods to talk to. Two settings control the pace (`kubectl get deploy kubernetes-bootcamp -o jsonpath='{.spec.strategy}'`):
- `maxSurge: 25%`: how many **extra** Pods above the desired count may exist during the update
- `maxUnavailable: 25%`: how many Pods may be **missing** during the update

(The tutorial says both default to 1. On your cluster they're 25%, which is the real Kubernetes default.)

Verify v2 is serving:

```bash
kubectl exec deploy/kubernetes-bootcamp -- curl -s localhost:8080    # ...| v=2
```

`deploy/kubernetes-bootcamp` instead of a Pod name: kubectl picks one of the Deployment's Pods for you. Much easier than copying Pod names.

**A broken release, and rollback.** Deploy an image tag that doesn't exist:

```bash
kubectl set image deployment/kubernetes-bootcamp kubernetes-bootcamp=gcr.io/google-samples/kubernetes-bootcamp:v10
kubectl get pods
```

You'll see new Pods stuck in `ErrImagePull` / `ImagePullBackOff`, **while most of the old v2 Pods keep running**. That's the rolling update protecting you: it won't kill old Pods until new ones become ready, which these never do. Users still get served (by fewer Pods).

```bash
kubectl describe pods | grep -A5 Events        # "Failed to pull image ... not found"
kubectl rollout history deployment/kubernetes-bootcamp
kubectl rollout undo deployment/kubernetes-bootcamp
kubectl rollout status deployment/kubernetes-bootcamp
kubectl get pods                                # all Running again, on v2
```

`rollout undo` goes back to the **previous revision** (not a named version). Each change to the Pod template creates a revision; `rollout history` lists them, and `rollout undo --to-revision=N` picks a specific one.

This is the heart of your team's job: **safe releases, fast detection of bad ones, fast rollback.**

**Clean up:**

```bash
kubectl delete deployment/kubernetes-bootcamp service/kubernetes-bootcamp
kubectl get all
```

---

# Part D - Imperative vs declarative: YAML manifests

Everything so far was **imperative**: commands that say "do this now" (`create`, `expose`, `scale`, `set image`). Good for learning and emergencies. But real teams work **declaratively**: they write the desired state in **YAML files** (manifests), keep them in git, and run `kubectl apply`.

Why: the YAML in git is the record of what *should* be running. Changes go through code review, history shows who changed what, and you can recreate the whole system from the files. (Same principle as `pyproject.toml` + `uv.lock` in git.)

**See the YAML behind what you created imperatively:**

```bash
kubectl create deployment kubernetes-bootcamp --image=gcr.io/google-samples/kubernetes-bootcamp:v1 --dry-run=client -o yaml
```

`--dry-run=client -o yaml` prints the object instead of creating it. A great way to generate a starting manifest.

**Anatomy of a manifest** (save as `k8s/bootcamp.yaml`):

```yaml
apiVersion: apps/v1               # which API group/version defines this kind
kind: Deployment                  # what type of object
metadata:
  name: kubernetes-bootcamp       # its name (unique per kind per namespace)
  labels:
    app: kubernetes-bootcamp
spec:                             # DESIRED STATE
  replicas: 3
  selector:                       # which Pods this Deployment owns...
    matchLabels:
      app: kubernetes-bootcamp
  template:                       # ...and the template for creating them
    metadata:
      labels:
        app: kubernetes-bootcamp  # must match the selector above
    spec:
      containers:
        - name: kubernetes-bootcamp
          image: gcr.io/google-samples/kubernetes-bootcamp:v1
          ports:
            - containerPort: 8080
---                               # separates multiple objects in one file
apiVersion: v1
kind: Service
metadata:
  name: kubernetes-bootcamp
spec:
  type: ClusterIP
  selector:
    app: kubernetes-bootcamp      # send traffic to Pods with this label
  ports:
    - port: 8080                  # the Service's port
      targetPort: 8080            # the container's port
```

Every object has the same four top-level keys: `apiVersion`, `kind`, `metadata`, `spec`. (Kubernetes adds a fifth, `status`, which you never write.)

```bash
kubectl apply -f k8s/bootcamp.yaml       # create or update to match the file
kubectl get deploy,svc,pods
# edit the file: change replicas to 5
kubectl diff -f k8s/bootcamp.yaml        # preview what would change (like git diff)
kubectl apply -f k8s/bootcamp.yaml       # apply the change
kubectl delete -f k8s/bootcamp.yaml      # delete everything in the file
```

`apply` is idempotent: run it 10 times, you get the same result. It only changes what differs. That's what makes it safe to run from CI.

Explore any field's documentation from the terminal:

```bash
kubectl explain deployment.spec.strategy
kubectl explain pod.spec.containers.livenessProbe
```

---

# Part E - Project: run `pinger` in the cluster

Your `pinger` from Module 1 is a perfect Kubernetes **Job**: it runs, checks URLs, and exits with 0 (healthy) or 1 (unhealthy). Kubernetes reads that exit code. Tested end to end.

Before starting: in `uv/pinger/pyproject.toml`, make sure `pytest` is only in `[dependency-groups] dev`, not in `dependencies` (`uv remove pytest` if needed).

## E1. Write a Dockerfile

Create `uv/pinger/Dockerfile`:

```dockerfile
FROM python:3.14-slim
COPY --from=ghcr.io/astral-sh/uv:0.13.7 /uv /bin/uv
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --locked --no-dev --no-install-project
COPY src ./src
RUN uv sync --locked --no-dev
ENV PATH="/app/.venv/bin:$PATH"
ENTRYPOINT ["pinger"]
```

Line by line:

| Line | Meaning |
|---|---|
| `FROM python:3.14-slim` | Start from an official image that has Python 3.14 on a minimal Debian. Must satisfy your `requires-python`. |
| `COPY --from=ghcr.io/astral-sh/uv:0.13.7 /uv /bin/uv` | Copy just the `uv` binary out of uv's official image. Pinned version, so builds are reproducible. |
| `WORKDIR /app` | `cd /app` (creating it) for all following steps. |
| `ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy` | Precompile `.pyc` files (faster startup); copy files instead of linking from the cache (there's no persistent cache in an image). |
| `COPY pyproject.toml uv.lock README.md ./` | Copy only the dependency definition first. |
| `RUN uv sync --locked --no-dev --no-install-project` | Install dependencies only (httpx...), exactly from the lock (`--locked`, Module 1 D6), without dev tools (`--no-dev`), and not your project yet. |
| `COPY src ./src` | Now copy your code. |
| `RUN uv sync --locked --no-dev` | Install your project itself, creating `.venv/bin/pinger`. |
| `ENV PATH=...` | Put the venv's `bin` first, so `pinger` is found. |
| `ENTRYPOINT ["pinger"]` | The command the container runs. Arguments given at run time are appended to it. |

**Why copy dependencies before code?** Docker caches each step as a **layer** and reuses it if its inputs haven't changed. Your code changes often; your dependencies rarely. With this order, editing `__init__.py` only re-runs the last few steps, and the slow dependency install comes from cache.

Also create `uv/pinger/.dockerignore` so local junk isn't sent into the build:

```
.venv
dist
.git
__pycache__
```

## E2. Build the image inside minikube

```bash
cd ~/Developer/python-learn/uv/pinger
minikube image build -t pinger:0.1.0 .
minikube image ls | grep pinger          # docker.io/library/pinger:0.1.0
```

`minikube image build` builds the image directly inside the cluster's container runtime, so Pods can use it without a registry. (At IMC, CI would build the image and push it to a company registry, and clusters pull from there.) `-t pinger:0.1.0` is the name and tag. Use a real version tag, not `latest`: with `latest`, Kubernetes always tries to pull from a registry, which fails for a local-only image.

## E3. Run it as a Job

Start something for pinger to check:

```bash
kubectl create deployment kubernetes-bootcamp --image=gcr.io/google-samples/kubernetes-bootcamp:v1
kubectl expose deployment/kubernetes-bootcamp --port 8080       # ClusterIP: internal only
kubectl rollout status deployment/kubernetes-bootcamp
```

Run pinger against it, imperatively first:

```bash
kubectl create job pinger-ok --image=pinger:0.1.0 -- \
  pinger http://kubernetes-bootcamp:8080 http://kubernetes-bootcamp.default.svc.cluster.local:8080
kubectl get jobs --watch                 # COMPLETIONS 1/1, then Ctrl+C
kubectl logs job/pinger-ok
```

Output (from the test run):

```
http://kubernetes-bootcamp:8080: 200 in 56 ms
http://kubernetes-bootcamp.default.svc.cluster.local:8080: 200 in 17 ms
Checked 2 URL(s) in 78 ms (async)
```

- Both URLs are the **same Service**. Inside a cluster, a Service is reachable as `<name>` (same namespace) or the full DNS name `<name>.<namespace>.svc.cluster.local`.
- The Job is `Complete` because pinger **exited 0**. Your exit code design from Module 1 is exactly what Kubernetes uses to decide success.

## E4. A failing Job, declaratively

Save as `k8s/pinger-job.yaml`:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: pinger-bad
spec:
  backoffLimit: 2                  # retry up to 2 times after the first failure
  template:
    spec:
      restartPolicy: Never         # a failed Pod is not restarted in place; the Job makes a new Pod
      containers:
        - name: pinger
          image: pinger:0.1.0
          args: ["http://kubernetes-bootcamp:8080", "http://does-not-exist:8080"]
```

`args` are appended to the image's `ENTRYPOINT` (`pinger`), so the container runs `pinger http://kubernetes-bootcamp:8080 http://does-not-exist:8080`.

```bash
kubectl apply -f k8s/pinger-job.yaml
kubectl get pods -l job-name=pinger-bad --watch
kubectl logs job/pinger-bad
kubectl describe job pinger-bad
```

What you'll see (from the test run):

```
pinger-bad-kfbnj   0/1   Error   ...
pinger-bad-hd5m4   0/1   Error   ...
pinger-bad-pdhtk   0/1   Error   ...

http://kubernetes-bootcamp:8080: 200 in 14 ms
http://does-not-exist:8080: DOWN (ConnectError: [Errno -2] Name or service not known)

Pods Statuses:    0 Active / 0 Succeeded / 3 Failed
Warning  BackoffLimitExceeded   Job has reached the specified backoff limit
```

pinger exited 1, so Kubernetes marked the Pod `Error` and retried (1 try + 2 retries = 3 Pods), then gave up and marked the Job **Failed**. An alerting system would page someone on that. A health checker that always exited 0 would make all of this invisible.

## E5. Run it on a schedule with a CronJob

```bash
kubectl create cronjob pinger-cron --image=pinger:0.1.0 --schedule="*/5 * * * *" -- \
  pinger http://kubernetes-bootcamp:8080
kubectl get cronjobs
kubectl create job pinger-manual --from=cronjob/pinger-cron    # trigger once now instead of waiting
kubectl logs job/pinger-manual
```

`*/5 * * * *` is cron syntax: minute, hour, day-of-month, month, day-of-week. `*/5` in the minute field means "every 5 minutes". https://crontab.guru explains any expression.

Your challenge: write the CronJob as a YAML file instead (start from `kubectl create cronjob ... --dry-run=client -o yaml`), set `successfulJobsHistoryLimit: 3` and `failedJobsHistoryLimit: 3`, and apply it.

## E6. Ship a new version (the full release loop)

1. Change something visible in pinger (e.g. add `"OK"`/`"UNHEALTHY"` to the output line).
2. Bump the version: `uv version --bump patch` (0.1.1).
3. Rebuild: `minikube image build -t pinger:0.1.1 .`
4. Update the CronJob to the new image: `kubectl set image cronjob/pinger-cron pinger-cron=pinger:0.1.1`
5. Trigger it and check the logs show the new output.

That's the release cycle your team supervises at IMC: change, version, build, roll out, verify.

## E7. Clean up

```bash
kubectl delete cronjob pinger-cron           # also deletes Jobs it created (they're owned by it)
kubectl delete job pinger-ok pinger-bad
kubectl delete deployment/kubernetes-bootcamp service/kubernetes-bootcamp
minikube stop
```

Note: deleting the CronJob also deleted `pinger-manual`, because Jobs created from a CronJob carry an **owner reference** to it, and Kubernetes garbage-collects owned objects when the owner goes. Same mechanism as Deployment → ReplicaSet → Pod.

---

# Part F - Debugging cheat sheet

The usual order when something's wrong: **`get` → `describe` (Events) → `logs` → `exec`**.

| Pod status | Meaning | Look at |
|---|---|---|
| `Pending` | Not scheduled yet: no node has enough CPU/memory, or volumes aren't ready | `kubectl describe pod` Events |
| `ContainerCreating` | Pulling image / starting. Normal briefly (slow for amd64 images on your Mac) | wait; then `describe` |
| `ErrImagePull` / `ImagePullBackOff` | Can't pull the image: wrong name/tag, no access to registry | `describe` Events show the exact error |
| `CrashLoopBackOff` | Container starts and keeps crashing; Kubernetes waits longer between restarts | `kubectl logs <pod> --previous` (the crashed run's logs) |
| `Error` | Container exited non-zero (normal for a failed Job) | `kubectl logs` |
| `Completed` | Exited 0 (normal for a Job) | |
| `Running` but not working | App is up but misbehaving | `logs -f`, `exec` in, `port-forward` and test |
| `Terminating` (stuck) | Waiting for the process to shut down | `describe`, and check finalizers |

Other handy commands:

```bash
kubectl get events --sort-by=.lastTimestamp       # everything that happened recently, cluster-wide
kubectl get pods -A                               # all namespaces (-A = --all-namespaces)
kubectl top pods                                  # CPU/memory use (needs: minikube addons enable metrics-server)
kubectl get pod <name> -o yaml                    # full spec and status
```

---

# Part G - Reference and checkpoint

## G1. kubectl command reference

| Command | Does |
|---|---|
| `kubectl get <kind>` | list objects (`pods`, `deploy`, `rs`, `svc`, `jobs`, `cronjobs`, `nodes`, `all`) |
| `kubectl get ... -o wide / -o yaml / -o jsonpath=...` | more columns / full object / extract fields |
| `kubectl get ... -l key=value` | filter by label |
| `kubectl get ... --watch` | keep watching for changes |
| `kubectl describe <kind> <name>` | details and Events |
| `kubectl logs <pod>` (`-f`, `--previous`, `job/<name>`, `deploy/<name>`) | container output |
| `kubectl exec -ti <pod> -- <cmd>` | run a command in a container |
| `kubectl create deployment/job/cronjob ...` | create imperatively |
| `kubectl expose deployment/<name> --port N [--type T]` | create a Service |
| `kubectl scale deployment/<name> --replicas=N` | scale |
| `kubectl set image deployment/<name> <container>=<image>` | rolling update |
| `kubectl rollout status / history / undo` | follow / list / roll back a rollout |
| `kubectl apply -f file.yaml` / `diff -f` / `delete -f` | declarative workflow |
| `kubectl port-forward svc/<name> LOCAL:REMOTE` | tunnel to a Service from your Mac |
| `kubectl run tmp --rm -ti --image=... --restart=Never -- <cmd>` | throwaway debug Pod |
| `kubectl explain <kind.field>` | docs for any field |
| `kubectl config get-contexts / use-context` | which cluster you're talking to |
| `... --dry-run=client -o yaml` | print the object instead of creating it |

Short names: `po` pods, `deploy` deployments, `rs` replicasets, `svc` services, `ns` namespaces, `cj` cronjobs.

## G2. Checkpoint questions

You're ready for Module 3 (Fluent Python) when you can answer these:

1. What does "desired state and reconciliation" mean? Give an example you saw happen.
2. What's the difference between a Pod, a ReplicaSet and a Deployment? Why do you almost never create Pods directly?
3. Why do Services exist? What would break without them?
4. How does a Service know which Pods to send traffic to?
5. What are the four Service types, and which one is the default?
6. During a rolling update to a broken image, why did the app keep serving traffic?
7. What does `kubectl rollout undo` go back to?
8. Your Pod is in `CrashLoopBackOff`. What are your first two commands?
9. Why does the Dockerfile copy `pyproject.toml`/`uv.lock` and install dependencies **before** copying `src/`?
10. Why does it matter that pinger exits 1 on failure when it runs as a Job?
11. Imperative vs declarative: what's the difference, and why do teams prefer declarative?
12. Inside the cluster, how did pinger reach the bootcamp app by name?

<details>
<summary>Answers (try first!)</summary>

1. You declare what should exist (e.g. 4 replicas); controllers continuously compare actual state to desired state and act to close the gap. Example: deleting a Pod in C5 made the ReplicaSet immediately create a replacement.
2. A Pod is one running instance (one or more containers). A ReplicaSet keeps N identical Pods running. A Deployment manages ReplicaSets to add rolling updates and rollbacks. Bare Pods aren't replaced if they die or their node fails, and can't be updated in a controlled way, so you create Deployments (or Jobs) and let them manage Pods.
3. Pods are disposable and get new IPs when replaced; with several replicas there are several IPs. A Service gives one stable name/IP and load-balances across the current Pods. Without it, every client would need to track changing Pod IPs.
4. By its label **selector**: it targets all Pods whose labels match (e.g. `app=kubernetes-bootcamp`). The matching Pod IPs appear as its Endpoints and update automatically.
5. ClusterIP (default, internal only), NodePort (a port on every node), LoadBalancer (external cloud load balancer), ExternalName (DNS alias to an external name).
6. A rolling update only removes old Pods once new Pods are ready. The new Pods never became ready (image pull failed), so most old Pods were kept (only up to `maxUnavailable` could be taken down) and kept serving.
7. The previous revision of the Deployment's Pod template (or a specific one with `--to-revision`).
8. `kubectl describe pod <name>` (Events, exit codes, restart count) and `kubectl logs <name> --previous` (output of the run that crashed).
9. Docker caches layers. Dependencies change rarely and code changes often; installing dependencies in an earlier layer means code edits reuse the cached dependency layer and rebuilds are fast.
10. Kubernetes uses the exit code to decide whether the Job succeeded. Exit 1 makes it retry and eventually mark the Job Failed, which monitoring can alert on. If pinger always exited 0, failures would be invisible.
11. Imperative: commands that perform actions now (`create`, `scale`, `set image`). Declarative: you write the desired state in YAML and `kubectl apply` makes the cluster match. Declarative files live in git, so changes are reviewed, versioned, reproducible and can be applied safely and repeatedly from CI.
12. Cluster DNS: every Service gets a DNS name, `<service>` within the same namespace or `<service>.<namespace>.svc.cluster.local` in full.

</details>

When you're done, say "quiz me on kubernetes" for a harder follow-up round.
