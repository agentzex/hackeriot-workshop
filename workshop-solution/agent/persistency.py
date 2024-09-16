import subprocess
import os
import datetime




def get_utc_time():
    return datetime.datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S")


def is_server_running(agent_port):
    # Use netstat or ss to check if a process is listening on agent_port
    print(f"[+] {get_utc_time()} - Checking if agent server running on port {agent_port}")

    result = subprocess.run(['netstat', '-ltnp'], capture_output=True, text=True)

    # Check if agent_port is in the result
    for line in result.stdout.splitlines():
        if f':{agent_port}' in line and 'python' in line:
            return True
    return False


def create_cron(cmdline):
    # will check if cron job exists for agent_server_monitor.py
    # if not will create it
    print(f"[+] Trying to create cron job for agent's server persistency")

    agent_root_dir = os.path.dirname(os.path.abspath(__file__))
    cron_log_file = os.path.join(agent_root_dir, "cron.log")
    cron_entry = f"* * * * * {cmdline} >> {cron_log_file} 2>&1\n"  # will run every 1 minute
    print(f"[+] Checking if cron job for agent server already exists"
          f"\n\tLog path: {cron_log_file}")

    # Check if the cron job already exists
    result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
    cron_jobs = result.stdout.splitlines()
    if cron_entry.strip() in cron_jobs:
        print(f"[+] cron job already exists")
        return

    print(f"[+] cron job doesn't exist. Trying to add it now.")
    print(f"[+] Trying to add execute permissions for {agent_root_dir}")
    chm = subprocess.run(['chmod', '-R', 'u+x', agent_root_dir], check=True, capture_output=True, text=True)
    cron_jobs.append(cron_entry.strip())
    new_cron = "\n".join(cron_jobs) + "\n"

    # Write the new cron jobs to crontab
    process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE)
    process.communicate(input=new_cron.encode())
    print(f"[+] cron job added")


