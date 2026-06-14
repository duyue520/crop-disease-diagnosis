import paramiko
import sys

HOST = "119.91.113.191"
USER = "ubuntu"
PASSWORD = "1323547070@Du"

def run_ssh(commands, timeout=60):
    """Connect via SSH and run commands, returning stdout/stderr for each."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(HOST, username=USER, password=PASSWORD, timeout=15)
    except Exception as e:
        print(f"SSH connection failed: {e}")
        return None

    results = {}
    for label, cmd in commands:
        try:
            stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
            out = stdout.read().decode('utf-8', errors='replace')
            err = stderr.read().decode('utf-8', errors='replace')
            results[label] = (out.strip(), err.strip())
        except Exception as e:
            results[label] = ("", f"ERROR: {e}")

    client.close()
    return results

commands = [
    # --- 1. Disk usage ---
    ("disk_usage_root", "sudo du -sh /* 2>/dev/null | sort -rh | head -40"),
    ("disk_usage_home", "sudo du -sh /home/* 2>/dev/null | sort -rh"),
    ("disk_usage_var", "sudo du -sh /var/* 2>/dev/null | sort -rh"),
    ("df_h", "df -h"),
    # large files (>100MB)
    ("large_files", "sudo find / -type f -size +100M -exec ls -lh {} \\; 2>/dev/null | awk '{print $5, $NF}' | sort -rh | head -30"),
    # top 50 largest dirs
    ("largest_dirs", "sudo du -h --max-depth=3 / 2>/dev/null | sort -rh | head -50"),

    # --- 2. Running processes and memory ---
    ("memory", "free -h"),
    ("top_processes_mem", "ps aux --sort=-%mem | head -20"),
    ("top_processes_cpu", "ps aux --sort=-%cpu | head -20"),
    ("process_count", "ps aux | wc -l"),

    # --- 3. Nginx config ---
    ("nginx_conf", "sudo cat /etc/nginx/nginx.conf 2>/dev/null"),
    ("nginx_sites", "sudo ls -la /etc/nginx/sites-enabled/ 2>/dev/null; sudo ls -la /etc/nginx/conf.d/ 2>/dev/null"),
    ("nginx_conf_files", "for f in /etc/nginx/sites-enabled/* /etc/nginx/conf.d/*.conf; do echo '=== FILE: '$f' ==='; sudo cat \"$f\" 2>/dev/null; done"),

    # --- 4. Systemd services ---
    ("systemd_services", "sudo ls /etc/systemd/system/*.service 2>/dev/null; sudo ls /etc/systemd/system/multi-user.target.wants/*.service 2>/dev/null"),
    ("systemd_custom", "for f in /etc/systemd/system/*.service; do echo '=== FILE: '$f' ==='; sudo cat \"$f\" 2>/dev/null; done"),

    # --- 5. Pip packages ---
    ("pip_list_all", "pip3 list --format=columns 2>/dev/null || pip list --format=columns 2>/dev/null"),
    ("pip_outdated", "pip3 list --outdated --format=columns 2>/dev/null || pip list --outdated --format=columns 2>/dev/null"),
    ("python_version", "python3 --version 2>/dev/null; python --version 2>/dev/null"),

    # --- Extra useful info ---
    ("os_release", "cat /etc/os-release 2>/dev/null"),
    ("uptime", "uptime"),
    ("docker_ps", "sudo docker ps -a 2>/dev/null || echo 'no docker or not running'"),
    ("docker_images", "sudo docker images 2>/dev/null || echo 'no docker'"),
    ("inodes", "df -i"),
]

results = run_ssh(commands, timeout=120)

if results is None:
    sys.exit(1)

for label, (out, err) in results.items():
    print(f"\n{'='*80}")
    print(f"=== {label} ===")
    print(f"{'='*80}")
    if out:
        print(out)
    if err:
        print(f"[STDERR]: {err}")
