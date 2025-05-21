import requests


def get_bmc_token(bmc_ip, username, password):
    url = f"https://{bmc_ip}/redfish/v1/SessionService/Sessions"
    payload = {"UserName": username, "Password": password}
    r = requests.post(url, json=payload, verify=False)
    r.raise_for_status()
    token = r.headers.get('X-Auth-Token')
    if not token:
        raise Exception("Failed to get BMC token")
    return token

def release_bmc_token(bmc_ip, username, password):
    # 假設你要先取得token後刪除session或呼叫釋放API
    token = get_bmc_token(bmc_ip, username, password)
    session_url = f"https://{bmc_ip}/redfish/v1/SessionService/Sessions"
    headers = {"X-Auth-Token": token}
    r = requests.delete(session_url, headers=headers, verify=False)
    return r.status_code == 200
