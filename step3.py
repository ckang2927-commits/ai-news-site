import sys, io, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

with open("src/build.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add search_data parameter to page_frame
content = content.replace(
    "def page_frame(title, body_html, nav_depth=0, og_desc=None, og_image=None):",
    "def page_frame(title, body_html, nav_depth=0, og_desc=None, og_image=None, search_data=None):"
)

# 2. Add json import
content = content.replace("import re, os", "import re, os, json")

# 3. Add search JS variable after theme_init_js
search_js_code = '''
    search_json = json.dumps(search_data or [], ensure_ascii=False)
    search_js = """var searchData = SEARCH_DATA_PLACEHOLDER;
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
    var rank=i<3?"<span class=\\"rank "+rc+"\\">#"+(i+1)+"</span>":"<span class=\\"rank\\">"+(i+1)+"</span>";
    item.innerHTML=rank+"<span>"+d.t+"</span><span class=\\"item-tag\\">"+d.g+"</span>";drop.appendChild(item);
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
  if(!top.length){drop.innerHTML="<div class=\\"search-empty\\">\u6ca1\u6709\u5339\u914d\u7ed3\u679c</div>";}
  else{top.forEach(function(r){
    var item=document.createElement("a");item.className="search-item";item.href=r.d.u;
    var idx2=r.d.t.toLowerCase().indexOf(q);
    var th=idx2>=0?r.d.t.substring(0,idx2)+"<span class=\\"match-text\\">"+r.d.t.substring(idx2,idx2+q.length)+"</span>"+r.d.t.substring(idx2+q.length):r.d.t;
    item.innerHTML="<span class=\\"rank\\"></span><span>"+th+"</span><span class=\\"item-tag\\">"+r.d.g+"</span>";drop.appendChild(item);
  })}drop.classList.add("show");
}
""".replace("SEARCH_DATA_PLACEHOLDER", search_json)
'''

content = content.replace(
    '    theme_init_js = "if(localStorage.getItem(theme)===light)document.body.classList.add(light-theme)"',
    '    theme_init_js = "if(localStorage.getItem(theme)===light)document.body.classList.add(light-theme)"' + search_js_code
)

# 4. Update main to include search init script
old_main = '  <main class="max-w-5xl mx-auto px-4 sm:px-6 py-6 relative" style="z-index:1;">\n    {body_html}\n  </main>'
new_main = '''  <script>
    {search_js}
    var isHome = ''' + '"' + '{str(nav_depth == 0).lower()}' + '"' + ''';
    document.addEventListener("DOMContentLoaded", function() {
      var scope = isHome ? null : "''' + '"' + '{html_escape(title)}' + '"' + '''";
      initSearch("globalSearch", "globalDropdown", scope);
    });
  </script>
  <main class="max-w-5xl mx-auto px-4 sm:px-6 py-6 relative" style="z-index:1;">
    {body_html}
  </main>'''

content = content.replace(old_main, new_main)

# 5. Add bottom buttons to list_page
content = content.replace(
    '</div>\n<script>\n{filter_js}\n</script>\n\'\'\'',
    '</div>\n<script>\n{filter_js}\n</script>\n<div class="bottom-bar">\n  <a href="{np}/index.html" class="cyber-btn">&larr; \u8fd4\u56de\u9996\u9875</a>\n  <a href="javascript:history.back()" class="cyber-btn">\U0001f3e0 \u8fd4\u56de\u4e0a\u4e00\u9875</a>\n</div>\n\'\'\''
)

# 6. Update page_frame calls to pass search_data
content = content.replace(
    'return page_frame(title, body, nav_depth=nav_d, og_desc=title)',
    'return page_frame(title, body, nav_depth=nav_d, og_desc=title, search_data=search_data)'
)
content = content.replace(
    'return page_frame("\u9996\u9875", body, nav_depth=nav_d)',
    'return page_frame("\u9996\u9875", body, nav_depth=nav_d, search_data=search_data)'
)

# 7. Update function signatures
content = content.replace(
    "def detail_page(title, content_html, source=\"\", nav_d=1):",
    "def detail_page(title, content_html, source=\"\", nav_d=1, search_data=None):"
)
content = content.replace(
    "def list_page(title, desc, cards_html, nav_d=1):",
    "def list_page(title, desc, cards_html, nav_d=1, search_data=None):"
)
content = content.replace(
    "def index_page(module_cards):",
    "def index_page(module_cards, search_data=None):"
)

# 8. Update build() to collect and pass search data
content = content.replace(
    "def build():",
    "def build():\n    all_search_data = []"
)

content = content.replace(
    '        module_infos.append((label, desc, len(entries), slug))',
    '''        module_infos.append((label, desc, len(entries), slug))
        module_search_data = []
        for ei, e in enumerate(entries):
            t = e.get("title", e.get("name", "\\u672a\\u547d\\u540d"))
            module_search_data.append({
                "t": t,
                "u": f"{slug}/{e[chr(39)+chr(115)+chr(108)+chr(117)+chr(103)]}.html",
                "d": e.get("description", ""),
                "g": label,
                "s": label,
                "tags": e.get("tags", ""),
                "pop": ei < 3
            })
        all_search_data.extend(module_search_data)'''
)

# Fix the slug reference - use proper escaping
content = content.replace("chr(39)+chr(115)+chr(108)+chr(117)+chr(103)", "'slug'")

# 9. Update function calls in build()
content = content.replace(
    'list_html = list_page(label, desc, "\\n".join(cards))',
    'list_html = list_page(label, desc, "\\n".join(cards), search_data=module_search_data)'
)
content = content.replace(
    'detail_html = detail_page(title, e["html"], source)',
    'detail_html = detail_page(title, e["html"], source, search_data=all_search_data)'
)
content = content.replace(
    'f.write(index_page("\\n".join(module_cards)))',
    'f.write(index_page("\\n".join(module_cards), search_data=all_search_data))'
)

with open("src/build.py", "w", encoding="utf-8") as f:
    f.write(content)

print("All modifications done!")