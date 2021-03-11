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
from jira import JIRA

def run_checks(remote_server_username, remote_server_ip, private_rsa_key, remote_logfile, **remote_commands):
    remote_report= dict()
    for check_types in remote_commands:
        try:
            for i in remote_commands[check_types]:
                with Connection(user=remote_server_username, host=remote_server_ip, connect_kwargs={"key_filename": private_rsa_key}) as conn:
                    result = conn.run(i, hide=True)
                    msg = "##################### {0.command!r} on {0.connection.host} #####################\n\n{0.stdout}"
                    print(msg.format(result))
                    remote_report[i] = result.stdout
        except TypeError:
            pass
    pprint.pprint(remote_report)
    with open(remote_logfile, "w+") as log_file:
        pprint.pprint(remote_report, log_file)

def update_jira_ticket(jira_ticket_nr, jira_report_comment, jira_report_attachment_path):
    jira = JIRA(basic_auth=('USER', 'PASS'), options={'server':'https://JIRA-IP', 'verify':False})
    issue = jira.issue(jira_ticket_nr)
    jira.add_comment(issue, jira_report_comment)
    with open(jira_report_attachment_path, "rb") as report_to_upload:
        jira.add_attachment(issue=issue, attachment=report_to_upload)

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
    parser.add_argument('--private-key', required=False, help='Specify the rsa private key to use for ssh to your machines')
    parser.add_argument('--ticket', required=False, help='Specify the Jira ticket you want to')
    return parser.parse_args()

def start(args):
    remote_report_logs_path="/tmp/"
    remote_report_logs_name="test.log"
    remote_report_logs=remote_report_logs_path+remote_report_logs_name
    validate(args.ip)
    with open('commands.yml') as f:
        commands_dict = yaml.safe_load(f)
        print(commands_dict)
        ret = run_checks(args.username, args.ip, **commands_dict)
    ret = run_checks(args.username, args.ip, args.private_key, remote_report_logs)
    if args.ticket is not None:
        update_jira_ticket(args.ticket, "{code:java}Report ran on node: "+args.ip+" is attached on this ticket with name "+remote_report_logs_name+"{code}", remote_report_logs)
    return ret

if __name__ == '__main__':
    parsed_args = parse_args()
    ret = start(parsed_args)
    sys.exit(ret)