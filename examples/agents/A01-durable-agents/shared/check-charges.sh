#!/usr/bin/env bash
# Print what the sink has recorded. After a correct resume, charges == 1.
# After a crash that duplicated work, charges == 2.
set -euo pipefail
kubectl exec -i deploy/sink -- python - <<'PY'
import json, urllib.request
d = json.load(urllib.request.urlopen("http://localhost:8080/effects"))
print("total effects:", d["total"], "| charges:", d["charges"])
for e in d["effects"]:
    print("  ", e["type"], e["key"])
PY
