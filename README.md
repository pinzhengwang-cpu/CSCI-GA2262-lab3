# Lab 3 – DNS + Fibonacci Services

## Overview
This project implements a DNS-based service discovery system with three components:

- **AS** – UDP DNS server that stores and resolves `hostname → IP`
- **FS** – HTTP Fibonacci server that registers with AS
- **US** – HTTP server that queries AS to locate FS and returns Fibonacci results

---

## Ports

| Service | Protocol | Port |
|--------|----------|------|
| AS | UDP | 53533 |
| FS | HTTP | 9090 |
| US | HTTP | 8080 |

### Kubernetes NodePorts (Extra Credit)

| Service | NodePort |
|--------|----------|
| AS | 30001 (UDP) |
| FS | 30002 (TCP) |
| US | 30003 (TCP) |

---

## Run with Docker

### Build images
```bash
docker network create dnsnet
docker build -t as ./AS
docker build -t fs ./FS
docker build -t us ./US
