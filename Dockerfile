FROM python:3.7-alpine3.7

ARG https_proxy_url

ENV HTTP_PROXY "$https_proxy_url"
ENV HTTPS_PROXY "$https_proxy_url"

ENV WORKING_DIRECTORY /opt/stix
RUN mkdir -p $WORKING_DIRECTORY
WORKDIR $WORKING_DIRECTORY

COPY . $WORKING_DIRECTORY

RUN pip3 install pipenv --default-timeout=100
RUN pipenv install --system

EXPOSE 5000
