#!/usr/bin/env python3

import argparse
import aws_utility


def main():
    ec2_client = aws_utility.client(
        command_line_arguments().account,
        command_line_arguments().role,
        "ec2")
    instances = ec2_client.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running', 'starting']}])
    for instance in instances:
        print('-------------------------')
        print(instance)
        print('-------------------------')
        print(instance.id, instance.instance_type)
        print('-------------------------')


def command_line_arguments():
    parser = argparse.ArgumentParser(
        description='Detect long running instances.')
    parser.add_argument('account', help='The AWS Account ID to target')
    parser.add_argument('role', help='The AWS Account role to assume', default="ci")
    parser.add_argument('max_age', help='Maximum age in hours', default="24")
    parser.add_argument('tag_name_to_ignore', help='A tag name to exclude a vm from analysis', default="long_lived_vm")
    parser.add_argument('tag_value_to_ignore', help='A tag name to exclude a vm from analysis', default="True")
    return parser.parse_args()


if __name__ == '__main__':
    main()
