FROM python:3.6
ENV PYTHONBUFFERED 1

RUN apt-get -y update && \
    apt-get -y install ruby-sass

RUN mkdir /code
WORKDIR /code
ADD . /code
RUN pip install -r requirements.txt
EXPOSE 80
CMD ["gunicorn", "--bind", "0.0.0.0:80", "spartan.wsgi"]
