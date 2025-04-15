# Airflow Docker Container
FROM apache/airflow
WORKDIR /
COPY /requirements.txt .
USER root

RUN sudo apt-get update && apt-get install -y curl && apt-get clean
RUN pip3 install -r requirements.txt
RUN pip3 install apache-airflow --upgrade

EXPOSE 8501
CMD ["streamlit", "run", "streamlit/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
