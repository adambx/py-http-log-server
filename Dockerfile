FROM python:3.9-slim

WORKDIR /app

COPY logserver.py .

EXPOSE 8000

CMD ["python", "-u", "logserver.py"]