# Mint for Omarchy

- Password generation through [Mint](https://github.com/steveclarke/mint).
- Length, character classes, allowed symbols and named site rules.
- Sensitive clipboard copies with conditional clearing after 45 seconds.
- New Login creation through Mint and 1Password CLI.
- Native Quattro controls, keyboard actions and shared state across monitors.

## Installation

1. Install Mint and `wl-clipboard` 2.3 or newer. Both `mint` and `mint-app` belong on PATH.
2. Run `omarchy plugin add https://github.com/steveclarke/omarchy-mint --enable`.
3. Run `omarchy restart shell`.

## Panel

| Action | Result |
|---|---|
| New / Ctrl+R | Generates a fresh password with the selected rules |
| Copy / Enter | Copies the displayed password with the sensitive MIME hint |
| Save new / Ctrl+S | Generates a different password and creates a Login in the selected vault |
| Show / Hide | Reveals or conceals the displayed password |
| Escape | Returns from a form or closes the panel |
| Settings | Sets clipboard lifetime, default site rule and default vault |

- The saved password replaces the preview after confirmation.
- An unconfirmed save requires checking 1Password before another creation.
- Closing the panel removes its displayed password.
- Zero clipboard lifetime disables automatic clearing.
- Linux clipboard clearing compares the current text before clearing; that comparison and clear are separate operations.
- Clipboard history exclusion depends on the manager honoring the sensitive MIME hint.

## Removal

1. Run `omarchy plugin remove io.github.steveclarke.mint`.
2. Run `omarchy restart shell`.

- The Mint binaries and Hyprland binding are separate from the plugin.
- The plugin stores no password files or account credentials.

## Development

- `bin/check` runs model tests, stubbed helper tests and the agent-file guard.
- Local checks also validate the manifest and lint QML against installed Omarchy.
- `docs/design/` contains the panel prototype and state reference.
- `omarchy-shell io.github.steveclarke.mint debugState ready` enables a fixed preview; preview actions cannot launch processes.
- `omarchy-shell io.github.steveclarke.mint debugState off` returns to normal operation.
- Diagnostics report state and password presence, never password content.
