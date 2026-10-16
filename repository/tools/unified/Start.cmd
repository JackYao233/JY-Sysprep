@echo off
setlocal
set "jy_runtime="
if /i "%PROCESSOR_ARCHITECTURE%"=="AMD64" goto architecture_ok
if /i "%PROCESSOR_ARCHITEW6432%"=="AMD64" goto architecture_ok
echo This package requires x64 Windows on an AMD64-compatible processor.
exit /b 2
:architecture_ok
ver | "%SystemRoot%\System32\findstr.exe" /r /c:" 6\.0\." >nul
if not errorlevel 1 set "jy_runtime=vista"
if defined jy_runtime goto selected
ver | "%SystemRoot%\System32\findstr.exe" /r /c:" 6\.[123]\." /c:" 10\.0\." >nul
if not errorlevel 1 set "jy_runtime=modern"
if not defined jy_runtime (
  echo Unsupported Windows version. This candidate targets Vista SP2 through Windows 11 x64.
  exit /b 2
)
:selected
set "jy_exe=JY Sysprep.exe"
if /i "%jy_runtime%"=="vista" set "jy_exe=JY Sysprep Vista.exe"
if not exist "%~dp0runtimes\%jy_runtime%\%jy_exe%" (
  echo Missing runtime. Extract the entire ZIP before starting.
  exit /b 3
)
if /i "%jy_runtime%"=="modern" if not exist "%~dp0runtimes\modern\JY Sysprep Worker.exe" (
  echo Missing background worker. Extract the entire ZIP before starting.
  exit /b 3
)
if /i "%~1"=="--route-only" (
  echo %jy_runtime%
  exit /b 0
)
"%~dp0runtimes\%jy_runtime%\%jy_exe%" %*
set "jy_exit_code=%errorlevel%"
if /i "%jy_runtime%"=="modern" if /i not "%~1"=="--help" if /i not "%~1"=="--runtime-self-test" "%~dp0runtimes\%jy_runtime%\%jy_exe%" --check-last-run
exit /b %jy_exit_code%
