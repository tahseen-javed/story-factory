# fetch_videos.ps1 - pulls finished, age-encrypted video bundles from this repo's GitHub Releases into
# <Documents>\Animated Long Video 1st Channel. Needs only: age.exe + backup.key in %USERPROFILE%\.story-factory (outside the repo).
# One output line per delivered video. No installs, nothing heavy.
param(
  [string]$Repo = "tahseen-javed/story-factory",
  [double]$MinFreeGB = 15,   # mirrors delivery.min_free_gb in config/factory.yaml
  [switch]$All
)
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$sf     = Join-Path $env:USERPROFILE ".story-factory"
$age    = Join-Path $sf "age.exe"
$key    = Join-Path $sf "backup.key"
$ledger = Join-Path $sf "delivered.json"
$dest   = Join-Path ([Environment]::GetFolderPath('MyDocuments')) "Animated Long Video 1st Channel"

if (-not (Test-Path $age)) { Write-Output "STOP: age.exe missing in $sf (see docs/SETUP_LOCAL.md)"; exit 1 }
if (-not (Test-Path $key)) { Write-Output "STOP: backup.key missing in $sf (see docs/SETUP_SECRETS.md)"; exit 1 }
New-Item -ItemType Directory -Force -Path $dest | Out-Null

$done = @{}
if (Test-Path $ledger) { try { (Get-Content $ledger -Raw | ConvertFrom-Json).PSObject.Properties | ForEach-Object { $done[$_.Name] = $_.Value } } catch {} }

$hdr = @{ "User-Agent" = "story-factory-fetch"; "Accept" = "application/vnd.github+json" }
$rels = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/releases?per_page=100" -Headers $hdr
$todo = @($rels | Where-Object { $_.tag_name -match '^video-(\d{3})$' } | Sort-Object tag_name)
if (-not $All) { $todo = @($todo | Where-Object { -not $done.ContainsKey($_.tag_name) }) }
if ($todo.Count -eq 0) { Write-Output "Nothing new to fetch."; exit 0 }

$drive = (Get-Item $dest).PSDrive
foreach ($rel in $todo) {
  $tag = $rel.tag_name
  $nnn = $tag.Substring(6)
  $man = $rel.assets | Where-Object { $_.name -like "*.manifest.json" } | Select-Object -First 1
  if (-not $man) { Write-Output "${nnn}: SKIPPED (no manifest yet)"; continue }
  $manifest = Invoke-RestMethod -Uri $man.browser_download_url -Headers @{ "User-Agent" = "story-factory-fetch" }
  $total = ($manifest.parts | Measure-Object -Property bytes -Sum).Sum
  $free = (Get-PSDrive $drive.Name).Free
  if (($free - 2 * $total) -lt ($MinFreeGB * 1GB)) {
    Write-Output ("{0}: REFUSED - needs {1:N0} MB, free {2:N1} GB would drop below {3} GB" -f $nnn, ($total / 1MB), ($free / 1GB), $MinFreeGB)
    continue
  }
  $tmp = Join-Path $env:TEMP "sf-fetch-$nnn"
  New-Item -ItemType Directory -Force -Path $tmp | Out-Null
  try {
    $partFiles = @()
    foreach ($p in $manifest.parts) {
      $asset = $rel.assets | Where-Object { $_.name -eq $p.name } | Select-Object -First 1
      if (-not $asset) { throw "asset $($p.name) missing in release" }
      $out = Join-Path $tmp $p.name
      Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $out -Headers @{ "User-Agent" = "story-factory-fetch" } -UseBasicParsing
      $h = (Get-FileHash -Algorithm SHA256 -Path $out).Hash.ToLower()
      if ($h -ne $p.sha256) { throw "SHA256 mismatch for $($p.name)" }
      $partFiles += $out
    }
    $enc = Join-Path $tmp "bundle.tar.age"
    if ($partFiles.Count -eq 1) { Move-Item -Force $partFiles[0] $enc }
    else {
      $fs = [IO.File]::Create($enc)
      foreach ($pf in ($partFiles | Sort-Object)) { $b = [IO.File]::OpenRead($pf); $b.CopyTo($fs); $b.Close() }
      $fs.Close()
    }
    $tar = Join-Path $tmp "bundle.tar"
    & $age -d -i $key -o $tar $enc
    if ($LASTEXITCODE -ne 0) { throw "age decrypt failed (wrong backup.key?)" }
    $before = @(Get-ChildItem $dest -File | Select-Object -ExpandProperty Name)
    $tarExe = Join-Path $env:SystemRoot "System32\tar.exe"   # Windows bsdtar (GNU tar from Git treats "C:" as a remote host)
    if (-not (Test-Path $tarExe)) { $tarExe = "tar.exe" }
    & $tarExe -xf $tar -C $dest
    if ($LASTEXITCODE -ne 0) { throw "tar extract failed" }
    $new = @(Get-ChildItem $dest -File | Where-Object { $before -notcontains $_.Name } | Select-Object -ExpandProperty Name)
    # P-002: the channel folder gets exactly 3 files per video (mp4 + 2 thumbnails); info/srt stay inside the release bundle
    foreach ($f in @($new | Where-Object { $_ -notlike "*.mp4" -and $_ -notlike "*Thumbnail*.jpg" })) { Remove-Item -LiteralPath (Join-Path $dest $f) -Force }
    $new = @($new | Where-Object { $_ -like "*.mp4" -or $_ -like "*Thumbnail*.jpg" })
    $mp4 = $new | Where-Object { $_ -like "*.mp4" } | Select-Object -First 1
    $base = if ($mp4) { $mp4.Substring(0, $mp4.Length - 4) } else { "video $nnn" }
    $done[$tag] = (Get-Date).ToString("s")
    ($done | ConvertTo-Json) | Set-Content -Path $ledger -Encoding UTF8
    Write-Output ("{0}: delivered {1} files -> {2}" -f $nnn, $new.Count, $base)
  }
  catch { Write-Output ("{0}: FAILED - {1}" -f $nnn, $_.Exception.Message) }
  finally { Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue }
}
