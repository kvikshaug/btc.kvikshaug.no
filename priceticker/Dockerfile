FROM python:latest

RUN mkdir -p /app
WORKDIR /app

COPY requirements.txt requirements-dev.txt /app/
RUN pip install -r requirements.txt -r requirements-dev.txt

COPY . /app
CMD ["python", "-m", "priceticker.priceticker"]
