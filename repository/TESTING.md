# Alpha 0.5 test execution boundaries

This project can execute real Sysprep, BCD edits and shutdown/restart commands.
Earlier mocked tests restarted the development host twice; see
[the incident record](docs/CANDIDATE-4-TEST-SAFETY.md).

Do not run the full test suite, generated EXEs, deployment workers or privileged
flow probes on an everyday host. Use a disposable isolated VM with recoverable
snapshots and no writable host shares or mounted host disks. Mocking alone is
not an execution boundary. Do not add test discovery or application execution
to automatic host setup or CI without reviewing these constraints.

Building an EXE is distinct from running it. `tools/verify_single_exe_static.py`
parses source and reads embedded archive contents, hashes and PE headers only;
it does not import application workflows or launch the EXE.

In an isolated test VM, `--runtime-self-test` checks diagnostic GUI/runtime data
and a read-only system command. `--admin-worker-self-test` stages a probe under
the current elevated administrator, without Sysprep, BCD operations or power
actions. Both still launch real application processes and belong in the VM.

The default wizard test mode writes an answer file without executing Sysprep.
Formal deployment must be checked from a pre-deployment snapshot, including
the selected power action, OOBE and reaching the desktop.

On 2026-10-19 the maintainer reported the agreed cross-version Candidate 3
regression scope passed. This is not certification for every Windows build,
server role, account option or configuration. Logs were not independently
reviewed for each successful run. See docs/ALPHA-0.5-SINGLE-EXE.md.
