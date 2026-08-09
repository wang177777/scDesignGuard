# Installation

## Source checkout

Requirements: CPython 3.9 or later. The evaluated release was independently
reproduced with CPython 3.12.12.

```bash
git clone https://github.com/wang177777/scDesignGuard.git
cd scDesignGuard
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install .
scdesignguard --version
python -m unittest discover -s tests -v
```

Expected version: `0.1.0`.

## Exact evaluated wheel

Verify the wheel before installation:

```bash
shasum -a 256 artifacts/scdesignguard_nm03-0.1.0-py3-none-any.whl
python -m pip install --no-index --no-deps \
  artifacts/scdesignguard_nm03-0.1.0-py3-none-any.whl
```

Expected SHA-256:
`59b74e2e60315094fb5e9d70224eb7724d8839d75e2e3f8457042f2df0ec9986`.

## OCI image

The exact evaluated OCI archive is a GitHub release asset. After downloading
it, verify SHA-256
`ad675089b934e6d96c1bfd83b9deb4fc6c9ac8dbda345ce9e08a9d7d9b21c85d`
and load it:

```bash
podman load -i scdesignguard_nm03_0.1.0.oci.tar
podman image inspect localhost/scdesignguard-nm03:0.1.0
```

Run with a read-only filesystem, no network and read-only inputs:

```bash
mkdir -p public-inputs
cp tests/fixtures/valid.json public-inputs/contract.json
podman run --rm --network=none --read-only --cap-drop=all \
  --security-opt=no-new-privileges \
  -v "$PWD/public-inputs:/inputs:ro" \
  localhost/scdesignguard-nm03:0.1.0 verify /inputs/contract.json
```

Do not mount credentials, identifiable participant information, controlled
data or uncontrolled host directories into the container.

