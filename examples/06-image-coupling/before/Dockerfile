FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1

# Credentials and config set here so the container starts without extra steps.
# This is the antipattern: ENV instructions are baked into the image layer.
# They appear in `docker history`, in your registry, and in every node that pulls this image.
# Rotating a key means editing this file and rebuilding.
ENV AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
ENV AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
ENV WEIGHTS_SOURCE=/app/weights.txt

WORKDIR /app
COPY server.py .
COPY weights.txt .

CMD ["python", "-u", "server.py"]
