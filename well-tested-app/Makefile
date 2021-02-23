.DEFAULT_TARGET: setup

venv:
	python3 -m venv venv
	./venv/bin/python3 -m pip install --upgrade pip

reports:
	mkdir -p reports

.PHONY: setup
setup: venv
	./venv/bin/pip3 install -r requirements.txt

.PHONY: clean
clean:
	rm -rf venv h2o_wave.state .apps .pytest_cache reports
	find ./ -name '__pycache__' -exec rm -rf "{}" \;

.PHONY: setup-dev
setup-dev: venv setup
	./venv/bin/pip3 install -r requirements-dev.txt
	./venv/bin/playwright install

.PHONY: run
run:
	./venv/bin/wave run --no-reload tested_app.app

.PHONY: run-dev
run-dev:
	./venv/bin/wave run tested_app.app

.PHONY:
deploy:
	h2o bundle deploy

.PHONY: lint
lint:
	@./venv/bin/flake8

.PHONY: format
format:
	./venv/bin/isort .
	./venv/bin/black --exclude venv .

.PHONY: test
test:
	PYTHONPATH=. ./venv/bin/pytest -s --full-trace tests/unit_tests/

.PHONY: test-ci
test-ci: reports
	PYTHONPATH=. \
	./venv/bin/pytest \
		--junitxml=./reports/junit.xml \
		tests/unit_tests/

.PHONY: test-e2e
test-e2e:
	DEBUG=pw:api \
	PYTHONPATH=. \
	./venv/bin/pytest \
		-s \
		--headful \
		tests/e2e_tests/
