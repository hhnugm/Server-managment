import requests
from requests.auth import HTTPBasicAuth
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def redfish_power_control(host, username, password, action):
    url = f"https://{host}/redfish/v1/Systems/1/Actions/ComputerSystem.Reset"
    headers = {"Content-Type": "application/json"}

    if action == "on":
        body = {"ResetType": "On"}
    elif action == "gracefulshutdown":
        body = {"ResetType": "GracefulShutdown"}
    elif action == "gracefulrestart":
        body = {"ResetType": "GracefulRestart"}
    elif action == "forceoff":
        body = {"ResetType": "ForceOff"}
    else:
        return {"error": "Invalid action"}

    try:
        response = requests.post(url, json=body, headers=headers,
                                 auth=HTTPBasicAuth(username, password),
                                 verify=False, timeout=5)
        return {"status": response.status_code, "result": response.json()}
    except Exception as e:
        return {"error": str(e)}
