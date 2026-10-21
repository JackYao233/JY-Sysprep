# JY Sysprep Alpha 0.5

Alpha 0.5 adds Windows Server support and delivers the application as a single x64 executable.

- Supports the tested x64 client scope from Windows Vista SP2 through Windows 11, and Server 2008 SP2, 2008 R2, 2012, 2012 R2, 2016, 2019, 2022 and 2025.
- Retains the six-step GUI and F8 switching to TUI.
- Bundles Python, GUI libraries and the independent windowless deployment helper; no Python installation or manual extraction is required.
- Reduces the download from the previous 50.7 MB unified candidate ZIP to approximately **16.2 MB**, about **68% smaller**.
- Fixes Python 3.6 standard-handle handling in the elevated worker workflow. Windows 11 deployment and the remaining agreed cross-version VM regression scope were reported successful.

Run `JY Sysprep Alpha 0.5 x64.exe` as administrator in Windows Audit Mode. Start with the default test mode to review the answer file before performing formal deployment.

The release EXE is byte-for-byte identical to the tested single-EXE Candidate 3. The original candidate label remains in the interface. Embedded resources are automatically extracted at startup, and the deployment helper runs as a separate process when required.

**Validation limits:** Results are based on maintainer VM feedback for the tested configurations. Vista formal deployment is single-system only. Server Core, domain environments, configured server roles, x86 and ARM64 have not been validated. Other Windows builds and option combinations may behave differently.

**SHA256**

```text
D23689BD766B09EC5C32F2D746F7742085EB64DCE2D1FD6AD1015DB39CC61ACF
```

Download the EXE and its `.sha256` file. This is an **Alpha prerelease**.
