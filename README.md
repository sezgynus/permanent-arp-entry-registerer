# Permanent ARP Entry Registerer

This script automates the process of registering a permanent ARP entry on a ZTE ZXHN H298A V1.0 router.

## Table of Contents
- [Usage](#usage)
- [Features](#features)
- [Installation](#installation)
- [Developer](#developer)
- [License](#license)

## Usage
https://youtu.be/vuDeCseHWLg?t=789
1. Install the required dependencies:

   ```bash
   pip install paramiko
   
2. Run the script:

   ```bash
   permanent_arp_entry_registerer.py [-h] --host HOST --port PORT --username USERNAME --password PASSWORD --arp_ip ARP_IP --arp_mac ARP_MAC --linux_user LINUX_USER --linux_password LINUX_PASSWORD [-q]
   
## Features

- Automatic registration of a permanent ARP entry
-  Supports custom Linux username and password

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/sezgynus/permanent-arp-entry-registerer.git
   
2. Navigate to the project directory:

   ```bash
   cd permanent-arp-entry-registerer

3. Install the required dependencies:

   ```bash
   pip install paramiko
