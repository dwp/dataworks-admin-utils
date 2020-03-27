# dataworks-admin-utils
Contains DataWorks administrative utilities

## lambda-cleanup

A utility to clean up old (i.e. redundant) lambda versions.

### Installation (as a concourse pipeline)

1. Check out this repo and run `make boostrap` in the root folder
1. Log into Concourse with `make concourse-login`
1. Create / update the pipelines with `make update-lambda-cleanup-pipeline`
1. Browse to the concourse UI `lambda-cleanup` pipeline and run the job for the environment of your choice, e.g. `lambda-cleanup-development-job`.
    1. The job will checkout this repo, and execute the script `./utils/lambda-cleanup/lambda_prune.py`

### Pipeline maintenance
* There are also Makefile targets for `pause-lambda-cleanup-pipeline` and `unpause-lambda-cleanup-pipeline`

## detect-old-instances

A concourse job that runs hourly, checks if any instances are long running that should not be, and sends an sns message to a monitored queue for each offender.

### Running locally

First , log into aws cli with your usual credentials.
Then, execute this and wait for the report on the console:
    ```
    make detect-old-instances-local aws_account=12345678 aws_role=administrator
    ```
For testing, you may optionally override the max age, tag name and value
    ```
    make detect-old-instances-local ... max_age=2 tag_name_to_ignore=some_tag tag_value_to_ignore=other_value
    ```

### Installation (as a concourse pipeline)

1. Check out this repo and run `make boostrap` in the root folder
1. Log into Concourse with `make concourse-login`
1. Create / update the pipelines with `make update-detect-old-instances-pipeline`
1. Browse to the concourse UI `detect-old-instances` examine the pipeline
    1. The job should run hourly in each account.
    1. The job will checkout this repo, and execute the script `./utils/detect-old-instances/detect_old_instances.py`

### Pipeline maintenance
* There are also Makefile targets for `pause-detect-old-instances-pipeline` and `unpause-detect-old-instances-pipeline`
