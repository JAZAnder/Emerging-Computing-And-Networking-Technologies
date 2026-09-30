#!/usr/bin/env python

import time
from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
from mn_wifi.cli import CLI

def topology():
    "Create a mininet-wifi network"
    net = Mininet_wifi()

    info("*** Adding Controller\n")
    c0 = net.addController('c0')

    info("*** Creating Nodes\n")
    # Stationary Access Point
    ap1 = net.addAccessPoint('ap1', ssid='mininet-wifi-ssid', mode='g', channel='1', position='45,20,0')

    # Mobile Station
    sta1 = net.addStation('sta1', ip='10.0.0.1/8')

    info("*** Attached wifi networks\n")
    net.configureWifiNodes()

    info("*** Configuring path trajectory\n")
    # Initialize mobility thread at t=0
    net.startMobility(time=0)

    # Configure linear path trajectory from (10,20,0) to (80,20,0) over 10 seconds
    net.mobility(sta1, 'start', time=0, position='10,20,0')
    net.mobility(sta1, 'stop', time=10, position='80,20,0')

    # Finalize mobility time range
    net.stopMobility(time=10)

    info("*** Starting Network\n")
    net.build()
    c0.start()
    ap1.start([c0])

    info("\n*** Monitoring Spatial Coordinate Progression over Time ***\n")
    for current_second in range(11):
        info(f"[t = {current_second:2d}s] sta1 position (X, Y, Z): {sta1.position}\n")
        time.sleep(1)


    info("*** Stopping Network\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology()
