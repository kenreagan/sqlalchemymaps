FROM python:latest

WORKDIR   /myapp

COPY . /myapp

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["gunicorn", "-w 4", "-b :5000", "app:app"]
