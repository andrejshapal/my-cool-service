FROM python:3.13-slim

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

RUN adduser --system --uid 1000 --no-create-home nonroot
USER 1000

EXPOSE 5000

CMD ["./scripts/entrypoint.sh"]