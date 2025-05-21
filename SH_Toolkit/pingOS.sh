#!/bin/bash


echo "Checking deployment status..."

read -p "Enter IP range 10.*.*: " IP_RANGE
read -p "Enter start IP (e.g., 1): " START
read -p "Enter end IP (e.g., 254): " END


for i in $(seq $START $END); do
    IP="$IP_RANGE.$i"

    # 使用 ping 測試目標主機
    ping -c 1 -W 1 $IP &>/dev/null
    if [ $? -eq 0 ]; then
        echo "$IP: Ping Successfully"
    else
        echo "$IP: Ping Fail"
    fi
done

