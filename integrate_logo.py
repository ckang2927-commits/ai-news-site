import sys
sys.stdout.reconfigure(encoding="utf-8")
P = "C:/Users/kangg/Desktop/网站搭建/ai-news-site/src/build.py"
c = open(P, "r", encoding="utf-8").read()

# Replace text logo with SVG image
old_logo = '<a href="$NP/index.html" class="site-logo">\u2248 AI \u8d44\u8baf\u7ad9</a>'
new_logo = '<a href="$NP/index.html" class="site-logo"><img src="$NP/images/logo.svg" alt="AI \u8d44\u8baf\u7ad9" style="height:34px;width:auto;vertical-align:middle"></a>'
if old_logo in c:
    c = c.replace(old_logo, new_logo)
    print("[OK] Logo replaced with SVG")
else:
    print("[WARN] Exact logo not found, trying alternatives...")
    for variant in ['site-logo">\u2248 AI', 'site-logo">~ AI', 'site-logo">\u2192\u2192 AI', 'site-logo">.. AI', 'site-logo">\u25b6 AI']:
        idx = c.find(variant)
        if idx > 0:
            start = c.rfind("<a ", 0, idx)
            end = c.find("</a>", idx) + 4
            old = c[start:end]
            new = '<a href="$NP/index.html" class="site-logo"><img src="$NP/images/logo.svg" alt="AI \u8d44\u8baf\u7ad9" style="height:34px;width:auto;vertical-align:middle"></a>'
            c = c.replace(old, new)
            print(f"[OK] Logo replaced (variant match: {variant})")
            break
    else:
        idx = c.find("site-logo\">")
        if idx > 0:
            start = c.rfind("<a ", 0, idx)
            end = c.find("</a>", idx) + 4
            old = c[start:end]
            print(f"[WARN] Found logo at {idx}: {repr(old[:60])}")
        else:
            print("[WARN] No logo found at all")

open(P, "w", encoding="utf-8").write(c)
print("[DONE] Logo integration complete")