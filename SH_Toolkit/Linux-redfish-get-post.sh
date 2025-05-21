curl --insecure -X POST -D headers.txt https://${bmc}/redfish/v1/SessionService/Sessions -d '{"UserName":"root", "Password":"0penBmc"}'
