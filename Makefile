SHELL:=bash

aws_account=NOT_SET
aws_role=NOT_SET
max_age=12
tag_name_to_ignore=long_lived_vm
tag_value_to_ignore=True

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
concourse-login: ## Login to concourse using Fly
	fly -t concourse login -c https://concourse.service.dw/ -k -n dataworks

.PHONY: update-lambda-cleanup-pipeline
update-lambda-cleanup-pipeline: ## Update the lambda-cleanup pipeline
	aviator -f aviator-lambda-cleanup.yml

.PHONY: pause-lambda-cleanup-pipeline
pause-lambda-cleanup-pipeline: ## Pause the lambda-cleanup pipeline
	fly --target concourse pause-pipeline --pipeline lambda-cleanup

.PHONY: unpause-lambda-cleanup-pipeline
unpause-lambda-cleanups-pipeline: ## Unpause the lambda-cleanup pipeline
	fly --target concourse unpause-pipeline --pipeline lambda-cleanup

detect-old-instances-local:
	@{ \
		pushd ./utils; \
		python3 ./detect-old-instances/detect_old_instances.py account=$(aws_account) role=$(aws_role) max_age=$(max_age) tag_name_to_ignore=$(tag_name_to_ignore) tag_value_to_ignore=$(tag_value_to_ignore); \
		popd; \
	}

.PHONY: update-detect-old-instances-pipeline
update-detect-old-instances-pipeline: ## Update the detect-old-instances pipeline
	aviator -f aviator-detect-old-instances.yml

.PHONY: pause-detect-old-instances-pipeline
pause-detect-old-instances-pipeline: ## Pause the detect-old-instances pipeline
	fly --target concourse pause-pipeline --pipeline detect-old-instances

.PHONY: unpause-detect-old-instances-pipeline
unpause-detect-old-instances-pipeline: ## Unpause the detect-old-instances pipeline
	fly --target concourse unpause-pipeline --pipeline detect-old-instances
