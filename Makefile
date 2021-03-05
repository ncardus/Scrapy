init:
	pre-commit install

env: init
	python3 -m venv .venv
	source .venv/bin/activate; \
	pip install -r requirements.txt ;\
	ipython kernel install --user --name=scrapySel

