all: ## Build wheel
	zip -r \
        --exclude=".git/*" \
        --exclude="/venv/*" \
        --exclude="*.csv" \
        --exclude="*__pycache__/*" \
        $(shell basename $$PWD).qz .

setup: ## Create venv and install dependencies on it
	python3 -m venv venv
	./venv/bin/pip install -U pip
	./venv/bin/pip install wheel
	./venv/bin/pip install -r requirements.txt

install: ## Install dependencies on active python environment
	pip install -r requirements.txt

clean: ## Clean
	rm -rf dist venv *.whl *.qz

help: ## List all make tasks
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
