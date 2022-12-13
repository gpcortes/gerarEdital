FROM mcr.microsoft.com/vscode/devcontainers/python:3.8-buster

# Setup env
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1

RUN useradd -ms /bin/bash python

RUN apt update && apt install git -y
RUN apt-get install -y libreoffice

RUN pip install pipenv

USER python

WORKDIR /home/python/app

ENV PIPENV_VENV_IN_PROJECT=True
ENV PIPENV_SITE_PACKAGES=True
ENV PATH="~/.venv/bin:$PATH"

ADD Pipfile.lock ./
ADD Pipfile ./

RUN pipenv install

CMD [ "tail", "-f", "/dev/null" ]