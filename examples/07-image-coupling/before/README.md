# Before: credentials managed outside the image, scattered across environments

`server.py` reads credentials and config from environment variables -- that part is correct. Reading from env vars keeps secrets out of source code.

The problem is where those env vars come from. The natural next step when containerising is to set them in the Dockerfile as `ENV` instructions so the container starts without extra setup. That bakes them into the image layer: visible in `docker history`, cached in your registry and CI system, and present on every node that ever pulled the image.

## Run it locally

Copy the example env file, fill in the demo values, and run:

```bash
cd examples/07-image-coupling/before
cp .env.example .env
```

```bash
sed -i '' \
  -e 's/AWS_ACCESS_KEY_ID=.*/AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE/' \
  -e 's/AWS_SECRET_ACCESS_KEY=.*/AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI\/K7MDENG\/bPxRfiCYEXAMPLEKEY/' \
  .env
```

Then run:

```bash
export $(grep -v '^#' .env | xargs) && python3 server.py
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

Press `Ctrl+C` in the terminal running `server.py` to stop it. The same `.env` file is used here:

```bash
docker build -t inference-server-before:v1 .
docker run -p 8080:8080 --env-file .env inference-server-before:v1
```

Expected output:

```
[startup] Connecting to /app/weights.txt
[startup] Using key: AKIAIOSFODNN7EXAMPLE (from env var -- but where did that env var come from?)
[startup] Weights staged in 0.001s -> /tmp/weights.txt
[startup] Model loaded. Preview: these are fake model weights...
[ready] Inference server listening on port 8080
```

In a second terminal:

```bash
curl localhost:8080/predict
```

```
prediction using model: [these are fake model weights
layer_0: 0.312 0.847 0.193 0.65...]
```

Docker offers several ways to pass secrets to a container at runtime. None of them should be `ENV` in the Dockerfile.

| Method | How | Credentials in image? | Visible in `docker inspect`? | Rotation |
|---|---|---|---|---|
| Inline `-e` | `docker run -e KEY=val` | No | Yes | Restart container manually |
| Env file | `docker run --env-file .env` | No (if file not COPYed) | Yes | Update file, restart container |
| Docker secrets (Swarm) | `docker secret create` + mounted at `/run/secrets/` | No | No | Update secret, redeploy service |
| BuildKit `--secret` | `RUN --mount=type=secret,id=s` | No | Build-time only | N/A |

**Inline `-e`** (what we used above) is fine for local development. **`--env-file`** is a small improvement -- secrets live in a file you keep out of git rather than inline on the command line. **Docker secrets** are the production-grade native option, but only available in Swarm mode.

The gap: none of these handle the questions that matter at scale -- where do the values come from in CI, how do you rotate across dozens of containers, how do you scope per environment? In a second terminal:

```bash
docker inspect $(docker ps -q) | grep -A2 "AWS_"
```

```
"AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE",
"AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
```

Kubernetes Secrets address the gap: a single object per cluster, scoped to a namespace, rotatable without restarting the image, and backed by external vaults via External Secrets Operator. That is what the [`after/`](../after/) example shows.

## Now feel the pain

Your security team just flagged the access key as compromised. Rotate it.

Here is the full path using `--env-file`, which is the cleanest local Docker option:

**1. Update `.env` with the new key**

```bash
sed -i '' \
  -e 's/AWS_ACCESS_KEY_ID=.*/AWS_ACCESS_KEY_ID=AKIAI99999NEWKEY/' \
  -e 's/AWS_SECRET_ACCESS_KEY=.*/AWS_SECRET_ACCESS_KEY=newSecret\/K7MDENG\/bPxRfiCYNEWKEY/' \
  .env
```

**2. Stop the running container**

Press `Ctrl+C`, then restart with the env file:

```bash
docker run -p 8080:8080 --env-file .env inference-server-before:v1
```

**3. Verify the new key is in use**

In a second terminal:

```bash
curl localhost:8080/health
docker inspect $(docker ps -q) | grep "AWS_ACCESS_KEY_ID"
```

The container is now using the new key. No image rebuild needed -- for this one container.

**The problem doesn't stop here.** The same credentials almost certainly exist in other places too:

- Your CI pipeline (GitHub Actions secrets, Jenkins credentials store)
- Your staging and prod deploy scripts, each running their own `docker run -e`
- A Helm values file that passes them through to Kubernetes
- A `.env.staging` and `.env.prod` that a teammate manages separately

Each of those has to be found and updated. There is no single place to change. It is easy to miss one and leave a compromised key still active in staging.

Now imagine doing this at 2am after a credential leak, or six times a year on a routine rotation schedule.

The [`after/`](../after/) example removes the scatter entirely: credentials live in one Kubernetes Secret object, injected at pod startup. Rotation is `kubectl apply` on one file -- one place, one command, picked up by every new pod automatically.

## Clean up

Stop the container before moving to the `after` example — both use port 8080.

If the container is running in the foreground, press `Ctrl+C`. If it is running in the background:

```bash
docker stop $(docker ps -q --filter ancestor=inference-server-before:v1)
```
