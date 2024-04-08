FROM python:3.10-slim-bullseye

RUN apt-get update \ 
    && apt-get -y install tesseract-ocr \
    && apt-get -y install libtesseract-dev

WORKDIR /app
COPY ./requirements.txt /app

RUN pip install --no-cache-dir --requirement /app/requirements.txt
COPY . /app

CMD ["python3", "ocr.py"]