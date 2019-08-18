FROM python:2.7-alpine

#RUN adduser -D telegrambot

WORKDIR /home/sender

COPY requirements.txt requirements.txt
#COPY wialon_parser.py wialon_parser.py
#COPY server.py server.py
#ENV TZ=Europe/Saratov
#RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
#RUN python -m venv venv
#RUN pip install virtualenv
#RUN virtualenv -p venv venv
RUN apk --update add python py-pip openssl ca-certificates py-openssl wget
RUN apk --update add --virtual build-dependencies g++ gcc libxslt-dev libffi-dev openssl-dev python-dev py-pip build-base \
  && pip install --upgrade pip \
  && pip install -r requirements.txt \
  && pip install gunicorn pymysql
#  && apk del build-dependencies
#RUN apk add --update py-pip gcc python3 python-dev python3-dev g++ make
#RUN venv/bin/pip install -r requirements.txt
#RUN venv/bin/pip install gunicorn

#COPY app app
#COPY migrations migrations
#COPY oriportal.py config.py boot.sh ./
#COPY boot.sh ./
#RUN flask translate init
#RUN flask translate update
#RUN chmod +x boot.sh

#ENV FLASK_APP oriportal.py

#RUN chown -R telegrambot:telegrambot ./
#USER telegrambot

CMD [ "python", "./server.py" ]
#EXPOSE 5000
#ENTRYPOINT ["./boot.sh"]