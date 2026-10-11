# Custom Buildozer CI image — Python 3.11 instead of the broken 3.14 in
# kivy/buildozer:latest. Build & push to ghcr.io once, then reuse via the
# `image:` field in build.yml.
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
        software-properties-common \
        ca-certificates curl wget git unzip zip \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        python3.11 python3.11-venv python3.11-dev python3.11-distutils \
        openjdk-17-jdk-headless \
        build-essential ccache \
        libffi-dev libssl-dev libsqlite3-dev \
        autoconf automake libtool pkg-config libltdl-dev \
        ninja-build \
    && rm -rf /var/lib/apt/lists/*

# Make python3 default to 3.11
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 100 \
    && update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 100 \
    && python3 -m pip install --upgrade pip setuptools wheel \
    && python3 -m pip install buildozer==1.5.0 cython

WORKDIR /workspace

# Aapt a known user so file ownership doesn't trip the runner
RUN useradd -m -s /bin/bash builder
USER builder
WORKDIR /home/builder