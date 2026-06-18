import paramiko
import time

HOST = "80.74.28.245"
USER = "root"
PASS = "Narzan@0"
PROJECT_DIR = "/root/video-to-blog-converter"

def update():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {HOST}...")
        ssh.connect(HOST, username=USER, password=PASS)
        
        print("Pulling latest code...")
        stdin, stdout, stderr = ssh.exec_command(f"cd {PROJECT_DIR} && git pull")
        print(stdout.read().decode())
        
        print("Restarting service...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart seo-bot")
        
        print("Checking status...")
        time.sleep(2)
        stdin, stdout, stderr = ssh.exec_command("systemctl status seo-bot")
        print(stdout.read().decode())

    except Exception as e:
        print(f"Update failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    update()
