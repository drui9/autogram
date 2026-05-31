src := main.py
env := .venv

start:
	$(env)/bin/python $(src)

clean:
	rm -rf **/__pycache__

