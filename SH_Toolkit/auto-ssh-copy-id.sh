#!/bin/bash

do_expect(){
	echo
	echo "----------------------------"
	echo "${NAME}"
	echo "----------------------------"
	#echo -n "${NAME}: "
	#printf "%-12s" $NAME;

	expect -c "
		set timeout 3
		spawn ssh-copy-id -i "$KEY" "$NAME"
		expect \"(yes/no/[fingerprint])?\"
		send \"yes\n\"
		expect \"password:\"
		send \"${PW}\n\"
		expect \"#\"
		interact
	" | egrep "$EGREP"
}

LIST="qh{001..016}-m"
PW="Smci@123"
KEY="/root/.ssh/id_rsa.pub"
EGREP=""

for NAME in $(eval echo ${LIST}); do
	#echo "$NAME"
	do_expect
	sleep 0.5
done
