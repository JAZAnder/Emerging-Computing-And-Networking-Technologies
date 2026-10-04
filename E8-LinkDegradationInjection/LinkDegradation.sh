#Establish Base Line Ping
echo "=== Running Baseline Ping ==="
baseline_stats=$(ping -c 20 -i 0.2 8.8.8.8 | tee /dev/tty | tail -n 2)


#100ms static latency +/- 10ms with normal distribution, and a 10% packet drop ratio.
echo -e "\n=== Applying Netem Rules ===" 
sudo tc qdisc add dev eth0 root netem delay 100ms 10ms distribution normal loss 10%



#Show Config
tc qdisc show dev eth0

#Ping 8.8.8.8 20 times
echo -e "\n=== Running Modified Ping ==="
netem_stats=$(ping -c 20 -i 0.2 8.8.8.8 | tee /dev/tty | tail -n 2)

#Reset Interface
echo -e "\n=== Resetting Interface ==="
sudo tc qdisc del dev eth0 root
#Show Config to verify reset
tc qdisc show dev eth0

echo -e "\n========================================"
echo "         CAPTURED PING SUMMARY"
echo "========================================"
echo -e "\nBaseline Stats:\n$baseline_stats\n"
echo -e "\nNetem Stats:\n$netem_stats"

    