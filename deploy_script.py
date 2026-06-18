import paramiko
import time
import os

HOST = "80.74.28.245"
USER = "root"
PASS = "Narzan@0"
REPO = "https://github.com/bobrihha/video-to-blog-converter.git"
PROJECT_DIR = "/root/video-to-blog-converter"
ENV_CONTENT = f"""
GEMINI_API_KEY=AIzaSyCrkEJoPqDxx6G6NTREh1CLoaiPKjJHbvE
TELEGRAM_BOT_TOKEN=8556657207:AAEWIc9We7EOiq-bD2IPs81fecmX76itgEk
"""

def execute_command(ssh, command):
    print(f"Running: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out: print(f"Output: {out}")
    if err: print(f"Error: {err}")
    
    if exit_status != 0:
        print(f"Command failed with status {exit_status}")
    return exit_status

def deploy():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {HOST}...")
        ssh.connect(HOST, username=USER, password=PASS)
        print("Connected.")

        # 1. Update system and install dependencies
        execute_command(ssh, "apt-get update && apt-get install -y python3-venv git python3-pip")

        # 2. Clone/Update Repo
        # Check if dir exists
        check_dir = execute_command(ssh, f"test -d {PROJECT_DIR}")
        if check_dir == 0:
             print("Directory exists, pulling latest changes...")
             execute_command(ssh, f"cd {PROJECT_DIR} && git pull")
        else:
             print("Cloning repository...")
             execute_command(ssh, f"git clone {REPO} {PROJECT_DIR}")

        # 3. Setup Virtual Environment
        print("Setting up venv...")
        execute_command(ssh, f"cd {PROJECT_DIR} && python3 -m venv .venv")
        execute_command(ssh, f"cd {PROJECT_DIR} && .venv/bin/pip install -r requirements.txt")

        # 4. Create .env
        print("Creating .env file...")
        # Escape newlines for echo
        # Actually safer to use sftp to write the file
        sftp = ssh.open_sftp()
        with sftp.file(f"{PROJECT_DIR}/.env", "w") as f:
            f.write(ENV_CONTENT.strip())
        sftp.close()

        # 5. Setup Systemd
        service_content = f"""
[Unit]
Description=YouTube to SEO Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={PROJECT_DIR}
ExecStart={PROJECT_DIR}/.venv/bin/python bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
        print("Configuring Systemd...")
        sftp = ssh.open_sftp()
        with sftp.file("/etc/systemd/system/seo-bot.service", "w") as f:
            f.write(service_content)
        sftp.close()

        execute_command(ssh, "systemctl daemon-reload")
        execute_command(ssh, "systemctl enable seo-bot")
        execute_command(ssh, "systemctl restart seo-bot")
        
        print("Deployment complete! Checking status...")
        time.sleep(2)
        execute_command(ssh, "systemctl status seo-bot")

    except Exception as e:
        print(f"Deployment failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy()
