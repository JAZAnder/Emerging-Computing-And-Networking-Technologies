import os
import re
import time
from netmiko import ConnectHandler

#Local Log File
LOG_FILE = "./simulated_syslog.log"

# Map Simulated inventory
INVENTORY = {
    "router1": { "device_type": "linux","host": "127.0.0.1", "port": 2231, "username": "netmiko.test", "password": "Password123!", "use_keys": False},
    "router2": { "device_type": "linux","host": "127.0.0.1", "port": 2232, "username": "netmiko.test", "password": "Password123!", "use_keys": False},
    "router3": { "device_type": "linux","host": "127.0.0.1", "port": 2233, "username": "netmiko.test", "password": "Password123!", "use_keys": False},
}

## Regular Expressions
# Match Flapping Error extract host and foreign ip address 
ERROR_PATTERN = re.compile(r"\b(\S+)\s+BGP_ERR:\s+Peer\s+(\S+)\s+flapping")
# Match ip route command to extract device name
ROUTE_PATTERN = re.compile(r"\bdev\s+(\S+)")

def execute_remediation(device, peer_ip):
    print(f"\n[ERROR FOUND] Routing error detected for BGP peer: {peer_ip} on device: {device}")
    try:
        # Establish SSH connection to device using hostname from inventory
        session = ConnectHandler(**INVENTORY[device], session_log="netmiko_debug.log", global_delay_factor=2, fast_cli=False,)
        
        # Find route for IP address
        route_out = session.send_command(f"ip route get {peer_ip}")
        match = ROUTE_PATTERN.search(route_out)
        
        if match:
            interface = match.group(1)
            print(f"[INTERFACE FOUND] Peer {peer_ip} routes via container interface: {interface}")
            
            # Disable interface
            cmd = f"sudo ip link set dev {interface} down"
            output = session.send_command(cmd, expect_string=r".*")
            print(f"[REMEDIATION SUCCESS] Executed command on container: '{cmd}'")
        else:
            print(f"[ERROR] Could not parse egress interface from output: {route_out}")
            
        session.disconnect()
    except Exception as e:
        print(f"[REMEDIATION ERROR] SSH remediation failed: {e}")

def monitor_syslog():
    #Check file path
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, "a").close()

    print(f"Actively monitoring syslog stream at {LOG_FILE}...")
    with open(LOG_FILE, "r") as f:
        #Jump to end of file
        f.seek(0, os.SEEK_END)
        #Check for new line, if found try to match error
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue
            
            m = ERROR_PATTERN.search(line)
            if m:
                execute_remediation(m.group(1), m.group(2))

#Only run monitor if script is ran, not imported
if __name__ == "__main__":
    monitor_syslog()