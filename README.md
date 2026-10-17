# Market Lab workspace

This parent versions workspace setup and an explicit market-integration
submodule selection, preserving its separate last-published baseline. Integration owns its own45 component submodules, product
plans and qualification. Existing development checkouts can deliberately be
ahead of this published selection; status reports that difference without
changing them.

Origin is git@bitbucket.org:gargacious/market_lab.git; the GitHub mirror remote
is named `github`. This checkout combines the Linux bootstrap source with the
Mac workspace editor settings, legacy `repos.txt` inventory and Games recovery
location note. The original `~/market_lab_old` directory is unchanged.

The integration selection is its cleaned, published master `77dad77f`. Earlier
pre-cleanup commit IDs and workspace-backup branch notes below are historical.
This parent does not establish a new qualification of integration or its leaves.

Three independently versioned child repositories are registered:

| Path | Repository | Selected commit |
| --- | --- | --- |
| `market-integration` | [Bitbucket](https://bitbucket.org/gargacious/market-integration/src/master/) / [GitHub](https://github.com/gargacious/market-integration/tree/master) | `77dad77f` |
| `protocol_lab` | [Bitbucket](https://bitbucket.org/gargacious/protocol_lab/src/master/) / [GitHub](https://github.com/gargacious/protocol_lab/tree/master) | `45c6f10` |
| `market_games` | [Bitbucket](https://bitbucket.org/gargacious/market_lab_games/src/master/) / [GitHub](https://github.com/gargacious/market_lab_games/tree/master) | `4e5fef5` |

All `.gitmodules` URLs are relative, so clones use the same host as the parent.
Bitbucket may show relative submodules as plain text in its source browser; use
the explicit repository links above. This is a web-view limitation, not a clone
failure. See https://jira.atlassian.com/browse/BCLOUD-12521.

Children are intentionally not initialized by this consolidation. In a NEW
checkout, initialize only the child you need; recursive integration checkout
also downloads its independently pinned components:

```sh
git submodule update --init --recursive -- market-integration
# Later, when resuming these separate projects:
git submodule update --init -- protocol_lab market_games
```

The parent records exact commits. Fetching newer child master commits is a
separate reviewed update to its gitlink, not an automatic consequence of pulling
this parent. No standalone FPGA checkout belongs here; it is already owned by
market-integration's submodule graph.

The preserved VS Code C++ profile is Mac-specific and optional; Linux tooling
continues to use the existing bootstrap/tool locks. `repos.txt` is a historical
Mac inventory, not an authoritative replacement for `.gitmodules` or integration's
component lock. Plans/status/checks install no tools and move no child checkouts.

Local recovery archives are deliberately NOT committed:
- Games: `~/project-backups/market_games/local-recovery`; see its sibling
  `RESUME.txt` before restoring into the original `~/market_lab/market_games`.
- Retired fin_tech Git history: verified copy at
  `~/project-backups/market_lab/fin_tech-retired-all-refs-2026-10-14.bundle`.

The latter is not a Games recovery archive. Neither archive is protected by
pushing this parent. Do not put bundles, builds, caches or private inputs in Git.

Do not run submodule update in an existing development workspace merely to
satisfy an indexed snapshot pointer. Inspect status and preserve work first.
The parent never moves or absorbs the child's existing .git directory.

Setup is explicit: install --tool conan --execute creates the pinned isolated
Conan environment; install --tool iverilog --execute builds the exact official
Icarus13 source on supported Debian/Ubuntu Linux without sudo. These commands
are not run by status/check/plan. Exact original tools/iverilog-13.0/install.py and README.txt are retained as
source-controlled historical references, including the old host-specific path.
The existing installation stays local; tools/iverilog/bootstrap.py is the
recommended relocatable source-controlled installer. Generated tools, source clones,
apt archives, venvs, Conan home/cache, artifacts, tmp and worktrees are ignored.
No credentials or profiles are embedded or copied.

Recovery limits: this Git repo protects only committed parent source and a
selected integration pointer. Push this parent and all intended child commits
to real remotes for disk-loss recovery. Unpublished branches, uncommitted work,
ignored evidence/required inputs, credentials/keys/certificates/profiles and
working environments need separately approved secure backups. A Git submodule
pointer does not publish the referenced child commit. Never infer that ignored
files can be deleted. Tool caches/binaries can be rebuilt; Icarus source and
Conan version are pinned, while distro build dependencies and transitive Python
wheel hashes are not yet hermetically locked. Native platform/toolchain and
retained Linux evidence still require their own checks.

Run focused source fixtures with a scratch directory on the same intended
workspace drive (D: on Windows):

    python3 -B tooling/tests/bootstrap_tests.py --scratch <workspace-scratch>

No build, retained evidence, publication or actual tool installation is part of
these fixtures. Configuring origin does not publish or back up any source.
Initial committed bootstrap source was published at4047db63; ignored work,
uncommitted source and unpublished child commits retain the separate backup
limits above. The offline status/check commands do not verify remote contents.


Status/check inspect source selection and path availability only; selected tool
versions are lock declarations, not a fresh binary or platform qualification.
For Linux shells after an explicit successful setup, select the existing
versioned Conan home and local tools without copying private profiles:

    export CONAN_HOME="$PWD/tooling/conan-home-2.31.2"
    export PATH="$PWD/tooling/conan-2.31.2/bin:$PWD/tools/iverilog-13.0/installed/bin:$PATH"

The Conan cache/profile directory remains private and ignored. On Windows,
the isolated Conan executable directory is tooling/conan-2.31.2/Scripts.


Conan plan output includes only its selected workspace environment, without
exposing inherited variables. Explicit install passes PIP_CACHE_DIR under
tooling/pip-cache, CONAN_HOME at tooling/conan-home-2.31.2 and all of TEMP/TMP/
TMPDIR under tmp/tool-bootstrap to both venv/pip subprocesses. These directories
are created only with --execute. Planning creates none. This keeps future
Windows project downloads and temporary build material on the workspace drive.


The integration lock accepts optional selected_commit and selection_kind fields.
Legacy locks default to published_commit and kind published. A published
selection must equal that baseline. Kind development_backup requires an explicit
exact selected_commit; it does not relabel published_commit, master or Linux
qualification. Check compares the parent indexed gitlink with selected_commit.
Status shows both identities, kind and actual child HEAD without moving anything.

The parent maintainer must independently verify the intended development commit
and its provider commits are backed up before recording that gitlink/selection.
The offline CLI never asserts remote publication or backup from this declaration.
Changing these fields does not move an existing checkout or recover ignored,
dirty or unpublished work. Current lock fields are unchanged by this feature.
