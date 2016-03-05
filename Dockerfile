FROM python:3.4.4

ENV PYTHONUNBUFFERED 1

RUN mkdir /code

WORKDIR /code

ADD . /code/

RUN pip install -r requirements.txt

RUN cp -R example/project project && cp example/manage.py .

RUN yes yes | python manage.py spiritinstall
