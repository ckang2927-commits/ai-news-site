import sys
sys.stdout.reconfigure(encoding="utf-8")
P = "C:/Users/kangg/Desktop/网站搭建/ai-news-site/src/build.py"
c = open(P, "r", encoding="utf-8").read()

changes = []

# ===== Fix 1: content_card - add img_path parameter =====
old_sig = "def content_card(title, desc, link, tags, date_str):"
new_sig = "def content_card(title, desc, link, tags, date_str, img_path=\"images/\"):"
c = c.replace(old_sig, new_sig)
changes.append("Added img_path param to content_card")

# ===== Fix 2: Replace the icon logic with SVG =====
# Find the icon selection and return block
old_icon_block = '''icon_emoji = "\\U0001f4d6"
    tag_text = " ".join(tags).lower()
    if any(x in tag_text for x in ["news", "ai", "\\u65b0\\u95fb", "\\u5927\\u6a21\\u578b"]):
        icon_emoji = "\\U0001f9e0"
    elif any(x in tag_text for x in ["\\u5de5\\u5177", "\\u6846\\u67b6", "tool", "framework"]):
        icon_emoji = "\\U0001f527"
    elif "github" in tag_text:
        icon_emoji = "\\U0001f525"
    elif "skill" in tag_text:
        icon_emoji = "\\U0001f4bb"
    desc_preview = html_escape(desc[:150])
    return f\'<a href="{link}" class="content-card" style="padding-bottom:0.75rem;">\\n  <div class="flex gap-3">\\n    <div class="featured-image" style="width:70px;height:70px;min-width:70px;border-radius:10px;margin-bottom:0;flex-shrink:0;display:flex;align-items:center;justify-content:center;">\\n      <span style="font-size:1.8rem;opacity:0.7;">{icon_emoji}</span>\\n    </div>'''

new_icon_block = '''tag_text = " ".join(tags).lower()
    icon_map = [
        ("ai", "ai-brain.svg"), ("news", "ai-brain.svg"), ("\\u65b0\\u95fb", "ai-brain.svg"),
        ("tool", "ai-tool.svg"), ("\\u5de5\\u5177", "ai-tool.svg"), ("framework", "ai-framework.svg"), ("\\u6846\\u67b6", "ai-framework.svg"),
        ("github", "ai-github.svg"), ("skill", "ai-skill.svg"),
        ("data", "ai-data.svg"), ("\\u6570\\u636e", "ai-data.svg"), ("test", "ai-data.svg"), ("\\u6d4b\\u8bd5", "ai-data.svg"),
        ("top", "ai-star.svg"), ("star", "ai-star.svg"),
    ]
    icon_file = "ai-default.svg"
    for kw, fn in icon_map:
        if kw in tag_text:
            icon_file = fn
            break
    desc_preview = html_escape(desc[:150])
    return f\'<a href="{link}" class="content-card" style="padding-bottom:0.75rem;">\\n  <div class="flex gap-3">\\n    <div class="featured-image" style="width:70px;height:70px;min-width:70px;border-radius:10px;margin-bottom:0;flex-shrink:0;display:flex;align-items:center;justify-content:center;overflow:hidden;padding:6px;">\\n      <img src="{img_path}{icon_file}" alt="" style="width:100%;height:100%;object-fit:contain;">\\n    </div>'''

if old_icon_block in c:
    c = c.replace(old_icon_block, new_icon_block)
    changes.append("Updated content_card icon logic to Q-version SVGs")
else:
    changes.append("WARN: icon block not found")
    # Debug: find the icon_emoji line
    idx = c.find("icon_emoji")
    if idx > 0:
        changes.append(f"  icon_emoji found at {idx}: ...{c[idx:idx+60]}...")
    else:
        # Maybe already replaced?
        if "ai-default.svg" in c:
            changes.append("  Already updated")

# ===== Fix 3: Update content_card calls in build() to pass img_path =====
# On homepage (index_page context): img_path="images/"
# On list pages: img_path="../images/"
# Find the card building loop
old_card_call = "cards.append(content_card(title, desc_text, link, tags, date_str))"
new_card_call = "cards.append(content_card(title, desc_text, link, tags, date_str, img_path=\"../images/\"))"
c = c.replace(old_card_call, new_card_call)
changes.append("Updated card calls with img_path=../images/")

# ===== Fix 4: Update module cards on homepage =====
old_mod_card = '''    module_cards.append(f\'''\n    <a href="{slug}/index.html" class="block bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg hover:border-primary-300 transition-all duration-200 group">\n      <div class="text-3xl mb-3">{icon}</div>\n      <h2 class="text-lg font-semibold text-gray-900 group-hover:text-primary-600 transition">{label}</h2>\n      <p class="text-sm text-gray-500 mt-1">{desc}</p>\n      <p class="text-xs text-primary-500 mt-2">共 {count} 篇文章 &rarr;</p>\n    </a>\')'''

new_mod_card = '''    module_cards.append(f\'''\n    <a href="{slug}/index.html" class="block bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg hover:border-primary-300 transition-all duration-200 group">\n      <div class="mb-3" style="display:flex;justify-content:center;"><img src="images/module-{slug}.svg" alt="{label}" style="width:80px;height:80px;border-radius:12px;"></div>\n      <h2 class="text-lg font-semibold text-gray-900 group-hover:text-primary-600 transition">{label}</h2>\n      <p class="text-sm text-gray-500 mt-1">{desc}</p>\n      <p class="text-xs text-primary-500 mt-2">共 {count} 篇文章 &rarr;</p>\n    </a>\')'''

if old_mod_card in c:
    c = c.replace(old_mod_card, new_mod_card)
    changes.append("Updated module cards with Q-version SVGs")
else:
    changes.append("WARN: module card template not found")
    # Check what's in the file
    idx = c.find('module_cards.append')
    if idx > 0:
        end = c.find("\\n    </a>\\')", idx)
        if end > 0:
            end += 15
            changes.append(f"  Found at {idx}: {repr(c[idx:end])[:80]}...")

open(P, "w", encoding="utf-8").write(c)
print("\n".join(f"  {ch}" for ch in changes))
print("\n[DONE]")