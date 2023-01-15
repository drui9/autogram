run:
	@./venv/bin/python3 launch.py

build:
	@./venv/bin/python3 -m build

clean:
	@rm -rf dist build *.egg-info __pycache__/
