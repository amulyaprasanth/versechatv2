FROM mcr.microsoft.com/devcontainers/python:3.14-bookworm

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  neovim \
  curl \
  ripgrep \
  build-essential \
  && rm -rf /var/lib/apt/lists/*
