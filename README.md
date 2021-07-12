# dataworks-admin-utils
Contains DataWorks administrative utilities

## CI Pipelines

There are multiple admin style pipelines which are released to the CI system:

0. `lambda-cleanup`
0. `scale-down-services`
0. `scale-up-services`
0. `manage-ecs-services`
0. `manage-environments`
0. `generate-snapshots`
0. `send-snapshots`
0. `hbase-data-ingestion`
0. `ami-cleanup`
0. `adg-emr-admin`
0. `clive-emr-admin`
0. `uc-feature-emr-admin`
0. `kickstart-adg-emr-admin`
0. `mongo-latest-emr-admin`
0. `pdm-emr-admin`

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

### Pipeline: manage-ecs-services

This is used to manage the following ECS containers:
* Kafka connectors like kafka-to-s3 and kafka-to-hbase 
* k2hb metadata reconciliation services for ucfs and equality feeds
* UCFS Claimant Kafka consumer

The files for this pipeline are in the ci/manage-ecs-services folder in this repo. To update this pipeline in CI, you can run the following make command:

* `make update-manage-ecs-services-pipeline`

You can also pause or unpause the pipeline:

* `make pause-manage-ecs-services-pipeline`
* `make unpause-manage-ecs-services-pipeline`

### Pipeline: manage-environments

This is used to shutdown services in a given environment. The files for this pipeline are in the ci/manage-environments folder in this repo. To update this pipeline in CI, you can run the following make command:

* `make update-manage-environments-pipeline`

You can also pause or unpause the pipeline:

* `make pause-manage-environments-pipeline`
* `make unpause-manage-environments-pipeline`

### Pipeline: generate-snapshots

This is used to start the snapshot generation process within the desired environment - it only kicks it off and does not monitor it. The files for this pipeline are in the ci/generate-snapshots folder in this repo. To update this pipeline in CI, you can run the following make command:

* `make update-generate-snapshots-pipeline`

You can also pause or unpause the pipeline:

* `make pause-generate-snapshots-pipeline`
* `make unpause-generate-snapshots-pipeline`

#### Overrides

The following overrides can be passed through as config params from the environment jobs to the generate snapshots task in the pipelines:

* `GENERATE_SNAPSHOTS_TOPICS_OVERRIDE` -> a string to denote the specific topics/collections to be exported from HBase in to the generated snapshots. Can be either "ALL" for the full default topic list, a comma separated list of full Kafka topic names representing the desired collections (i.e. `db.core.aaa,db.agentCore.bbbb`) or if not passed in it defaults to the job name.
* `SNAPSHOT_TYPE` -> either `full` or `incremental` to denote which type of snapshots to create - there are specific jobs for each scenario per environment so it is recommended not to edit this.
* `GENERATE_SNAPSHOTS_START_TIME_OVERRIDE` -> if snapshot type passed in as "incremental" this can be used to provide the start time cut off for records to include in the incremental snapshot - must be a valid date in the format `%Y-%m-%dT%H:%M:%S.%f` and will default to midnight yesterday if not passed in.
* `GENERATE_SNAPSHOTS_END_TIME_OVERRIDE` -> if snapshot type passed in as "incremental" this can be used to provide the end time cut off for records to include in the incremental snapshot - must be a valid date in the format `%Y-%m-%dT%H:%M:%S.%f` and will default to midnight today if not passed in.
* `GENERATE_SNAPSHOTS_TRIGGER_SNAPSHOT_SENDER_OVERRIDE` -> if passed in as `true` then this will cause the generated snapshots to *also be sent down to Crown by Snapshot Sender* - default is `false`
* `GENERATE_SNAPSHOTS_REPROCESS_FILES_OVERRIDE` -> this flag sets whether when Snapshot Sender sends a file, it will error if it already exists. There are specific jobs to set this so should not be changed on standard ones.
* `GENERATE_SNAPSHOTS_CORRELATION_ID_OVERRIDE` -> override the correlation id which is useful for re-running new nightly generate and send topics
* `GENERATE_SNAPSHOTS_EXPORT_DATE_OVERRIDE` -> Used to specify the location for the snapshots so if re-sending a day that is not today then set this to the relevant day in the format `YYYY-MM-DD`
* `GENERATE_SNAPSHOTS_TRIGGER_ADG_OVERRIDE` -> True to trigger ADG after HTME has finished - default is `false`
* `GENERATE_SNAPSHOTS_CLEAR_S3_SNAPSHOTS` -> True to delete any existing snapshots for the given export date before HTME runs (default is `false`)
* `GENERATE_SNAPSHOTS_CLEAR_S3_MANIFESTS` -> True to delete any existing manifests for the given export date before HTME runs (default is `false`)

### Pipeline: send-snapshots

This is used to start the snapshot sending to Crown process within the desired environment - it only kicks it off and does not monitor it. The files for this pipeline are in the ci/generate-snapshots folder in this repo. To update this pipeline in CI, you can run the following make command:

* `make update-send-snapshots-pipeline`

You can also pause or unpause the pipeline:

* `make pause-send-snapshots-pipeline`
* `make unpause-send-snapshots-pipeline`

#### Overrides

The following overrides can be passed through as config params from the environment jobs to the send snapshots task in the pipelines:

* `SEND_SNAPSHOTS_DATE_OVERRIDE` -> a string for sending snapshots from a specific date folder in S3, must be in the format "YYYY-MM-DD" and will default to today's date if not overridden.
* `SEND_SNAPSHOTS_TOPICS_OVERRIDE` -> a string to denote the specific topics/collections to be sent to Crown. Can be either "ALL" for the full default topic list, a comma separated list of full Kafka topic names representing the desired collections (i.e. `db.core.aaa,db.agentCore.bbbb`) or if not passed in it defaults to the job name.
* `SEND_SNAPSHOTS_REPROCESS_FILES_OVERRIDE` -> this flag sets whether when Snapshot Sender sends a file, it will error if it already exists. There are specific jobs to set this so should not be changed on standard ones.
* `SNAPSHOT_SENDER_SCALE_UP_OVERRIDE` -> if the amount of snappy instances needs to be fixed can use this to scale to a specific number, else will be the snappy asg max number
* `SEND_SNAPSHOTS_CORRELATION_ID_OVERRIDE` -> use this to override the correlation id that is used for this run against the given topics (will overwrite existing dynamo db statuses for the topics you pass in, so use only when necessary to fix a prod run)

### Pipeline: hbase-data-ingestion

This is used to start the data ingestion process from the relevant snapshot folders to HBase within the desired environment. The files for this pipeline are in the ci/hbase-data-ingestion folder in this repo. To update this pipeline in CI, you can run the following make command:

* `make update-hbase-data-ingestion-pipeline`

You can also pause or unpause the pipeline:

* `make pause-hbase-data-ingestion-pipeline`
* `make unpause-hbase-data-ingestion-pipeline`

#### Job groups

This pipeline has the following job groups:

* `historic-data-import` -> this runs the HDI component (https://github.com/dwp/uc-historic-data-importer) to import historic data in to HBase via the HBase API
* `corporate-data-load` -> this runs the CDL component (https://github.com/dwp/corporate-data-loader) to load corporate streamed data in to HBase via the HBase bulk loading technique
* `historic-data-load` -> this runs the HDI component (https://github.com/dwp/historic-data-loader) to import historic data in to HBase via the HBase bulk loading technique

#### Overrides

The following overrides can be passed through as config params from the environment jobs to the `historic-data-import` tasks in the pipelines:

* `HISTORIC_IMPORTER_USE_ONE_MESSAGE_PER_PATH` -> a string of "true" will ensure that the prefixes passed from terraform will be split in to one message per comma delimited part of the string when sent to SQS and HDI uses one message per run, else one single message is sent to SQS with the comma delimited fill string in and HDI uses all the paths on one single run.
* `HISTORIC_DATA_INGESTION_SKIP_EARLIER_THAN_OVERRIDE` -> if passed in, records with a timestamp earlier than this are skipped in the historic import - format of date time must be `yyyy-MM-dd'T'HH:mm:ss.SSS` with an optional literal `Z` at the end.
* `HISTORIC_DATA_INGESTION_SKIP_LATER_THAN_OVERRIDE` -> if passed in, records with a timestamp later than this are skipped in the historic import - format of date time must be `yyyy-MM-dd'T'HH:mm:ss.SSS` with an optional literal `Z` at the end.
* `HISTORIC_DATA_INGESTION_SKIP_EXISTING_RECORDS_OVERRIDE` -> if passed in as "true", records are checked for being in HBase first and only "put" if they do not exist.

The following overrides can be passed through as config params from the environment jobs to the `corporate-data-load` or `historic-data-load` tasks in the pipelines:

* `DATA_LOAD_TOPICS` -> must be a comma delimited list of the topics to load or can be `ALL` to use the default list - will default to `ALL`.
* `DATA_LOAD_METADATA_STORE_TABLE` -> either `ucfs`, `equalities` or audit to represent the metadata store table to write to (for CDL only, this also decides the s3 base path as well as the s3 file pattern to use - HDL only ever has one) - will default to `ucfs`.
* `DATA_LOAD_S3_SUFFIX` -> if passed in, will add a suffix to the base S3 path that is used to store the historic or corporate storage and can be used to filter to files from a specific date (for corporate data) or database (for historic data) - will default to no suffix. If multiple suffixes required, pass in a comma delimited list, each one will be added to the base S3 path in turn and a comma delimited list of these full prefixes passed to HDL/CDL.

The following overrides can be passed through as config params from the environment jobs to the `historic-data-load` tasks only in the pipeline:

* `HISTORIC_DATA_INGESTION_SKIP_EARLIER_THAN_OVERRIDE` -> if passed in, records with a timestamp earlier than this are skipped in the historic data load - format of date time must be `yyyy-MM-dd'T'HH:mm:ss.SSS` with an optional literal `Z` at the end.
* `HISTORIC_DATA_INGESTION_SKIP_LATER_THAN_OVERRIDE` -> if passed in, records with a timestamp later than this are skipped in the historic data load - format of date time must be `yyyy-MM-dd'T'HH:mm:ss.SSS` with an optional literal `Z` at the end.

The following overrides can be passed through as config params from the environment jobs to the `corporate-data-load` tasks only in the pipeline:

* `CORPORATE_DATA_INGESTION_SKIP_EARLIER_THAN_OVERRIDE` -> if passed in, the data load is run from the files from this day (inclusive) onwards (if not passed in runs on the entire dataset) - format of date must be `yyyy-MM-dd`.
* `CORPORATE_DATA_INGESTION_SKIP_LATER_THAN_OVERRIDE` -> if CORPORATE_DATA_INGESTION_SKIP_EARLIER_THAN_OVERRIDE is passed in, then this must be too and it must be a date later than that one or the same as - this signifies the last day (inclusive) of date to load (if it is the same as CORPORATE_DATA_INGESTION_SKIP_EARLIER_THAN_OVERRIDE then only one day is processed) - format of date must be `yyyy-MM-dd`.
* `CORPORATE_DATA_INGESTION_PREFIX_PER_EXECUTION_OVERRIDE` -> if passed in as `true` then for every prefix that will be loaded, a new execution of the data load will occur. If not then all the prefixes will be sent to one execution of the jar at the same time (this is the default).

### Pipeline: ami-cleanup

A utility to clean up old AMIs. The files for this pipeline are in the ci/ami-cleanup folder in this repo. To update this pipeline in CI, you can run the following make command:

* `make update-ami-cleanup-pipeline`

You can also pause or unpause the pipeline:

* `make pause-ami-cleanup-pipeline`
* `make unpause-ami-cleanup-pipeline`

### Pipeline: terraform-taint

A utility to taint Terraform resources. Considering the danger the jobs are disabled in the code by commenting out the `taint` command. The `state show` command that precedes it allows you to test the resource address.

To use:
1. Add the Terraform repo that contains TF resource to be tainted as a Concourse resource in `ci/terraform-taint/resources-terraform-taint`.
1. Modify the job for the given environment, TF repo and TF resource(s):
    1. In the appropriate file under `ci/terraform-taint/jobs`,
    1. modify resource reference in `get` step;
    1. modify `input_mapping` to match the resource reference above;
    1. modify `TF_WORKSPACE` value;
    1. put a space-separated list of TF resource addresses into `RESOURCE_ADDRESS_LIST` variable.
1. Aviator and run, verify that `state show` output lists the expected resources.
1. Uncomment the line with `taint` command.
1. Aviator and run.
1. When done, reset to HEAD of master branch and aviator in so that `taint` command is commented out in Concourse.

### Pipelines ending `*-emr-admin`

Administrative jobs for the data products have been collated into the utility team to permit the removal of aviator privileges. These can be used to stop and start specified EMR clusters.

You can update one of these pipeline using this:

* `make update-<PIPELINE-NAME>-emr-admin-pipeline`

You can also pause or unpause the pipeline:

* `make pause-<PIPELINE-NAME>-emr-admin-pipeline`
* `make unpause-<PIPELINE-NAME>-emr-admin-pipeline`

To use:
1. Follow steps 1 to 3 in the `Installing as a concourse pipeline` section above
1. Add the required variables to your local file as per defined in the jobs `.yml` files
1. Aviator your changes using `make update-<PIPELINE-NAME>-emr-admin-pipeline`
1. Browse to the concourse UI for your pipeline and run the job for the environment of your choice
