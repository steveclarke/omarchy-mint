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
- [Linux toggle and Arch packaging](https://github.com/steveclarke/mint/pull/4): source readiness is independent of pending installation proof.

## Review repair evidence — 2026-10-05

- Mint source: `4d545c8`; shared stdin copy, fixed Wayland executable paths, bounded I/O and acknowledged clearer startup.
- Bridge: 18 stubbed tests pass; no production executable override hooks.
- Model: six tests pass, including DEL, C1 and bidi controls across labels, identities and passwords.
- Offscreen Quickshell: 11 cases pass, including busy-preview refusal, cancelled-save uncertainty and preview-state cycling.
- Native component loading, manifest validation and QML lint pass.
- Grep audit: runtime text sinks explicitly use PlainText; host labels use fixed or cleaned strings; output collection and filesystem-write hits belong to test/tooling code. No network or privilege-command matches in the scanned plugin tree.
- Preview: the existing 612 × 757 capture contains the demo banner. The final capture from the live installed panel without the banner remains pending installation.
- Installed repair, package/chroot proof, full live-state sweep and real-item save/delete proof remain pending.

## Source follow-up evidence — 2026-10-05

- Copy failures retain the bridge's missing-command, timeout, overflow, process-failure and response classes. Mint JSON stderr contributes only known kind/exit-code pairs; messages are fixed, with no stderr or secret echo.
- Bridge: 22 stubbed tests pass, including missing Mint, all copy failure classes, malformed success responses and hostile JSON stderr.
- Model: six tests pass. Offscreen Quickshell: 11 cases pass; native components, manifest validation and QML lint pass.
- Grep audit: every git-tracked file is scanned, with positive controls and no depth or size exclusions. QML text sinks have explicit formats; host labels are fixed or cleaned. Filesystem-write and whole-output collection matches belong to tests and tooling. Network and privilege patterns have no matches in this scope.
- Final preview: pending installation; the existing demo-banner capture does not satisfy the final-preview requirement.
- Installation proof: package/chroot checks, StartupWMClass, updated-plugin live states and real-item save/delete remain pending.
