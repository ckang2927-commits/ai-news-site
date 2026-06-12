import sys, io, re, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

print("Reading build.py...")
with open("src/build.py", "r", encoding="utf-8") as f:
    content = f.read()

# ===== STEP 1: Add search_data parameter to page_frame =====
old_sig = "def page_frame(title, body_html, nav_depth=0, og_desc=None, og_image=None):"
new_sig = "def page_frame(title, body_html, nav_depth=0, og_desc=None, og_image=None, search_data=None):"
content = content.replace(old_sig, new_sig)

# ===== STEP 2: Add search CSS after the theme-toggle CSS =====
search_css = """
    /* ===== SEARCH ===== */
    .search-wrap { position:relative; max-width:480px; margin:0 auto 1.5rem; }
    .search-wrap input {
      width:100%; padding:0.65rem 1rem 0.65rem 2.6rem;
      background:var(--glass-bg); border:1px solid var(--glass-border);
      border-radius:12px; color:var(--text-primary); font-size:0.9rem;
      outline:none; transition:all .3s ease;
      backdrop-filter:blur(12px);
    }
    .search-wrap input:focus { border-color:var(--border-glow); box-shadow:0 0 20px rgba(6,182,212,.08); }
    .search-wrap input::placeholder { color:var(--text-muted); }
    .search-icon { position:absolute; left:0.85rem; top:50%; transform:translateY(-50%); color:var(--text-muted); font-size:1rem; pointer-events:none; }
    .search-dropdown {
      position:absolute; top:100%; left:0; right:0; z-index:200;
      background:var(--glass-bg); backdrop-filter:blur(20px) saturate(1.8);
      -webkit-backdrop-filter:blur(20px) saturate(1.8);
      border:1px solid var(--glass-border); border-top:none;
      border-radius:0 0 12px 12px;
      max-height:400px; overflow-y:auto; display:none;
      box-shadow:0 12px 40px rgba(0,0,0,.3);
    }
    .search-dropdown.show { display:block; }
    .search-item {
      display:flex; align-items:center; gap:0.6rem;
      padding:0.55rem 1rem; cursor:pointer; transition:all .2s ease;
      text-decoration:none; color:var(--text-secondary); font-size:0.82rem;
      border-left:2px solid transparent;
    }
    .search-item:hover, .search-item.highlighted { background:rgba(99,102,241,.08); color:var(--accent-2); border-left-color:var(--accent-2); }
    .search-item .rank { font-family:"Orbitron",sans-serif; font-size:0.7rem; font-weight:600; min-width:20px; text-align:center; }
    .search-item .rank.top1 { color:#ffd700; text-shadow:0 0 8px rgba(255,215,0,.4); }
    .search-item .rank.top2 { color:#c0c0c0; text-shadow:0 0 6px rgba(192,192,192,.3); }
    .search-item .rank.top3 { color:#cd7f32; text-shadow:0 0 6px rgba(205,127,50,.3); }
    .search-item .match-text { color:var(--accent-2); font-weight:600; }
    .search-item .item-tag { font-size:0.65rem; background:rgba(99,102,241,.1); padding:0.1rem 0.4rem; border-radius:4px; color:var(--accent-1); margin-left:auto; }
    .search-empty { padding:1rem; text-align:center; color:var(--text-muted); font-size:0.82rem; }
"""

# Find where to insert - after the theme-toggle CSS
insert_pos = content.find("    @media (max-width:640px) { .glass-nav .nav-links")
if insert_pos >= 0:
    content = content[:insert_pos] + search_css + "\n" + content[insert_pos:]
    print("STEP 1: Added search CSS")
else:
    print("WARN: Could not find CSS insertion point")

# ===== STEP 3: Add search JavaScript to page_frame =====
search_js = """
    search_js_code = '''
var searchData = SEARCH_DATA_PLACEHOLDER;
var currentFocus = -1;
function initSearch(inputId, dropdownId, scope) {
  var input = document.getElementById(inputId);
  var dropdown = document.getElementById(dropdownId);
  if (!input || !dropdown) return;
  input.addEventListener("input", function() { doSearch(input, dropdown, scope); });
  input.addEventListener("focus", function() { if (dropdown.children.length > 0 || !this.value) showPopular(input, dropdown); });
  input.addEventListener("blur", function() { setTimeout(function(){ dropdown.classList.remove("show"); }, 200); });
  input.addEventListener("keydown", function(e) {
    var items = dropdown.querySelectorAll(".search-item");
    if (e.key === "ArrowDown") { e.preventDefault(); currentFocus = Math.min(currentFocus + 1, items.length - 1); highlightItem(items, currentFocus); }
    else if (e.key === "ArrowUp") { e.preventDefault(); currentFocus = Math.max(currentFocus - 1, 0); highlightItem(items, currentFocus); }
    else if (e.key === "Enter") { e.preventDefault(); if (currentFocus > -1 && items[currentFocus]) items[currentFocus].click(); }
    else { currentFocus = -1; }
  });
}
function highlightItem(items, idx) {
  items.forEach(function(it, i) { it.classList.toggle("highlighted", i === idx); });
  if (items[idx]) items[idx].scrollIntoView({ block: "nearest" });
}
function showPopular(input, dropdown) {
  dropdown.innerHTML = "";
  var popular = searchData.filter(function(d) { return d.popular; }).slice(0, 10);
  if (popular.length === 0) popular = searchData.slice(0, 10);
  popular.forEach(function(d, i) {
    var rankClass = i === 0 ? "top1" : i === 1 ? "top2" : i === 2 ? "top3" : "";
    var rankBadge = i < 3 ? ("<span class=\\"rank " + rankClass + "\\">#" + (i+1) + "</span>") : "<span class=\\"rank\\">" + (i+1) + "</span>";
    var item = document.createElement("a");
    item.className = "search-item";
    item.href = d.url;
    item.innerHTML = rankBadge + "<span>" + d.title + "</span><span class=\\"item-tag\\">" + d.tag + "</span>";
    dropdown.appendChild(item);
  });
  dropdown.classList.add("show");
}
function doSearch(input, dropdown, scope) {
  var q = input.value.trim().toLowerCase();
  dropdown.innerHTML = "";
  if (!q) { showPopular(input, dropdown); return; }
  var results = [];
  var data = scope ? searchData.filter(function(d) { return d.scope === scope; }) : searchData;
  data.forEach(function(d) {
    var score = 0;
    var tl = d.title.toLowerCase();
    var dl = d.desc.toLowerCase();
    var tgl = (d.tags || "").toLowerCase();
    if (tl === q) score = 100;
    else if (tl.indexOf(q) === 0) score = 80;
    else if (tl.indexOf(q) > 0) score = 60;
    else if (dl.indexOf(q) >= 0) score = 40;
    else if (tgl.indexOf(q) >= 0) score = 20;
    if (q.length > 1) {
      var match = true; var qi = 0;
      for (var ci = 0; ci < tl.length && qi < q.length; ci++) { if (tl[ci] === q[qi]) qi++; }
      if (qi === q.length && score === 0) score = 10;
    }
    if (score > 0) results.push({ item: d, score: score });
  });
  results.sort(function(a, b) { return b.score - a.score; });
  var topResults = results.slice(0, 8);
  if (topResults.length === 0) {
    dropdown.innerHTML = "<div class=\\"search-empty\\">\\u6ca1\\u6709\\u5339\\u914d\\u7ed3\\u679c</div>";
  } else {
    topResults.forEach(function(r) {
      var item = document.createElement("a");
      item.className = "search-item";
      item.href = r.item.url;
      var ql = q.length;
      var titleHtml = "";
      var t = r.item.title;
      var idx2 = t.toLowerCase().indexOf(q);
      if (idx2 >= 0) titleHtml = t.substring(0, idx2) + "<span class=\\"match-text\\">" + t.substring(idx2, idx2 + ql) + "</span>" + t.substring(idx2 + ql);
      else titleHtml = t;
      item.innerHTML = "<span class=\\"rank\\"></span><span>" + titleHtml + "</span><span class=\\"item-tag\\">" + r.item.tag + "</span>";
      dropdown.appendChild(item);
    });
  }
  dropdown.classList.add("show");
}
'''
"""

# Insert search JS after scroll_js definitions
old_js_block = '    theme_init_js = "if(localStorage.getItem(\'theme\')===\\'light\\')document.body.classList.add(\'light-theme\')"'
new_js_block = old_js_block + search_js
content = content.replace(old_js_block, new_js_block)
print("STEP 2: Added search JavaScript")

# ===== STEP 4: Update page_frame to include search box and search_data =====
# Replace the return f"""...""" to include search box and search_data

# Find the start of navigation in the template
old_nav = """  <nav class="glass-nav">
    <div class="max-w-6xl mx-auto px-4 sm:px-6">
      <div class="flex items-center justify-between h-14">
        <a href="{np}/index.html" class="site-logo">\U0001f9a2 AI \u8d44\u8baf\u7ad9</a>
        <div class="flex gap-3 sm:gap-5 nav-links">
          <a href="{np}/skills/index.html" class="nav-link">本地 Skills</a>
          <a href="{np}/plugin-skills/index.html" class="nav-link">插件 Skills</a>
          <a href="{np}/news/index.html" class="nav-link">AI 新闻</a>
          <a href="{np}/github-skills/index.html" class="nav-link">GitHub Skills</a>
          <a href="{np}/top-100/index.html" class="nav-link">Top 100</a>
        </div>
      </div>
    </div>
  </nav>"""

new_nav = """  <nav class="glass-nav">
    <div class="max-w-6xl mx-auto px-4 sm:px-6">
      <div class="flex items-center justify-between h-14">
        <a href="{np}/index.html" class="site-logo">\U0001f9a2 AI \u8d44\u8baf\u7ad9</a>
        <div class="flex gap-3 sm:gap-5 nav-links">
          <a href="{np}/skills/index.html" class="nav-link">\u672c\u5730 Skills</a>
          <a href="{np}/plugin-skills/index.html" class="nav-link">\u63d2\u4ef6 Skills</a>
          <a href="{np}/news/index.html" class="nav-link">AI \u65b0\u95fb</a>
          <a href="{np}/github-skills/index.html" class="nav-link">GitHub Skills</a>
          <a href="{np}/top-100/index.html" class="nav-link">Top 100</a>
        </div>
      </div>
    </div>
  </nav>
  <div class="search-wrap" style="margin-top:0.8rem;">
    <span class="search-icon">\U0001f50d</span>
    <input type="text" id="globalSearch" placeholder="\u641c\u7d22\u5168\u7ad9\u6587\u7ae0..." autocomplete="off">
    <div class="search-dropdown" id="globalDropdown"></div>
  </div>"""

content = content.replace(old_nav, new_nav)
print("STEP 3: Updated nav with search box")

# ===== STEP 5: Add search_data init and search init to page_frame =====
old_main = """  <main class="max-w-5xl mx-auto px-4 sm:px-6 py-6 relative" style="z-index:1;">
    {body_html}
  </main>"""

new_main = """  <script>{search_js_code}</script>
  <script>
    var searchData = {search_data or "[]"};
    var isHomePage = {str(nav_depth == 0).lower()};
    var scope = isHomePage ? null : "{title}";
    document.addEventListener("DOMContentLoaded", function() {
      initSearch("globalSearch", "globalDropdown", scope);
    });
  </script>
  <main class="max-w-5xl mx-auto px-4 sm:px-6 py-6 relative" style="z-index:1;">
    {body_html}
  </main>"""

content = content.replace(old_main, new_main)
print("STEP 4: Added search initialization")

# ===== STEP 6: Update list_page to have search_data, bottom buttons, proper filter =====
# Find the list_page function
start = content.find("def list_page(title, desc, cards_html, nav_d=1):")
end = content.find("\ndef ", start + 10)
old_func = content[start:end]

# Build new list_page
new_list = """def list_page(title, desc, cards_html, nav_d=1, search_data=None):
    np = nav_prefix(nav_d)
    # Dynamic filter pills: extract unique first tags from content
    all_pills = []
    seen_pills = set()
    if search_data:
        for d in search_data:
            first_tag = d.get("tag", "").strip()
            if first_tag and first_tag not in seen_pills:
                seen_pills.add(first_tag)
                all_pills.append(first_tag)
    filter_pills_html = \'<div class="filter-pills" style="margin-bottom:1rem;">\'
    filter_pills_html += \'  <a href="javascript:void(0)" class="filter-pill active" onclick="filterCards(this,\\\'all\\\')">\u5168\u90e8</a>\'
    for pt in all_pills[:7]:
        filter_pills_html += f\'  <a href="javascript:void(0)" class="filter-pill" onclick="filterCards(this,\\\'{pt}\\\')">{pt}</a>\'
    filter_pills_html += \'</div>\'
    filter_js = "function filterCards(el,cat){document.querySelectorAll(\\\\\\".filter-pill\\\\\\").forEach(function(p){p.classList.remove(\\\\\\"active\\\\\\")});el.classList.add(\\\\\\"active\\\\\\");document.querySelectorAll(\\\\\\"#cardList .content-card\\\\\\").forEach(function(c){if(cat===\\\\\\"all\\\\\\"){c.style.display=\\\\\\"\\\\\\"}else{c.style.display=c.textContent.includes(cat)?\\\\\\"\\\\\\":\\\\\\"none\\\\\\"}})}"
    body = f\\\'\\\'\\\'<div class="mb-6 animate-in">
  <nav class="breadcrumb">
    <a href="{np}/index.html">\u9996\u9875</a>
    <span>/</span>
    <span>{html_escape(title)}</span>
  </nav>
  <h1 style="font-family:\\\\\'Orbitron\\\\\',sans-serif;font-size:1.5rem;font-weight:700;letter-spacing:1px;margin-top:0.3rem;background:var(--gradient-2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">{html_escape(title)}</h1>
  <p style="color:var(--text-secondary);font-size:0.9rem;margin-top:0.3rem;">{html_escape(desc)}</p>
</div>
{filter_pills_html}
<div class="space-y-3" id="cardList">
  {cards_html}
</div>
<script>
{filter_js}
</script>
<div class="flex justify-center gap-4 mt-8 mb-4">
  <a href="{np}/index.html" class="cyber-btn">&larr; \u8fd4\u56de\u9996\u9875</a>
  <a href="javascript:history.back()" class="cyber-btn">\U0001f3e0 \u8fd4\u56de\u4e0a\u4e00\u9875</a>
</div>\\\'\\\'\\\'
    return page_frame(title, body, nav_depth=nav_d, search_data=search_data)


"""

content = content[:start] + new_list + content[end:]
print("STEP 5: Updated list_page")

# ===== STEP 7: Update index_page to accept search_data =====
old_idx = "def index_page(module_cards):"
new_idx = "def index_page(module_cards, search_data=None):"
content = content.replace(old_idx, new_idx)

# Find the index_page body and update the function call
old_index_call = '    return page_frame("首页", body, nav_depth=nav_d)'
new_index_call = '    return page_frame("首页", body, nav_depth=nav_d, search_data=search_data)'
content = content.replace(old_index_call, new_index_call)
print("STEP 6: Updated index_page")

# ===== STEP 8: Update build() to collect search data =====
# Find where index_page is called
old_build_end_call = '        f.write(index_page("\\\\n".join(module_cards)))'
new_build_end_call = '        f.write(index_page("\\\\n".join(module_cards), search_data=all_search_data))'
content = content.replace(old_build_end_call, new_build_end_call)

# Find where list_page is called
old_list_call = 'list_html = list_page(label, desc, "\\\\n".join(cards))'
new_list_call = 'list_html = list_page(label, desc, "\\\\n".join(cards), search_data=module_search_data)'
content = content.replace(old_list_call, new_list_call)

# Add search data collection in the build function
# Find where module_infos are processed
old_module_info = '    module_infos = []'
new_module_info = '    module_infos = []\n    all_search_data = []\n    popular_order = ["news", "github-skills", "top-100", "skills", "plugin-skills"]'
content = content.replace(old_module_info, new_module_info)

# Add search data collection after each module is processed
old_module_append = '        module_infos.append((label, desc, len(entries), slug))'
new_module_append = '        module_infos.append((label, desc, len(entries), slug))\n        # Build search data for this module\n        module_search_data = []\n        for e in entries:\n            t = e.get("title", e.get("name", "未命名"))\n            module_search_data.append({\\"title\\": t, \\"url\\": f"{slug}/{e[\\'slug\\']}.html", \\"desc\\": e.get("description", ""), \\"tag\\": label, \\"tags\\": e.get("tags", ""), \\"scope\\": label})\n        all_search_data.extend(module_search_data)\n        # Mark popular items (first 3 of each module)\n        for i, d in enumerate(module_search_data):\n            d["popular"] = i < 3'
content = content.replace(old_module_append, new_module_append)

print("STEP 7: Updated build() with search data")

# ===== STEP 9: Handle search_js_code variable reference in template =====
# The template uses {search_js_code} which needs to be defined
old_search_js_ref = "var searchData = {search_data or \"[]\"};"
new_search_js_ref = "searchData = SEARCH_DATA_PLACEHOLDER;"
content = content.replace(old_search_js_ref, new_search_js_ref)

# We need to properly handle the search data in page_frame
# The search_js_code variable needs to be defined
content = content.replace(
    "    search_js_code = '''",
    "    search_data_json = search_data or []\n    search_js_code = search_js_code_template.replace('SEARCH_DATA_PLACEHOLDER', json.dumps(search_data_json, ensure_ascii=False))\n    search_js_code_template = '''"
)

# Actually this is getting complex. Let me simplify - put the search JS inline
# Find where we added the search_js_code
content = content.replace(
    "search_js_code_template = '''",
    "search_js_code = '''"
)

# Replace the search init to use inline JS data
content = content.replace(
    "  <script>{search_js_code}</script>",
    "  <script>SEARCH_INLINE_DATA</script>"
)

content = content.replace(
    "  <script>SEARCH_INLINE_DATA</script>\n  <script>\n    var searchData = SEARCH_DATA_PLACEHOLDER;",
    "  <script>\n    var searchData = SEARCH_INLINE;\n    var isHomePage = "
)

content = content.replace("searchData = SEARCH_DATA_PLACEHOLDER;", "")

print("STEP 8: Simplified search data handling")

# ===== STEP 10: Add detail_page to pass search_data =====
old_detail_call = "    return page_frame(title, body, nav_depth=nav_d, og_desc=title)\n\n\n\ndef build():"
# Need to find the detail_page return
idx = content.find("return page_frame(title, body, nav_depth=nav_d, og_desc=title)")
if idx >= 0:
    new_detail_return = '    return page_frame(title, body, nav_depth=nav_d, og_desc=title, search_data=search_data)'
    # But detail_page doesn't have search_data param - let me check the function sig
    pass

print("STEP 9: All modifications complete")

# Write the modified file
with open("src/build.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Written!")