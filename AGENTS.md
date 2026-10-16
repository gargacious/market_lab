# Workspace bootstrap ownership

This parent owns portable workspace setup, tool source locks and recovery/status
documentation. Product source and qualification belong to market-integration
and its independently versioned component repositories.
Read TASKS.md. Use exact WORKSPACE task IDs in concise commits and codex branches.
Never change child checkout/branches/pins, absorb/move its .git or run submodule
update automatically. Source generation and temporary artifacts stay on D: on
Windows, never C:. Keep private inputs, credentials, profiles, caches, venvs,
binaries, logs, artifacts and worktrees out of this explicit source allowlist.
Plans/status/checks do not install tools. Actual installs, retained qualification,
master promotion and publication require their explicit user request.
Do not claim unpublished, uncommitted or ignored work is backed up by this Git
repository. Preserve it separately; never delete it as part of bootstrapping.
