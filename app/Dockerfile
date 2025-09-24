# syntax=docker/dockerfile:1

FROM python:3.11.6-slim

RUN apt-get update && apt-get install -y \
 curl \
 build-essential \
 && rm -rf /var/lib/apt/lists/*

ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app
COPY pyproject.toml ./

RUN uv pip install -r pyproject.toml --system

COPY . .

RUN chmod 755 ./start.sh


EXPOSE 8000

CMD ["./start.sh"]