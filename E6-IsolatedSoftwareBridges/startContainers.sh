#!/bin/bash

#Create docker network --Internal Restricts external access to the network
docker network create --subnet=192.168.1.0/24 --internal edge-net

#Creates the containers --network edge-net addes them to the edge-net network
docker run -d --name edge-node-1 --network edge-net alpine sleep infinity
docker run -d --name edge-node-2 --network edge-net alpine sleep infinity

