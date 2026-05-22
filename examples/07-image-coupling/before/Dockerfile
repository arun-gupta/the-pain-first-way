FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1

# No credentials here -- Docker will warn if you use ENV for secrets,
# and rightly so: ENV values are baked into the image layer and visible
# in `docker history` and `docker inspect`.
# Pass AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and WEIGHTS_SOURCE
# via `docker run -e` at runtime instead.
ENV WEIGHTS_SOURCE=/app/weights.txt

WORKDIR /app
COPY server.py .
COPY weights.txt .

CMD ["python", "-u", "server.py"]
