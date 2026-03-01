import os
import socket

DB_FILE = os.environ.get("DB_FILE", "records.txt")
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "53533"))

def parse_kv_lines(msg: str) -> dict:
    """
    Supports both formats:
      TYPE=A
      NAME=fibonacci.com VALUE=1.2.3.4 TTL=10
    and
      TYPE=A
      NAME=fibonacci.com
    """
    data = {}
    lines = [ln.strip() for ln in msg.splitlines() if ln.strip()]
    for ln in lines:
        parts = ln.split()
        for p in parts:
            if "=" in p:
                k, v = p.split("=", 1)
                data[k.strip().upper()] = v.strip()
    return data

def load_records() -> dict:
    records = {}
    if not os.path.exists(DB_FILE):
        return records
    with open(DB_FILE, "r") as f:
        for line in f:
            line = line.strip()
            # stored as: NAME=fibonacci.com VALUE=1.2.3.4 TTL=10 TYPE=A
            if not line:
                continue
            kv = parse_kv_lines(line)
            name = kv.get("NAME")
            rtype = kv.get("TYPE")
            if name and rtype:
                records[(name, rtype)] = kv
    return records

def save_record(kv: dict) -> None:
    # store one record per line in a simple persistent file
    name = kv.get("NAME")
    rtype = kv.get("TYPE")
    value = kv.get("VALUE")
    ttl = kv.get("TTL")
    if not (name and rtype and value and ttl):
        return
    line = f"NAME={name} VALUE={value} TTL={ttl} TYPE={rtype}\n"
    with open(DB_FILE, "a") as f:
        f.write(line)

def is_registration(kv: dict) -> bool:
    return "VALUE" in kv and "TTL" in kv and "NAME" in kv and "TYPE" in kv

def is_query(kv: dict) -> bool:
    return "NAME" in kv and "TYPE" in kv and "VALUE" not in kv and "TTL" not in kv

def main():
    # Load existing records into memory (optional optimization)
    records = load_records()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    print(f"AS listening on UDP {HOST}:{PORT}, db={DB_FILE}")

    while True:
        data, addr = sock.recvfrom(4096)
        msg = data.decode("utf-8", errors="ignore").strip()
        kv = parse_kv_lines(msg)

        # Registration
        if is_registration(kv):
            name = kv["NAME"]
            rtype = kv["TYPE"]
            records[(name, rtype)] = kv
            save_record(kv)
            # Respond (keep it simple; spec doesn’t force exact ack content)
            sock.sendto(b"OK\n", addr)
            continue

        # DNS Query
        if is_query(kv):
            name = kv["NAME"]
            rtype = kv["TYPE"]
            rec = records.get((name, rtype))

            # If not in memory, try re-load (helps if restarted)
            if rec is None:
                records = load_records()
                rec = records.get((name, rtype))

            if rec is None:
                sock.sendto(b"ERROR\n", addr)
            else:
                # REQUIRED response format in the screenshots:
                # TYPE=A
                # NAME=fibonacci.com VALUE=IP_ADDRESS TTL=10
                resp = f"TYPE={rtype}\nNAME={name} VALUE={rec['VALUE']} TTL={rec['TTL']}\n"
                sock.sendto(resp.encode("utf-8"), addr)
            continue

        sock.sendto(b"ERROR\n", addr)

if __name__ == "__main__":
    main()