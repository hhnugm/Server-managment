#!/bin/bash

read -p "Enter the IP range 10.*.*:" BASE_IP
read -p "Enter the start IP (e.g., 0): " START
read -p "Enter the end IP (e.g.,255): " END
USER=root
PASSWORD=Smci@123

# 創建存儲結果的目錄
OUTPUT_DIR="output_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"
echo "Results will be saved to directory: $OUTPUT_DIR"

echo "Checking SSH access and saving command outputs..."
for i in $(seq $START $END); do
    IP="$BASE_IP.$i"

    # 檢查 SSH 是否可用
    sshpass -p "$PASSWORD" ssh -o ConnectTimeout=2 -o StrictHostKeyChecking=no $USER@$IP "exit" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "$IP: Login successful"

        # 定義輸出文件，存儲到指定目錄
        OUTPUT_FILE="$OUTPUT_DIR/${IP}_output.txt"
        echo "Output for $IP" > "$OUTPUT_FILE"

        # 執行多條命令並附加到文件
        COMMANDS=(
            "sudo dmidecode -t 1"
            "uname -a"
            "df -h"
            "lspci -vv | grep -i H100"
        )
        for CMD in "${COMMANDS[@]}"; do
            echo -e "\nRunning: $CMD" >> "$OUTPUT_FILE"
            sshpass -p "$PASSWORD" ssh -o ConnectTimeout=2 -o StrictHostKeyChecking=no $USER@$IP "$CMD" >> "$OUTPUT_FILE" 2>/dev/null
            if [ $? -eq 0 ]; then
                echo "$CMD executed successfully." >> "$OUTPUT_FILE"
            else
                echo "$CMD execution failed." >> "$OUTPUT_FILE"
            fi
        done

        echo "$IP: Outputs saved to $OUTPUT_FILE"
    else
        echo "$IP: Login failed"
    fi
done

