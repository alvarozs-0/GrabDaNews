FROM python:3.13.5

ENV PYTHONDONOTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Default to SQLite for containerized deployment
ENV DB_ENGINE=django.db.backends.sqlite3
ENV DB_NAME=db.sqlite3
ENV DEBUG=True
ENV SECRET_KEY=container-default-secret-key-change-in-production

# For simplicity, allow all hosts in containerized deployment
ENV ALLOWED_HOSTS=*

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

# Run database migrations and start server
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
