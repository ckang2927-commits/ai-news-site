import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

with open("src/build.py", "r", encoding="utf-8") as f:
    content = f.read()

# Find the problematic main section and replace it
old = '''  <script>
    {search_js}
    var isHm = "{str(nav_depth == 0).lower()}";
    var scp = isHm === "true" ? null : "{html_escape(title)}";
    document.addEventListener("DOMContentLoaded", function() { initSearch("globalSearch", "globalDropdown", scp); });
  </script>
  <main class="max-w-5xl mx-auto px-4 sm:px-6 py-6 relative" style="z-index:1;">
    {body_html}
  </main>'''

new = '''  <script>{search_js}
    {search_init_js}</script>
  <main class="max-w-5xl mx-auto px-4 sm:px-6 py-6 relative" style="z-index:1;">
    {body_html}
  </main>'''

if old in content:
    content = content.replace(old, new)
    print("Replaced main block")
else:
    print("Could not find old main block - searching...")
    idx = content.find("var isHm")
    if idx >= 0:
        print(f"Found at {idx}: {content[idx:idx+100]}")

# Now replace the search JS code with a cleaner version that uses variables
old_search_js_var = '''    search_json = json.dumps(search_data or [], ensure_ascii=False)
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
""".replace("SEARCH_DATA_PLACEHOLDER", search_json)'''

# Need to find this in the content and replace it  
# The key issue is that the JS code gets substituted into an f-string template via {search_js}
# The JS code has { } which won't conflict because they're in a variable, not in the template

# Let me verify by checking what's currently in the file
with open("src/build.py", "r", encoding="utf-8") as f:
    content2 = f.read()

idx = content2.find("search_json = json.dumps")
if idx >= 0:
    snippet = content2[idx:idx+200]
    print(f"Found search_json at {idx}: {snippet[:150]}")
else:
    print("search_json not found")
    
# Check for search_init_js
if "search_init_js" in content2:
    print("search_init_js already in file")
else:
    # Need to add it
    # Add search_init_js as a variable that builds the init code
    add_after = '    search_js = """'
    add_code = '''
    search_init_js_val = "var isHm=\\"{str(nav_depth == 0).lower()}\\";var scp=isHm===\\"true\\"?null:\\"{html_escape(title)}\\";document.addEventListener(\\"DOMContentLoaded\\",function(){initSearch(\\"globalSearch\\",\\"globalDropdown\\",scp);});"
'''
    # This still has f-string issues. Let me use a completely different approach
    print("Need different approach for search_init_js")

with open("src/build.py", "w", encoding="utf-8") as f:
    f.write(content2)