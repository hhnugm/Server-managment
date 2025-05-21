#!/bin/bash

# 提示使用者輸入主機名稱或 IP 地址，以空格分隔
read -p "請輸入要測試的主機（用空格分隔，例如：google.com 8.8.8.8 example.com）: " -a hosts

# 使用 for 迴圈遍歷每個主機並測試連通性
for host in "${hosts[@]}"; do
    # 執行 ping 並隱藏輸出
    ping -c 1 $host 2>/dev/null 1>/dev/null

    # 檢查 ping 的退出狀態
    if [ $? -eq 0 ]; then
        echo "Host $host is reachable"
    else
        echo "Host $host is unreachable"
    fi
done

