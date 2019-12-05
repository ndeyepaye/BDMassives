FROM python:3.7-slim

WORKDIR /

ADD requirements.txt /

RUN pip install -r requirements.txt

ADD . /

EXPOSE 8080

CMD ["python", "app.py"]