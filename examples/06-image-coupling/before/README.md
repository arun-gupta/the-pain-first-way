# Before: credentials baked into the image via Dockerfile ENV

`server.py` reads credentials and config from environment variables -- that part is correct. Reading from env vars keeps secrets out of source code.

The problem is where those env vars come from. The natural next step when containerising is to set them in the Dockerfile as `ENV` instructions so the container starts without extra setup. That bakes them into the image layer: visible in `docker history`, cached in your registry and CI system, and present on every node that ever pulled the image.

## Run it locally

Set the env vars inline and run with Python -- no Docker needed:

```bash
cd examples/06-image-coupling/before

AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE \
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY \
python3 server.py
```

Expected output:

```
[startup] Connecting to ./weights.txt
[startup] Using key: AKIAIOSFODNN7EXAMPLE (from env var -- but where did that env var come from?)
[startup] Weights staged in 0.001s -> /tmp/weights.txt
[startup] Model loaded. Preview: these are fake model weights...
[ready] Inference server listening on port 8080
```

In another terminal:

```bash
curl localhost:8080/predict
```

```
prediction using model: [these are fake model weights
layer_0: 0.312 0.847 0.193 0.65...]
```

## Run it with Docker

Press `Ctrl+C` in the terminal running `server.py` to stop it, then build the image -- credentials are set via `ENV` in the Dockerfile:

```bash
docker build -t inference-server-before:v1 .
docker run -p 8080:8080 inference-server-before:v1
```

Now inspect what ended up in the image:

```bash
docker history inference-server-before:v1
```

You will see the credentials in the layer history:

```
IMAGE          CREATED         CREATED BY
...            ...             ENV AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/...
...            ...             ENV AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
```

Anyone with pull access to the registry can read them.

## Now feel the pain

Your security team just flagged the access key as compromised. Rotate it.

Here is what that requires with this setup:

**1. Edit the Dockerfile**

```bash
sed -i '' \
  -e 's/AWS_ACCESS_KEY_ID=.*/AWS_ACCESS_KEY_ID=AKIAI99999NEWKEY/' \
  -e 's/AWS_SECRET_ACCESS_KEY=.*/AWS_SECRET_ACCESS_KEY=newSecret\/K7MDENG\/bPxRfiCYNEWKEY/' \
  Dockerfile
```

**2. Commit the change**

```bash
git add Dockerfile
git commit -m "rotate access key"
```

**3. Rebuild the image**

```bash
docker build -t myregistry/inference-server:v2 .
```

**4. Push the new image**

```bash
docker push myregistry/inference-server:v2
```

**5. Redeploy every running instance**

```bash
kubectl set image deployment/inference-server \
  inference-server=myregistry/inference-server:v2
kubectl rollout status deployment/inference-server
```

You changed two string values. You triggered a full build-push-deploy pipeline. The serving logic did not change by a single character.

Note that the old image -- with the compromised key -- is still in your registry, still cached in your CI system, and still present on every node that pulled it. Rotating the key does not remove it from those places.

Now imagine doing this at 2am after a credential leak. Or six times a year on a routine rotation schedule. Or across three environments (dev, staging, prod) that each need different keys -- each gets its own image tag, tracked and promoted separately.

The [`after/`](../after/) example removes this entirely: a key rotation is `kubectl apply` on one YAML file, with no image rebuild, no redeploy, and nothing left in the image to rotate.
