import paramiko
import time
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

def execute_commands(client, commands, arp_params, linux_user, linux_password):
    channel = client.invoke_shell()

    for command in commands:
        if wait_for_message(channel, command["wait_for"]):
            if "{arp_ip}" in command["send"] and "{arp_mac}" in command["send"]:
                command["send"] = command["send"].format(**arp_params)

            command["send"] = command["send"].replace("root", linux_user).replace("$F1r1@dl", linux_password)
            send_command(channel, command["send"])

            if "Password:" in command["wait_for"]:
                print(f"{command['send']}", end="")
            if "CLI>" in command["wait_for"]:
                print(f"{command['send']}")
            if "BusyBox" in command["wait_for"]:
                print(f"{command['send']}")
        else:
            print(f"{command['wait_for']} mesajı belirtilen süre içinde bulunamadı.")
            break

    client.close()

def print_colored(text, color_code):
    return f"\033[{color_code}m{text}\033[0m"

def print_banner():
    line_length = 75
    title = "Permanent ARP Entry registerer"
    version = "for \"ZTE ZXHN H298A V1.0\""
    developer = f"Developed by {print_colored('sezgynus', '92')}"
    github_repo = "GitHub Repository: [Learn More](https://github.com/sezgynus)"

    print("*" * line_length)
    print(f"*{title.center(line_length - 2)}*")
    print(f"*{version.center(line_length - 2)}*")
    print(f"*{developer.center(line_length + 7)}*")
    print(f"*{github_repo.center(line_length - 2)}*")
    print("*" * line_length)

def main():
    print_banner()
    if len(sys.argv) != 9:
        print("Kullanım: python program.py <host ip or name> <port> <ssh username> <ssh password> <arp_ip> <arp_mac> <linux_user> <linux_password>")
        sys.exit(1)

    hostname, port, username, password, arp_ip, arp_mac, linux_user, linux_password = sys.argv[1:9]
    client = ssh_connect(hostname, int(port), username, password)

    commands = [
        {"wait_for": "Username:", "send": linux_user},
        {"wait_for": "Password:", "send": linux_password},
        {"wait_for": "CLI>", "send": "shell"},
        {"wait_for": "Login:", "send": linux_user},
        {"wait_for": "Password:", "send": linux_password},
        {"wait_for": "BusyBox", "send": f"ip neighbour replace {arp_ip} lladdr {arp_mac} dev br0 nud permanent"}
    ]

    arp_params = {"arp_ip": arp_ip, "arp_mac": arp_mac}
    execute_commands(client, commands, arp_params, linux_user, linux_password)

if __name__ == "__main__":
    main()
