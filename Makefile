SHELL:=bash

default: help

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: bootstrap
bootstrap: ## Bootstrap local environment for first use
	make git-hooks

.PHONY: git-hooks
git-hooks: ## Set up hooks in .git/hooks
	@{ \
		HOOK_DIR=.git/hooks; \
		for hook in $(shell ls .githooks); do \
			if [ ! -h $${HOOK_DIR}/$${hook} -a -x $${HOOK_DIR}/$${hook} ]; then \
				mv $${HOOK_DIR}/$${hook} $${HOOK_DIR}/$${hook}.local; \
				echo "moved existing $${hook} to $${hook}.local"; \
			fi; \
			ln -s -f ../../.githooks/$${hook} $${HOOK_DIR}/$${hook}; \
		done \
	}

.PHONY: concourse-login
concourse-login: ## Login to dataworks team using Fly
	fly -t aws-concourse login -c https://ci.dataworks.dwp.gov.uk/ -n dataworks

.PHONY: utility-login
utility-login: ## Login to utility team using Fly
	fly -t utility login -c https://ci.dataworks.dwp.gov.uk/ -n utility

.PHONY: update-all-pipelines
update-all-pipelines: ## Update all the pipelines
	aviator -f aviator-lambda-cleanup.yml
	aviator -f aviator-scale-down-services.yml
	aviator -f aviator-scale-up-services.yml
	aviator -f aviator-manage-ecs-services.yml
	aviator -f aviator-manage-environments.yml
	aviator -f aviator-generate-snapshots.yml
	aviator -f aviator-send-snapshots.yml
	aviator -f aviator-ami-cleanup.yml
	aviator -f aviator-hbase-data-ingestion.yml
	aviator -f aviator-terraform-taint.yml
	aviator -f aviator-mongo-latest-emr-services.yml
	aviator -f aviator-adg-emr-services.yml
	aviator -f aviator-clive-emr-services.yml
	aviator -f aviator-pdm-emr-services.yml
	aviator -f aviator-kickstart-adg-emr-services.yml

.PHONY: update-kickstart-adg-emr-services-pipeline
update-kickstart-adg-emr-services-pipeline: ## Update the kickstart-adg-emr-services pipeline
	aviator -f aviator-kickstart-adg-emr-services.yml

.PHONY: update-mongo-latest-emr-services-pipeline
update-mongo-latest-emr-services-pipeline: ## Update the mongo-latest-emr-services pipeline
	aviator -f aviator-mongo-latest-emr-services.yml

.PHONY: update-adg-emr-services-pipeline
update-adg-emr-services-pipeline: ## Update the adg-emr-services pipeline
	aviator -f aviator-adg-emr-services.yml

.PHONY: update-clive-emr-services-pipeline
update-clive-emr-services-pipeline: ## Update the clive-emr-services pipeline
	aviator -f aviator-clive-emr-services.yml

.PHONY: update-pdm-emr-services-pipeline
update-pdm-emr-services-pipeline: ## Update the pdm-emr-services pipeline
	aviator -f aviator-pdm-emr-services.yml

.PHONY: update-lambda-cleanup-pipeline
update-lambda-cleanup-pipeline: ## Update the lambda-cleanup pipeline
	aviator -f aviator-lambda-cleanup.yml

.PHONY: update-scale-down-services-pipeline
update-scale-down-services-pipeline: ## Update the scale-down-services pipeline
	aviator -f aviator-scale-down-services.yml

.PHONY: update-scale-up-services-pipeline
update-scale-up-services-pipeline: ## Update the scale-up-services pipeline
	aviator -f aviator-scale-up-services.yml

.PHONY: update-manage-ecs-services-pipeline
update-manage-ecs-services-pipeline: ## Update the manage-ecs-services pipeline
	aviator -f aviator-manage-ecs-services.yml

.PHONY: update-manage-environments-pipeline
update-manage-environments-pipeline: ## Update the manage-environments pipeline
	aviator -f aviator-manage-environments.yml

.PHONY: update-generate-snapshots-pipeline
update-generate-snapshots-pipeline: ## Update the generate snapshots pipeline
	aviator -f aviator-generate-snapshots.yml

.PHONY: update-send-snapshots-pipeline
update-send-snapshots-pipeline: ## Update the send snapshots pipeline
	aviator -f aviator-send-snapshots.yml

.PHONY: update-ami-cleanup-pipeline
update-ami-cleanup-pipeline: ## Update the ami-cleanup pipeline
	aviator -f aviator-ami-cleanup.yml

.PHONY: update-hbase-data-ingestion-pipeline
update-hbase-data-ingestion-pipeline: ## Update the hbase-data-ingestion pipeline
	aviator -f aviator-hbase-data-ingestion.yml

.PHONY: update-terraform-taint-pipeline
update-terraform-taint-pipeline: ## Update the terraform-taint pipeline
	aviator -f aviator-terraform-taint.yml

.PHONY: pause-kickstart-adg-emr-services-pipeline
pause-kickstart-adg-emr-services-pipeline: ## pause the kickstart-adg-emr-services pipeline
	fly --target utility pause-pipeline --pipeline kickstart-adg-emr-services

.PHONY: pause-mongo-latest-emr-services-pipeline
pause-mongo-latest-emr-services-pipeline: ## pause the mongo-latest-emr-services pipeline
	fly --target utility pause-pipeline --pipeline mongo-latest-emr-services

.PHONY: pause-adg-emr-services-pipeline
pause-adg-emr-services-pipeline: ## pause the adg-emr-services pipeline
	fly --target utility pause-pipeline --pipeline adg-emr-services

.PHONY: pause-clive-emr-services-pipeline
pause-clive-emr-services-pipeline: ## pause the clive-emr-services pipeline
	fly --target utility pause-pipeline --pipeline clive-emr-services

.PHONY: pause-pdm-emr-services-pipeline
pause-pdm-emr-services-pipeline: ## pause the pdm-emr-services pipeline
	fly --target utility pause-pipeline --pipeline pdm-emr-services

.PHONY: pause-lambda-cleanup-pipeline
pause-lambda-cleanup-pipeline: ## Pause the lambda-cleanup pipeline
	fly --target utility pause-pipeline --pipeline lambda-cleanup

.PHONY: pause-scale-down-services-pipeline
pause-scale-down-services-pipeline: ## Pause the scale down services pipeline
	fly --target utility pause-pipeline --pipeline scale-down-services

.PHONY: pause-scale-up-services-pipeline
pause-scale-up-services-pipeline: ## Pause the scale up services pipeline
	fly --target utility pause-pipeline --pipeline scale-up-services

.PHONY: pause-manage-ecs-services-pipeline
pause-manage-ecs-services-pipeline: ## Pause the manage-ecs-services pipeline
	fly --target utility pause-pipeline --pipeline manage-ecs-services

.PHONY: pause-manage-environments-pipeline
pause-manage-environments-pipeline: ## Pause the manage-environmentss pipeline
	fly --target utility pause-pipeline --pipeline manage-environments

.PHONY: pause-generate-snapshots-pipeline
pause-generate-snapshots-pipeline: ## Pause the generate snapshots pipeline
	fly --target utility pause-pipeline --pipeline generate-snapshots

.PHONY: pause-send-snapshots-pipeline
pause-send-snapshots-pipeline: ## Pause the send snapshots pipeline
	fly --target utility pause-pipeline --pipeline send-snapshots

.PHONY: pause-hbase-data-ingestion-pipeline
pause-hbase-data-ingestion-pipeline: ## Pause the hbase-data-ingestion pipeline
	fly --target utility pause-pipeline --pipeline hbase-data-ingestion

.PHONY: pause-ami-cleanup-pipeline
pause-ami-cleanup-pipeline: ## Pause the ami-cleanup pipeline
	fly --target utility pause-pipeline --pipeline ami-cleanup

.PHONY: pause-terraform-taint-pipeline
pause-terraform-taint-pipeline: ## Pause the terraform-taint pipeline
	fly --target utility pause-pipeline --pipeline terraform-taint
	
.PHONY: unpause-kickstart-adg-emr-services-pipeline
unpause-kickstart-adg-emr-services-pipeline: ## unpause the kickstart-adg-emr-services pipeline
	fly --target utility unpause-pipeline --pipeline kickstart-adg-emr-services

.PHONY: unpause-mongo-latest-emr-services-pipeline
unpause-mongo-latest-emr-services-pipeline: ## unpause the mongo-latest-emr-services pipeline
	fly --target utility unpause-pipeline --pipeline mongo-latest-emr-services

.PHONY: unpause-adg-emr-services-pipeline
unpause-adg-emr-services-pipeline: ## unpause the adg-emr-services pipeline
	fly --target utility unpause-pipeline --pipeline adg-emr-services

.PHONY: unpause-clive-emr-services-pipeline
unpause-clive-emr-services-pipeline: ## unpause the clive-emr-services pipeline
	fly --target utility unpause-pipeline --pipeline clive-emr-services

.PHONY: unpause-pdm-emr-services-pipeline
unpause-pdm-emr-services-pipeline: ## unpause the pdm-emr-services pipeline
	fly --target utility unpause-pipeline --pipeline pdm-emr-services

.PHONY: unpause-lambda-cleanup-pipeline
unpause-lambda-cleanup-pipeline: ## Unpause the lambda-cleanup pipeline
	fly --target utility unpause-pipeline --pipeline lambda-cleanup

.PHONY: unpause-scale-down-services-pipeline
unpause-scale-down-services-pipeline: ## Unpause the scale down services pipeline
	fly --target utility unpause-pipeline --pipeline scale-down-services

.PHONY: unpause-scale-up-services-pipeline
unpause-scale-up-services-pipeline: ## Unpause the scale up services pipeline
	fly --target utility unpause-pipeline --pipeline scale-up-services

.PHONY: unpause-manage-ecs-services-pipeline
unpause-manage-ecs-services-pipeline: ## Unpause the manage-ecs-services pipeline
	fly --target utility unpause-pipeline --pipeline manage-ecs-services

.PHONY: unpause-manage-environments-pipeline
unpause-manage-environments-pipeline: ## Unpause the manage-environments pipeline
	fly --target utility unpause-pipeline --pipeline manage-environments

.PHONY: unpause-generate-snapshots-pipeline
unpause-generate-snapshots-pipeline: ## Unpause the generate snapshots pipeline
	fly --target utility unpause-pipeline --pipeline generate-snapshots

.PHONY: unpause-send-snapshots-pipeline
unpause-send-snapshots-pipeline: ## Unpause the send snapshots pipeline
	fly --target utility unpause-pipeline --pipeline send-snapshots

.PHONY: unpause-hbase-data-ingestion-pipeline
unpause-hbase-data-ingestion-pipeline: ## Unpause the hbase-data-ingestion pipeline
	fly --target utility unpause-pipeline --pipeline hbase-data-ingestion

.PHONY: unpause-ami-cleanup-pipeline
unpause-ami-cleanup-pipeline: ## Unpause the ami-cleanup pipeline
	fly --target utility unpause-pipeline --pipeline ami-cleanup

.PHONY: unpause-terraform-taint-pipeline
unpause-terraform-taint-pipeline: ## Unpause the terraform-taint pipeline
	fly --target utility unpause-pipeline --pipeline terraform-taint
