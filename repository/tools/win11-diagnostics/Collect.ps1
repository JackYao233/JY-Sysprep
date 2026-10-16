# Read-only system diagnostics; writes reports/copies only to a new Desktop folder.
$ErrorActionPreference = 'Continue'
$desktopPath = [Environment]::GetFolderPath('Desktop')
$reportPath = Join-Path $desktopPath ('JY-Win11-Diagnostics-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + [guid]::NewGuid().ToString('N').Substring(0,6))
New-Item -ItemType Directory -Path $reportPath -ErrorAction Stop | Out-Null

function Save-Report($name, [scriptblock]$readAction) {
    try { & $readAction 2>&1 | Out-String -Width 300 | Out-File -LiteralPath (Join-Path $reportPath $name) -Encoding utf8 }
    catch { $_ | Out-String | Out-File -LiteralPath (Join-Path $reportPath $name) -Encoding utf8 }
}

Save-Report 'identity.txt' {
    Get-Date -Format o
    [TimeZoneInfo]::Local.Id
    [Security.Principal.WindowsIdentity]::GetCurrent().Name
    [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
    'USERPROFILE=' + $env:USERPROFILE
    'COMPUTERNAME=' + $env:COMPUTERNAME
    Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion' |
        Select-Object ProductName,DisplayVersion,CurrentBuild,UBR,InstallationType
}
Save-Report 'profiles.txt' {
    Get-CimInstance Win32_UserProfile | Select-Object SID,LocalPath,Loaded,Special,Status,LastUseTime | Format-List
    Get-ChildItem 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList' |
        ForEach-Object { Get-ItemProperty -LiteralPath $_.PSPath } |
        Select-Object PSChildName,ProfileImagePath,State,RefCount | Format-List
}
Save-Report 'setup-state.txt' {
    Get-ItemProperty 'HKLM:\SYSTEM\Setup' | Select-Object SystemSetupInProgress,OOBEInProgress,SetupType,CmdLine | Format-List
    Get-ItemProperty 'HKLM:\SYSTEM\Setup\Status\SysprepStatus' | Format-List
    Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Setup\State' | Format-List
    Get-Item -LiteralPath (Join-Path $env:SystemRoot 'System32\Sysprep\Sysprep_succeeded.tag') | Select-Object FullName,Length,LastWriteTimeUtc
    Get-Process sysprep -ErrorAction SilentlyContinue | Select-Object Id,StartTime,CPU
}
Save-Report 'bcd-current.txt' { & "$env:SystemRoot\System32\bcdedit.exe" /enum '{current}' /v; 'ExitCode=' + $LASTEXITCODE }
Save-Report 'execution-processes.txt' {
    Get-Date -Format o
    Get-CimInstance Win32_Process |
        Where-Object { $_.Name -in @('worker.exe','sysprep.exe','JY Sysprep Modern.exe','WerFault.exe') } |
        Select-Object Name,ProcessId,ParentProcessId,SessionId,CreationDate,ExecutablePath | Format-List
}
Save-Report 'bcd-loaders.txt' { & "$env:SystemRoot\System32\bcdedit.exe" /enum osloader /v; 'ExitCode=' + $LASTEXITCODE }
Save-Report 'recent-events.txt' {
    foreach ($logName in @('Application','System','Microsoft-Windows-User Profile Service/Operational')) {
        'LOG: ' + $logName
        Get-WinEvent -LogName $logName -MaxEvents 150 -ErrorAction Continue |
            Select-Object TimeCreated,Id,LevelDisplayName,ProviderName,Message | Format-List
    }
}

# Formatted Message may be empty after generalization. Preserve raw EventData
# independently of message-resource availability; these reads do not enable logs.
foreach ($jyEventLog in @('Application','System',
        'Microsoft-Windows-AppXDeploymentServer/Operational',
        'Microsoft-Windows-AppModel-Runtime/Admin',
        'Microsoft-Windows-Windows Defender/Operational',
        'Microsoft-Windows-CodeIntegrity/Operational')) {
    $jySafeName = $jyEventLog.Replace('/','-')
    Save-Report ('raw-events-' + $jySafeName + '.xml') {
        '<Events>'
        try {
            Get-WinEvent -FilterHashtable @{LogName=$jyEventLog;StartTime=(Get-Date).AddHours(-2)} -MaxEvents 400 -ErrorAction Stop |
                ForEach-Object { $_.ToXml() }
        } catch {
            '<!-- Log unavailable or no events: ' + [Security.SecurityElement]::Escape($_.Exception.Message) + ' -->'
        }
        '</Events>'
    }
}

$profileRegistry = Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList'
$profilesRoot = [Environment]::ExpandEnvironmentVariables($profileRegistry.ProfilesDirectory)
$profileFolders = Get-ChildItem -LiteralPath $profilesRoot -Directory -Force -ErrorAction SilentlyContinue
$logIndex = 0
foreach ($profileFolder in $profileFolders) {
    $appLogs = Join-Path $profileFolder.FullName 'Desktop\JY Sysprep Logs'
    if (Test-Path -LiteralPath $appLogs) {
        $logIndex++
        $target = Join-Path $reportPath ('AppLogs-' + $logIndex)
        New-Item -ItemType Directory -Path $target | Out-Null
        $appLogs | Out-File -LiteralPath (Join-Path $target 'source.txt') -Encoding utf8
        Get-ChildItem -LiteralPath $appLogs -Filter '*.log' -File | Sort-Object LastWriteTime -Descending | Select-Object -First 5 |
            Copy-Item -Destination $target -ErrorAction Continue
    }
}
foreach ($relative in @('System32\Sysprep\Panther','Panther','Panther\UnattendGC')) {
    $source = Join-Path $env:SystemRoot $relative
    $target = Join-Path $reportPath ($relative.Replace('\','-'))
    New-Item -ItemType Directory -Path $target | Out-Null
    foreach ($fileName in @('setupact.log','setuperr.log')) {
        $filePath = Join-Path $source $fileName
        if (Test-Path -LiteralPath $filePath) { Copy-Item -LiteralPath $filePath -Destination $target -ErrorAction Continue }
    }
}
$backupRoot = Join-Path $env:ProgramData 'JY Sysprep\BootBackups'
Get-ChildItem -LiteralPath $backupRoot -Directory -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 3 | ForEach-Object {
    $target = Join-Path $reportPath ('Boot-' + $_.Name)
    New-Item -ItemType Directory -Path $target | Out-Null
    Get-ChildItem -LiteralPath $_.FullName -File | Where-Object { $_.Extension -in '.txt','.json' } |
        Copy-Item -Destination $target -ErrorAction Continue
}
$executionRoot = Join-Path $env:ProgramData 'JY Sysprep\ExecutionRecords'
Get-ChildItem -LiteralPath $executionRoot -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    $recordFile = Join-Path $_.FullName 'execution.json'
    if (Test-Path -LiteralPath $recordFile) {
        Copy-Item -LiteralPath $recordFile -Destination (Join-Path $reportPath ('Execution-' + $_.Name + '.json')) -ErrorAction Continue
    }
}
Get-ChildItem -LiteralPath $env:ProgramData -Filter 'JY-Sysprep-Job-*' -Directory -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending | Select-Object -First 5 | ForEach-Object {
        $target = Join-Path $reportPath $_.Name
        New-Item -ItemType Directory -Path $target | Out-Null
        foreach ($name in @('status.json','worker.log','bootstrap.log','launch.json')) {
            $file = Join-Path $_.FullName $name
            if (Test-Path -LiteralPath $file) { Copy-Item -LiteralPath $file -Destination $target -ErrorAction Continue }
        }
        Get-ChildItem -LiteralPath (Join-Path $_.FullName 'ExecutionRecords') -Filter 'execution.json' -Recurse -File -ErrorAction SilentlyContinue |
            ForEach-Object { Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $target ('Execution-' + $_.Directory.Name + '.json')) }
        Get-ChildItem -LiteralPath (Join-Path $_.FullName 'BootBackups') -Recurse -File -ErrorAction SilentlyContinue |
            Where-Object { $_.Extension -in '.txt','.json' } | ForEach-Object {
                Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $target ('Boot-' + $_.Name)) -ErrorAction Continue
            }
    }
Compress-Archive -LiteralPath $reportPath -DestinationPath ($reportPath + '.zip') -ErrorAction Continue
Write-Host ('Reports: ' + $reportPath)
Write-Host ('Archive: ' + $reportPath + '.zip')
Write-Host 'No Sysprep, shutdown, profile deletion or BCD modification was performed.'
