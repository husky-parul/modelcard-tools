## Core Assumptions for the Demo 1

- Flat ModelCard JSON (no nesting)

- 1:1 mapping between model and ModelCard

- Filter-based search only (e.g., f1_score > 0.25, license = MIT)

- Manual indexing to start, extend to cronjob later

- Registry-agnostic design, even though we start with quay.io. For the demo `registry:2` is used. It is official lightweight Docker Registry. OCI-compliant. Works perfectly with oras. Simple to run in Podman

