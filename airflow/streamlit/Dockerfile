FROM python:3.9-slim

USER root

WORKDIR /streamlit

COPY requirements.txt .
RUN apt-get update && apt-get install -y curl && apt-get clean

RUN pip install --upgrade pip &&\
pip install -r requirements.txt &&\
pip install apache-airflow streamlit

COPY main.py .
COPY .env .


EXPOSE 8501

CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]