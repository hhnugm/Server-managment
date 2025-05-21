#!/bin/bash

# 請用戶輸入 IP 位址
read -p "Enter the IP address to connect: " IP

# 請用戶輸入 grep 篩選條件
read -p "Enter the grep range to search: " GREP

# Telnet 登入憑證
USERNAME="ADMIN"
PASSWORD="ADMIN"

# 組合指令
COMMAND="show mac-address-table | grep $GREP"

# 輸出文件
OUTPUT_FILE="MAC_$IP.txt"

echo "Connecting to $IP via Telnet..."

(
    # 開始 Telnet
    sleep 2
    echo "$USERNAME"          # 輸入使用者名稱
    sleep 1
    echo "$PASSWORD"          # 輸入密碼
    sleep 1
    echo "$COMMAND"           # 執行指令
    sleep 2
    echo "exit"               # 結束連線
) | telnet "$IP" > "$OUTPUT_FILE"


if grep -q "$GREP" "$OUTPUT_FILE"; then
    echo "Command executed successfully, result saved to $OUTPUT_FILE"
else
    echo "Command execution failed or no matching output found."
fi
