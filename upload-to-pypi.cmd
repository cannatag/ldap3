CALL venv\Scripts\activate.bat
REM API token for upload to PyPi must be in $HOME/.pypirc
twine upload --skip-existing dist/*
