docker run -d \
  --name ubuntu-ssh-test-1 \
  -p 2231:22 \
  ubuntu:latest \
  bash -c "apt-get update && apt-get install -y openssh-server sudo && \
           mkdir -p /var/run/sshd && \
           useradd -rm -d /home/netmiko.test -s /bin/bash -g root -G sudo netmiko.test && \
           echo 'netmiko.test:Password123!' | chpasswd && \
           /usr/sbin/sshd -D"

docker run -d \
  --name ubuntu-ssh-test-2 \
  -p 2232:22 \
  ubuntu:latest \
  bash -c "apt-get update && apt-get install -y openssh-server sudo && \
           mkdir -p /var/run/sshd && \
           useradd -rm -d /home/netmiko.test -s /bin/bash -g root -G sudo netmiko.test && \
           echo 'netmiko.test:Password123!' | chpasswd && \
           /usr/sbin/sshd -D"

docker run -d \
  --name ubuntu-ssh-test-3 \
  -p 2233:22 \
  ubuntu:latest \
  bash -c "apt-get update && apt-get install -y openssh-server sudo && \
           mkdir -p /var/run/sshd && \
           useradd -rm -d /home/netmiko.test -s /bin/bash -g root -G sudo netmiko.test && \
           echo 'netmiko.test:Password123!' | chpasswd && \
           /usr/sbin/sshd -D"

for i in 1 2 3; do
  docker exec ubuntu-ssh-test-$i bash -c '
    rm -f /etc/profile.d/*
    mkdir -p /home/netmiko.test
    echo "unset PROMPT_COMMAND; export PS1=\"\u@\h:\w\$ \"" > /home/netmiko.test/.bashrc
    echo "source /home/netmiko.test/.bashrc" > /home/netmiko.test/.bash_profile
    chown -R netmiko.test:root /home/netmiko.test
  '
done

docker ps -a