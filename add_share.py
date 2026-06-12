import sys
sys.stdout.reconfigure(encoding="utf-8")

P = "C:/Users/kangg/Desktop/网站搭建/ai-news-site/src/build.py"
c = open(P, "r", encoding="utf-8").read()

changes = []

# ===== 1. Add QR modal CSS =====
modal_css = '''
    /* QR Modal */
    .qr-overlay { position:fixed; inset:0; background:rgba(0,0,0,0.6); backdrop-filter:blur(6px); z-index:999; display:none; align-items:center; justify-content:center; animation:fadeIn .2s ease; }
    .qr-overlay.show { display:flex; }
    .qr-modal { background:var(--bg-secondary); border:1px solid var(--glass-border); border-radius:16px; padding:2rem; text-align:center; max-width:320px; width:90%; position:relative; box-shadow:0 20px 60px rgba(0,0,0,0.4); }
    .qr-modal img { width:200px; height:200px; border-radius:8px; margin:1rem 0; border:1px solid var(--glass-border); }
    .qr-modal h3 { font-family:"Orbitron",sans-serif; font-size:.85rem; font-weight:600; letter-spacing:1px; color:var(--accent-2); margin-bottom:.5rem; }
    .qr-modal p { color:var(--text-muted); font-size:.78rem; line-height:1.5; }
    .qr-modal .close-qr { position:absolute; top:10px; right:14px; font-size:1.2rem; cursor:pointer; color:var(--text-muted); transition:color .2s; background:none; border:none; }
    .qr-modal .close-qr:hover { color:var(--accent-2); }
    @keyframes fadeIn { from{opacity:0;} to{opacity:1;} }
'''

# Insert before the closing of CSS_STYLE (before @media)
idx = c.rfind("@media (max-width:640px)")
if idx > 0:
    # Find the end of the media query and add modal CSS before the closing """
    media_end = c.find('"""', idx)
    c = c[:media_end] + modal_css + '\n' + c[media_end:]
    changes.append("Added QR modal CSS")
else:
    changes.append("WARN: Could not find media query")

# ===== 2. Replace share buttons in detail_page =====
# Find the share buttons section in detail_page body
old_share = """    <div class="flex gap-2">
      <a href="https://twitter.com/intent/tweet?text={html_escape(title)}&url=https://ckang2927-commits.github.io/ai-news-site/{np}/index.html" target="_blank" rel="noopener" class="share-btn" aria-label="分享到Twitter">? Twitter</a>
      <a href="javascript:void(0)" onclick="navigator.clipboard.writeText(window.location.href);alert('链接已复制！')" class="share-btn" aria-label="复制链接">⌘ 复制链接</a>
    </div>"""

new_share = """    <div class="flex gap-2">
      <a href="javascript:void(0)" onclick="var u=encodeURIComponent(window.location.href);var t=encodeURIComponent('{html_escape(title)}');window.open('https://connect.qq.com/widget/shareqq/index.html?url='+u+'&title='+t+'&desc=&summary=&site=AI%E8%B5%84%E8%AE%AF%E7%AB%99','_blank','width=700,height=520')" class="share-btn" aria-label="分享到QQ">QQ</a>
      <a href="javascript:void(0)" onclick="showQRCode(window.location.href)" class="share-btn" aria-label="微信分享">微信</a>
      <a href="https://twitter.com/intent/tweet?text={html_escape(title)}&url=https://ckang2927-commits.github.io/ai-news-site/{np}/index.html" target="_blank" rel="noopener" class="share-btn" aria-label="分享到Twitter">𝕏</a>
      <a href="javascript:void(0)" onclick="navigator.clipboard.writeText(window.location.href).then(function(){alert('链接已复制！')})" class="share-btn" aria-label="复制链接">⌘</a>
    </div>"""

if old_share in c:
    c = c.replace(old_share, new_share)
    changes.append("Updated share buttons (QQ + WeChat + Twitter + Copy)")
else:
    changes.append("WARN: Share buttons section not found, trying to find variant...")
    # Try finding without the Twitter icon character
    idx = c.find("Twitter</a>")
    if idx > 0:
        # Find the div.flex.gap-2 containing it
        div_start = c.rfind("<div class=\"flex gap-2\">", 0, idx)
        div_end = c.find("</div>", idx) + 6
        print(f"Found share div at {div_start}-{div_end}: {repr(c[div_start:div_end])}")
        c = c[:div_start] + new_share + c[div_end:]
        changes.append("Replaced share div (alt method)")

# ===== 3. Add QR code JS and modal HTML =====
qr_js_and_html = """
  <!-- QR Code Modal -->
  <div class="qr-overlay" id="qrOverlay" onclick="if(event.target===this)closeQR()">
    <div class="qr-modal">
      <button class="close-qr" onclick="closeQR()">&times;</button>
      <h3>&#128261; 微信分享</h3>
      <p>截图二维码，在微信中打开分享</p>
      <img id="qrImage" src="" alt="QR Code">
      <p style="font-size:.7rem;color:var(--text-muted);">扫描二维码查看当前页面</p>
    </div>
  </div>
  <script>
  function showQRCode(url) {
    var img = document.getElementById("qrImage");
    img.src = "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=" + encodeURIComponent(url);
    document.getElementById("qrOverlay").classList.add("show");
  }
  function closeQR() {
    document.getElementById("qrOverlay").classList.remove("show");
  }
  </script>
"""

# Insert before </body> in the page_frame template
old_body_close = "</body>"
new_body_close = qr_js_and_html + "\n</body>"
if old_body_close in c:
    # Only replace the LAST occurrence (in the template, not in CSS)
    idx = c.rfind("</body>")
    c = c[:idx] + qr_js_and_html + "\n</body>" + c[idx+7:]
    changes.append("Added QR modal HTML + JS")
else:
    changes.append("WARN: </body> not found")

# ===== 4. Also add the QR/WeChat share buttons on list pages =====
# Add share buttons at the bottom of list pages (before bottom-bar)
# Find the bottom-bar HTML and add share buttons before it
old_bb = """<div class="bottom-bar">
  <a href="{np}/index.html" class="cyber-btn">&larr; 返回首页</a>
  <a href="javascript:history.back()" class="cyber-btn">&#127968; 返回上一页</a>
</div>"""

list_share = """<div style="display:flex;justify-content:center;gap:.5rem;margin-bottom:.8rem;" class="animate-in">
  <a href="javascript:void(0)" onclick="var u=encodeURIComponent(window.location.href);var t=encodeURIComponent('{html_escape(title)}');window.open('https://connect.qq.com/widget/shareqq/index.html?url='+u+'&title='+t,'_blank','width=700,height=520')" class="share-btn" aria-label="分享到QQ">QQ</a>
  <a href="javascript:void(0)" onclick="showQRCode(window.location.href)" class="share-btn" aria-label="微信分享">微信</a>
  <a href="javascript:void(0)" onclick="navigator.clipboard.writeText(window.location.href).then(function(){alert('链接已复制！')})" class="share-btn" aria-label="复制链接">⌘</a>
</div>
""" + old_bb

c = c.replace(old_bb, list_share)
changes.append("Added share buttons on list pages")

open(P, "w", encoding="utf-8").write(c)
print("\n".join(f"  [OK] {ch}" for ch in changes))
print("\n[DONE] Share features added!")