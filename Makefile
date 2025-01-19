env := .venv

run: $(env)
	@clear;$(env)/Scripts/python start.py

clean:
	@rm -rf dist build *.egg-info **/__pycache__/

$(env):
	python -m venv $@

install: $(env)
	@$(env)\Scripts\pip install -e .

