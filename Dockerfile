FROM python:3.10.8-alpine
RUN apk --no-cache add curl postgresql-dev

# install build tools
RUN apk add --no-cache --virtual .build-deps build-base git

COPY requirements.txt .
# install deps & build psycopg2
RUN pip install -r requirements.txt --no-cache-dir

# remove build tools
RUN apk del .build-deps

COPY app /app
WORKDIR /app
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]