param(
    [string]$DesktopSource = "screenshots\desktop-final",
    [string]$MobileSource = "screenshots\mobile-final-true"
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing
$root = Split-Path -Parent $PSScriptRoot

function New-ContactSheet {
    param(
        [string]$Source,
        [string]$Output,
        [int]$ThumbWidth,
        [int]$ThumbHeight
    )
    $files = Get-ChildItem -LiteralPath $Source -File -Filter "*.png" |
        Sort-Object { if ($_.BaseName -match '^(\d+)') { [int]$Matches[1] } else { 999 } }
    if ($files.Count -ne 10) {
        throw "Esperadas 10 imagens em $Source; encontradas $($files.Count)."
    }
    $margin = 20
    $labelHeight = 36
    $columns = 2
    $rows = 5
    $bitmap = [System.Drawing.Bitmap]::new(
        ($ThumbWidth * $columns) + ($margin * ($columns + 1)),
        (($ThumbHeight + $labelHeight) * $rows) + ($margin * ($rows + 1))
    )
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.Clear([System.Drawing.Color]::FromArgb(8, 13, 20))
    $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $font = [System.Drawing.Font]::new("Segoe UI", 14, [System.Drawing.FontStyle]::Bold)
    $brush = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(232, 238, 247))
    try {
        for ($index = 0; $index -lt $files.Count; $index++) {
            $column = $index % $columns
            $row = [math]::Floor($index / $columns)
            $x = $margin + ($column * ($ThumbWidth + $margin))
            $y = $margin + ($row * ($ThumbHeight + $labelHeight + $margin))
            $image = [System.Drawing.Image]::FromFile($files[$index].FullName)
            try {
                $graphics.DrawImage($image, $x, $y, $ThumbWidth, $ThumbHeight)
                $graphics.DrawString($files[$index].BaseName, $font, $brush, $x, $y + $ThumbHeight + 4)
            } finally {
                $image.Dispose()
            }
        }
        $bitmap.Save($Output, [System.Drawing.Imaging.ImageFormat]::Png)
    } finally {
        $brush.Dispose()
        $font.Dispose()
        $graphics.Dispose()
        $bitmap.Dispose()
    }
}

New-ContactSheet -Source (Join-Path $root $DesktopSource) -Output (Join-Path $root "screenshots\desktop-contact-sheet-final.png") -ThumbWidth 668 -ThumbHeight 410
New-ContactSheet -Source (Join-Path $root $MobileSource) -Output (Join-Path $root "screenshots\mobile-contact-sheet-final.png") -ThumbWidth 546 -ThumbHeight 410
"CONTACT_SHEETS_CREATED"
