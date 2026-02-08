$ErrorActionPreference = "Stop"

# Minimal .env loader so MCP can start with secrets without putting them in git-tracked config.
$envPath = Join-Path $PSScriptRoot "..\.env"
if (Test-Path $envPath) {
  Get-Content $envPath | ForEach-Object {
    $line = $_.Trim()
    if (-not $line) { continue }
    if ($line.StartsWith("#")) { continue }
    $m = [regex]::Match($line, '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$')
    if (-not $m.Success) { continue }
    $key = $m.Groups[1].Value
    $val = $m.Groups[2].Value.Trim()
    if (($val.StartsWith('"') -and $val.EndsWith('"')) -or ($val.StartsWith("'") -and $val.EndsWith("'"))) {
      $val = $val.Substring(1, $val.Length - 2)
    }
    [Environment]::SetEnvironmentVariable($key, $val)
  }
}

# Map your existing .env keys to what the Jira MCP expects (keep both so other tools keep working).
if ((-not $env:ATLASSIAN_SITE_NAME -or $env:ATLASSIAN_SITE_NAME.StartsWith("$")) -and $env:JIRA_URL) {
  try {
    $uri = [Uri]$env:JIRA_URL
    $host = $uri.Host
    if ($host.EndsWith(".atlassian.net")) {
      $env:ATLASSIAN_SITE_NAME = $host.Substring(0, $host.Length - ".atlassian.net".Length)
    }
  } catch { }
}
if ((-not $env:ATLASSIAN_USER_EMAIL -or $env:ATLASSIAN_USER_EMAIL.StartsWith("$")) -and $env:JIRA_USERNAME) { $env:ATLASSIAN_USER_EMAIL = $env:JIRA_USERNAME }
if ((-not $env:ATLASSIAN_API_TOKEN -or $env:ATLASSIAN_API_TOKEN.StartsWith("$")) -and $env:JIRA_API_TOKEN) { $env:ATLASSIAN_API_TOKEN = $env:JIRA_API_TOKEN }

if (-not $env:ATLASSIAN_SITE_NAME -or -not $env:ATLASSIAN_USER_EMAIL -or -not $env:ATLASSIAN_API_TOKEN) {
  Write-Error "Missing Jira credentials. Set ATLASSIAN_SITE_NAME, ATLASSIAN_USER_EMAIL, ATLASSIAN_API_TOKEN (or JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN in .env)."
}

function Start-McpWithStdoutFilter {
  param(
    [Parameter(Mandatory = $true)][string]$FileName,
    [Parameter(Mandatory = $true)][string]$Arguments
  )

  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName = $FileName
  $psi.Arguments = $Arguments
  $psi.UseShellExecute = $false
  $psi.RedirectStandardInput = $true
  $psi.RedirectStandardOutput = $true
  $psi.RedirectStandardError = $true
  $psi.CreateNoWindow = $true

  $p = New-Object System.Diagnostics.Process
  $p.StartInfo = $psi

  if (-not $p.Start()) {
    throw "Failed to start process: $FileName $Arguments"
  }

  # Pump stdin bytes -> child stdin (MCP is bidirectional over stdio).
  $stdinThread = [System.Threading.Thread]::new([System.Threading.ParameterizedThreadStart]{
    param($proc)
    try {
      $inStream = [Console]::OpenStandardInput()
      $outStream = $proc.StandardInput.BaseStream
      $buf = New-Object byte[] 8192
      while ($true) {
        $n = $inStream.Read($buf, 0, $buf.Length)
        if ($n -le 0) { break }
        $outStream.Write($buf, 0, $n)
        $outStream.Flush()
      }
    } catch {
      # Ignore broken pipe on shutdown.
    } finally {
      try { $proc.StandardInput.Close() } catch { }
    }
  })
  $stdinThread.IsBackground = $true
  $stdinThread.Start($p)

  # Stdout: forward only JSON-RPC protocol lines; send other noise to stderr.
  $stdoutThread = [System.Threading.Thread]::new([System.Threading.ParameterizedThreadStart]{
    param($proc)
    try {
      # MCP stdio uses LSP-style framing:
      #   Content-Length: N\r\n\r\n<JSON bytes>
      # Some servers print logs to stdout; we drop everything until we can resync on Content-Length frames.
      $outStream = $proc.StandardOutput.BaseStream
      $stdout = [Console]::OpenStandardOutput()
      $pat = [System.Text.Encoding]::ASCII.GetBytes("Content-Length:")
      $hdrEnd = [System.Text.Encoding]::ASCII.GetBytes("`r`n`r`n")
      $buf = New-Object 'System.Collections.Generic.List[byte]'
      $tmp = New-Object byte[] 8192

      function IndexOfBytes([System.Collections.Generic.List[byte]]$hay, [byte[]]$needle) {
        if ($hay.Count -lt $needle.Length) { return -1 }
        for ($i = 0; $i -le $hay.Count - $needle.Length; $i++) {
          $ok = $true
          for ($j = 0; $j -lt $needle.Length; $j++) {
            if ($hay[$i + $j] -ne $needle[$j]) { $ok = $false; break }
          }
          if ($ok) { return $i }
        }
        return -1
      }

      while ($true) {
        $n = $outStream.Read($tmp, 0, $tmp.Length)
        if ($n -le 0) { break }
        for ($k = 0; $k -lt $n; $k++) { [void]$buf.Add($tmp[$k]) }

        while ($true) {
          $idx = IndexOfBytes $buf $pat
          if ($idx -lt 0) {
            # Keep a small tail for partial pattern match; emit the rest as noise.
            $keep = [Math]::Min($buf.Count, $pat.Length - 1)
            $emitCount = $buf.Count - $keep
            if ($emitCount -gt 0) {
              $noise = [System.Text.Encoding]::UTF8.GetString($buf.GetRange(0, $emitCount).ToArray())
              if ($noise.Trim().Length -gt 0) { [Console]::Error.WriteLine("[jira-mcp stdout] $noise") }
              $buf.RemoveRange(0, $emitCount)
            }
            break
          }

          if ($idx -gt 0) {
            $noise = [System.Text.Encoding]::UTF8.GetString($buf.GetRange(0, $idx).ToArray())
            if ($noise.Trim().Length -gt 0) { [Console]::Error.WriteLine("[jira-mcp stdout] $noise") }
            $buf.RemoveRange(0, $idx)
          }

          $hdrIdx = IndexOfBytes $buf $hdrEnd
          if ($hdrIdx -lt 0) { break }

          $headerLen = $hdrIdx + $hdrEnd.Length
          $headerText = [System.Text.Encoding]::ASCII.GetString($buf.GetRange(0, $headerLen).ToArray())
          $m = [regex]::Match($headerText, 'Content-Length:\s*(\d+)', 'IgnoreCase')
          if (-not $m.Success) {
            # Corrupt header; drop one byte and resync.
            $buf.RemoveAt(0)
            continue
          }
          $contentLen = [int]$m.Groups[1].Value
          $frameLen = $headerLen + $contentLen
          if ($buf.Count -lt $frameLen) { break }

          $frame = $buf.GetRange(0, $frameLen).ToArray()
          $stdout.Write($frame, 0, $frame.Length)
          $stdout.Flush()
          $buf.RemoveRange(0, $frameLen)
        }
      }
    } catch {
      # Ignore on shutdown.
    }
  })
  $stdoutThread.IsBackground = $true
  $stdoutThread.Start($p)

  # Stderr: passthrough.
  $stderrThread = [System.Threading.Thread]::new([System.Threading.ParameterizedThreadStart]{
    param($proc)
    try {
      while (-not $proc.StandardError.EndOfStream) {
        $line = $proc.StandardError.ReadLine()
        if ($null -eq $line) { break }
        [Console]::Error.WriteLine($line)
      }
    } catch {
      # Ignore on shutdown.
    }
  })
  $stderrThread.IsBackground = $true
  $stderrThread.Start($p)

  $p.WaitForExit()
  exit $p.ExitCode
}

# Start Jira MCP server (stdio transport) but filter noisy stdout so MCP handshake succeeds.
Start-McpWithStdoutFilter -FileName "npx" -Arguments "-y @aashari/mcp-server-atlassian-jira"
