# Generate product detail pages from catalog HTML
$ErrorActionPreference = 'Stop'
$Dir = $PSScriptRoot
$IndexPath = Join-Path $Dir 'index.html'
$UrlMapPath = Join-Path $Dir 'product-url-map.json'
$MetaPath = Join-Path $Dir 'product-category-meta.json'
$StringsPath = Join-Path $Dir 'product-ui-strings.json'
$CategoryMeta = (Get-Content $MetaPath -Raw -Encoding UTF8 | ConvertFrom-Json)
$Ui = (Get-Content $StringsPath -Raw -Encoding UTF8 | ConvertFrom-Json)

function Escape-Html([string]$s) {
    if ($null -eq $s) { return '' }
    return [System.Net.WebUtility]::HtmlEncode($s)
}

function Slugify-Title([string]$title) {
    $map = @{
        [char]0x0430='a';[char]0x0431='b';[char]0x0432='v';[char]0x0433='g';[char]0x0434='d';[char]0x0435='e';[char]0x0436='zh'
        [char]0x0437='z';[char]0x0438='i';[char]0x0439='y';[char]0x043A='k';[char]0x043B='l';[char]0x043C='m';[char]0x043D='n'
        [char]0x043E='o';[char]0x043F='p';[char]0x0440='r';[char]0x0441='s';[char]0x0442='t';[char]0x0443='u';[char]0x0444='f'
        [char]0x0445='h';[char]0x0446='ts';[char]0x0447='ch';[char]0x0448='sh';[char]0x0449='sht';[char]0x044A='a'
        [char]0x044C='y';[char]0x044E='yu';[char]0x044F='ya'
    }
    $lower = $title.ToLower()
    $sb = New-Object System.Text.StringBuilder
    foreach ($ch in $lower.ToCharArray()) {
        if ($map.ContainsKey($ch)) { [void]$sb.Append($map[$ch]) }
        elseif ($ch -match '[a-z0-9]') { [void]$sb.Append($ch) }
        elseif ($ch -match '[ \-_/|,]') { [void]$sb.Append('-') }
    }
    $slug = ($sb.ToString() -replace '-+', '-').Trim('-')
    if ($slug.Length -gt 120) { $slug = $slug.Substring(0, 120).Trim('-') }
    if (-not $slug) { $slug = 'product' }
    return $slug
}

function Get-ProductFilename($prod) {
    $url = [string]$prod.url
    if ($url -match '/([^/]+\.html)$') {
        $name = $Matches[1]
        if ($name.Length -le 100) { return $name }
    }
    $slug = Slugify-Title $prod.title
    if ($slug.Length -gt 55) { $slug = $slug.Substring(0, 55).Trim('-') }
    return "$slug-$($prod.id).html"
}

function Decode-HtmlEntities([string]$s) {
    if ($null -eq $s) { return '' }
    return [System.Net.WebUtility]::HtmlDecode($s)
}

function Parse-RedesignArticle([string]$article, [string]$categoryId) {
    if ($article -notmatch 'data-id="(\d+)"') { return $null }
    $id = $Matches[1]
    $title = ''
    if ($article -match '<img[^>]+alt="([^"]*)"') { $title = (Decode-HtmlEntities $Matches[1]).Trim() }
    if ($article -match 'class="hover:text-apricot[^"]*"[^>]*>([^<]+)</a>') {
        $linkTitle = (Decode-HtmlEntities $Matches[1]).Trim()
        if ($linkTitle.Length -gt $title.Length) { $title = $linkTitle }
    }
    $url = ''
    if ($article -match '<a href="([^"]+)" class="block w-full h-full relative"') { $url = $Matches[1] }
    $image = ''
    if ($article -match 'data-image="([^"]+)"') { $image = $Matches[1] }
    elseif ($article -match '<img[^>]+src="([^"]+)"') { $image = $Matches[1] }
    $price = $null
    if ($article -match 'data-price="([^"]+)"') { $price = [double]$Matches[1] }
    $oldPrice = $null
    if ($article -match 'line-through[^>]*>([\d.]+)\s*') { $oldPrice = [double]$Matches[1] }
    $discount = 0
    if ($article -match 'data-discount-percent="(\d+)"') { $discount = [int]$Matches[1] }
    $upgraded = $article -match 'data-upgraded="true"'
    $specs = @()
    foreach ($m in [regex]::Matches($article, '<li class="text-on-surface-variant text-body-sm">([^<]+)</li>')) {
        $specs += $m.Groups[1].Value.Trim()
    }
    $subcategory = ''
    if ($article -match 'data-subcategory="([^"]+)"') { $subcategory = $Matches[1] }
    return [pscustomobject]@{ id=$id; title=$title; url=$url; image=$image; price=$price; oldPrice=$oldPrice; discount=$discount; upgraded=$upgraded; specs=$specs; categoryId=$categoryId; subcategory=$subcategory }
}

function Get-CategoryPriority([string]$categoryId) {
    if ($categoryId -eq 'laptopi') { return 0 }
    return 1
}

function Merge-Product($existing, $incoming) {
    if (-not $existing) { return $incoming }
    $keep = $existing
    $replace = $incoming
    $existingPri = Get-CategoryPriority $existing.categoryId
    $incomingPri = Get-CategoryPriority $incoming.categoryId
    if ($incomingPri -gt $existingPri) {
        $keep = $incoming
        $replace = $existing
    }
    if ($replace.title -and ($replace.title.Length -gt $keep.title.Length)) { $keep.title = $replace.title }
    if ($replace.specs.Count -gt $keep.specs.Count) { $keep.specs = $replace.specs }
    if (-not $keep.image -and $replace.image) { $keep.image = $replace.image }
    if (-not $keep.url -and $replace.url) { $keep.url = $replace.url }
    if (-not $keep.price -and $replace.price) { $keep.price = $replace.price }
    if (-not $keep.oldPrice -and $replace.oldPrice) { $keep.oldPrice = $replace.oldPrice }
    if ($keep.discount -lt $replace.discount) { $keep.discount = $replace.discount }
    if ($replace.upgraded) { $keep.upgraded = $true }
    return $keep
}

function Add-Product([hashtable]$products, $prod) {
    if (-not $prod -or -not $prod.title) { return }
    if ($products.ContainsKey($prod.id)) {
        $products[$prod.id] = Merge-Product $products[$prod.id] $prod
    } else {
        $products[$prod.id] = $prod
    }
}

function Parse-MirrorArticle([string]$body, [string]$id, [string]$categoryId) {
    $title = ''
    if ($body -match '<a class="mainlink" href="[^"]+"[^>]*title="([^"]*)"') { $title = $Matches[1].Trim(' -') }
    if (-not $title -and $body -match '<span class="ttl"[^>]*>([^<]+)</span>') { $title = $Matches[1].Trim() }
    $url = ''
    if ($body -match '<a class="mainlink" href="([^"]+)"') { $url = $Matches[1] }
    $image = ''
    if ($body -match '<img[^>]+src="([^"]+)"') { $image = $Matches[1] }
    $price = $null; $oldPrice = $null
    if ($body -match '<span class="oldprice">([^<]+(?:<[^>]+>[^<]*)*)</span>') {
        $oldText = ($Matches[1] -replace '<[^>]+>', '')
        if ($oldText -match '([\d]+)\.([\d]{2})') { $oldPrice = [double]"$($Matches[1]).$($Matches[2])" }
    }
    if ($body -match '<span class="price">([^<]+(?:<[^>]+>[^<]*)*)</span>') {
        $pText = ($Matches[1] -replace '<[^>]+>', '')
        if ($pText -match '([\d]+)\.([\d]{2})') { $price = [double]"$($Matches[1]).$($Matches[2])" }
    }
    $specs = @()
    if ($body -match '<ul class="specs-list">(.*?)</ul>') {
        foreach ($m in [regex]::Matches($Matches[1], '<li>(.*?)</li>')) { $specs += ($m.Groups[1].Value -replace '<[^>]+>', '').Trim() }
    }
    $discount = 0
    if ($oldPrice -and $price -and $oldPrice -gt $price) { $discount = [int][math]::Round(($oldPrice - $price) / $oldPrice * 100) }
    return [pscustomobject]@{ id=$id; title=$title; url=$url; image=$image; price=$price; oldPrice=$oldPrice; discount=$discount; upgraded=($title.ToUpper().StartsWith('UPGRADED')); specs=$specs; categoryId=$categoryId; subcategory='' }
}

function Collect-Products {
    $products = @{}
    $slugMap = @{
        computers='computers'; components='components'; monitors='monitors'; used='used'
        'office-chairs'='office-chairs'; gchairs='gchairs'; audio='audio'; bags='bags'
        flash='flash'; external='external'; printers='printers'; accessories='accessories'
        cctv='cctv'; network='network'; hubs='hubs'; cables='cables'; ups='ups'
    }
    foreach ($slug in ($slugMap.Keys | Sort-Object)) {
        $catId = $slugMap[$slug]
        $path = Join-Path $Dir "hot-summer-sale-2026\$slug.html"
        if (-not (Test-Path $path)) { continue }
        $html = Get-Content $path -Raw -Encoding UTF8
        if ($html -match 'id="product-grid"') {
            foreach ($m in [regex]::Matches($html, '<article[^>]*>.*?</article>', 'Singleline')) {
                $p = Parse-RedesignArticle $m.Value $catId
                Add-Product $products $p
            }
        } else {
            foreach ($m in [regex]::Matches($html, '<article\s+data-id="(\d+)"[^>]*class="product-box[^"]*">(.*?)</article>', 'Singleline')) {
                $p = Parse-MirrorArticle $m.Groups[2].Value $m.Groups[1].Value $catId
                Add-Product $products $p
            }
        }
    }
    $main = Join-Path $Dir 'hot-summer-sale-2026.html'
    if (Test-Path $main) {
        $html = Get-Content $main -Raw -Encoding UTF8
        if ($html -match 'id="product-grid"') {
            foreach ($m in [regex]::Matches($html, '<article[^>]*>.*?</article>', 'Singleline')) {
                $p = Parse-RedesignArticle $m.Value 'laptopi'
                Add-Product $products $p
            }
        }
    }
    return @($products.Values)
}

function Get-Shell {
    $index = Get-Content $IndexPath -Raw -Encoding UTF8
    $headEnd = $index.IndexOf('</head>')
    $head = $index.Substring(0, $headEnd + 7)
    $head = $head -replace 'href="home.css"', 'href="product-page.css"'
    $head = $head -replace '<title>.*?</title>', '<title>{{TITLE}}</title>'
    $head = $head -replace '<meta name="description" content="[^"]*"', '<meta name="description" content="{{DESCRIPTION}}"'
    $hStart = $index.IndexOf('<header id="site-header"')
    $hEnd = $index.IndexOf('</header>', $hStart) + 9
    $header = $index.Substring($hStart, $hEnd - $hStart)
    $fStart = $index.IndexOf('<footer class=')
    $fEnd = $index.IndexOf('</html>')
    $footer = $index.Substring($fStart, $fEnd - $fStart)
    $footer = $footer -replace 'src="home.js" defer', 'src="product-page.js"'
    $footer = $footer -replace '<script src="product-card-actions.js"></script>\s*', ''
    if ($footer -notmatch 'product-page.js') {
        $footer = $footer -replace '<script src="auth-modal.js"></script>', "<script src=`"auth-modal.js`"></script>`r`n<script src=`"product-page.js`"></script>"
    }
    return @{ head=$head; header=$header; footer=$footer; bodyOpen='<body class="font-body-md selection:bg-apricot/30 custom-scrollbar product-page-body light-theme-page" data-category-map="category-map.json">' }
}

function Get-CategoryMeta([string]$categoryId) {
    $meta = $CategoryMeta.PSObject.Properties[$categoryId].Value
    if ($meta) { return $meta }
    return $CategoryMeta.PSObject.Properties['laptopi'].Value
}

function Render-Page($prod, $allProducts, $urlMap, $shell) {
    $meta = Get-CategoryMeta $prod.categoryId
    $title = Escape-Html $prod.title
    $short = $prod.title; if ($short.Length -gt 60) { $short = $short.Substring(0,57) + [char]0x2026 }; $short = Escape-Html $short
    $priceHtml = if ($prod.price) { "<div class=`"product-price`">$($prod.price.ToString('F2')) &euro;</div>" } else { '<div class="product-price">&mdash;</div>' }
    if ($prod.oldPrice -and $prod.price -and $prod.oldPrice -gt $prod.price) { $priceHtml += "<div class=`"product-price-old`">$($prod.oldPrice.ToString('F2')) &euro;</div>" }
    $badges = ''
    if ($prod.discount -gt 0) { $badges += "<span class=`"product-badge product-badge--promo`">-$($prod.discount)%</span>" }
    if ($prod.upgraded) { $badges += '<span class="product-badge product-badge--upgraded">Upgraded</span>' }
    if ($badges) { $badges = "<div class=`"product-badge-row`">$badges</div>" }
    $img = Escape-Html $prod.image
    $specItems = ($prod.specs | ForEach-Object { "<li>$(Escape-Html $_)</li>" }) -join ''
    $specItems += "<li>$($Ui.art_no): $(Escape-Html $prod.id)</li>"
    $similar = $allProducts | Where-Object { $_.categoryId -eq $prod.categoryId -and $_.id -ne $prod.id } | Select-Object -First 8
    $simHtml = ''
    foreach ($s in $similar) {
        $sh = Escape-Html $urlMap[$s.id]
        $st = Escape-Html $s.title
        $stShort = if ($s.title.Length -gt 70) { Escape-Html $s.title.Substring(0,70) } else { $st }
        $si = Escape-Html $s.image
        $sp = if ($s.price) { "$($s.price.ToString('F2')) &euro;" } else { '&mdash;' }
        $simHtml += "<div class=`"product-similar-card`"><a href=`"$sh`" class=`"product-similar-card__media`" tabindex=`"-1`" aria-hidden=`"true`"><img class=`"product-similar-card__img`" src=`"$si`" alt=`"`" loading=`"lazy`" width=`"56`" height=`"56`"/></a><div><a href=`"$sh`" class=`"product-similar-card__name`">$stShort</a><div class=`"product-similar-card__price`">$sp</div></div><button type=`"button`" class=`"product-similar-card__add`" data-similar-add data-similar-id=`"$($s.id)`" data-similar-title=`"$st`" data-similar-price=`"$($s.price)`" data-similar-image=`"$si`" data-similar-href=`"$sh`" aria-label=`"$($Ui.add_to_cart)`"><span class=`"material-symbols-outlined`">add_circle</span></button></div>"
    }
    $simSection = ''
    if ($simHtml) { $simSection = "<section class=`"product-similar`"><h2 class=`"product-similar__title`"><a href=`"$($meta.listing_href)`">$($Ui.similar_prefix) $(Escape-Html $meta.label)</a></h2><div class=`"product-similar__grid`">$simHtml</div></section>" }
    $pageTitle = Escape-Html "$($prod.title) | Plasico.bg"
    $desc = Escape-Html "$($prod.title)"
    $head = $shell.head.Replace('{{TITLE}}', $pageTitle).Replace('{{DESCRIPTION}}', $desc)
    $dp = if ($prod.price) { $prod.price.ToString('F2') } else { '0' }
    $main = @"
<main class="pt-[var(--site-header-offset)]">
  <div class="product-page" data-product-page data-product-id="$($prod.id)" data-product-title="$title" data-product-price="$dp" data-product-image="$img">
    <nav class="product-breadcrumb" aria-label="Breadcrumb">
      <a href="index.html">Plasico</a><span class="product-breadcrumb__sep">&rsaquo;</span>
      <a href="$($meta.parent_href)">$(Escape-Html $meta.parent)</a><span class="product-breadcrumb__sep">&rsaquo;</span>
      <a href="$($meta.listing_href)">$(Escape-Html $meta.label)</a><span class="product-breadcrumb__sep">&rsaquo;</span>
      <span class="product-breadcrumb__current">$short</span>
    </nav>
    <div class="product-layout">
      <div class="product-card product-gallery"><div class="product-gallery__main"><img src="$img" alt="$title" data-gallery-main loading="eager" width="800" height="600"/></div></div>
      <aside class="product-card product-buybox">
        <h1 class="product-buybox__title">$title</h1>
        <div class="product-buybox__meta"><span>$($Ui.art_no): $($prod.id)</span><div class="product-buybox__actions"><button type="button" class="product-icon-btn product-icon-btn--compare" data-product-compare><span class="material-symbols-outlined">swap_vert</span> $($Ui.compare)</button><button type="button" class="product-icon-btn" data-product-fav><span class="material-symbols-outlined">favorite</span> $($Ui.favorites)</button></div></div>
        $badges
        <div class="product-price-block">$priceHtml</div>
        <div class="product-buy-row"><div class="product-qty"><button type="button" class="product-qty__btn" data-qty-delta="-1">&minus;</button><span class="product-qty__value" data-qty-value>1</span><button type="button" class="product-qty__btn" data-qty-delta="1">+</button></div><button type="button" class="product-buy-btn" data-product-buy><span class="material-symbols-outlined">shopping_cart</span> $($Ui.buy)</button></div>
        <div class="product-availability"><div class="product-availability__in"><span class="material-symbols-outlined">check_circle</span> $($Ui.in_stock)</div><p class="product-availability__ship">$($Ui.delivery)</p></div>
        <div class="product-contact-row"><a href="tel:070020810">0700 20 810</a><a href="kontakti.html">$($Ui.contact)</a></div>
        <div class="product-installment"><img src="https://static.plasico.bg/images/bnp_button_new.webp" alt="PostBank" loading="lazy" width="155" height="52"/><img src="https://static.plasico.bg/images/bnp_button_card.webp" alt="PostBank card" loading="lazy" width="154" height="52"/></div>
        <form class="product-mini-form" data-fast-order><p class="product-mini-form__title">$($Ui.fast_order)</p><p class="product-mini-form__hint">$($Ui.fast_hint)</p><input type="tel" name="phone" placeholder="08xxxxxxxx" required/><button type="submit">$($Ui.order)</button></form>
      </aside>
    </div>
    <section class="product-card product-specs"><h2 class="product-specs__title">$($Ui.specs_title)</h2><ul class="product-specs__list">$specItems</ul></section>
    $simSection
  </div>
</main>
"@
    return "$head`r`n$($shell.bodyOpen)`r`n$($shell.header)`r`n$main`r`n$($shell.footer)</html>`r`n"
}

Write-Host 'Collecting products...'
$products = Collect-Products
if ($products.Count -eq 0) { throw 'No products found' }
$urlMap = @{}
foreach ($p in $products) { $urlMap[$p.id] = Get-ProductFilename $p }
$shell = Get-Shell
Write-Host "Generating $($products.Count) product pages..."
$written = 0; $failed = 0
foreach ($p in $products) {
    $fname = $urlMap[$p.id]
    $out = Join-Path $Dir $fname
    $html = Render-Page $p $products $urlMap $shell
    for ($try = 0; $try -lt 3; $try++) {
        try {
            [System.IO.File]::WriteAllText($out, $html, [System.Text.UTF8Encoding]::new($false))
            $written++
            break
        } catch {
            if ($try -eq 2) { $failed++; Write-Warning "Failed: $fname - $($_.Exception.Message)" }
            else { Start-Sleep -Milliseconds 300 }
        }
    }
    if ($written % 250 -eq 0) { Write-Host "  $written pages..." }
}
Write-Host "  wrote $written pages, failures: $failed"
$mapJson = @{ generatedAt = (Get-Date -Format 'yyyy-MM-dd'); count = $products.Count; byId = $urlMap } | ConvertTo-Json -Depth 5
Set-Content -Path $UrlMapPath -Value $mapJson -Encoding UTF8
$updated = 0
function Save-TextFile([string]$path, [string]$text) {
    for ($try = 0; $try -lt 5; $try++) {
        try {
            [System.IO.File]::WriteAllText($path, $text, [System.Text.UTF8Encoding]::new($false))
            return
        } catch {
            if ($try -eq 4) { throw }
            Start-Sleep -Milliseconds (400 * ($try + 1))
        }
    }
}

function Update-CatalogLinks([string]$text, [hashtable]$urlMap, [string]$prefix) {
    foreach ($id in $urlMap.Keys) {
        $local = if ($prefix) { "$prefix$($urlMap[$id])" } else { $urlMap[$id] }
        $text = [regex]::Replace($text, "https://plasico\.bg/[^`"'']*-$id\.html", $local)
    }
    return $text
}

function Update-IndexProductLinks([string]$text, [hashtable]$urlMap) {
    return [regex]::Replace($text, '(<article[^>]*class="[^"]*home-product[^"]*"[^>]*data-id="(\d+)"[^>]*>.*?</article>)', {
        param($m)
        $block = $m.Groups[1].Value
        $id = $m.Groups[2].Value
        if (-not $urlMap.ContainsKey($id)) { return $block }
        $href = $urlMap[$id]
        return [regex]::Replace($block, 'href="[^"]*"', "href=`"$href`"")
    }, 'Singleline')
}

foreach ($pat in @('hot-summer-sale-2026.html','index.html','poruchka.html')) {
    $path = Join-Path $Dir $pat
    if (-not (Test-Path $path)) { continue }
    $text = Get-Content $path -Raw -Encoding UTF8
    $orig = $text
    $text = Update-CatalogLinks $text $urlMap ''
    if ($pat -eq 'index.html') {
        $text = Update-IndexProductLinks $text $urlMap
    }
    if ($text -ne $orig) { Save-TextFile $path $text; $updated++; Write-Host "  updated $pat" }
}
Get-ChildItem -Path (Join-Path $Dir 'hot-summer-sale-2026') -Filter '*.html' -File | Where-Object { $_.Name -notlike '*.mirror-backup' } | ForEach-Object {
    $text = Get-Content $_.FullName -Raw -Encoding UTF8
    $orig = $text
    $text = Update-CatalogLinks $text $urlMap '../'
    if ($text -ne $orig) { Save-TextFile $_.FullName $text; $updated++; Write-Host "  updated hot-summer-sale-2026/$($_.Name)" }
}
Write-Host "Done: $($products.Count) pages, $updated catalog files updated"
