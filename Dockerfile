# Airflow Docker Container
FROM apache/airflow
WORKDIR /
COPY /requirements.txt .

USER root

RUN sudo apt-get update && apt-get install -y curl && apt-get clean
RUN pip3 install -r requirements.txt
RUN pip3 install apache-airflow --upgrade
