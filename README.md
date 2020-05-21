# dataworks-admin-utils
Contains DataWorks administrative utilities

## CI Pipelines

There are multiple admin style pipelines which are released to the CI system:

1. `lambda-cleanup`
2. `scale-down-services`
3. `scale-up-services`
4. `manage-kafka-connectors`
5. `manage-environments`
6. `generate-snapshots`
7. `send-snapshots`
8. `uc-list-snapshots`
9. `uc-data-load`
10. `ami-cleanup`

### Installing as a concourse pipeline

1. Check out this repo and run `make bootstrap` in the root folder
2. Log into Concourse with `make concourse-login`
3. Create / update the pipelines with the relevant pipeline `make update-xxx command` - see pipeline information below
4. Browse to the concourse UI for your pipeline and run the job for the environment of your choice

### Pipeline: lambda-cleanup

This is used to clean up old lambdas on environments. The job will checkout this repo, and execute the script `./utils/lambda-cleanup/lambda-cleanup.py`. The files for this pipeline are in the ci/lambda-cleanup folder in this repo. To update this pipeline in CI, you can run the following make command:

* `make update-lambda-cleanup-pipeline`

You can also pause or unpause the pipeline:

* `make pause-lambda-cleanup-pipeline`
* `make unpause-lambda-cleanup-pipeline`

### Pipeline: scale-down-services

This is used to scale down the given service to 0 within the desired environment. The files for this pipeline are in the ci/scale-down-services folder in this repo. To update this pipeline in CI, you can run the following make command:

* `make update-scale-down-services-pipeline`

You can also pause or unpause the pipeline:

* `make pause-scale-down-services-pipeline`
* `make unpause-scale-down-services-pipeline`

### Pipeline: scale-up-services

This is used to scale up the given service to 1 within the desired environment. The files for this pipeline are in the ci/scale-down-services folder in this repo. To update this pipeline in CI, you can run the following make command:

* `make update-scale-up-services-pipeline`

You can also pause or unpause the pipeline:

* `make pause-scale-up-services-pipeline`
* `make unpause-scale-up-services-pipeline`

### Pipeline: manage-kafka-connectors

This is used recycle the Kafka connector ECS containers (kafka-to-hbase and kafka-to-s3) in a given environment. The files for this pipeline are in the ci/manage-kafka-connectors folder in this repo. To update this pipeline in CI, you can run the following make command:

* `make update-manage-kafka-connectors-pipeline`

You can also pause or unpause the pipeline:

* `make pause-manage-kafka-connectors-pipeline`
* `make unpause-manage-kafka-connectors-pipeline`

### Pipeline: manage-environments

This is used to shutdown services in a given environment. The files for this pipeline are in the ci/manage-environments folder in this repo. To update this pipeline in CI, you can run the following make command:

* `make update-manage-environments-pipeline`

You can also pause or unpause the pipeline:

* `make pause-manage-environments-pipeline`
* `make unpause-manage-environments-pipeline`

### Pipeline: generate-snapshots

This is used to start the snapshot generation process within the desired environment - it only kicks it off and does not monitor it. The files for this pipeline are in the ci/generate-snapshots folder in this repo. To update this pipeline in CI, you can run the following make command:

* `make update-snapshots-pipeline`

You can also pause or unpause the pipeline:

* `make pause-snapshots-pipeline`
* `make unpause-snapshots-pipeline`

### Pipeline: send-snapshots

This is used to start the snapshot sending to Crown process within the desired environment - it only kicks it off and does not monitor it. The files for this pipeline are in the ci/generate-snapshots folder in this repo. To update this pipeline in CI, you can run the following make command:

* `make update-send-snapshots-pipeline`

You can also pause or unpause the pipeline:

* `make pause-send-snapshots-pipeline`
* `make unpause-send-snapshots-pipeline`

### Pipeline: uc-list-snapshots

This is used to list the files in the current folder set to be ingested by the import process. The files for this pipeline are in the ci/uc-list-snapshots folder in this repo. To update this pipeline in CI, you can run the following make command:

* `make update-uc-list-snapshots-pipeline`

You can also pause or unpause the pipeline:

* `make pause-uc-list-snapshots-pipeline`
* `make unpause-uc-list-snapshots-pipeline`

### Pipeline: uc-data-load

This is used to start the import process from the snapshot folders to HBase within the desired environment - it only kicks it off and does not monitor it. The files for this pipeline are in the ci/uc-data-load folder in this repo. To update this pipeline in CI, you can run the following make command:

* `make update-uc-data-load-pipeline`

You can also pause or unpause the pipeline:

* `make pause-uc-data-load-pipeline`
* `make unpause-uc-data-load-pipeline`

### Pipeline: ami-cleanup

A utility to clean up old AMIs. The files for this pipeline are in the ci/ami-cleanup folder in this repo. To update this pipeline in CI, you can run the following make command:

* `make update-ami-cleanup-pipeline`

You can also pause or unpause the pipeline:

* `make pause-ami-cleanup-pipeline`
* `make unpause-ami-cleanup-pipeline`

### Pipeline: terraform-taint

A utility to taint Terraform resources. Considering the danger the jobs are disabled in the code by commenting out the `taint` command. `state show` command that precedes it allows you to test the resource address.

To use:
1. Add the Terraform repo that contains TF resource to be tainted as a Concourse resource in `ci/terraform-taint/resources-terraform-taint`
1. Modify the job for the given environment, TF repo and TF resource(s):
    1. In the appropriate file under `ci/terraform-taint/jobs`,
    1. modify resource reference in `get` step;
    1. put space-separated list of TF resources into `RESOURCE_NAMES` variable
1. Aviator and run, verify that `state show` output lists the expected resources.
1. Uncomment the line with `taint` command.
1. Aviator and run.
1. When done, reset to HEAD of master branch and aviator in so that `taint` command is commented out in Concourse 
