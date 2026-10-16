# Market Lab workspace

This parent versions workspace setup and the last published market-integration
submodule selection. Integration owns its own45 component submodules, product
plans and qualification. Existing development checkouts can deliberately be
ahead of this published selection; status reports that difference without
changing them.

For a NEW checkout only, after the user supplies this parent's remote URL:

    git clone --recurse-submodules <workspace-remote> market_lab
    cd market_lab
    python3 -B tooling/bootstrap.py status
    python3 -B tooling/bootstrap.py check
    python3 -B tooling/bootstrap.py plan --tool conan
    python3 -B tooling/bootstrap.py plan --tool iverilog

Do not run submodule update in an existing development workspace merely to
satisfy this older published pointer. Inspect status and preserve work first.
The parent never moves or absorbs the child's existing .git directory.

Setup is explicit: install --tool conan --execute creates the pinned isolated
Conan environment; install --tool iverilog --execute builds the exact official
Icarus13 source on supported Debian/Ubuntu Linux without sudo. These commands
are not run by status/check/plan. Existing tools/iverilog-13.0/install.py and its
installation remain local historical material; tools/iverilog/bootstrap.py is
the new relocatable source-controlled installer. Generated tools, source clones,
apt archives, venvs, Conan home/cache, artifacts, tmp and worktrees are ignored.
No credentials or profiles are embedded or copied.

Recovery limits: this Git repo protects only committed parent source and a
published integration pointer. Push this parent and all intended child commits
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
these fixtures. The workspace remote is intentionally unset until supplied.
