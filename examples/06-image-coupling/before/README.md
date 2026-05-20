# Before: source URL and credentials baked into the server image

`server.py` hardcodes `WEIGHTS_SOURCE`, `AWS_ACCESS_KEY_ID`, and `AWS_SECRET_ACCESS_KEY` as constants. The download logic and the serving logic live in the same file. When you containerize this, those constants end up in the image -- either as `ENV` instructions in the Dockerfile or as values in the source file copied into it. Either way they travel with the image: cached in your registry, your CI system, and on every node that ever pulled it.

## Run it

No dependencies beyond the standard library.

```bash
cd examples/06-image-coupling/before
python3 server.py
```

Expected output:

```
[startup] Connecting to .../before/weights.txt
[startup] Using key: AKIAIOS... (hardcoded in this file)
[startup] Weights staged in 0.000s -> /tmp/weights.txt
[startup] Model loaded. Preview: these are fake model weights...
[startup] To change the source or rotate the key, edit this file and rebuild.
[ready] Inference server listening on port 8080
[ready]   GET /health  -> liveness check
[ready]   GET /predict -> simulated inference
```

In another terminal:

```bash
curl localhost:8080/predict
```

```
prediction using model: [these are fake model weights
layer_0: 0.312 0.847 0.193 0.65...]
```

## Now feel the pain

Your security team just flagged the access key as compromised. Rotate it.

Here is what that requires with this setup:

**1. Edit the source file**

```bash
sed -i '' \
  -e 's/AWS_ACCESS_KEY_ID = ".*"/AWS_ACCESS_KEY_ID = "AKIAI99999NEWKEY"/' \
  -e 's/AWS_SECRET_ACCESS_KEY = ".*"/AWS_SECRET_ACCESS_KEY = "newSecret\/K7MDENG\/bPxRfiCYNEWKEY"/' \
  server.py
```

**2. Commit the change**

```bash
git add server.py
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

You changed two string values. You triggered a full build-push-deploy pipeline. The serving logic -- the part that actually handles inference requests -- did not change by a single character.

Now imagine doing this at 2am after a credential leak. Or doing it six times a year as part of a routine rotation policy. Or having three environments (dev, staging, prod) that each need different keys, so each gets its own image tag that has to be built, tracked, and promoted separately.

The [`after/`](../after/) example shows how a ConfigMap and a Secret remove this coupling so a key rotation is `kubectl apply` on one YAML file, with no image rebuild at all.
