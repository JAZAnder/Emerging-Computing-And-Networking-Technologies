#!/bin/sh
echo "===== Begining tests on edge-node-1 ===="
echo "  -  -  -  Pinging edge-node-2  -  -  -  "
docker exec -it edge-node-1 ping -c 4 edge-node-2
echo "  -  -  -  Pinging google.com  -  -  -  "
docker exec -it edge-node-1 ping -c 4 google.com
echo "==== Completed tests on edge-node-1 ===="

echo "===== Begining tests on edge-node-2 ===="
echo "  -  -  -  Pinging edge-node-1  -  -  -  "
docker exec -it edge-node-2 ping -c 4 edge-node-1
echo "   -   -   -  Pinging 8.8.8.8  -   -   -  "
docker exec -it edge-node-2 ping -c 4 8.8.8.8
echo "==== Completed tests on edge-node-2 ===="

