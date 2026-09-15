# Simple static file server for plasico.bg
# Usage: powershell -File serve.ps1

$Port = 3456
$Root = $PSScriptRoot

$MimeTypes = @{
    '.html' = 'text/html; charset=utf-8'
    '.css'  = 'text/css; charset=utf-8'
    '.js'   = 'application/javascript; charset=utf-8'
    '.json' = 'application/json; charset=utf-8'
    '.png'  = 'image/png'
    '.jpg'  = 'image/jpeg'
    '.jpeg' = 'image/jpeg'
    '.webp' = 'image/webp'
    '.svg'  = 'image/svg+xml'
    '.woff2'= 'font/woff2'
    '.ico'  = 'image/x-icon'
    '.pdf'  = 'application/pdf'
    '.gif'  = 'image/gif'
}

$Listener = New-Object System.Net.HttpListener
$Listener.Prefixes.Add("http://localhost:$Port/")
$Listener.Start()

Write-Host "Serving at http://localhost:$Port/"

try {
    while ($Listener.IsListening) {
        $Context = $Listener.GetContext()
        $Request = $Context.Request
        $Response = $Context.Response

        try {
            $RelativePath = [System.Uri]::UnescapeDataString($Request.Url.LocalPath.TrimStart('/'))

            if ([string]::IsNullOrWhiteSpace($RelativePath)) {
                $RelativePath = 'index.html'
            }

            $FullPath = [System.IO.Path]::GetFullPath(
                [System.IO.Path]::Combine($Root, $RelativePath.Replace('/', [System.IO.Path]::DirectorySeparatorChar))
            )
            $RootFull = [System.IO.Path]::GetFullPath($Root)

            if (-not $FullPath.StartsWith($RootFull, [StringComparison]::OrdinalIgnoreCase)) {
                $Response.StatusCode = 403
                $Buffer = [System.Text.Encoding]::UTF8.GetBytes('403 Forbidden')
                $Response.ContentType = 'text/plain; charset=utf-8'
            }
            elseif (-not (Test-Path -LiteralPath $FullPath -PathType Leaf)) {
                $Response.StatusCode = 404
                $Buffer = [System.Text.Encoding]::UTF8.GetBytes('404 Not Found')
                $Response.ContentType = 'text/plain; charset=utf-8'
            }
            else {
                $Extension = [System.IO.Path]::GetExtension($FullPath).ToLowerInvariant()
                $ContentType = $MimeTypes[$Extension]
                if (-not $ContentType) {
                    $ContentType = 'application/octet-stream'
                }

                $Buffer = [System.IO.File]::ReadAllBytes($FullPath)
                $Response.StatusCode = 200
                $Response.ContentType = $ContentType
            }

            $Response.ContentLength64 = $Buffer.Length
            $Response.OutputStream.Write($Buffer, 0, $Buffer.Length)
        }
        catch {
            try {
                if (-not $Response.Headers.Sent) {
                    $Response.StatusCode = 500
                    $Buffer = [System.Text.Encoding]::UTF8.GetBytes('500 Internal Server Error')
                    $Response.ContentType = 'text/plain; charset=utf-8'
                    $Response.ContentLength64 = $Buffer.Length
                    $Response.OutputStream.Write($Buffer, 0, $Buffer.Length)
                }
            } catch {
                # Response may already be closed; keep the listener alive.
            }
        }
        finally {
            try { $Response.OutputStream.Close() } catch {}
        }
    }
}
finally {
    $Listener.Stop()
    $Listener.Close()
}
