# Custom Buildozer CI image — Python 3.11 (Debian bullseye) + Buildozer +
# Android SDK + NDK + everything Buildozer needs.
FROM python:3.11-bullseye

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:${PATH}"

# Build deps for python-for-android (C extensions, SDL, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl wget git unzip zip xz-utils \
        build-essential ccache ninja-build pkg-config \
        libffi-dev libssl-dev libsqlite3-dev \
        autoconf automake libtool libltdl-dev \
        openjdk-17-jdk-headless \
        libtinfo5 \
    && rm -rf /var/lib/apt/lists/*

# Install Buildozer and Cython for ARM cross-compile
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir buildozer==1.5.0 cython

WORKDIR /workspace
CMD ["/bin/bash"]