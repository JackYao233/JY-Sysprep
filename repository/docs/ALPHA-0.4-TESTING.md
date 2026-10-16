# Test execution boundaries

The project has real Sysprep, BCD and shutdown/restart capabilities. Two earlier
unit-test runs restarted the developer host because a mocked import did not
reliably intercept the real power function. The detailed record is in
`docs/CANDIDATE-4-TEST-SAFETY.md`.

Do not run the full test suite, candidate executables, deployment workers,
or privileged flow probes on an everyday host. Use a disposable VM with a
recoverable snapshot, no writable host shares and no mounted host disks.
Mocking by itself is not an execution boundary. Test discovery must not be
added to automatic host-side setup or CI without reviewing these constraints.

Current source uses explicit power callbacks for workers. That closes the
identified mock gap but does not make every test safe. Existing runtime-test
sources are preserved for review; the latest build did not run the full suite.

`tools/check_unified_static.py` reads ZIP contents and hashes only. It does not
launch the application. Its historical candidate inputs must be present to use
it. Building EXEs is distinct from running them.

Formal VM validation for Alpha 0.4 was reported by the user. Reports do not
cover all Windows builds, account options or deployment configurations.
