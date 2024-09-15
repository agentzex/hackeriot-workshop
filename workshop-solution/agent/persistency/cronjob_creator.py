import subprocess
import os



def create(agent_server_port):
    # will check if cron job exists for agent_server_monitor.py
    # if not will create it
    print(f"[+] Trying to create cron job for agent's server persistency")
    agent_persistency_dir = os.path.dirname(os.path.abspath(__file__))
    agent_root_dir = os.path.dirname(agent_persistency_dir)
    server_monitor_path = os.path.join(agent_persistency_dir, "agent_server_monitor.py")
    agent_server_path = os.path.join(agent_root_dir, "agent_server.py")
    cron_log_file = os.path.join(agent_persistency_dir, "cron.log")
    cron_entry = f"* * * * * /usr/bin/python3 {server_monitor_path} {agent_server_port} {agent_server_path} >> {cron_log_file} 2>&1\n"  # will run every 1 minute
    print(f"[+] Checking if cron job for agent server already exists.\n\tServer Monitor path: {server_monitor_path}"
          f"\n\tLog path: {cron_log_file}")

    # Check if the cron job already exists
    result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
    cron_jobs = result.stdout.splitlines()
    if cron_entry.strip() not in cron_jobs:
        print(f"[+] cron job doesn't exist. Trying to add it now.")
        print(f"[+] Trying to add execute permissions for {agent_root_dir}")
        chm = subprocess.run(['chmod', '-R', 'u+x', agent_root_dir], check=True, capture_output=True, text=True)
        # print(f"[+] Result: {chm.stdout}")
        cron_jobs.append(cron_entry.strip())
        new_cron = "\n".join(cron_jobs) + "\n"

        # Write the new cron jobs to crontab
        process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE)
        process.communicate(input=new_cron.encode())
        print(f"[+] cron job added")
    else:
        print(f"[+] cron job already exists")


