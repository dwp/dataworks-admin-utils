#!/usr/bin/env python3

import argparse
import logging
import os
import sys
import boto3

# Snapshot description filters
snap_filter_1="Created by CreateImage*for AMI_ID*"
snap_filter_2="Copied for DestinationAmi AMI_ID*"

# Initialise logging
logger = logging.getLogger(__name__)
log_level = os.environ["LOG_LEVEL"] if "LOG_LEVEL" in os.environ else "INFO"
logger.setLevel(logging.getLevelName(log_level.upper()))
logging.basicConfig(
    stream=sys.stdout,
    format="%(asctime)s %(levelname)s %(module)s "
           "%(process)s[%(thread)s] %(message)s",
)
logger.info("Logging at {} level".format(log_level.upper()))

def get_arguments():
    parser = argparse.ArgumentParser(description='Delete older AMIs except for N latest.')

    parser.add_argument('--aws-profile', help='AWS profile ID for the account containing AMIs', required=True)
    parser.add_argument('--aws-region', help='AWS region', required=True)
    parser.add_argument('--ami-prefix', help='AMI name prefix', required=True)
    parser.add_argument('--keep-min', type=int, help='Minimum number of AMIs to keep', required=True)
    parser.add_argument('--aws-profile-list', nargs='*', help='List of additional AWS profile IDs to check AMI usage in')
    parser.add_argument('--dry-run', default=True, help='Set to False to perform deletion')

    return parser.parse_args()

def get_ec2_client(aws_profile, aws_region):
    session = boto3.Session(profile_name=aws_profile)
    ec2_client = session.client('ec2', region_name = aws_region)
    return ec2_client

def get_asg_client(aws_profile, aws_region):
    session = boto3.Session(profile_name=aws_profile)
    asg_client = session.client('autoscaling', region_name = aws_region)
    return asg_client

def create_deletion_list(boto_client, ami_prefix, keep_min):
    logger.debug(f"AMI prefix: {ami_prefix}, minimum number to keep: {keep_min}")
    try:
        full_list = boto_client.describe_images(Filters=[
            {
                'Name': 'name',
                'Values': [ami_prefix]
            }
            ])['Images']
        #logger.debug(full_list)
    except Exception as e:
        logger.debug(e)
    sorted_list = sorted(full_list, key=lambda k: k['CreationDate'])
    for ami in sorted_list:
        logger.debug(f"Date: {ami['CreationDate']}, AMI Name: {ami['Name']}")
    if len(sorted_list) > keep_min:
        del_offset = len(sorted_list) - keep_min
        del sorted_list[del_offset:]
    logger.debug(f"Trimmed list:")
    for ami in sorted_list:
        logger.debug(f"Date: {ami['CreationDate']}, AMI Name: {ami['Name']}")
    return sorted_list

def ami_used_in_instances(boto_client,ami_id):
    # Check against running instances
    is_used = False
    try:
        instance_list = boto_client.describe_instances(Filters=[
            {
                'Name': 'image-id',
                'Values': [ami_id]
            }
        ])['Reservations']
        if len(instance_list) > 0:
            is_used = True
            logger.debug(f"AMI ID: {ami_id} is used by instance(s)")
            return True
    except Exception as e:
        logger.debug(e)

def ami_used_in_launch_configs(boto_client,ami_id):
    # Check against launch configurations
    try:
        lc_list = boto_client.describe_launch_configurations()['LaunchConfigurations']
        for lc in lc_list:
            if lc['ImageId'] == ami_id:
                logger.debug(f"AMI {ami_id} is used by launch configuration {lc['LaunchConfigurationName']}")
                return True
    except Exception as e:
        logger.debug(e)

def ami_used_in_launch_templates(boto_client,ami_id):
    # Check against launch templates
    try:
        lt_list = boto_client.describe_launch_templates()['LaunchTemplates']
        for lt in lt_list:
            lt_desc = boto_client.describe_launch_template_versions(
                LaunchTemplateId = lt['LaunchTemplateId'],
                Versions = ['$Latest'],
                Filters=[
                    {
                        'Name': 'image-id',
                        'Values': [ami_id]
                    }
            ])['LaunchTemplateVersions']
            if len(lt_desc) > 0:
                logger.debug(f"AMI {ami_id} is used by launch template {lt['LaunchTemplateName']}")
                return True
    except Exception as e:
        logger.debug(e)

def check_ami_is_used(ec2_client, asg_client, ami_id):
    # Check against running instances
    is_used = False
    try:
        instance_list = ec2_client.describe_instances(Filters=[
            {
                'Name': 'image-id',
                'Values': [ami_id]
            }
        ])['Reservations']
        if len(instance_list) > 0:
            is_used = True
            logger.debug(f"AMI ID: {ami_id} is used by instance(s)")
            is_used = True
    except Exception as e:
        logger.debug(e)

    if not is_used:
        # Check against launch configurations
        try:
            lc_list = asg_client.describe_launch_configurations()['LaunchConfigurations']
            for lc in lc_list:
                if lc['ImageId'] == ami_id:
                    logger.debug(f"AMI {ami_id} is used by launch configuration {lc['LaunchConfigurationName']}")
                    is_used = True
        except Exception as e:
            logger.debug(e)

    if not is_used:
        # Check against launch templates
        try:
            lt_list = ec2_client.describe_launch_templates()['LaunchTemplates']
            for lt in lt_list:
                lt_desc = ec2_client.describe_launch_template_versions(
                    LaunchTemplateId = lt['LaunchTemplateId'],
                    Versions = ['$Latest'],
                    Filters=[
                        {
                            'Name': 'image-id',
                            'Values': [ami_id]
                        }
                    ])['LaunchTemplateVersions']
                if len(lt_desc) > 0:
                    logger.debug(f"AMI {ami_id} is used by launch template {lt['LaunchTemplateName']}")
                    is_used = True
        except Exception as e:
            logger.debug(e)
    return is_used

def common(lst1, lst2):
    return list(set(lst1) & set(lst2))


def delete_ami(ec2_client, ami_id, dry_run):
    # Deregister AMI

    try:
        if not dry_run:
            ec2_client.deregister_image(ImageId=ami_id)
            logger.info(f"AMI {ami_id} deregistered")
        else:
            logger.info(f"AMI {ami_id} would be deregistered if this wasn't a dry run")
    except Exception as e:
        logger.debug(f"Error while deregistering AMI {ami_id}")
        logger.debug(e)


    # Get a list of snapshots associated with the ami
    filter_string_1 = snap_filter_1.replace("AMI_ID", ami_id)
    filter_string_2 = snap_filter_2.replace("AMI_ID", ami_id)
    try:
        snapshot_list = ec2_client.describe_snapshots(Filters=[
            {
                'Name': 'description',
                'Values': [filter_string_1]
            }
        ])['Snapshots']
    except Exception as e:
        logger.debug(e)

    if len(snapshot_list) == 0:
        try:
            snapshot_list = ec2_client.describe_snapshots(Filters=[
                {
                    'Name': 'description',
                    'Values': [filter_string_2]
                }
            ])['Snapshots']
        except Exception as e:
            logger.debug(e)

    if len(snapshot_list) == 0:
        logger.error(f"No snapshots found for AMI {ami_id}")

    for snapshot in snapshot_list:
        snapshot_id = snapshot['SnapshotId']
        try:
            if not dry_run:
                ec2_client.delete_snapshot(SnapshotId=snapshot_id)
                logger.info(f"Snapshot {snapshot_id} deleted")
            else:
                logger.info(f"Snapshot {snapshot_id} would be deleted if this wasn't a dry run")
        except Exception as e:
            logger.debug(e)

def main():
    args = get_arguments()
    if args.aws_profile_list is None:
        args.aws_profile_list = []
    main_client = get_ec2_client(args.aws_profile, args.aws_region)
    candidate_list = create_deletion_list(main_client, args.ami_prefix, args.keep_min)
    aws_profile_list_to_check = [args.aws_profile] + args.aws_profile_list

    deletion_list = {}
    for profile in aws_profile_list_to_check:
        deletion_list[profile] = []
        ec2_client = get_ec2_client(profile, args.aws_region)
        asg_client = get_asg_client(profile, args.aws_region)
        for ami in candidate_list:
            if not check_ami_is_used(ec2_client,asg_client,ami['ImageId']):
                deletion_list[profile].append(ami['ImageId'])
        logger.debug(f"Deletion list for profile {profile}:")
        logger.debug(deletion_list[profile])

    deletion_list_total = deletion_list[aws_profile_list_to_check[0]]
    for profile in deletion_list:
        deletion_list_total = common(deletion_list_total,deletion_list[profile])

    logger.info(f"List of AMIs to delete: {deletion_list_total}")

    for ami_id in deletion_list_total:
        delete_ami(ec2_client,ami_id,args.dry_run)


if __name__ == '__main__':
    main()
