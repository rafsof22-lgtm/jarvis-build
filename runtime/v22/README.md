# Jarvis V22 Runtime Reconciliation Control Plane

Exposes merged registries and evidence-backed runtime/deployment status. It fails closed on external production and 100% acceptance.

The Docker build and CI run `scripts/build_v22_runtime.py` to generate the 38-instruction register and 51-module runtime matrix from the merged V21 canonical registries.
