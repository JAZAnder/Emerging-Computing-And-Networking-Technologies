for i in 1 2 3; do
  port=$((2230 + i))
  name="ubuntu-ssh-test-$i"
  docker rm -f "$name" >/dev/null 2>&1

  # Launch container with NET_ADMIN capabilities
  docker run -d --name "$name" --cap-add=NET_ADMIN -p "$port":22 ubuntu:latest sleep infinity

  # Install iproute2/sudo, configure NOPASSWD for sudo, and start sshd
  docker exec "$name" bash -c "
    apt-get update && apt-get install -y openssh-server sudo iproute2 iputils-ping && \
    mkdir -p /var/run/sshd /run/sshd && \
    ssh-keygen -A && \
    useradd -rm -d /home/netmiko.test -s /bin/bash -g root -G sudo netmiko.test && \
    echo 'netmiko.test:Password123!' | chpasswd && \
    echo 'netmiko.test ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers && \
    echo 'unset PROMPT_COMMAND' >> /etc/bash.bashrc && \
    echo 'export PS1=\"\u@\h:\w\$ \"' >> /etc/bash.bashrc && \
    /usr/sbin/sshd
  "
done

for i in 1 2 3; do
  docker exec ubuntu-ssh-test-$i bash -c '
    rm -f /etc/profile.d/*
    mkdir -p /home/netmiko.test
    echo "unset PROMPT_COMMAND; export PS1=\"\u@\h:\w\$ \"" > /home/netmiko.test/.bashrc
    echo "source /home/netmiko.test/.bashrc" > /home/netmiko.test/.bash_profile
    chown -R netmiko.test:root /home/netmiko.test
  '
done

docker exec -it ubuntu-ssh-test-1 ip addr add 10.0.0.1/24 dev eth0
docker exec -it ubuntu-ssh-test-2 ip addr add 10.0.0.2/24 dev eth0
docker exec -it ubuntu-ssh-test-3 ip addr add 10.0.0.3/24 dev eth0