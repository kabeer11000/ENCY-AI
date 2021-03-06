FROM python:3.7

RUN pip install pipenv

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./src/ .

COPY ./scripts/install_models.py .
RUN pwd && python install_models.py

ENV FLASK_APP main.py



