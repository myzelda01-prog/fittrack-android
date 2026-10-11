# Simple image: just add the bits kivy/buildozer:latest doesn't have
# (liblzma-dev for Python's _lzmamodule, plus tooling to patch p4a).
# The base image already has Python 3.14, buildozer, Java 17, Android SDK/NDK,
# and licenses pre-accepted — the Kivy team's officially-blessed setup.
FROM kivy/buildozer:latest

ENV DEBIAN_FRONTEND=noninteractive

# Extra system deps for Python recipe compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
        liblzma-dev \
        sed grep findutils \
    && rm -rf /var/lib/apt/lists/*