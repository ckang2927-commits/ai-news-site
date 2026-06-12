import sys, io, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Read the CLEAN version from build_prev (which has CSS+nav changes but no broken f-strings)
with open("src/build_prev.py", "r", encoding="utf-8") as f:
    content = f.read()

# ===== 1. Add search_data param to page_frame =====
content = content.replace(
    "def page_frame(title, body_html, nav_depth=0, og_desc=None, og_image=None):",
    "def page_frame(title, body_html, nav_depth=0, og_desc=None, og_image=None, search_data=None):"
)

# ===== 2. Add json import =====
content = content.replace("import re, os", "import re, os, json")

# ===== 3. Replace the page_frame body - use Template class instead of f-string =====
# Find the page_frame function body and replace the f-string section

# Add at the top of the file:
old_imports = "import re, os, json"
new_imports = "import re, os, json\nfrom string import Template"
content = content.replace(old_imports, new_imports)

# Find the return statement in page_frame and its template
# Strategy: build the HTML template using Template($) and avoid f-string entirely
# We need to find where return f""" starts and replace it

start_marker = "    scroll_event_js = "
idx = content.find(start_marker)
if idx < 0:
    print("ERROR: scroll_event_js not found")
else:
    # Find the return statement
    ret_idx = content.find("    return f", idx)
    if ret_idx < 0:
        print("ERROR: return statement not found")
    else:
        # Build the new template approach
        new_return = '''
    search_data_json = json.dumps(search_data or [], ensure_ascii=False)
    # Build search JS with inline data
    search_js_funcs = Template("""
var searchData = $SD;
var curFocus = -1;
function initSearch(inpId, dropId, scope) {
  var inp = document.getElementById(inpId), drop = document.getElementById(dropId);
  if (!inp || !drop) return;
  inp.addEventListener("input", function(){doSearch(inp,drop,scope);});
  inp.addEventListener("focus", function(){if(!this.value)showPop(inp,drop);});
  inp.addEventListener("blur", function(){setTimeout(function(){drop.classList.remove("show");},200);});
  inp.addEventListener("keydown", function(e){
    var its = drop.querySelectorAll(".search-item");
    if(e.key==="ArrowDown"){e.preventDefault();curFocus=Math.min(curFocus+1,its.length-1);hlight(its,curFocus);}
    else if(e.key==="ArrowUp"){e.preventDefault();curFocus=Math.max(curFocus-1,0);hlight(its,curFocus);}
    else if(e.key==="Enter"){e.preventDefault();if(curFocus>-1&&its[curFocus])its[curFocus].click();}
    else curFocus=-1;
  });
}
function hlight(its,idx){its.forEach(function(it,i){it.style.background=i===idx?"rgba(99,102,241,.15)":"";});if(its[idx])its[idx].scrollIntoView({block:"nearest"});}
function showPop(inp,drop){
  drop.innerHTML="";var pop=searchData.filter(function(d){return d.pop}).slice(0,10);if(!pop.length)pop=searchData.slice(0,10);
  pop.forEach(function(d,i){
    var rc=i===0?"top1":i===1?"top2":i===2?"top3":"";var item=document.createElement("a");item.className="search-item";item.href=d.u;
    var rank=i<3?'<span class="rank '+rc+'">#'+(i+1)+'</span>':'<span class="rank">'+(i+1)+'</span>';
    item.innerHTML=rank+'<span>'+d.t+'</span><span class="item-tag">'+d.g+'</span>';drop.appendChild(item);
  });drop.classList.add("show");
}
function doSearch(inp,drop,scope){
  var q=inp.value.trim().toLowerCase();drop.innerHTML="";if(!q){showPop(inp,drop);return;}
  var data=scope?searchData.filter(function(d){return d.s===scope;}):searchData;
  var res=[];data.forEach(function(d){
    var sc=0,tl=d.t.toLowerCase(),dl=d.d.toLowerCase();
    if(tl===q)sc=100;else if(tl.indexOf(q)===0)sc=80;else if(tl.indexOf(q)>0)sc=60;else if(dl.indexOf(q)>=0)sc=40;
    if(q.length>1){var qi=0;for(var ci=0;ci<tl.length&&qi<q.length;ci++){if(tl[ci]===q[qi])qi++;}if(qi===q.length&&sc===0)sc=10;}
    if(sc>0)res.push({d:d,s:sc});
  });res.sort(function(a,b){return b.s-a.s;});var top=res.slice(0,8);
  if(!top.length){drop.innerHTML='<div class="search-empty">\u6ca1\u6709\u5339\u914d\u7ed3\u679c</div>';}
  else{top.forEach(function(r){
    var item=document.createElement("a");item.className="search-item";item.href=r.d.u;
    var idx2=r.d.t.toLowerCase().indexOf(q);
    var th=idx2>=0?r.d.t.substring(0,idx2)+'<span class="match-text">'+r.d.t.substring(idx2,idx2+q.length)+'</span>'+r.d.t.substring(idx2+q.length):r.d.t;
    item.innerHTML='<span class="rank"></span><span>'+th+'</span><span class="item-tag">'+r.d.g+'</span>';drop.appendChild(item);
  })}drop.classList.add("show");
}
""").substitute(SD=search_data_json)
    search_init_js = "var isHm=" + repr(str(nav_depth == 0).lower()) + ";var scp=isHm==='true'?null:" + repr(html_escape(title)) + ";document.addEventListener('DOMContentLoaded',function(){initSearch('globalSearch','globalDropdown',scp);});"
    
    # Build HTML template using Template to avoid f-string { } conflicts with JS
    tmpl = Template("""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>$TITLE - $SITE_NAME</title>
  <meta name="description" content="$OG_DESC">
  <meta name="keywords" content="AI,\u5927\u6a21\u578b,GPT,Claude,DeepSeek,GitHub,\u5f00\u6e90,\u673a\u5668\u5b66\u4e60,\u6df1\u5ea6\u5b66\u4e60,\u4eba\u5de5\u667a\u80fd">
  <meta property="og:title" content="$TITLE - $SITE_NAME">
  <meta property="og:description" content="$OG_DESC">
  <meta property="og:type" content="website">
  <meta property="og:url" content="$OG_URL/index.html">
  <meta property="og:image" content="$OG_IMG">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="$TITLE - $SITE_NAME">
  <meta name="twitter:description" content="$OG_DESC">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;600;700&family=Orbitron:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  <style>$CSS_STYLE</style>
</head>
<body>
  <div class="particle" style="width:4px;height:4px;background:#818cf8;left:10%;animation-duration:18s;animation-delay:0s;"></div>
  <div class="particle" style="width:3px;height:3px;background:#22d3ee;left:25%;animation-duration:22s;animation-delay:3s;"></div>
  <div class="particle" style="width:5px;height:5px;background:#a78bfa;left:45%;animation-duration:20s;animation-delay:1s;"></div>
  <div class="particle" style="width:3px;height:3px;background:#06b6d4;left:65%;animation-duration:25s;animation-delay:5s;"></div>
  <div class="particle" style="width:4px;height:4px;background:#6366f1;left:85%;animation-duration:19s;animation-delay:2s;"></div>
  <div class="particle" style="width:2px;height:2px;background:#67e8f9;left:35%;animation-duration:23s;animation-delay:7s;"></div>
  <div class="particle" style="width:3px;height:3px;background:#818cf8;left:55%;animation-duration:21s;animation-delay:4s;"></div>
  <div class="particle" style="width:4px;height:4px;background:#a78bfa;left:75%;animation-duration:17s;animation-delay:6s;"></div>

  <nav class="glass-nav">
    <div class="max-w-6xl mx-auto px-4 sm:px-6">
      <div class="flex items-center justify-between h-14">
        <a href="$NP/index.html" class="site-logo">\U0001f9a2 AI \u8d44\u8baf\u7ad9</a>
        <div class="flex gap-3 sm:gap-5 nav-links">
          <a href="$NP/skills/index.html" class="nav-link">\u672c\u5730 Skills</a>
          <a href="$NP/plugin-skills/index.html" class="nav-link">\u63d2\u4ef6 Skills</a>
          <a href="$NP/news/index.html" class="nav-link">AI \u65b0\u95fb</a>
          <a href="$NP/github-skills/index.html" class="nav-link">GitHub Skills</a>
          <a href="$NP/top-100/index.html" class="nav-link">Top 100</a>
        </div>
      </div>
    </div>
  </nav>
  <div class="search-wrap" style="margin-top:0.8rem;">
    <span class="search-icon">\U0001f50d</span>
    <input type="text" id="globalSearch" placeholder="\u641c\u7d22\u5168\u7ad9\u6587\u7ae0..." autocomplete="off">
    <div class="search-dropdown" id="globalDropdown"></div>
  </div>
  <script>$SEARCH_JS_FUNCS
    $SEARCH_INIT_JS</script>
  <main class="max-w-5xl mx-auto px-4 sm:px-6 py-6 relative" style="z-index:1;">
    $BODY_HTML
  </main>
  <button onclick="$SCROLL_JS" class="back-to-top" id="backToTop" aria-label="\u56de\u5230\u9876\u90e8">\u2191</button>
  <button onclick="$THEME_JS" class="theme-toggle" id="themeToggle" aria-label="\u5207\u6362\u4e3b\u9898">\u2600</button>
  <script>$SCROLL_EVENT_JS; $THEME_INIT_JS;</script>
  <footer class="page-footer">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 text-center">
      <p>&copy; $YEAR $SITE_NAME &middot; \u7531 Codex \u6784\u5efa\u4e0e\u7ef4\u62a4</p>
      <p style="color:var(--text-muted);font-size:0.72rem;margin-top:0.25rem;">\u6570\u636e\u6765\u6e90\u6807\u6ce8\u4e8e\u5404\u6587\u7ae0\u5e95\u90e8 &middot; \u63a2\u7d22 AI \u7684\u65e0\u9650\u53ef\u80fd</p>
    </div>
  </footer>
</body>
</html>""")
    return tmpl.substitute(
        TITLE=html_escape(title),
        SITE_NAME=SITE_NAME,
        OG_DESC=og_desc,
        OG_URL=og_url_path,
        OG_IMG=og_image or og_url_path + "/images/hero.svg",
        NP=np,
        CSS_STYLE=CSS_STYLE,
        BODY_HTML=body_html,
        SEARCH_JS_FUNCS=search_js_funcs,
        SEARCH_INIT_JS=search_init_js,
        SCROLL_JS=scroll_js,
        THEME_JS=theme_js,
        SCROLL_EVENT_JS=scroll_event_js,
        THEME_INIT_JS=theme_init_js,
        YEAR=str(NOW.year),
    )
'''

        # Replace from the return statement to the next function
        next_func = content.find("\ndef ", ret_idx)
        content = content[:ret_idx] + new_return + content[next_func:]

        print(f"Replaced page_frame template (Template-based) at line ~{content[:ret_idx].count(chr(10))}")

# ===== 4. Add bottom bar to list_page =====
content = content.replace(
    "</div>\\n<script>\\n{filter_js}\\n</script>\\n\\'\\'\\'\\\"",
    "</div>\\n<script>\\n{filter_js}\\n</script>\\n<div class=\\\"bottom-bar\\\">\\n  <a href=\\\"{np}/index.html\\\" class=\\\"cyber-btn\\\">&larr; \u8fd4\u56de\u9996\u9875</a>\\n  <a href=\\\"javascript:history.back()\\\" class=\\\"cyber-btn\\\">\U0001f3e0 \u8fd4\u56de\u4e0a\u4e00\u9875</a>\\n</div>\\n\\'\\'\\'\\\""
)

# ===== 5. Add module-specific search + bottom buttons to build() =====
# This part needs build() modifications which will be done in a separate step

with open("src/build.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Rebuild complete!")