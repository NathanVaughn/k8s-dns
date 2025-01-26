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

## Deployment

The Docker container is located at `ghcr.io/nathanvaughn/k8s-dns`.

The following environment variables are required:

- `CLOUDFLARE_API_TOKEN`: This must have DNS zone edit permissions.
- `TECHNITIUM_API_TOKEN`
- `TECHNITIUM_HOST`

The custom resource definition in the `crd` folder also must be applied.

The following permissions are also required:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: k8s-dns-account
  namespace: k8s-dns
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: k8s-dns-role-cluster
rules:
  - apiGroups: [""]
    resources: [services, namespaces]
    verbs: [get, list, watch]
  - apiGroups: [apiextensions.k8s.io]
    resources: [customresourcedefinitions]
    verbs: [get, list, watch]
  - apiGroups: [admissionregistration.k8s.io/v1, admissionregistration.k8s.io/v1beta1]
    resources: [validatingwebhookconfigurations, mutatingwebhookconfigurations]
    verbs: [create, patch]
  - apiGroups: [""]
    resources: [events]
    verbs: [create]
  - apiGroups: [nathanv.me]
    resources: [dnsconfigs]
    verbs: [get, list, watch, patch, update]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: k8s-dns-role
  namespace: k8s-dns
rules:
  - apiGroups: [""]
    resources: [events]
    verbs: [create]
  - apiGroups: [nathanv.me]
    resources: [dnsconfigs]
    verbs: [get, list, watch, patch, update]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: k8s-dns-rolebinding-cluster
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: k8s-dns-role-cluster
subjects:
  - kind: ServiceAccount
    name: k8s-dns-account
    namespace: k8s-dns
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: k8s-dns-rolebinding
  namespace: k8s-dns
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: k8s-dns-role
subjects:
  - kind: ServiceAccount
    name: k8s-dns-account
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
