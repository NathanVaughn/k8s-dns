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

## Assumptions

This Operator is not very smart. It assumes the IP address of a referenced
service will never change. If it does, DNS records will need to manually
updated. It also cannot handle referenced services being deleted or recreated.
Lastly, it assumes the zones have already been created in both providers.

## Deployment

The Docker container is located at `ghcr.io/nathanvaughn/k8s-dns`.

The following environment variables are required:

- `CLOUDFLARE_API_TOKEN`: This must have DNS zone edit permissions.
- `TECHNITIUM_API_TOKEN`
- `TECHNITIUM_HOST`: This is the URL of the Technitium server,
  including prefix and port. Example:
  `http://technitium-dns-service.technitium-dns.svc.cluster.local:5380`

The manifests in the `manifests` folder must also be applied:

```bash
kubectl apply -f https://raw.githubusercontent.com/NathanVaughn/k8s-dns/refs/heads/main/manifests/cluster-role-binding.yaml
kubectl apply -f https://raw.githubusercontent.com/NathanVaughn/k8s-dns/refs/heads/main/manifests/cluster-role.yaml
kubectl apply -f https://raw.githubusercontent.com/NathanVaughn/k8s-dns/refs/heads/main/manifests/dnsconfigs.yaml
kubectl apply -f https://raw.githubusercontent.com/NathanVaughn/k8s-dns/refs/heads/main/manifests/role-binding.yaml
kubectl apply -f https://raw.githubusercontent.com/NathanVaughn/k8s-dns/refs/heads/main/manifests/role.yaml
kubectl apply -f https://raw.githubusercontent.com/NathanVaughn/k8s-dns/refs/heads/main/manifests/service-account.yaml
```

## Development

Use the provided [devcontainer](https://containers.dev/)
or run the following for local development:

```bash
# Install uv
# https://docs.astral.sh/uv/getting-started/installation/
uv tool install vscode-task-runner
vtr install
```
