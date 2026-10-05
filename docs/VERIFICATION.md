# Verification

- Mint base: merged `main`, `f9ed322`.
- Core and CLI tests: 33 passed with `MINT_OP=/usr/bin/false`.
- Linux release: CLI and Tauri window compiled on Arch Linux.
- Installed CLI and window hashes matched build outputs.
- Clipboard proof: copied password hash absent from 289 Quattro text entries; existing entry matched as the reader's positive control.
- Clipboard offers `x-kde-passwordManagerHint`; five-second conditional clear passed.
- 1Password proof: item-list preflight failed with authorization prompt dismissed; no item created. Save/delete proof remains untested.
- UI review: first-party layout retained; save action explicitly creates a different password; uncertain outcomes require checking 1Password.
- Bridge: 18 stub tests passed, including bounded output, pipe-only secrets and no sensitive-copy fallback after save.
- Model: five tests cover malformed responses, metadata limits, settings bounds and exact preset identity.
- Offscreen Quickshell: eight cases pass, including actual request I/O, malformed/oversized streams, cancellation, generation/presets, preview isolation and panel ownership.
- Native bar and panel instantiate offscreen against installed first-party components; visual and keyboard behavior remains unverified.
- Real bridge: generated password and clipboard matched; three-second conditional clear passed.
- Linux toggle fix: the same window address cycles shown, absent, shown; keyboard focus remains untested while locked.
- Super+Ctrl+M: bound in dotfiles; reload reports no configuration errors.
- Plugin installed from its public Git URL and enabled; active=false pending shell restart after unlock.
- Live multi-monitor, keyboard and light/dark panel captures remain untested while the desktop is locked.
- Local manifest validation and QML lint passed.
- Local marketplace static detection reported no findings; remote exact-commit review remains unperformed.

## Open verification

- [Unlocked desktop checks](https://github.com/steveclarke/omarchy-mint/issues/1), dated 2026-10-05.
- [Real save and cleanup proof](https://github.com/steveclarke/omarchy-mint/issues/2), dated 2026-10-05.
- [Linux toggle and Arch packaging](https://github.com/steveclarke/mint/pull/4) remains a draft until unlocked-session validation.
