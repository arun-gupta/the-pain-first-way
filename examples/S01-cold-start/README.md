# Pain S.01 example: the same model server, two approaches to weight loading

A working demonstration of [Pain S.01: Cold start for my 70B model takes 4 minutes](../../pains/S01-cold-start.md). Same inference server code, two deployment styles. The init container pattern is the only thing that changes. And that changes everything about portability.

## What's here

```
S01-cold-start/
├── before/        # the typical way: download logic baked into the server
│   ├── server.py
│   └── README.md
└── after/         # the cloud native way: init container stages weights, server is unaware
    ├── server.py          # serving code only -- no download logic, no credentials
    ├── downloader.py      # init container entrypoint -- fetches weights to /model/weights.txt
    ├── Dockerfile         # server image: serving code only
    ├── .dockerignore
    ├── build.sh
    ├── init-container.yaml  # Pod spec: init container + server sharing a volume
    ├── weights.txt          # the fake "model" -- a small text file
    └── README.md
```

No GPU required. The "model" is a tiny text file. The cloud native concepts are identical to a real 70B weight load.

## The point of the diff

`before/server.py` downloads the weights file from a hardcoded URL on startup. The download source is baked into the server code. Change from S3 to GCS, or from one bucket to another, and you change the server and rebuild the image.

`after/server.py` reads weights from `/model/weights.txt` and has no idea where they came from. The server image contains serving logic only. `after/downloader.py` fetches the weights; swap it to change the source. The server image never changes and never carries credentials.

## Run it

- [`before/README.md`](before/README.md) -- run bare with Python, observe the coupled startup
- [`after/README.md`](after/README.md) -- build, apply, watch the init container stage weights before the server starts

---

[← Back to Pain S.01](../../pains/S01-cold-start.md) · [Landscape](../../README.md) · [Examples index](../README.md)
