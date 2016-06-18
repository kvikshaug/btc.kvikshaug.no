FROM python:latest

RUN apt-get update && \
    apt-get install -y locales && \
    localedef -i nb_NO -c -f UTF-8 -A /usr/share/locale/locale.alias nb_NO.UTF-8

RUN mkdir -p /app
WORKDIR /app

COPY requirements.txt requirements-dev.txt /app/
RUN pip install -r requirements.txt -r requirements-dev.txt

COPY . /app/
CMD ["flask", "run", "--host=0.0.0.0"]
