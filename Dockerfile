FROM python:3.6
ENV PYTHONBUFFERED 1

RUN apt-get -y update && \
    apt-get -y install ruby-sass

RUN mkdir /code
WORKDIR /code

ADD requirements.txt /code
RUN pip install -r requirements.txt

ADD . /code

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "spartan.wsgi"]
