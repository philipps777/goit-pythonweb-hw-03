FROM python:3.10

RUN pip install jinja2

WORKDIR /app

COPY . .

EXPOSE 3000

CMD ["python", "main.py"]