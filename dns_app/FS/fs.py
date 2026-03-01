from flask import Flask, request, jsonify
import socket

app = Flask(__name__)

def fib(n: int) -> int:
    if n < 0:
        raise ValueError("negative")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def send_udp(host: str, port: int, msg: str, timeout=2.0) -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(timeout)
    s.sendto(msg.encode("utf-8"), (host, port))
    data, _ = s.recvfrom(4096)
    return data.decode("utf-8", errors="ignore")

@app.put("/register")
def register():
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "bad json"}), 400

    hostname = body.get("hostname")
    ip = body.get("ip")
    as_ip = body.get("as_ip")
    as_port = body.get("as_port")

    if not (hostname and ip and as_ip and as_port):
        return jsonify({"error": "missing fields"}), 400

    # DNS registration format (each line ends with \n)
    # TYPE=A
    # NAME=fibonacci.com VALUE=IP_ADDRESS TTL=10
    msg = f"TYPE=A\nNAME={hostname} VALUE={ip} TTL=10\n"

    try:
        _ = send_udp(as_ip, int(as_port), msg)
    except Exception:
        return jsonify({"error": "registration failed"}), 500

    return jsonify({"message": "registered"}), 201

@app.get("/fibonacci")
def fibonacci():
    number = request.args.get("number")
    if number is None:
        return jsonify({"error": "missing number"}), 400
    try:
        n = int(number)
    except Exception:
        return jsonify({"error": "number must be int"}), 400

    try:
        value = fib(n)
    except Exception:
        return jsonify({"error": "bad number"}), 400

    return jsonify({"fibonacci": value}), 200

if __name__ == "__main__":
    # listen on container port 9090
    app.run(host="0.0.0.0", port=9090)