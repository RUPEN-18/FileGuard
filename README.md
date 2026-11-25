# FileGuard
A read-only directory integrity checker that creates SHA-256 manifests and detects added, modified and removed files. Processes file bytes in chunks; symbolic links are skipped.

## Quick start
Python 3.10+; no third-party dependencies.
```sh
python fileguard.py snapshot example --manifest baseline.json
python fileguard.py verify example --manifest baseline.json
python -m unittest -v
```
Modify a file under `example/` and run verify again to see a change report. Exit codes: 0 = unchanged/snapshot successful, 1 = differences detected, 2 = input or operational error. Existing manifests are never overwritten by snapshot.

## Limitations
A trusted baseline is essential. This does not prevent modifications, detect malware, or authenticate an unsigned manifest. Run on a stable directory you have permission to read; concurrent writes can produce inconsistent results. Keep the manifest separately protected.
