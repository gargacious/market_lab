## WORKSPACE-01-RECOVERABLE-BOOTSTRAP-R1 - explicit development backup selection

Add optional exact selected_commit and published/development_backup kind, with
legacy published defaults. Published baseline remains independently identified;
offline checks compare the selected parent index and never verify remotes or
move a child checkout. The existing dirty-child fixture covers distinct selected
development/published/master identities, parent-index mismatch and invalid claim
denials while preserving the child .git, HEAD and uncommitted bytes.
This change leaves the actual lock and parent gitlink unchanged. The parent
will select backed-up development only after separate remote verification.
The affected dirty-child fixture passes on Windows with D-local scratch and on
Linux with isolated workspace fixtures. Source-only sync preserved the actual
child HEAD/.git inode, lock bytes and parent indexed gitlink. No tool install,
qualification, child movement or new remote-backup claim.

## WORKSPACE-01-RECOVERABLE-BOOTSTRAP-R1 - bounded source bootstrap complete

Linux outer workspace is initialized with exactly14 reviewed source/gitlink
entries. Last-published integration8b13352f remains the indexed pointer while
the existing development child and its original .git directory remain intact.
Original Icarus install.py/README.txt match source-controlled bytes without
rewriting their Linux inode or mtime. Source/tool caches, binaries, Conan venv
and versioned home, artifacts, tmp, worktrees and credentials remain ignored.

Eight original Windows/Linux fixture methods passed. Two changed legacy
allowlist/plan cases passed on Windows and Linux. New empty-child inheritance
denial passes on both; actual four-path symlink escape denial passes on Linux
and is skipped on Windows without native link privileges. Conan cache path is
selected from actual directory metadata as tooling/conan-home-2.31.2; profiles
and credentials were not opened. Only affected plan fixtures are repeated for
that path correction. No actual tool installs, child updates, retained evidence,
qualification or remote publication. Origin is configured as git@bitbucket.org:gargacious/market_lab.git; remote
access is confirmed. Initial committed bootstrap feature4047db63 was published;
ignored/uncommitted work and later development backup remain separately pending.

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
The user selected git@bitbucket.org:gargacious/market_lab.git; origin is
configured and read access is confirmed. Initial bootstrap feature4047db63 is
published. The earlier hyphen-named URL was incorrect. No recovery or backup of
ignored/uncommitted work or later unpublished development is claimed.
