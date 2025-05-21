from flask import Flask, render_template, redirect, url_for, flash, request, g, jsonify
import json
import os
import paramiko
import subprocess
import pymysql
#import math
import platform
import time
import threading
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from flask_caching import Cache
from redfish_power import redfish_power_control
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# 初始化快取
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# --------------------- Logging Configuration ---------------------
log_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

log_file = os.path.join(os.path.dirname(__file__), 'app.log')

file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8')
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO)

logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])
logging.info("🚀 Logging system initialized.")

# --------------------- Remote Host Configuration ---------------------
REMOTE_HOSTS = {}
REMOTE_HOSTS_FILE = os.path.join(os.path.dirname(__file__), 'remote_hosts.json')

def load_remote_hosts():
    global REMOTE_HOSTS
    try:
        with open(REMOTE_HOSTS_FILE, 'r', encoding='utf-8') as f:
            REMOTE_HOSTS = json.load(f)
            logging.info("Remote hosts loaded successfully.")
    except Exception as e:
        logging.error(f"Failed to load remote hosts: {e}")
        REMOTE_HOSTS = {}

load_remote_hosts()

# --------------------- Ping Monitoring ---------------------
ping_status = {hostname: "Unknown" for hostname in REMOTE_HOSTS}

def ping_once():
    for hostname, info in REMOTE_HOSTS.items():
        ip = info['host']
        try:
            cmd = ["ping", "-n", "1", ip] if platform.system().lower() == "windows" else ["ping", "-c", "1", "-W", "3", ip]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = result.stdout.decode('utf-8', errors='ignore')
            if result.returncode == 0 and ("TTL=" in output or "ttl=" in output):
                ping_status[hostname] = "🟢 Online"
            else:
                ping_status[hostname] = "🔴 Offline"
            logging.info(f"[即時PING] {ip} ({hostname}) -> {ping_status[hostname]}")
        except Exception as e:
            ping_status[hostname] = f"❌ Error: {str(e)}"
            logging.error(f"[即時PING] {ip} ({hostname}) -> Error: {str(e)}")

# --------------------- SSH Command Execution ---------------------
def run_ssh_command(hostname, command, use_sudo=False):
    if hostname not in REMOTE_HOSTS:
        return "", f"Unknown host: {hostname}"

    remote = REMOTE_HOSTS[hostname]
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(remote['host'], port=22, username=remote['username'], password=remote['password'])
        if use_sudo:
            command = "sudo -s " + command
            stdin, stdout, stderr = client.exec_command(command, get_pty=True)
            stdin.write(remote['password'] + '\n')
            stdin.flush()
        else:
            stdin, stdout, stderr = client.exec_command(command)
        out = stdout.read().decode('utf-8')
        err = stderr.read().decode('utf-8')
    except Exception as e:
        return "", str(e)
    finally:
        client.close()

    return out, err

# --------------------- Flask Routes ---------------------
@app.route('/')
@app.route('/')
@cache.cached(timeout=60)
def home():
    threading.Thread(target=ping_once).start()  # ✅ 在背景執行 ping
    return render_template('home.html', servers=REMOTE_HOSTS, ping_status=ping_status)


@app.route('/online/<hostname>')
def online(hostname):
    dns_page = request.args.get('dns_page', 1, type=int)
    show_all = request.args.get('show_all') == 'true'
    per_page = 20
    command_dnsmasq = "awk '{gsub(\":\" , \"\", $2); print $1, $2, $3}' /var/lib/dnsmasq/dnsmasq.leases"
    output_dnsmasq, error_dnsmasq = run_ssh_command(hostname, command_dnsmasq)

    dns_entries = []
    for line in output_dnsmasq.splitlines():
        parts = line.split()
        if len(parts) == 3:
            lease_time, mac, ip = parts
            human_readable_time = datetime.fromtimestamp(int(lease_time)).strftime('%Y-%m-%d %H:%M:%S')
            dns_entries.append({'lease_time': human_readable_time, 'mac': mac, 'ip': ip})

    total = len(dns_entries)
    if not show_all:
        dns_entries = dns_entries[(dns_page-1)*per_page:dns_page*per_page]

    return render_template('online.html', hostname=hostname, dns_entries=dns_entries,
                           total_dns_entries=total, dns_page=dns_page,
                           total_dns_pages=(total + per_page - 1) // per_page,
                           show_all=show_all, error=error_dnsmasq)

@app.route('/monitor/<hostname>')
def monitor(hostname):
    process_page = request.args.get('process_page', 1, type=int)
    show_all = request.args.get('show_all') == 'true'
    per_page = 20

    command_processes = r'''ps aux | awk '$7 != "?" {print $1,$2,$7}' | tail -n +2'''
    output_processes, error_processes = run_ssh_command(hostname, command_processes)

    processes = [{'user': p[0], 'pid': p[1], 'tty': p[2]}
                 for line in output_processes.splitlines()
                 if (p := line.split()) and len(p) >= 3]

    if not show_all:
        processes = processes[(process_page-1)*per_page:process_page*per_page]

    command_mysql = 'mysql -uroot -psupermicro -e "SHOW FULL PROCESSLIST"'
    output_mysql, error_mysql = run_ssh_command(hostname, command_mysql)

    mysql_processes = []
    lines = output_mysql.strip().split("\n")
    if len(lines) > 1:
        headers = lines[0].split("\t")
        for line in lines[1:]:
            cols = line.split("\t")
            if len(cols) >= 6:
                mysql_processes.append({
                    "user": cols[0], "host": cols[1], "db": cols[2],
                    "command": cols[3], "time": cols[4], "info": cols[5]
                })

    return render_template('monitor.html', hostname=hostname, processes=processes,
                           total_processes=len(processes), process_page=process_page,
                           total_process_pages=(len(processes) + per_page - 1) // per_page,
                           mysql_processes=mysql_processes,
                           error_processes=error_processes, error_mysql=error_mysql)

@app.route('/kill/<hostname>/<pid>', methods=['POST'])
def kill_process(hostname, pid):
    output, error = run_ssh_command(hostname, f'kill -9 {pid}', use_sudo=True)
    flash(f"Error killing process {pid}" if error else f"Process {pid} killed", 'danger' if error else 'success')
    return redirect(url_for('monitor', hostname=hostname))

@app.route('/ssh/<hostname>', methods=['POST'])
def ssh_connect(hostname):
    if hostname not in REMOTE_HOSTS:
        flash("Unknown host", 'danger')
        return redirect(url_for('monitor', hostname=hostname))

    remote = REMOTE_HOSTS[hostname]
    try:
        ssh_cmd = f"ssh {remote['username']}@{remote['host']}"
        command = f'powershell.exe -Command "Start-Process powershell -ArgumentList \'-NoExit\', \'-Command {ssh_cmd}\'"'
        subprocess.run(command, check=True, shell=True)
        flash(f"SSH 連線到 {hostname} 開啟中...", 'success')
    except Exception as e:
        flash(f"SSH 錯誤: {e}", 'danger')

    return redirect(request.referrer or url_for('home'))

@app.route('/db/<hostname>')
def db_connection(hostname):
    connection, error = get_db_connection(hostname)
    page = request.args.get('page', 1, type=int)
    show_all = request.args.get('show_all') == 'true'

    if error:
        return render_template('db.html', hostname=hostname, results=None, columns=None, error=error,
                               total_records=0, total_pages=0, page=page, show_all=show_all)

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS total FROM sfcstatus")
            total_records = cursor.fetchone()["total"]
            per_page = 20
            offset = (page - 1) * per_page

            if show_all:
                cursor.execute("SELECT DATETIME, RACKSER, BMCMAC, BMCIP, BMCPAS, SYSTEMIP, STATUS FROM sfcstatus")
            else:
                cursor.execute("SELECT DATETIME, RACKSER, BMCMAC, BMCIP, BMCPAS, SYSTEMIP, STATUS FROM sfcstatus LIMIT %s OFFSET %s", (per_page, offset))

            results = cursor.fetchall()

        total_pages = (total_records + per_page - 1) // per_page

        return render_template('db.html', hostname=hostname, results=results,
                               columns=["DATETIME", "RACKSER", "BMCMAC", "BMCIP", "BMCPAS", "SYSTEMIP", "STATUS"],
                               error=None, total_records=total_records,
                               page=page, total_pages=total_pages, show_all=show_all)
    except Exception as e:
        return render_template('db.html', hostname=hostname, results=None, columns=None, error=str(e),
                               total_records=0, total_pages=0, page=page, show_all=show_all)

@app.teardown_request
def close_db_connection(exception=None):
    db_conn = g.pop('db_conn', None)
    hostname = g.pop('db_hostname', 'unknown')
    if db_conn:
        db_conn.close()
        logging.info(f"Closed DB connection for {hostname}")

@app.route('/troubleshoot')
def troubleshoot():
    hostname = request.args.get('hostname')
    return render_template('troubleshoot.html', hostname=hostname)

# --------------------- DB Helper ---------------------
def get_db_connection(hostname):
    if 'db_conn' not in g:
        host_info = REMOTE_HOSTS.get(hostname)
        if not host_info or "db" not in host_info:
            return None, "No DB configuration found"
        db_conf = host_info["db"]
        try:
            g.db_conn = pymysql.connect(
                host=db_conf["host"],
                user=db_conf["username"],
                password=db_conf["password"],
                database=db_conf["database"],
                port=db_conf.get("port", 3306),
                cursorclass=pymysql.cursors.DictCursor
            )
            g.db_hostname = hostname
            return g.db_conn, None
        except Exception as e:
            return None, str(e)
    return g.db_conn, None

#--------------------------------------------------------------------------------

@app.route('/open_kvm/<hostname>', methods=['POST'])
def open_kvm(hostname):
    if hostname not in REMOTE_HOSTS:
        flash("Unknown host", "danger")
        return redirect(url_for("home"))

    info = REMOTE_HOSTS[hostname]
    bmc_ip = info.get("bmc_ip")
    username = info.get("username")
    password = info.get("password")

    if not all([bmc_ip, username, password]):
        flash("Missing BMC credentials or IP", "danger")
        return redirect(url_for("home"))

    try:
        chrome_options = Options()
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_experimental_option("detach", True)

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(f"https://{bmc_ip}")
        time.sleep(2)

        driver.find_element(By.NAME, "name").send_keys(username)
        driver.find_element(By.NAME, "pwd").send_keys(password)
        driver.find_element(By.NAME, "Login").click()
        time.sleep(3)

        kvm_url = f"https://{bmc_ip}/cgi/url_redirect.cgi?url_name=man_ikvm_html5_bootstrap"
        driver.execute_script(f"window.open('{kvm_url}', '_blank');")
        driver.switch_to.window(driver.window_handles[1])

        logging.info(f"✅ Opened KVM for {hostname} ({bmc_ip})")
        flash("KVM 頁面已開啟", "success")

    except Exception as e:
        logging.error(f"❌ Failed to open KVM for {hostname}: {e}")
        flash(f"KVM 開啟失敗: {e}", "danger")

    return redirect(url_for("home"))

@app.route('/api/ping_status')
def api_ping_status():
    return jsonify(ping_status)

@app.route("/redfish/<hostname>/<action>", methods=["POST"])
def redfish_power_action(hostname, action):
    remote = REMOTE_HOSTS.get(hostname)
    if not remote or "bmc_ip" not in remote:
        return jsonify({"error": "Unknown host"}), 404
    bmc_ip = remote["bmc_ip"]
    result = redfish_power_control(bmc_ip, remote["username"], remote["password"], action)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
