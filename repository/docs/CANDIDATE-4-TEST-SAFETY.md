# Candidate 4: test incident and execution hold

Status: runtime validation remains on hold on the developer host. The user
subsequently explicitly requested a packaged executable, authorizing a build
and delivery for their isolated VM. This does not authorize running the test
suite, generated executable, or background probes on the host.

During development, two test-suite runs caused the developer host to restart.
The worker success test selected reboot and attempted to mock an executor
module obtained through a package attribute. The worker dynamically imported
the power function later. Tests elsewhere restore `sys.modules`, which can
leave package attributes referring to an older module instance. Consequently,
that mock is not a reliable boundary against the real power command. The exact
runtime module identities at the incident were not captured.

## Static correction

- `worker_main` requires an explicit keyword-only `power_action` callable.
- It has no default and does not dynamically import a real power function.
- The production CLI supplies its power callback explicitly.
- The worker test supplies a local Mock directly; it does not import or patch
  the executor power function.
- Missing or non-callable power capabilities fail before worker initialization.

These changes close the identified power-mock gap, but do not constitute
complete test isolation. Other worker operations (task commands, deployment,
identity and mutex checks) still depend on test substitutes. Production
Sysprep and power operations remain available elsewhere in the application.

## Execution hold

Do not run the test suite, worker probes, or candidate executables on the
developer host while this hold is in effect. Build-only execution was later
authorized explicitly. Existing candidate packages are preserved.

Before any execution resumes, explain the isolation to the user and obtain
explicit approval. Use a disposable guest VM with a recoverable snapshot,
without writable host shares or mounted host disks. Unit checks should run
without administrator privileges; actual SYSTEM-task and deployment checks
belong in that disposable guest only. Mocking alone is insufficient protection.

Windows 11 investigation remains unresolved: the diagnostic record stopped at
`sysprep_running`, while Sysprep subsequently recorded success. The independent
worker is an unverified proposed mitigation, not a confirmed fix.
