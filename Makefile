run:
	@clear;./venv/bin/python3 start.py

build:
	@./venv/bin/pip install build;./venv/bin/python3 -m build

clean:
	@rm -rf dist build *.egg-info **/__pycache__/

stable: clean build
	git push;git checkout releases;git merge main;git push;twine upload dist/*;git checkout main;
