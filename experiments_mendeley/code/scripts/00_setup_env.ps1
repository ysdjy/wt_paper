<#
.SYNOPSIS
  One-shot bootstrap: verify the dcpsr conda env, install dependencies from the
  official PyPI, install a GPU build of PyTorch, write the environment report,
  then run selftest -> HDF5 audit -> feature extraction -> sanity check.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File scripts\00_setup_env.ps1 `
      -RawDir "C:\Users\banghai\Documents\BaiduSyncdisk\西工大\王婷\论文\Multivariate time series data of milling processes with varying tool wear and machine tools"

  Add -SkipFeatures to re-run only the sanity check after features already exist.
  Add -AuditOnly    to stop after the HDF5 schema audit.
#>
param(
  [Parameter(Mandatory = $true)][string]$RawDir,
  [string]$EnvName = "dcpsr",
  [string]$OutRoot = "experiments_mendeley",
  [switch]$AuditOnly,
  [switch]$SkipInstall,
  [switch]$SkipFeatures
)

$ErrorActionPreference = "Continue"
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
New-Item -ItemType Directory -Force -Path $OutRoot, "$OutRoot\10_logs" | Out-Null
$log = "$OutRoot\10_logs\setup_$(Get-Date -Format yyyyMMdd_HHmmss).log"
function Say($m) { Write-Host $m; Add-Content -Path $log -Value $m }
function Run($cmd) { Say "`n>>> $cmd"; $o = Invoke-Expression $cmd 2>&1 | Out-String; Say $o; return $o }

Say "=============================================================="
Say " DC-PSR bootstrap   $(Get-Date -Format s)"
Say " repo   : $root"
Say " raw    : $RawDir"
Say " env    : $EnvName"
Say "=============================================================="

# ---------------------------------------------------------------- 1. conda
$py = Run "conda run -n $EnvName python --version"
if ($py -notmatch "3\.11") {
  Say "!! Python in '$EnvName' is not 3.11. Stopping."
  Say "   create it with:  conda create -n $EnvName python=3.11 -y"
  exit 1
}
Run "conda run -n $EnvName python -m pip --version" | Out-Null

# ------------------------------------------------------------ 2. pip config
$cfg = Run "conda run -n $EnvName python -m pip config list"
if ($cfg -match "tsinghua|aliyun|ustc|douban|mirrors\.") {
  Say "!! A mainland-China mirror is configured. Every install below pins"
  Say "   -i https://pypi.org/simple explicitly, so the mirror is bypassed."
  Say "   To clear it permanently:  conda run -n $EnvName python -m pip config unset global.index-url"
}

# --------------------------------------------------------------- 3. GPU
$smi = Run "nvidia-smi"
$driver = if ($smi -match "Driver Version:\s*([\d.]+)") { $Matches[1] } else { $null }
$cuda   = if ($smi -match "CUDA Version:\s*([\d.]+)")   { $Matches[1] } else { $null }
$gpu    = if ($smi -match "\|\s+\d+\s+(NVIDIA[^|]+?)\s{2,}") { $Matches[1].Trim() } else { $null }
Say "`nGPU        : $gpu"
Say "Driver     : $driver"
Say "CUDA (smi) : $cuda"

$chan = "cpu"
if ($cuda) {
  $c = [double]($cuda -replace '^(\d+\.\d+).*$', '$1')
  if     ($c -ge 12.8) { $chan = "cu128" }
  elseif ($c -ge 12.6) { $chan = "cu126" }
  elseif ($c -ge 12.4) { $chan = "cu124" }
  elseif ($c -ge 12.1) { $chan = "cu121" }
  elseif ($c -ge 11.8) { $chan = "cu118" }
}
Say "torch wheel channel selected: $chan"
if ($chan -eq "cpu") {
  Say "!! No usable NVIDIA CUDA runtime detected. The sanity check can run on CPU,"
  Say "   but do NOT start the 5-seed protocol on CPU. Report this instead."
}

# ------------------------------------------------------------ 4. install
if (-not $SkipInstall) {
  $pkgs = "numpy pandas scipy scikit-learn matplotlib h5py pyarrow xgboost joblib tqdm"
  Run "conda run -n $EnvName python -m pip install --upgrade pip -i https://pypi.org/simple" | Out-Null
  $o = Run "conda run -n $EnvName python -m pip install -i https://pypi.org/simple $pkgs"
  if ($o -match "ERROR:") { Say "!! base package install reported errors -- see above" }

  $tried = @()
  foreach ($ch in @($chan, "cu126", "cu124", "cu121", "cu118") | Select-Object -Unique) {
    if ($ch -eq "cpu") { break }
    if ($tried -contains $ch) { continue }
    $tried += $ch
    Say "`n--- installing torch ($ch) ---"
    Run "conda run -n $EnvName python -m pip install torch --index-url https://download.pytorch.org/whl/$ch" | Out-Null
    $chk = Run "conda run -n $EnvName python -c `"import torch;print(torch.cuda.is_available())`""
    if ($chk -match "True") { Say "torch GPU build OK ($ch)"; break }
    Say "!! $ch did not yield a working CUDA build, trying the next channel"
  }
  if ($chan -eq "cpu") {
    Run "conda run -n $EnvName python -m pip install torch --index-url https://download.pytorch.org/whl/cpu" | Out-Null
  }
}

# ------------------------------------------------------------ 5. verify
$verify = @'
import json, platform, sys
mods = {}
for m in ("numpy","pandas","scipy","sklearn","h5py","pyarrow","xgboost","matplotlib","joblib","tqdm"):
    try:
        mods[m] = __import__(m).__version__
    except Exception as e:
        mods[m] = f"MISSING ({type(e).__name__})"
import torch
print(json.dumps(dict(python=platform.python_version(), platform=platform.platform(),
    torch=torch.__version__, torch_cuda_build=torch.version.cuda,
    cuda_available=torch.cuda.is_available(),
    gpu=torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
    modules=mods), indent=2))
'@
$verify | Out-File -FilePath "$env:TEMP\dcpsr_verify.py" -Encoding utf8
$env_json = Run "conda run -n $EnvName python `"$env:TEMP\dcpsr_verify.py`""

@"
DC-PSR environment report
generated : $(Get-Date -Format s)
host OS   : $((Get-CimInstance Win32_OperatingSystem).Caption) $((Get-CimInstance Win32_OperatingSystem).Version)
conda env : $EnvName
GPU       : $gpu
driver    : $driver
CUDA(smi) : $cuda
wheel ch. : $chan

$env_json
"@ | Out-File -FilePath "$OutRoot\environment_report.txt" -Encoding utf8
Run "conda run -n $EnvName python -m pip freeze" | Out-File -FilePath "$OutRoot\requirements_snapshot.txt" -Encoding utf8
Say "`nwrote $OutRoot\environment_report.txt and $OutRoot\requirements_snapshot.txt"

if ($env_json -notmatch '"cuda_available": true') {
  Say "`n!! torch.cuda.is_available() is False."
  Say "   The sanity check will still run (on CPU) so the pipeline can be validated,"
  Say "   but the 5-seed protocol must not be started until this is True."
}

# ------------------------------------------------------------ 6. selftest
Say "`n=== selftest ==="
$o = Run "conda run -n $EnvName python scripts\selftest.py"
if ($o -notmatch "6/6 checks passed") { Say "!! selftest did not report 6/6 -- stopping."; exit 1 }

# ------------------------------------------------------- 7. HDF5 audit
Say "`n=== HDF5 schema audit ==="
Run "conda run -n $EnvName python scripts\00_extract_features.py --raw-dir `"$RawDir`" --out-root $OutRoot --audit-only" | Out-Null
if ($AuditOnly) { Say "`n-AuditOnly set. Review $OutRoot\00_dataset_audit\ then re-run without it."; exit 0 }

# ------------------------------------------------ 8. feature extraction
if (-not $SkipFeatures) {
  Say "`n=== run-level feature extraction (resumable, sharded by tool) ==="
  Run "conda run -n $EnvName python scripts\00_extract_features.py --raw-dir `"$RawDir`" --out-root $OutRoot" | Out-Null
}

# ------------------------------------------------------- 9. sanity check
Say "`n=== sanity check: D1-M (M1+M2 -> M3), seed 42 ==="
$o = Run "conda run -n $EnvName python scripts\03_sanity_check.py --out-root $OutRoot"
if ($o -match "10/10 criteria passed") {
  Say "`nSANITY CHECK PASSED. Send back:"
  Say "   $OutRoot\environment_report.txt"
  Say "   $OutRoot\00_dataset_audit\channel_summary.csv"
  Say "   $OutRoot\00_dataset_audit\excluded_channel_report.csv"
  Say "   $OutRoot\03_sanity_check\sanity_report.json"
  Say "   $log"
  exit 0
}
Say "`nSANITY CHECK DID NOT PASS -- do not start the full protocol. Log: $log"
exit 1
