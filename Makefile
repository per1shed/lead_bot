dev:
	watchfiles --filter python --ignore-path .venv,__pycache__ "python main.py"
prod:
	python main.py