import socket
import re
import sys
import json
import argparse
from netmiko import ConnectHandler



#Listener Details
LISTEN_IP = "192.168.100.1"  # Bound to virbr1 interface
LISTEN_PORT = 514

#Pattern matches  down/link fault signals in RFC 5424 logs
FAULT_PATTERN = re.compile(r"^<\d+>\d*\s*\S+\s+(\S+).*?\b(eth\d+).*(?:Link is Down|link down|state to down|carrier lost)", re.IGNORECASE)

#Load router
with open("inventory.json") as f:
    INVENTORY = json.load(f)

#Find router in inventory
def get_router_config(hostname, source_ip):
    if hostname in INVENTORY:
        return INVENTORY[hostname]

    for device_name, config in INVENTORY.items():
        if source_ip == config["connection"]["host"] or source_ip in config.get("allowed_syslog_ips", []):
            return config

    return None

#Disable effected interface
def apply_automated_remediation(config, interface_name):
    router_host = config["connection"]["host"]
    print(f"\n[REMEDIATION]: Initiating SSH session to VyOS ({router_host})...")
    try:
        with ConnectHandler(**config["connection"]) as session:
            print(f"[REMEDIATION]: Disabling faulty interface: {interface_name}")

            #VyOS CLI commands
            config_commands = [
                f"set interfaces ethernet {interface_name} disable",
                "commit",
                "save"
            ]

            output = session.send_config_set(config_commands)

            print(f"[REMEDIATION SUCCESS]: Interface {interface_name} administrative shutdown complete.")
            print(f"[ROUTER OUTPUT]:\n{output}")
    except Exception as e:
        print(f"[ERROR]: Failed to execute remediation via SSH: {e}")

#Open Port and listen for logs
def start_syslog_listener():
    """Binds UDP socket to capture real-time syslog datagrams."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)



    try:
        sock.bind((LISTEN_IP, LISTEN_PORT))
        print(f"[*]: Controller active. Listening for UDP RFC 5424 Syslog on {LISTEN_IP}:{LISTEN_PORT}...")
    except PermissionError:
        print(f"[ERROR]: Permission denied: Binding to port {LISTEN_PORT} requires root/sudo privileges.")
        sys.exit(1)

    processed_events = set()

    if args.reset:
        print("[Resesting Logs]: Clearing processed_events state.")
        processed_events.clear()

    while True:
        data, addr = sock.recvfrom(4096)
        raw_msg = data.decode("utf-8", errors="ignore").strip()

        print(f"[SYSLOG INGEST]: ({addr[0]}): {raw_msg}")

        match = FAULT_PATTERN.search(raw_msg)
        if match:
            hostname = match.group(1)
            interface = match.group(2)
            source_ip = addr[0]
            event_key = (hostname, interface)

            # Prevent douplicate logs
            if event_key not in processed_events:
                print(f"\n[CRITICAL EVENT]: Link failure detected on interface '{interface}'!")
                processed_events.add(event_key)
                config = get_router_config(hostname, source_ip)
                if config:
                    apply_automated_remediation(config, interface)
                else:
                    print(f"[ERROR] No matching router configuration found for host '{hostname}' or IP '{source_ip}'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remediation Script")
    parser.add_argument("--reset", action="store_true", help="Clears past events before running")
    args = parser.parse_args()
    start_syslog_listener()
