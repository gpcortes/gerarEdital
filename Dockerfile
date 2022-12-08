FROM python:3.7-slim

# Setup env
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1

RUN useradd -ms /bin/bash python

RUN apt update && apt install git -y

RUN pip install pipenv

USER python

WORKDIR /home/python

ENV PIPENV_VENV_IN_PROJECT=True
ENV PIPENV_SITE_PACKAGES=True
ENV PATH="~/.venv/bin:$PATH"

ADD Pipfile.lock ./
ADD Pipfile ./

# RUN pipenv sync
RUN pipenv install --system

COPY src/. /home/python/app

WORKDIR /home/python/app

CMD [ "python", "main.py" ]
