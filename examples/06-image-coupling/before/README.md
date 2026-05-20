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

Press `Ctrl+C` in the terminal running `server.py` to stop it, then build and run:

```bash
docker build -t inference-server-before:v1 .
docker run -p 8080:8080 \
  -e AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE \
  -e AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY \
  inference-server-before:v1
```

Passing credentials via `-e` at runtime is the right Docker pattern -- they are not baked into the image and will not appear in `docker history`. But they are still visible on the running container:

```bash
docker inspect $(docker ps -q) | grep -A2 "AWS_"
```

```
"AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE",
"AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
```

And you still have the harder questions: where do these values come from in your CI pipeline? How do you rotate them across dozens of running containers? How do you give staging different credentials than prod without maintaining separate run commands per environment? Docker has no answer for these at scale -- that is where Kubernetes Secrets come in.

## Now feel the pain

Your security team just flagged the access key as compromised. Rotate it.

Here is what that requires with this setup:

**1. Find every place the credentials are set**

They could be in your CI pipeline environment variables, a deploy script, a `.env` file committed to a config repo, or hardcoded in a Helm values file. There is no single source of truth -- you have to hunt.

**2. Update each one**

```bash
# In your CI system: update the secret variable via the UI or CLI
# e.g. for GitHub Actions:
gh secret set AWS_ACCESS_KEY_ID --body "AKIAI99999NEWKEY"
gh secret set AWS_SECRET_ACCESS_KEY --body "newSecret/K7MDENG/bPxRfiCYNEWKEY"
```

**3. Restart every running container**

```bash
kubectl rollout restart deployment/inference-server
```

Each new pod picks up the updated values -- but only if your deployment is already wired to pass them through. If a container was started directly with `docker run -e`, you restart it manually.

You changed two string values. You touched your CI system, your deployment config, and restarted every instance. With no single place to update, it is easy to miss one.

Now imagine doing this at 2am after a credential leak. Or six times a year on a routine rotation schedule. Or across three environments (dev, staging, prod) that each need different keys -- each gets its own image tag, tracked and promoted separately.

The [`after/`](../after/) example removes this entirely: a key rotation is `kubectl apply` on one YAML file, with no image rebuild, no redeploy, and nothing left in the image to rotate.
