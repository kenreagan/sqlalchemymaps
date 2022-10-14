FROM python:latest

WORKDIR   /myapp

COPY . /myapp

RUN python -m venv venv && source venv/bin/activate

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["gunicorn", "-w 4", "-b :5000", "app:app"]
