import json
import re
from netmiko import ConnectHandler

pattern = r"up\s+(?:.*?\b(\d+)\s+days?,\s*)?(?:.*?\b(\d+)\s+hours?,\s*)?(\d+)\s+minutes?"

# Load device list from JSON
with open("devices.json", "r") as f:
    devices = json.load(f)

for device in devices:
    try:
        session = ConnectHandler(**device, session_log="netmiko_debug.log", global_delay_factor=2, fast_cli=False,)
        hostname = session.send_command("hostname").strip()
        uptime_output = session.send_command("uptime -p")
        session.disconnect()

        match = re.search(pattern, uptime_output)
        if match:
            
            days = match.group(1) if match.group(1) else "0"
            hours = match.group(2) if match.group(2) else "0"
            minutes = match.group(3) if match.group(3) else "0"


            print(f"Host: {hostname} ({device['host']}:{device['port']}) | Uptime: {days}d {hours}h {minutes}m")
        else:
            print(f"[{hostname}] Could not parse uptime string: '{uptime_output}'")
    except Exception as e:
        print(f"[{device['host']}] Connection failed: {e}")



