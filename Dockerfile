FROM python:3.13-slim AS builder

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY ./requirements.txt /tmp/requirements.txt

RUN python3 -m pip install --upgrade pip \
 && python3 -m pip install wheel \
 && python3 -m pip install  --disable-pip-version-check --no-cache-dir -r /tmp/requirements.txt

FROM python:3.13-slim

RUN adduser --system --uid 1000 --no-create-home nonroot

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app:/opt/venv/lib/python3.13/site-packages"

WORKDIR /app
RUN chown 1000:1000 /app
COPY --chown=1000:1000 . /app

USER 1000

EXPOSE 5000
CMD ["./scripts/entrypoint.sh"]
