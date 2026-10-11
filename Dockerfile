# Custom Buildozer CI image — Ubuntu 22.04 (jammy) + Python 3.11 via pyenv +
# OpenJDK 17 + Buildozer + everything p4a needs.
#
# We don't use python:3.11-bullseye because that image's security pool
# has 404s for several packages. We don't use kivy/buildozer because it
# ships Python 3.14 (which has a broken pip in p4a's venv).

FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYENV_ROOT="/opt/pyenv" \
    PATH="/opt/pyenv/shims:/opt/pyenv/bin:/root/.local/bin:${PATH}"

# Build deps for python-for-android + Python 3.11 source build
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl wget git unzip zip xz-utils \
        build-essential ccache ninja-build pkg-config cmake \
        libssl-dev zlib1g-dev libbz2-dev libreadline-dev \
        libsqlite3-dev libncursesw5-dev tk-dev \
        libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev \
        libffi-dev libssl-dev libsqlite3-dev \
        autoconf automake libtool libltdl-dev \
        openjdk-17-jdk-headless \
    && rm -rf /var/lib/apt/lists/*

# Install pyenv and Python 3.11
RUN git clone --depth 1 https://github.com/pyenv/pyenv.git "$PYENV_ROOT" \
    && cd "$PYENV_ROOT" && git pull --unshallow || true
RUN pyenv install 3.11.13 \
    && pyenv global 3.11.13

# Install Buildozer and Cython for ARM cross-compile
RUN python -m pip install --upgrade pip setuptools wheel \
    && python -m pip install buildozer==1.5.0 cython

WORKDIR /workspace
CMD ["/bin/bash"]