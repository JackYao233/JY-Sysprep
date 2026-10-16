# JY Sysprep Alpha 0.4

Alpha 0.4 brings back the graphical wizard while keeping the TUI, adds a portable Vista runtime, and improves the Windows 11 multiboot deployment workflow.

## Highlights

- Six-step GUI with F8 switching to the TUI.
- One x64 package with separate runtimes for Windows Vista SP2 and Windows 7–11. No Python installation is required.
- Windows 11 multiboot deployment runs through an elevated, windowless helper process.
- BCD backup and verification before completing the selected shutdown or restart action.
- Durable execution records, interrupted-run notifications, and bundled diagnostics.

## Validation

The user reported successful VM regression testing for Windows Vista SP2, 7, 8, 8.1, 10, and 11 within the tested configurations. Windows 11 testing included automatic restart, OOBE, and reaching the desktop; shutdown and OOBE were subsequently confirmed with the unified package.

This is an alpha release. These results do not cover every Windows build or configuration. Vista deployment is limited to single-system x64 installations. Windows Server, x86, and ARM64 are outside this release's validation scope.

## Getting started

Download `JY Sysprep Alpha 0.4 x64.zip`, extract the entire archive, and run `Start.cmd` as administrator. Use `Start GUI.cmd` or `Start TUI.cmd` to choose an interface directly.

Keep both modern executables together. The original candidate labels remain visible because this package preserves the tested binaries without recompilation. The existing root-level single EXE from build 3 is an older artifact; use the ZIP package for this release.
