from flask import Flask, request, jsonify
import socket
import requests

app = Flask(__name__)

def send_udp(host: str, port: int, msg: str, timeout=2.0) -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(timeout)
    s.sendto(msg.encode("utf-8"), (host, port))
    data, _ = s.recvfrom(4096)
    return data.decode("utf-8", errors="ignore")

def parse_dns_response(resp: str) -> dict:
    # Expect:
    # TYPE=A
    # NAME=fibonacci.com VALUE=IP TTL=10
    kv = {}
    lines = [ln.strip() for ln in resp.splitlines() if ln.strip()]
    for ln in lines:
        for part in ln.split():
            if "=" in part:
                k, v = part.split("=", 1)
                kv[k.strip().upper()] = v.strip()
    return kv

@app.get("/fibonacci")
def fibonacci():
    hostname = request.args.get("hostname")
    fs_port = request.args.get("fs_port")
    number = request.args.get("number")
    as_ip = request.args.get("as_ip")
    as_port = request.args.get("as_port")

    # If any missing => 400
    if not all([hostname, fs_port, number, as_ip, as_port]):
        return jsonify({"error": "missing parameters"}), 400

    # Query AS via UDP to get FS IP
    query_msg = f"TYPE=A\nNAME={hostname}\n"

    try:
        dns_resp = send_udp(as_ip, int(as_port), query_msg)
    except Exception:
        return jsonify({"error": "dns query failed"}), 500

    if dns_resp.strip() == "ERROR":
        return jsonify({"error": "dns record not found"}), 500

    kv = parse_dns_response(dns_resp)
    fs_ip = kv.get("VALUE")
    if not fs_ip:
        return jsonify({"error": "bad dns response"}), 500

    # Call FS to get fibonacci
    try:
        r = requests.get(
            f"http://{fs_ip}:{int(fs_port)}/fibonacci",
            params={"number": number},
            timeout=3.0,
        )
    except Exception:
        return jsonify({"error": "fs request failed"}), 500

    # If FS returns 400, US should also return 400 (bad format)
    if r.status_code == 400:
        return (r.text, 400, {"Content-Type": r.headers.get("Content-Type", "application/json")})

    if r.status_code != 200:
        return jsonify({"error": "fs error"}), 500

    return (r.text, 200, {"Content-Type": r.headers.get("Content-Type", "application/json")})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)