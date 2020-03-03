#!/bin/bash
port=`python3 port_ssh_tunnel.py`
if pgrep -f "localhost:23" >/dev/null
then
    echo "ssh tunnel 1 is running"
else
    echo "ssh tunnel 1 stopped"
    sshpass -p 'protecia2020' ssh -o StrictHostKeyChecking=no -N -R $port:localhost:23 -p 2222 sshtunnel@client.protecia.com &
fi
if pgrep -f "localhost:2525" >/dev/null
then
    echo "ssh tunnel 2 is running"
else
    echo "ssh tunnel 2 stopped"
    sshpass -p 'protecia2020' ssh -o StrictHostKeyChecking=no -N -R $(($port+1)):localhost:2525 -p 2222 sshtunnel@client.protecia.com &
fi
