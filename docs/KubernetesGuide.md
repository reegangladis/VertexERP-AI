# Kubernetes Production Manifests & Scaling Guide — VertexERP AI

## Overview
This document details the production Kubernetes architecture, autoscaling, ingress configuration, and security context.

---

## Kubernetes Objects Summary

| Object | File | Purpose |
|--------|------|---------|
| **Namespace** | `k8s/namespace.yaml` | Isolates `vertexerp-production` cluster environment |
| **API Deployment** | `k8s/api-deployment.yaml` | Runs 4 backend replicas with non-root security context |
| **Horizontal Pod Autoscaler** | `k8s/hpa.yaml` | Scales API pods dynamically from 4 to 20 replicas |
| **Ingress Controller** | `k8s/ingress.yaml` | Manages Nginx Ingress routing & Let's Encrypt TLS certs |
