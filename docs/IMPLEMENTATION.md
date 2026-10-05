# Mint integration

- Goal: a first-party Omarchy panel backed by the Mint CLI.
- Design: native hero, password display, rule controls and explicit copy/save actions; one shared service across monitors.
- Secret boundary: password data travels through stdin and bounded stdout, never argv or files.
- Save identity: `mint save` generates a new password; the form names this action and replaces the preview only after success.
- Clipboard: sensitive Wayland writes, timed conditional clearing, no unhinted fallback in the plugin.
- Recovery: unknown save outcomes require checking 1Password before another creation.

## Implementation sequence

1. `Model.js`, `Service.qml`, `Request.qml`: bounded responses, isolated requests, watchdogs and stale response suppression; node state tests.
2. `bin/mint-bridge`: validated JSON requests, bounded child streams, deadline and pipe-only secrets; Python stub tests.
3. `BarWidget.qml`, `Panel.qml`: shared service, native controls, keyboard navigation, settings and explicit recovery.
4. Arch package and desktop entry: CLI and window from merged Mint; real clipboard and one throwaway vault proof.
5. Live verification: small-screen fit, multiple monitors, all states, light/dark, native installation and clipped captures.
6. Security audit and independent review: grep findings, marketplace baseline, tests and CI.

## Review focus

- A stale generation response cannot replace newer rules.
- A save that loses its response cannot invite an immediate duplicate.
- Revealed text cannot use ordinary selection copy or persist after panel close.
- Test states cannot invoke real processes or vault actions.
- Missing tools and oversized output produce bounded recovery states.
