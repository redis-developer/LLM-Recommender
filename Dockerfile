FROM python:3.8-slim

RUN apt-get update && apt-get install python3 curl python3-pip -y

COPY ./requirements.txt .
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

WORKDIR /hotel
COPY . /hotel

ENTRYPOINT [ "streamlit", "run" ]
CMD [ "run.py", "--server.fileWatcherType", "none", "--browser.gatherUsageStats", "false", "--server.address", "0.0.0.0"]
