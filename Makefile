env := .venv

run:
	@clear;./$(env)/bin/python start.py

clean:
	@rm -rf dist build *.egg-info **/__pycache__/

$(env):
	python -m venv $@

install: $(env)
	@./$(env)/bin/pip install -e .

