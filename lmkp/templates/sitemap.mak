<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    % for url in urls:
    <url>
        <loc>${url['loc']}</loc>
        <lastmod>${url['lastmod']}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.5</priority>
    </url>
    % endfor
</urlset>