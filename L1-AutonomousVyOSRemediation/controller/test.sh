echo "[SENDING]: <14>1 2026-09-23T21:00:00Z vyos eth1 - - - Interface eth1: Link is Down >> 192.168.100.1:514" 
echo "<14>1 2026-09-23T21:00:00Z vyos eth1 - - - Interface eth1: Link is Down" | nc -u -w1 192.168.100.1 514
