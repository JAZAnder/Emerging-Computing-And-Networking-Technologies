#!/usr/bin/env python3
import subprocess
import time
import os
from containernet.node import Docker
from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.link import wmediumd
from mn_wifi.net import Mininet_wifi

def run_experiment():
    print("*** Building Docker image 'edge-container'...")
    subprocess.run(["docker", "build", "-t", "edge-container", "."], check=True)

    setLogLevel('info')

    # Initialize Mininet_wifi with wmediumd signal tracking & RSSI auto-handoff
    net = Mininet_wifi(link=wmediumd, ac_method='s')

    info("*** Adding Access Points\n")
    ap1 = net.addAccessPoint('ap1', ssid='edge-net', mode='g', channel='1', position='20,50,0', range=60)
    ap2 = net.addAccessPoint('ap2', ssid='edge-net', mode='g', channel='6', position='80,50,0', range=60)

    info("*** Adding Mobile Station\n")
    sta1 = net.addStation('sta1', ip='10.0.0.10/24', position='10,50,0', ssid='edge-net')

    info("*** Adding Edge Docker Containers\n")
    #privileged to allow network configuration inside of container
    edge1 = net.addHost('edge1', cls=Docker, ip='10.0.0.100/24', dimage='edge-container', privileged=True, cmd='python3 -m http.server 80')
    edge2 = net.addHost('edge2', cls=Docker, ip='10.0.0.200/24', dimage='edge-container', privileged=True, cmd='python3 -m http.server 80')

    info("*** Setting Up Distance Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=3)

    info("*** Configuring WiFi Nodes\n")
    net.configureWifiNodes()

    info("*** Connecting Edge Containers to AP Backhaul with tc-netem\n")
    net.addLink(ap1, edge1, intfName2='edge1-eth0')
    net.addLink(ap2, edge2, intfName2='edge2-eth0')


    info("*** Defining Traversal Path\n")
    net.startMobility(time=0)
    net.mobility(sta1, 'start', time=1, position='10,50,0')
    net.mobility(sta1, 'stop', time=30, position='90,50,0')
    net.stopMobility(time=30)

    info("*** Starting Network\n")
    net.build()
    net.start()

    info("*** Enforcing Standalone Switch Mode on Host OVS\n")
    os.system("ovs-vsctl set-fail-mode ap1 standalone")
    os.system("ovs-vsctl set-fail-mode ap2 standalone")

    info("*** Assigning IP Addresses & Bringing Up Container Interfaces\n")
    edge1.setIP('10.0.0.100', prefixLen=24, intf='edge1-eth0')
    edge2.setIP('10.0.0.200', prefixLen=24, intf='edge2-eth0')
    edge1.cmd('ip link set dev edge1-eth0 up')
    edge2.cmd('ip link set dev edge2-eth0 up')

    info("*** Applying tc-netem Rules Inside Container Namespaces\n")
    #Remove defult setting and apply netem directly to container
    edge1.cmd('tc qdisc del dev edge1-eth0 root 2>/dev/null')
    edge1.cmd('tc qdisc add dev edge1-eth0 root netem delay 10ms 6ms loss 2%')
    edge2.cmd('tc qdisc del dev edge2-eth0 root 2>/dev/null')
    edge2.cmd('tc qdisc add dev edge2-eth0 root netem delay 20ms 3ms loss 4%')

    info("*** Launching HTTP Microservices Bound to Active Interfaces\n")
    # Kill any pre-existing background server instances and bind freshly to port 80 0.0.0.0
    edge1.cmd('pkill -f http.server')
    edge2.cmd('pkill -f http.server')
    edge1.cmd('python3 -m http.server 80 &')
    edge2.cmd('python3 -m http.server 80 &')
    time.sleep(1) 


    info("*** Initializing Wi-Fi Association & ARP Warmup...\n")
    sta1.setAssociation(ap1, intf='sta1-wlan0')
    time.sleep(2)

    # Pre-populate ARP entries
    sta1.cmd('ping -c 1 10.0.0.100')
    sta1.cmd('ping -c 1 10.0.0.200')

    
    info("*** Executing Continuous Edge Telemetry Loop on sta1\n")
    # Prepare CSV log header
    log_file = "handoff_log.csv"
    with open(log_file, "w") as f:
        f.write("timestamp,elapsed_time,associated_ap,http_code,response_time_ms,status\n")

    start_time = time.time()
    duration = 35  # Run slightly past mobility duration

    print("[*] Monitoring traversal and pinging edge containers...")
    while time.time() - start_time < duration:
        curr_time = time.time()
        elapsed = round(curr_time - start_time, 2)

        ap1bssid = ap1.cmd("iw dev ap1-wlan1 info | grep addr | awk '{print$2}'").strip()
        ap2bssid = ap2.cmd("iw dev ap2-wlan1 info | grep addr | awk '{print$2}'").strip()

        # Get currently associated BSSID/AP interface name from sta1
        bssid = sta1.cmd("iw dev sta1-wlan0 link | grep Connected | awk '{print $3}'").strip()
        
        # Determine target edge container based on associated AP
        if bssid == ap1bssid:
            target_ip = "10.0.0.100"
            print("Connected to AP1")
        elif bssid == ap2bssid:
            target_ip = "10.0.0.200"
            print("Connected to AP2")
        else:
            target_ip = "0.0.0.0"

        # Continuous HTTP curl request capturing status code and latency (seconds -> ms)
        curl_cmd = (
            f'curl -s -o /dev/null -w "%{{http_code}},%{{time_total}}" '
            f'--connect-timeout 0.5 http://{target_ip}/'
        )
        output = sta1.cmd(curl_cmd).strip()

        try:
            http_code, resp_time = output.split(',')
            resp_ms = float(resp_time) * 1000.0
            status = "SUCCESS" if http_code == "200" else "DROP"
        except ValueError:
            http_code = "000"
            resp_ms = 500.0  # Timeout / dropped packet penalty representation
            status = "DROP"

        ap_label = "ap1" if target_ip == "10.0.0.100" else "ap2"
        # Append record to CSV log
        with open(log_file, "a") as f:
            f.write(f"{curr_time:.2f},{elapsed},{ap_label},{http_code},{resp_ms:.2f},{status}\n")

        time.sleep(0.2)  # High-frequency sampling (5 Hz)

    info("*** Experiment Completed. Logs written to handoff_log.csv\n")
    net.stop()

if __name__ == '__main__':
    run_experiment()