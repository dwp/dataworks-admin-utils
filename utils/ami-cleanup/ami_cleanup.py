#!/usr/bin/env python3

import argparse
import logging
import os
import sys
import boto3

# Snapshot description filters
snap_filter_templates = [
    "Created by CreateImage*for AMI_ID*",
    "Copied for DestinationAmi AMI_ID*",
]

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
    parser = argparse.ArgumentParser(
        description="Delete older AMIs except for N latest."
    )

    parser.add_argument(
        "--aws-profile",
        help="AWS profile ID for the account that owns the AMIs",
        required=True,
    )
    parser.add_argument("--aws-region", help="AWS region", required=True)
    parser.add_argument("--ami-prefix", help="AMI name prefix", required=True)
    parser.add_argument(
        "--keep-min", type=int, help="Minimum number of AMIs to keep", required=True
    )
    parser.add_argument(
        "--aws-profile-list",
        nargs="*",
        help="List of additional AWS profile IDs to use to check for AMI usage in other accounts, i.e. accounts with which the AMI is shared",
    )
    parser.add_argument(
        "--dry-run", help="Set to False to perform deletion", required=True,
    )

    args = parser.parse_args()
    args.dry_run = parse_dry_run_value(args.dry_run)

    return args


def parse_dry_run_value(argument):
    return argument.lower() != "false"


def get_boto_client(aws_service_name, aws_region):
    session = boto3.Session()
    return session.client(aws_service_name, region_name=aws_region)


def get_deletion_list(aws_region, ami_prefix, keep_min):
    logger.debug(f"AMI prefix: {ami_prefix}, minimum number to keep: {keep_min}")

    ec2_client = get_boto_client("ec2", aws_region)
    sts_client = get_boto_client("sts", aws_region)

    # Filter AMIs returned to only those owned by aws-profile account
    account_number = sts_client.get_caller_identity()["Account"]
    try:
        full_list = ec2_client.describe_images(
            Filters=[
                {"Name": "name", "Values": [ami_prefix]},
                {"Name": "owner-id", "Values": [account_number]},
            ]
        )["Images"]
    except Exception as e:
        logger.error(f"Failed to get list of AMIs for name prefix {ami_prefix} : {e}")
        raise
    sorted_list = sorted(full_list, key=lambda k: k["CreationDate"])
    if logger.isEnabledFor(logging.DEBUG):
        for ami in sorted_list:
            logger.debug(f"Date: {ami['CreationDate']}, AMI Name: {ami['Name']}")
    if len(sorted_list) > keep_min:
        del sorted_list[len(sorted_list) - keep_min :]
    else:
        sorted_list = []
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Trimmed list:")
        for ami in sorted_list:
            logger.debug(
                f"Date: {ami['CreationDate']}, AMI Name: {ami['Name']}, AMI ID: {ami['ImageId']}"
            )
    return sorted_list


def check_ami_is_used(aws_region, ami_id):
    ec2_client = get_boto_client("ec2", aws_region)
    asg_client = get_boto_client("autoscaling", aws_region)

    # Check against running instances
    try:
        instance_list = ec2_client.describe_instances(
            Filters=[{"Name": "image-id", "Values": [ami_id]}]
        )["Reservations"]
        if len(instance_list) > 0:
            logger.debug(f"AMI ID: {ami_id} is used by instance(s)")
            return True
    except Exception as e:
        logger.error(f"Failed to get list of Instances using AMI ID {ami_id} : {e}")
        raise

    # Check against launch configurations
    try:
        lc_list = asg_client.describe_launch_configurations()["LaunchConfigurations"]
        for lc in lc_list:
            if lc["ImageId"] == ami_id:
                logger.debug(
                    f"AMI {ami_id} is used by launch configuration {lc['LaunchConfigurationName']}"
                )
                return True
    except Exception as e:
        logger.error(
            f"Failed to get list of Launch Configurations using AMI ID {ami_id} : {e}"
        )
        raise

    # Check against launch templates
    try:
        lt_list = ec2_client.describe_launch_templates()["LaunchTemplates"]
        for lt in lt_list:
            lt_desc = ec2_client.describe_launch_template_versions(
                LaunchTemplateId=lt["LaunchTemplateId"],
                Versions=["$Latest"],
                Filters=[{"Name": "image-id", "Values": [ami_id]}],
            )["LaunchTemplateVersions"]
            if len(lt_desc) > 0:
                logger.debug(
                    f"AMI {ami_id} is used by Launch Template {lt['LaunchTemplateName']}"
                )
                return True
    except Exception as e:
        logger.error(
            f"Failed to get list of Launch Templates using AMI ID {ami_id} : {e}"
        )
        raise

    return False


def delete_ami(aws_region, ami_id, dry_run):
    # Deregister AMI

    ec2_client = get_boto_client("ec2", aws_region)

    try:
        if not dry_run:
            ec2_client.deregister_image(ImageId=ami_id)
            logger.info(f"AMI {ami_id} deregistered")
        else:
            logger.info(f"AMI {ami_id} would be deregistered if this wasn't a dry run")
    except Exception as e:
        logger.error(f"Error while deregistering AMI {ami_id}: {e}")
        raise

    # Get a list of snapshots associated with the ami
    snap_filters = [
        template.replace("AMI_ID", ami_id) for template in snap_filter_templates
    ]
    snapshot_list = []

    for snap_filter in snap_filters:
        try:
            snapshot_list_for_filter = ec2_client.describe_snapshots(
                Filters=[{"Name": "description", "Values": [snap_filter]}]
            )["Snapshots"]
        except Exception as e:
            logger.error(f"Failed to get list of Snapshots for AMI ID {ami_id} : {e}")
            raise
        if len(snapshot_list_for_filter) > 0:
            snapshot_list.append(snapshot_list_for_filter)

    if len(snapshot_list) > 0:
        # Flatten list of lists generated above
        flat_snapshot_list = []
        for sublist in snapshot_list:
            for item in sublist:
                flat_snapshot_list.append(item)

        for snapshot in flat_snapshot_list:
            snapshot_id = snapshot["SnapshotId"]
            try:
                if not dry_run:
                    ec2_client.delete_snapshot(SnapshotId=snapshot_id)
                    logger.info(f"Snapshot {snapshot_id} deleted")
                else:
                    logger.info(
                        f"Snapshot {snapshot_id} would be deleted if this wasn't a dry run"
                    )
            except Exception as e:
                logger.debug(e)
    else:
        # If no snapshots exist for an AMI due to e.g. manual deletion without deregestering AMI, log an error and continue.
        logger.error(f"No snapshots found for AMI {ami_id}")


def main():

    args = get_arguments()

    if args.aws_profile_list is None:
        args.aws_profile_list = []
    candidate_list = get_deletion_list(
        args.aws_region, args.ami_prefix, args.keep_min
    )

    deletion_list = {}
    for profile in aws_profile_list:
        deletion_list[profile] = []
        for ami in candidate_list:
            if not check_ami_is_used(args.aws_region, ami["ImageId"]):
                deletion_list[profile].append(ami["ImageId"])
        logger.debug(f"Deletion list for profile {profile}:")
        logger.debug(deletion_list[profile])

    deletion_list_total = deletion_list[aws_profile_list[0]]
    for profile in deletion_list:
        deletion_list_total = deletion_list_total + deletion_list[profile]

    deletion_list_total = list(set(deletion_list_total))
    logger.info(f"List of AMIs to delete: {deletion_list_total}")

    for ami_id in deletion_list_total:
        delete_ami(args.aws_region, ami_id, args.dry_run)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        logger.error(error)
        raise
