## WORKSPACE-01-RECOVERABLE-BOOTSTRAP-R1 - exact historical source retention

Retain the original976-byte Icarus installer and330-byte README unchanged in
two explicit allowlist exceptions. Compiled/source-cache/deb/log trees remain
ignored. The new relocatable installer is recommended; legacy host-specific
bytes remain available for source recovery. Eight original focused Windows and
Linux source fixtures passed; only two affected allowlist/plan cases are resumed
after this source-retention change. No actual tool installation or child update.

# WORKSPACE-01-RECOVERABLE-BOOTSTRAP-R1

Registered2026-10-17 by explicit user request. Track a minimal parent workspace,
market-integration as a submodule at last published8b13352f, portable tool/setup
sources and source-only tests. Existing child development HEAD and .git stay
unchanged. Existing local tool installation, venv, caches, artifacts, private
inputs, credentials and worktrees stay intact and ignored. No actual tool
installation, child update, qualification, master promotion or remote push.
Parent remote URL remains separately selected by the user.
