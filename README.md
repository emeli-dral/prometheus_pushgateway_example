﻿# prometheus_pushgateway_example

This example shows how to get Grafana dashboards for data monitoring using Prometheus Gateway and Evidently Metrics. 

<img width="1389" alt="Screenshot 2023-02-13 at 16 54 15" src="https://user-images.githubusercontent.com/22995068/219074659-3570eb65-80d0-47c1-b39d-73040ea28200.png">

## Prerequisites
You need following tools installed:
- [docker](https://docs.docker.com/get-docker) 
- docker-compose (included to Docker Desktop for Mac and Docker Desktop for Windows )

## Preparation
Note: all actions expected to be executed in repo folder.

Create virtual environment and activate it (eg. python -m venv venv && ./venv/bin/activate)

Install required packages pip install -r requirements.txt

## Starting services
Go to the project directory and run the following command from the terminal: ```docker-compose up --build``` 
Note:
- to stop the docker later, run: docker-compose down;
- to rebuild docker image (for example, to get the latest version of the libraries) run: docker compose build --no-cache

## Sending Data
To start sending data to service, execute:
```python data_loader.py```

This script will expose a single batch of calculated metrics through prometheus pushgateway every 10 seconds

## Setting up Dashboards
- Run the example using the above instructions
- Open the Grafana web interface (localhost:3000)
- Customize the visuals in the Grafana interface.
- Apply your changes to the Dashboard and check that you like what you see :)
- Click the button "save" from the Grafana Top Menu. This will open a dialog window. Select the option "Download JSON" to save the configurations in the JSON file if like to reuse it later.
