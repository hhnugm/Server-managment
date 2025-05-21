#!/bin/bash

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/root/pbs_conf_backup/$TIMESTAMP"

mkdir -p $BACKUP_DIR

qmgr -c "print server" > $BACKUP_DIR/pbs_server_$TIMESTAMP.txt
qmgr -c "print queue" > $BACKUP_DIR/pbs_queues_$TIMESTAMP.txt
pbsnodes -av > $BACKUP_DIR/pbs_nodes_$TIMESTAMP.txt

