# Verification

## Installed proof — 2026-10-05

- Installed plugin: normal default-branch update to `5da19ca6f471f425da905820b2637d37f9b2292d`, followed by Omarchy shell restart.
- Engine: Arch package `mint 0.1.0-2`, compiled in a clean chroot from release merge `0c4aed5bf5e195b2f08421b012e9d64c358eb414`.
- Package: both binaries, desktop entry and icon have verified pacman ownership and match the package byte for byte; obsolete local binaries are removed through trash.
- Package checks: 47 tests pass with two Cargo jobs and the 1Password stub. Namcap has no errors or implicit-dependency warnings; four retained runtime-dependency warnings have documented uses.
- [Arch packaging evidence](https://github.com/steveclarke/mint/pull/5) records the package contents, checksum and retained warnings.
- Native Wayland class: `mint-app`, matching `StartupWMClass`; X11 `WM_CLASS` does not apply to this native Wayland run.
- Super+Ctrl+M: five physical-key hide/show transitions pass, with focus on each show and the same application process throughout.
- Native captures: ten stand-in service states and the save form in both the active light palette and the stock Catppuccin dark palette; normal generation, copied state and settings also have installed captures.
- Monitors: the native bar opens the panel on both 2880 × 1620 logical displays.
- Preview: actual installed panel in normal operation, masked generated password, no demo banner; all four borders inspected at zoom.
- Theme cleanup: the runtime theme API restores the exact original palette; theme files remain unchanged.
- Clipboard: native panel Copy advertises the sensitive MIME hint; its hash is absent from 289 text-history entries. An existing-entry positive control and an injected in-memory match both pass.
- Auto-clear: clipboard becomes empty after 44.78 seconds under the default 45-second setting; panel closure discards its password.
- Test cleanup: temporary input devices are closed, pointer position restored, clipboard empty, and panel state idle with demo off and no retained password.
- Scope: smaller-screen runtime fit remains untested.

## Source checks

- Bridge: 22 stubbed tests pass, including bounded output, pipe-only secrets, executable resolution, copy error classes and malformed responses.
- Model: six tests pass, including DEL, C1 and bidi controls across labels, identities and passwords.
- Offscreen Quickshell: 11 cases pass, including actual request I/O, oversized streams, cancellation, panel ownership, busy-preview refusal and cancelled-save uncertainty.
- Native component loading, manifest validation, QML lint and repository hygiene pass.
- Automated test commands set `MINT_OP=/usr/bin/false`; stand-in panel states cannot invoke vault operations.
- Runtime text sinks explicitly use PlainText; host labels are fixed or cleaned. Output collection and filesystem-write matches belong to test/tooling code.
- Prior runtime-source marketplace baseline: `23a0360f76ff442702b65be03d0ed9fe07de2bb0`, passed with no findings or capabilities. Updated evidence commits require their own exact-commit baseline.

## Real-account proof

- [Save and cleanup follow-up](https://github.com/steveclarke/omarchy-mint/issues/2), dated 2026-10-05: the deliberate proof stops at the duplicate-title search because desktop authorization is dismissed.
- Creation attempts: zero. No item is created, no deletion is required, and no password reaches logs or captures.
- Remaining proof: one installed panel-path save of `mint test (delete me)` in Employee, immediate deletion, and verified absence.
