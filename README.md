# K8S-DNS

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![GitHub license](https://img.shields.io/github/license/NathanVaughn/k8s-dns)](https://github.com/NathanVaughn/k8s-dns/blob/main/LICENSE)

---

## Overview

This repository is for a Kubernetes Operator to manage DNS records
for my Kubernetes cluster. This is designed exclusively for my
use, so will not be useful for anyone else.

This publishes DNS records to [Cloudflare](https://www.cloudflare.com/)
and a local [Technitium](https://technitium.com/dns/) server.

## Deployment

The Docker container is located at `cr.nathanv.app/library/k8s-dns`.

The following environment variables are required:

- `CLOUDFLARE_API_TOKEN`
- `TECHNITIUM_API_TOKEN`
- `TECHNITIUM_HOST`

The custom resource definition in the `crd` folder also must be applied.

## Development

Use the provided [devcontainer](https://containers.dev/)
or run the following for local development:

```bash
# Install uv
# https://docs.astral.sh/uv/getting-started/installation/
uv tool install vscode-task-runner
vtr install
```
