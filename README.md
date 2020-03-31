# dataworks-admin-utils
Contains DataWorks administrative utilities

## lambda-cleanup

A utility to clean up old (i.e. redundant) lambda versions.

### Installation (as a concourse pipeline)

1. Check out this repo and run `make boostrap` in the root folder
1. Log into Concourse with `make concourse-login`
1. Create / update the pipelines with `make update-lambda-cleanup-pipeline`
1. Browse to the concourse UI `lambda-cleanup` pipeline and run the job for the environment of your choice, e.g. `lambda-cleanup-development-job`.
    1. The job will checkout this repo, and execute the script `./utils/lambda-cleanup/lambda-cleanup.py`

### Pipeline maintenance
* There are also Makefile targets for `pause-lambda-cleanup-pipeline` and `unpause-lambda-cleanup-pipeline`

## ami-cleanup

An utility to clean up old AMIs.

### Usage

1. Aviator the pipeline in: `aviator -f aviator-ami-cleanup.yml`
1. Browse to the concourse UI `ami-cleanup` pipeline and run the job for the environment of your choice
