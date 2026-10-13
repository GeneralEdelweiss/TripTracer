# GitHub KiCad 10 checks

The repository is temporarily public at the owner's explicit request, to use standard GitHub-hosted runners during development. Restore private visibility when the overall project work is complete; that step remains pending. Public copies cannot be recalled.

Workflow: `.github/workflows/kicad10-checks.yml`. Only the `design/solid-state-power-v1` branch is checked, on relevant pushes. Manual dispatch is defined but may not be discoverable until the workflow exists on GitHub's default branch; push triggering works without changing main. The job is skipped for private repositories, preventing automatic paid hosted checks after visibility is restored.

Runs official `kicad/kicad:10.0` container and native CLI, with actual version/commit recorded. This is the same base image used by `actions-for-kicad/kicad-actions`; direct invocation additionally enables all severities, exclusions, PCB parity, all track errors and zone refill. It does not save the PCB or generate manufacturing files. Both checks execute even when one fails; the final gate fails if ERC, DRC or netlist export fails. Reports are retained one day. No secrets or write permission are needed. KiCad 10 minor tag may receive patch updates; version is recorded on every run.

These are electrical/geometry software checks only. Existing documented failures are expected to keep the workflow red. No lab, thermal, automotive, mechanical-fit, or manufacturing approval follows from CI passing.
