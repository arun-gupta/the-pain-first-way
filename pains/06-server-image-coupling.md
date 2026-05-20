# Pain 6: My server image is coupled to its config and secrets

> *The server image carries more than serving code. It carries the weights source URL, the credentials to fetch them, the model name, the server parameters, and anything else that differs between environments. That coupling means every operational change flows through the image build pipeline -- even when not a single line of serving logic changed.*
>
> *Rotating a credential: rebuild. Moving weights to a new bucket: rebuild. Switching from S3 to GCS: rebuild. Changing a server parameter for staging: rebuild. Deploying to prod with different settings than dev: a different image tag per environment, each one a fork that has to be tracked and promoted separately.*

## The pattern

The serving code (vLLM, TGI, a custom FastAPI app) and everything it needs to start -- where weights come from, which model to load, which credentials to use, what parameters to apply -- are bundled in one image. Any change to any of those forces an image rebuild and redeploy even when the serving code is unchanged. The same image ends up carrying dev settings, staging settings, and prod settings as separate tags, or credentials live in environment variables baked into the Dockerfile itself.

```mermaid
flowchart LR
    subgraph Coupled["Server image (before)"]
        direction TB
        A[Serving code]
        B[Download tool<br/>aws-cli / gcsfuse /<br/>HuggingFace hub]
        C[Source URL<br/>s3://my-bucket/model/]
        D[Credentials<br/>AWS_ACCESS_KEY_ID<br/>AWS_SECRET_ACCESS_KEY]
        E[Model config<br/>model name, max batch size,<br/>quantization settings]
    end
    Coupled -->|starts| F[Downloads weights<br/>then serves]
```

The coupling surfaces in every operational change that has nothing to do with serving logic:

- Rotating a credential or API token
- Moving weights to a new bucket or region
- Switching storage backends (S3 to GCS, GCS to Azure Blob)
- Changing the model name or version
- Tuning a server parameter (max batch size, quantization, sequence length) per environment
- Promoting from dev to staging to prod -- each environment needs different values, so each gets a different image tag

And a security consequence that compounds all of the above: credentials inside an image get cached in your registry, your CI system, and on every node that ever pulled the image. Rotating a key doesn't remove the old one from those caches.

## The primitives

The fix is to decouple everything that changes for operational reasons from the image itself. Config values -- source URL, model name, server parameters -- move into cluster objects that can be updated without touching the image. Secrets -- credentials, API tokens -- move into a separate store, injected at runtime and never baked in. The fetch logic moves into a separate setup step that runs once at startup, stages weights to a shared location, and exits before the server starts. The result: the server image changes only when serving code changes, and is identical across every environment.

```mermaid
flowchart LR
    CM[ConfigMap<br/>source URL<br/>model name<br/>server params]
    SEC[Secret<br/>credentials<br/>API tokens]

    subgraph Init["Init container"]
        I1[Download tool]
    end

    CM -->|source URL| Init
    SEC -->|credentials| Init
    Init -->|stages weights to<br/>shared volume| Vol[(/model/weights.txt)]
    Vol --> Server["Server image<br/>serving code only"]
    CM -->|model name<br/>server params| Server
```

- **[Init containers](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/)** (setup steps that must complete before your model server starts): move the download tool, source URL, and credentials out of the server image into a separate container. The server image becomes serving code only. Swap the init container to change the weight source; the server image never changes and never carries credentials. An init container that fails stops the pod before it serves a single request -- a fast-fail that prevents a server with missing or partial weights from ever becoming live.

- **[Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)** (Kubernetes objects that store sensitive data as key-value pairs, scoped to a namespace, and mountable into containers without embedding values in the image): store bucket credentials as a Secret and mount it into the init container only. The server image never sees the credentials. Rotate the Secret and the next pod picks up the new value without any image rebuild. The Secret API is the same on any cluster; what backs it -- AWS Secrets Manager, GCP Secret Manager, HashiCorp Vault -- is a separate concern that [External Secrets Operator](https://external-secrets.io) can abstract.

- **[ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/)** (Kubernetes objects that store non-sensitive configuration, also mountable as environment variables or files): store any config that changes independently of serving logic -- the weights source URL, the model name, max batch size, quantization settings, environment-specific endpoints -- as a ConfigMap. Each environment gets its own ConfigMap; the image is identical across all of them. Changing a value is a `kubectl apply` on one YAML object, not a code change.

The resulting split:

| Concern | Lives in |
|---|---|
| Serving logic | Server image (built once, identical across all environments) |
| Download tool | Init container image |
| Source URL | ConfigMap |
| Model name, server parameters | ConfigMap |
| Credentials, API tokens | Secret |

## Trade-offs

**What you keep**: your model and your model server. The server image is now a stable artifact -- identical across dev, staging, and prod, and across weight source, model name, and credential changes.

**What you give up**: the simplicity of one image. You now build and maintain two images (server and init container), and coordinate their versions when the download interface changes. Init container failures are also highly visible: a bad Secret or wrong bucket URL blocks the pod from starting, which surfaces problems early but means the pod never reaches `Running` until credentials and source are correct.

## Try it

A working demonstration lives in [`examples/06-image-coupling/`](../examples/06-image-coupling/). The before case runs without Docker or Kubernetes and shows the hardcoded source URL and credentials printed on every startup. The after case uses an init container, a ConfigMap, and a Secret to decouple them from the image; the walkthrough includes steps to simulate a key rotation and a source change without rebuilding. Runnable on a Mac with a local Kind cluster and no GPU required.

---

[← Pain 5: Cold start](05-cold-start.md) · [Landscape](../README.md) · [Pain 7: GPU underutilization →](07-gpu-underutilized.md)
