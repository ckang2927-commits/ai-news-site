import os, re
P = "C:/Users/kangg/Desktop/网站搭建/ai-news-site/src/build.py"
c = open(P, "r", encoding="utf-8").read()

# 1) Fix hardcoded filter pills -> dynamic
lines = c.split("\n")
in_list = False
result = []
i = 0
while i < len(lines):
    l = lines[i]
    # Detect the hardcoded pills section in list_page body f-string
    if 'filter-pill active' in l and "filterCards(this," in l and "filter-pills" not in l:
        # Skip old hardcoded pills, insert dynamic placeholder
        while i < len(lines) and ('filter-pill' in lines[i] or '</div>' == lines[i].strip()):
            i += 1
        result.append('  <a href="javascript:void(0)" class="filter-pill active" data-cat="all">全部</a>')
        result.append('  {custom_pills_str}')
        result.append('</div>')
        print(f"  Replaced pills at line {i}")
        continue
    result.append(l)
    i += 1
c2 = "\n".join(result)

# 2) Fix nav active class CSS
if ".glass-nav .nav-link.active" not in c2:
    nav_css = "\n    .glass-nav .nav-link.active { color:var(--accent-2); }\n"
    nav_css += "    .glass-nav .nav-link.active::after { width:100%; }\n"
    c2 = c2.replace('@media (max-width:640px)', nav_css + '        @media (max-width:640px)')
    print("  Added nav active CSS")

# 3) Fix Enter key handler
c2 = c2.replace(
    'else if(e.key==="Enter"){e.preventDefault();if(curFocus>-1&&its[curFocus])its[curFocus].click();}',
    'else if(e.key==="Enter"){e.preventDefault();if(drop.classList.contains("show")){var fi=drop.querySelector(".search-item");if(fi)fi.click();}}'
)
print("  Fixed Enter handler")

# 4) Fix logo
c2 = c2.replace('\U0001f9e2 AI \u8d44\u8baf\u7ad9', '\u26a1 AI \u8d44\u8baf\u7ad9')

open(P, "w", encoding="utf-8").write(c2)
print("\n[DONE] All fixes complete!")