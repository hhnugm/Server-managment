import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_bmc_login_status(bmc_ip, username, password):
    session_url = f"https://{bmc_ip}/redfish/v1/SessionService/Sessions"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "UserName": username,
        "Password": password
    }

    try:
        response = requests.post(session_url, json=payload, headers=headers, verify=False, timeout=5)
        if response.status_code in [200, 201]:
            return True, "登入成功"
        elif response.status_code == 401:
            return False, "帳號或密碼錯誤"
        elif response.status_code == 403:
            return False, "權限被拒絕 (可能帳號被鎖)"
        else:
            return False, f"登入失敗，狀態碼: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"BMC 無法連線: {e}"
