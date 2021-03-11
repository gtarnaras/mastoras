#!/usr/bin/env python3
"""
Simple script to use when trying to troubleshoot issues with your Linux server
or an application that is running on this server.
Copyright (c) 2021, George Tarnaras
"""

import sys
import argparse
import re
import yaml
from fabric import Connection

def run_checks(remote_server_username, remote_server_ip, **remote_commands):
    remote_server= remote_server_username+'@'+remote_server_ip
    for check_types in remote_commands:
        try:
            for i in remote_commands[check_types]:
                result = Connection(remote_server).run(i, hide=True)
                msg = "##################### {0.command!r} on {0.connection.host} #####################\n\n{0.stdout}"
                print(msg.format(result))
        except TypeError:
            pass

def validate_ip(ip_to_validate):
    reg = r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
    if re.match(reg, ip_to_validate):
        return True
    else:
        print("Invalid IP address, please check your input and try again")
        sys.exit(1)
        return False

def validate(ip_from_argparse):
    validate_ip(ip_from_argparse)

def parse_args():
    parser = argparse.ArgumentParser(description='Simple script to help you with your troubleshooting.')
    parser.add_argument('--username', required=True, help='Specify the remote server logon username')
    parser.add_argument('--ip', required=True, help='Specify the ip of the remote server')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    validate(args.ip)
    with open('commands.yml') as f:
        commands_dict = yaml.safe_load(f)
        print(commands_dict)
        ret = run_checks(args.username, args.ip, **commands_dict)
    sys.exit(ret)