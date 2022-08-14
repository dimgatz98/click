# API client

Install dependencies:
``` bash
# Change your working directory in the current directory and execute the following commands:
$ python -m venv ./venv
$ pip install -r requirements.txt
```

If the virtual environment is created correctly as shown above then you will be able to run the api client as shown below:
``` bash
$ ./apiclient --help
```
else you will either have to modify the shebang [here](https://github.com/dimgatz98/click/blob/master/api_client/apiclient) or use the python3 keyword (e.g. "python3 apiclient --help").
