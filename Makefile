GIT_DESCR = $(shell git describe --always) 
# build output folder
OUTPUTFOLDER = dist
# docker image
DOCKER_IMAGE_APP = welance/anna-ai
DOCKER_IMAGE_TRAINING = welance/anna-ai-training
DOCKER_TAG = $(shell git describe --always)

.PHONY: list
list:
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$' | xargs


local-setup:
	@echo installing virtualenv and related resources
	./setup.sh
	@done

local-run:
	@echo installing virtualenv and related resources
	./run.sh
	@done


docker-build-app:
	@echo build image
	docker build -t $(DOCKER_IMAGE_APP):$(DOCKER_TAG) -f ./build/docker/app/Dockerfile .
	docker tag $(DOCKER_IMAGE_APP):$(DOCKER_TAG) $(DOCKER_IMAGE_APP):latest
	@echo done

docker-push-app: 
	@echo push image
	docker tag $(DOCKER_IMAGE_APP):$(DOCKER_TAG) $(DOCKER_IMAGE_APP):latest
	docker push $(DOCKER_IMAGE_APP)
	@echo done

docker-run-app: 
	@docker run -p 5000:5000 $(DOCKER_IMAGE_APP) 

docker-build-training:
	@echo build image
	docker build -t $(DOCKER_IMAGE_TRAINING):$(DOCKER_TAG) -f ./build/docker/training/Dockerfile .
	docker tag $(DOCKER_IMAGE_TRAINING):$(DOCKER_TAG) $(DOCKER_IMAGE_TRAINING):latest
	@echo done

docker-push-training: 
	@echo push image
	docker tag $(DOCKER_IMAGE_TRAINING):$(DOCKER_TAG) $(DOCKER_IMAGE_TRAINING):latest
	docker push $(DOCKER_IMAGE_TRAINING)
	@echo done
