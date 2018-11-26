FROM python:3.7-alpine3.7

ARG https_proxy_url

ENV HTTP_PROXY "$https_proxy_url"
ENV HTTPS_PROXY "$https_proxy_url"

ENV WORKING_DIRECTORY /opt/stix
RUN mkdir -p $WORKING_DIRECTORY
WORKDIR $WORKING_DIRECTORY

COPY . $WORKING_DIRECTORY

RUN pip3 install flask --default-timeout=100
RUN pip3 install stix2-validator --default-timeout=100
RUN pip3 install stix-pattern-translator --default-timeout=100
RUN pip3 install gunicorn --default-timeout=100
RUN pip3 install pytest --default-timeout=100
# Start Application
EXPOSE 5000

CMD ["gunicorn", "--config", "$WORKING_DIRECTORY/gunicorn_config.py", "app:app"]
