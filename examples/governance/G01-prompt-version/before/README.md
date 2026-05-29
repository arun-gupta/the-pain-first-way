# before/ -- the prompt is scattered, and the running version is a mystery

Run it bare with Python. No build, no cluster.

```bash
cd before
python3 server.py
```

In another terminal:

```bash
curl localhost:8080/predict
curl -i localhost:8080/version
```

The answer comes from `DEFAULT_PROMPT` in `server.py`. Looks settled. The
`/version` request returns `HTTP/1.0 404 Not Found` with an empty body: there is
no version concept to report. (Use `curl -i` to see the status line; a plain
`curl` prints only the empty body, which looks like nothing happened.)

Now simulate the override that someone added on the prod box two weeks ago:

```bash
# stop the server (Ctrl-C), then:
set -a; source .env.example; set +a
python3 server.py
```

Hit `/predict` again:

```bash
curl localhost:8080/predict
```

The reply is different now. The first run used the *helpful assistant, ends with a
ticket link* prompt baked into the `DEFAULT_PROMPT` constant. This run uses the
*terse, one sentence* prompt from `.env.example`, because the `SYSTEM_PROMPT`
environment variable silently overrides the constant. **Same code, same command, different
behavior, and the value that decided it lives in a `.env` that was never committed.**

## The point

A customer reports a regression "from about two weeks ago." You cannot answer
"what prompt was running on August 12th" because:

- the prompt lives partly in code, partly in `.env`, partly in a doc,
- the override isn't in git, so there's no history to read,
- there's no version stamped on anything the running server can report.

The fix isn't a better doc. It's making the prompt a versioned config object with
an owner and a history.

When you're done here, stop this server with Ctrl+C, then continue to
[`../after/`](../after/README.md) to see that fix. Both walkthroughs use port 8080,
so leaving this one running blocks the after/ `kubectl port-forward` with an
"address already in use" error.

---

[← Example index](../README.md)
