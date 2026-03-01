# Lab 3 – DNS + Fibonacci Services

## Overview
This project implements a DNS-based service discovery system with three components:

- **AS** – UDP DNS server (stores and resolves hostname → IP)  
- **FS** – HTTP Fibonacci server that registers with AS  
- **US** – HTTP server that queries AS to locate FS and returns Fibonacci results  

---

## Ports
AS: UDP 53533  
FS: HTTP 9090  
US: HTTP 8080  

Kubernetes NodePorts:  
AS → 30001/UDP  
FS → 30002/TCP  
US → 30003/TCP  

---

## Run with Docker

### Build
```bash
docker network create dnsnet
docker build -t as ./AS
docker build -t fs ./FS
docker build -t us ./US

Run
docker run --network dnsnet --name as -p 53533:53533/udp as
docker run --network dnsnet --name fs -p 9090:9090 fs
docker run --network dnsnet --name us -p 8080:8080 us

Register FS
curl -X PUT "http://localhost:9090/register" \
  -H "Content-Type: application/json" \
  -d '{"hostname":"fibonacci.com","ip":"fs","as_ip":"as","as_port":"53533"}'
Query via US
curl "http://localhost:8080/fibonacci?hostname=fibonacci.com&fs_port=9090&number=10&as_ip=as&as_port=53533"
Kubernetes (Extra Credit)
Deploy
docker build -t as:latest ./AS
docker build -t fs:latest ./FS
docker build -t us:latest ./US
kubectl apply -f deploy_dns.yml
kubectl get pods
Register FS
curl -X PUT "http://localhost:30002/register" \
  -H "Content-Type: application/json" \
  -d '{"hostname":"fibonacci.com","ip":"fs-svc","as_ip":"as-svc","as_port":"53533"}'
Query via US
curl "http://localhost:30003/fibonacci?hostname=fibonacci.com&fs_port=9090&number=10&as_ip=as-svc&as_port=53533"
