# official python image
FROM python:3.14-slim 

# copy the uv binary from uv's official image to /bin/uv so uv works as a command
COPY --from=ghcr.io/astral-sh/uv:0.13.7 /uv /bin/uv

# set the working folder in the image's own complete linux filesystem
WORKDIR /app 

# sets environment variables 
# UV_COMPILE_BYTECODE=1 precompiles .py to .pyc bytecode so python doesn't have to compile 
# them everytime a container starts -> faster startup

# UV_LINK_MODE=copy: uv normally links files from its cache to save disk space. In an image, the
# cache isn't kept, so links would point at nothing. This tells uv to copy real files instead. 
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy 

# copy only the dependency files 
COPY pyproject.toml uv.lock README.md ./

# install dependencies only 
# --locked: use exactly what's in uv.lock
# --no-dev, skip the dev group (pytest, ruff)
# --no-install-project: install only the dependencies, not pinger itself (it can't anyway)
RUN uv sync --locked --no-dev --no-install-project

# copy the source code 
COPY src ./src 

# install the actual project
# why two runs instead of one (layer caching): Docker caches each step and re-runs everything 
# after the first step whose inputs changed. With two steps, when one line changes in the source
# file, only this line runs again, the dependencies won't be installed again. 
RUN uv sync --locked --no-dev 

# pinger is installed in /app/.venv/bin; prepend it to PATH so the
# "pinger" command (and the venv's python) can be found by name
ENV PATH="/app/.venv/bin:$PATH"

# run time line, when a container starts from this image, it runs pinger
# kubectl run ... --image=pinger:0.1.0 -- https://example.com
#                  └───────┬─────────┘
# container runs:  pinger https://example.com
ENTRYPOINT ["pinger"]



