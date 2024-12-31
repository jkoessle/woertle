FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install poetry

RUN poetry config virtualenvs.create false && poetry install --no-dev

COPY woertle/ ./

EXPOSE 8080

CMD ["poetry", "run", "gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app:app"]
