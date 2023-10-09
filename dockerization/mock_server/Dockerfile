FROM python:3.11

WORKDIR /app

COPY ./mock_server/requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./mock_server /app

COPY ./dockerization/prestart.sh /prestart.sh
RUN chmod +x /prestart.sh

CMD ["/prestart.sh"]

COPY ./dockerization/mock_server/start.sh /start.sh
RUN chmod +x /prestart.sh

EXPOSE 8001

ENTRYPOINT ["/start.sh"]

