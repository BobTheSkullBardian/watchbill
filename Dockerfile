# This file is a template, and might need editing before it works on your project.
FROM python:3.10

# Edit with mysql-client, postgresql-client, sqlite3, etc. for your needs.
# Or delete entirely if not needed.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY requirements.txt /code
RUN pip install --no-cache-dir -r requirements.txt

COPY . /code

# For Django
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


