all: ## Build wheel
	zip -r \
        --exclude=".git/*" \
        --exclude="/venv/*" \
        --exclude="*.csv" \
        --exclude="*__pycache__/*" \
        $(shell basename $$PWD).qz .

setup:
	python3 -m venv venv
	. ./venv/bin/activate
	pip install -U pip
	pip install wheel
	$(MAKE) install

install: ## Install dependencies
	pip install http://h2o-release.s3.amazonaws.com/h2o/rel-zermelo/1/Python/h2o-3.32.0.1-py2.py3-none-any.whl
	pip install -r requirements.txt

clean: ## Clean
	rm -rf dist venv *.whl *.qz

help: ## List all make tasks
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
