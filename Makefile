.PHONY: up down ps exec pip run run-migrator test publish publish-pypi publish-docker publish-nv-teams-pypi add-env-var

up:
	docker-compose up -d --build

down:
	docker-compose down

ps:
	docker-compose ps -a

exec:
	docker exec -it app bash

pip:
	pip install -r requirements.txt

run:
	python main.py

test:
	pytest tests

publish-pypi:
	./.scripts/publish_github_migrator_pypi_package.sh

publish-docker:
	./.scripts/publish_github_migrator_docker_image.sh

publish-nv-teams-pypi:
	./.scripts/publish_nv_teams_pypi_package.sh

add-env-var:
	./.scripts/add_new_environment_variable.sh $(word 2,$(MAKECMDGOALS))
