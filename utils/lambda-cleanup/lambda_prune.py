#!/usr/bin/env python3

import argparse
from common_files import aws_utility


def main():
    lambda_client = aws_utility.client(command_line_arguments().account, "ci", "lambda")
    [prune_function(lambda_client, function) for function
     in lambda_client.list_functions()['Functions']]


def prune_function(lambda_client, function):
    print(f"Pruning '{function['FunctionName']}'.")
    [remove_version(lambda_client, arn) for arn in old_versions(lambda_client, function)]


def old_versions(lambda_client, function):
    versions = all_versions(lambda_client, function)
    return [v['FunctionArn'] for v in [version for version in versions
                                           if version['Version'] !=
                                           function['Version']]]


def all_versions(lambda_client, function):
    return lambda_client.list_versions_by_function(
        FunctionName=function['FunctionArn'])['Versions']


def remove_version(client, arn):
    print(f"Deleting '{arn}'.")
    client.delete_function(FunctionName=arn)


def command_line_arguments():
    parser = argparse.ArgumentParser(
        description='Delete all but the latest version of a lambda.')
    parser.add_argument('account', help='The AWS Account ID to target')
    return parser.parse_args()


if __name__ == '__main__':
    main()
