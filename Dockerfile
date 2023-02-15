FROM python:3.9-slim

WORKDIR /app

COPY logserver.py .
COPY template.html .

EXPOSE 8000

CMD ["python", "-u", "logserver.py"]