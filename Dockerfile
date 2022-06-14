FROM python:latest

WORKDIR   /myapp

COPY . /myapp

RUN pip install -r requirements.txt

CMD ["gunicorn", "-w 4", "app:app"]