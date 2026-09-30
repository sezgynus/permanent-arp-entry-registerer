# Permanent ARP Entry Registerer

[English](README.md) | [Türkçe](README-tr.md)

**Permanent ARP Entry Registerer is a Python utility that automates creation of a permanent neighbor/ARP entry on a ZTE ZXHN H298A V1.0 router through its SSH, CLI, shell and BusyBox interfaces.**

The script connects to the router, navigates through its interactive command environment and ultimately executes:

```text
ip neighbour replace <ARP_IP> lladdr <ARP_MAC> dev br0 nud permanent
```

This repository is specifically built around the command flow exposed by the **ZTE ZXHN H298A V1.0**. It is not a generic ARP-management utility for arbitrary routers.

## What It Does

The script automates the following interaction:

```text
Python / Paramiko
      |
      v
SSH connection
      |
      v
wait for "Username:"
      |
      +--> send Linux username
      |
      v
wait for "Password:"
      |
      +--> send Linux password
      |
      v
wait for "CLI>"
      |
      +--> send "shell"
      |
      v
wait for "Login:"
      |
      +--> send Linux username
      |
      v
wait for "Password:"
      |
      +--> send the shell password expected by the current implementation
      |
      v
wait for "BusyBox"
      |
      v
ip neighbour replace <IP> lladdr <MAC> dev br0 nud permanent
```

The final command creates or replaces the neighbor-table entry for the supplied IP/MAC pair on interface `br0` and marks it with the Linux neighbor state `permanent`.

## Features

- Automates the router's interactive SSH/CLI login sequence.
- Registers a supplied IPv4/MAC mapping as a permanent neighbor entry.
- Uses `ip neighbour replace`, so the target entry can be created or an existing entry for that IP can be replaced.
- Targets the router's `br0` interface.
- Accepts SSH connection parameters from the command line.
- Accepts the router-side Linux username and password from the command line.
- Optional quiet mode suppresses banner, command-progress and timeout output.
- Uses Paramiko for SSH communication.
- No router firmware modification is performed by the script itself.

## Requirements

- Python 3
- [Paramiko](https://www.paramiko.org/)
- Network access to the router's SSH service
- Credentials that can reach the router CLI and shell flow expected by the script
- A ZTE ZXHN H298A V1.0 firmware/environment compatible with the prompts and commands used by this implementation

Install the Python dependency with:

```bash
python -m pip install paramiko
```

## Installation

Clone the repository:

```bash
git clone https://github.com/sezgynus/permanent-arp-entry-registerer.git
cd permanent-arp-entry-registerer
```

Install Paramiko:

```bash
python -m pip install paramiko
```

No package installation step is required for the project itself; the repository contains a standalone Python script.

## Usage

```text
python permanent_arp_entry_registerer.py \
  --host HOST \
  --port PORT \
  --username SSH_USERNAME \
  --password SSH_PASSWORD \
  --arp_ip ARP_IP \
  --arp_mac ARP_MAC \
  --linux_user LINUX_USERNAME \
  --linux_password LINUX_PASSWORD \
  [-q]
```

Example:

```bash
python permanent_arp_entry_registerer.py \
  --host 192.168.1.1 \
  --port 22 \
  --username ssh-user \
  --password ssh-password \
  --arp_ip 192.168.1.50 \
  --arp_mac 00:11:22:33:44:55 \
  --linux_user linux-user \
  --linux_password linux-password
```

Replace the example values with values appropriate for your router and network.

## Usage Video

A usage demonstration is available on YouTube:

https://youtu.be/vuDeCseHWLg?t=789

## Command-Line Arguments

| Argument | Required | Purpose |
|---|---:|---|
| `--host` | Yes | Router hostname or IP address passed to Paramiko |
| `--port` | Yes | SSH TCP port |
| `--username` | Yes | Username used for the initial Paramiko SSH connection |
| `--password` | Yes | Password used for the initial Paramiko SSH connection |
| `--arp_ip` | Yes | IP address to register in the permanent neighbor entry |
| `--arp_mac` | Yes | MAC address associated with `--arp_ip` |
| `--linux_user` | Yes | Username sent to the router's interactive CLI/shell login prompts |
| `--linux_password` | Yes | Password sent to the first interactive `Password:` prompt |
| `-q`, `--quiet` | No | Suppresses normal script output and prompt waiting |

All arguments except quiet mode are declared as required by `argparse`. The script also contains a secondary required-argument check.

## Quiet Mode

Use:

```bash
python permanent_arp_entry_registerer.py ... --quiet
```

In normal mode, `wait_for_message()` waits up to 10 seconds for each expected prompt and prints data received from the SSH channel.

In quiet mode, `wait_for_message()` immediately returns success instead of reading and validating each expected prompt. The script therefore sends commands with its fixed 200 ms delay without confirming that the router has reached the expected state.

Quiet mode should consequently be understood as more than output suppression: it also disables prompt synchronization.

## SSH and Host-Key Behavior

The script creates a Paramiko `SSHClient` and configures:

```python
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
```

An unknown SSH host key is therefore accepted automatically for this connection rather than requiring interactive verification.

The connection itself is opened with the supplied host, port, SSH username and SSH password.

## Router Command Sequence

The current command table is:

| Expected prompt | Value sent |
|---|---|
| `Username:` | `--linux_user` |
| `Password:` | `--linux_password` |
| `CLI>` | `shell` |
| `Login:` | `--linux_user` |
| second `Password:` | Router shell password embedded in the current source |
| `BusyBox` | `ip neighbour replace <ARP_IP> lladdr <ARP_MAC> dev br0 nud permanent` |

The second shell password is **hard-coded in the current implementation**; it is not taken from `--linux_password`. This makes the script firmware/environment-specific and means the source should be reviewed before use on a different firmware revision.

## Prompt Synchronization

For each step in normal mode, `wait_for_message()`:

1. waits for data to become available on the Paramiko channel;
2. reads up to 4096 bytes;
3. decodes the data as UTF-8;
4. prints the received data;
5. checks whether the expected substring is present;
6. waits up to 10 seconds before reporting a timeout.

After each command, `send_command()` appends a newline and waits 200 ms.

If an expected prompt is not found before the timeout, the command loop stops.

## ARP / Neighbor Entry Command

The generated router command is:

```text
ip neighbour replace ARP_IP lladdr ARP_MAC dev br0 nud permanent
```

Parameter mapping:

```text
ARP_IP   -> --arp_ip
ARP_MAC  -> --arp_mac
device   -> br0
state    -> permanent
```

The script does not expose the network interface or neighbor state as command-line options.

## Input Validation

The script checks whether required command-line values are present, but it does **not** validate the syntax or range of:

- the host;
- the SSH port beyond integer parsing;
- the ARP IP address;
- the MAC address;
- usernames or passwords.

Invalid values are therefore passed to Paramiko or to the router command flow and may fail there.

## Error Handling and Limitations

The current implementation is intentionally small and has several operational limitations:

- SSH connection/authentication exceptions are not caught by application-specific error handling.
- Prompt timeout handling exists only in non-quiet mode.
- Quiet mode bypasses prompt detection.
- The SSH channel is driven using fixed prompt strings and is therefore sensitive to firmware changes, localization or different CLI output.
- The router interface is fixed to `br0`.
- The second shell password is embedded in source.
- The script does not verify the resulting neighbor-table entry after sending the command.
- It does not provide a remove-entry command.
- It handles one IP/MAC mapping per invocation.
- It does not validate IP or MAC syntax.

These points describe the current source behavior rather than guarantees about every ZXHN H298A firmware revision.

## Security Considerations

Credentials supplied through command-line arguments may be visible to other local processes or retained in shell history, depending on the operating system and shell.

The current source also contains a router shell credential as a literal string. Review the script and understand the security implications before using or redistributing it.

Because `AutoAddPolicy` accepts unknown SSH host keys automatically, the script does not provide the same host-identity verification behavior as a strict known-hosts policy.

Use the utility only on networking equipment you own or are authorized to administer.

## Source Structure

```text
permanent-arp-entry-registerer/
├── .github/
│   └── workflows/
│       └── sign-commits.yml
├── .gitignore
├── LICENSE
├── README.md
└── permanent_arp_entry_registerer.py
```

| File | Purpose |
|---|---|
| `permanent_arp_entry_registerer.py` | SSH connection, prompt synchronization and permanent neighbor-entry registration |
| `.github/workflows/sign-commits.yml` | Repository commit-signing workflow |
| `LICENSE` | MIT license |

## License

This project is distributed under the [MIT License](LICENSE).

Copyright © 2023 Sezgin AÇIKGÖZ.
