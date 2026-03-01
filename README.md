Here is **exactly your content converted into clean GitHub Markdown**.
Single block. No extra text. No UI junk.

````markdown
## Run containers

```bash
docker run --network dnsnet --name as -p 53533:53533/udp as
docker run --network dnsnet --name fs -p 9090:9090 fs
docker run --network dnsnet --name us -p 8080:8080 us
````

## Register FS → AS

```bash
curl -X PUT "http://localhost:9090/register" \
  -H "Content-Type: application/json" \
  -d '{"hostname":"fibonacci.com","ip":"fs","as_ip":"as","as_port":"53533"}'
```

## Query Fibonacci via US

```bash
curl "http://localhost:8080/fibonacci?hostname=fibonacci.com&fs_port=9090&number=10&as_ip=as&as_port=53533"
```

Expected output:

```json
{"fibonacci":55}
```

---

## Kubernetes (Extra Credit)

### Build images

```bash
docker build -t as:latest ./AS
docker build -t fs:latest ./FS
docker build -t us:latest ./US
```

### Deploy

```bash
kubectl apply -f deploy_dns.yml
kubectl get pods
kubectl get svc
```

### Register FS (NodePort)

```bash
curl -X PUT "http://localhost:30002/register" \
  -H "Content-Type: application/json" \
  -d '{"hostname":"fibonacci.com","ip":"fs-svc","as_ip":"as-svc","as_port":"53533"}'
```

### Query via US (NodePort)

```bash
curl "http://localhost:30003/fibonacci?hostname=fibonacci.com&fs_port=9090&number=10&as_ip=as-svc&as_port=53533"
```

Expected output:

```json
{"fibonacci":55}
```

---

## Notes

* AS stores DNS records persistently
* FS returns HTTP 400 for invalid input
* US returns HTTP 400 for missing parameters

