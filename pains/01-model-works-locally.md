# Pain 1: Model works locally, breaks in prod

> *Your model serves perfectly on your laptop. On the prod VM, it crashes on import. Different Python, different CUDA, missing system lib, drift in `transformers` minor version. Nobody can reproduce your environment because nobody captured it.*

## The pattern

The unit of deployment is not your code, it's your code plus everything it depends on. You declare that whole thing once, freeze it, sign it, and ship the frozen artifact to every environment.

## The primitives

- **Container image**: your code, runtime, system libs, model weights (optionally), built from a Dockerfile, stored in a registry, addressable by digest
- **Dockerfile**: the declarative recipe for how that image gets built
- **Image registry** (GHCR, ECR, Harbor): the place every environment pulls from

## Trade-offs

**What you keep**: your code, your `requirements.txt`, your model artifacts. The Dockerfile is a wrapper.

**What you give up**: "it works on my machine" as a defense. The image either runs or doesn't, identically, everywhere.

---

[Landscape](../README.md) · [Pain 2: GPU job crashed →](02-gpu-job-crashed.md)
