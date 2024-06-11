env := .venv
deps := requirements.txt

run:
	@clear;./$(env)/bin/python start.py

build:
	@./$(env)/bin/pip install build;./$(env)/bin/python -m build

clean:
	@rm -rf dist build *.egg-info **/__pycache__/

stable: clean build
	git push;git checkout releases;git merge main;git push;twine upload dist/*;git checkout main;

$(env): $(deps)
	python -m venv $@

install: $(env)
	@./$(env)/bin/pip install -r $(deps)

