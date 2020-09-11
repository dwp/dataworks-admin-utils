#!/usr/bin/env python3

import boto3


def client(account, role, client_type):
    sts = boto3.client("sts")
    credentials = sts.assume_role(
        RoleArn=f"arn:aws:iam::{account}:role/{role}", RoleSessionName="clean_up"
    )["Credentials"]
    return boto3.client(
        client_type,
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"],
    )
