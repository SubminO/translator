FROM python:2.7-alpine

RUN mkdir /opt/translator \
    && cd /opt/translator

WORKDIR /opt/translator

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY ./* ./

CMD [ "python", "./server.py" ]
