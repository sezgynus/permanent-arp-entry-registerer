import paramiko
import time
import argparse
import sys

def ssh_connect(hostname, port, username, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, port, username, password)
    return client

def send_command(channel, command):
    channel.send(command + "\n")
    time.sleep(0.2)

def wait_for_message(channel, message, timeout=10):
    if not args.quiet:
        start_time = time.time()
        while time.time() - start_time < timeout:
            if channel.recv_ready():
                received_message = channel.recv(4096).decode("utf-8")
                print(received_message, end="")
                if message in received_message:
                    return True
            else:
                time.sleep(0.2)

        return False
    else:
        return True

def execute_commands(client, commands, arp_params, linux_user, linux_password):
    channel = client.invoke_shell()

    for command in commands:
        if wait_for_message(channel, command["wait_for"]):
            if "{arp_ip}" in command["send"] and "{arp_mac}" in command["send"]:
                command["send"] = command["send"].format(**arp_params)

            send_command(channel, command["send"])

            if "Password:" in command["wait_for"]:
                if not args.quiet:
                    print(f"{command['send']}", end="")
            if "CLI>" in command["wait_for"]:
                if not args.quiet:
                    print(f"{command['send']}")
            if "BusyBox" in command["wait_for"]:
                if not args.quiet:
                    print(f"{command['send']}")
        else:
            if not args.quiet:
                print(f"{command['wait_for']} mesajı belirtilen süre içinde bulunamadı.")
            break

    client.close()

def print_colored(text, color_code):
    if not args.quiet:
        return f"\033[{color_code}m{text}\033[0m"
    else:
        return ""

def print_banner():
    if not args.quiet:
        line_length = 82
        title = "Permanent ARP Entry registerer"
        version = "for \"ZTE ZXHN H298A V1.0\""
        developer = f"Developed by {print_colored('sezgynus', '92')}"
        github_repo = "GitHub Repository:(https://github.com/sezgynus/permanent-arp-entry-registerer)"

        print("*" * line_length)
        print(f"*{title.center(line_length - 2)}*")
        print(f"*{version.center(line_length - 2)}*")
        print(f"*{developer.center(line_length + 7)}*")
        print(f"*{github_repo.center(line_length - 2)}*")
        print("*" * line_length)
    else:
        pass

def parse_args():
    parser = argparse.ArgumentParser(description='Permanent ARP Entry registerer for ZTE ZXHN H298A V1.0')
    parser.add_argument('--host', type=str, help='Host IP or name', required=True)
    parser.add_argument('--port', type=int, help='SSH port', required=True)
    parser.add_argument('--username', type=str, help='SSH username', required=True)
    parser.add_argument('--password', type=str, help='SSH password', required=True)
    parser.add_argument('--arp_ip', type=str, help='ARP IP', required=True)
    parser.add_argument('--arp_mac', type=str, help='ARP MAC', required=True)
    parser.add_argument('--linux_user', type=str, help='Linux username', required=True)
    parser.add_argument('--linux_password', type=str, help='Linux password', required=True)
    parser.add_argument('-q', '--quiet', action='store_true', help='Disable print outputs')
    return parser.parse_args()

def check_required_args(args):
    required_args = ['host', 'port', 'username', 'password', 'arp_ip', 'arp_mac', 'linux_user', 'linux_password']
    missing_args = [arg for arg in required_args if not getattr(args, arg, None)]
    if missing_args:
        print(f"Uyarı: Lütfen şu zorunlu argümanları sağlayın: {', '.join(missing_args)}")
        print("Kullanım: python program.py --host <host_ip> --port <port> --username <ssh_username> --password <ssh_password> --arp_ip <arp_ip> --arp_mac <arp_mac> --linux_user <linux_user> --linux_password <linux_password> [-q]")
        sys.exit(1)

args = parse_args()
check_required_args(args)

def main():
    print_banner()
    client = ssh_connect(args.host, args.port, args.username, args.password)

    commands = [
        {"wait_for": "Username:", "send": args.linux_user},
        {"wait_for": "Password:", "send": args.linux_password},
        {"wait_for": "CLI>", "send": "shell"},
        {"wait_for": "Login:", "send": args.linux_user},
        {"wait_for": "Password:", "send": "$F1r1@dl"},
        {"wait_for": "BusyBox", "send": f"ip neighbour replace {args.arp_ip} lladdr {args.arp_mac} dev br0 nud permanent"}
    ]

    arp_params = {"arp_ip": args.arp_ip, "arp_mac": args.arp_mac}
    execute_commands(client, commands, arp_params, args.linux_user, args.linux_password)

if __name__ == "__main__":
    main()
