FROM python:3.10.13

RUN pip3 install prometheus_client uvicorn fastapi requests supervisor

RUN mkdir /etc/supervisord.d && \
    mkdir /usr/local/opensearch-prometheus-exporter && \
    mkdir /var/log/supervisor && \
    mkdir /var/run/supervisor

ADD main.py /usr/local/opensearch-prometheus-exporter
ADD build/supervisord.conf /etc/supervisord.conf
ADD build/supervisord.d/*.ini /etc/supervisord.d

CMD ["supervisord","-n","-c /etc/supervisord.conf"]