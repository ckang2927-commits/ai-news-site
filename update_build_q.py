import sys
sys.stdout.reconfigure(encoding="utf-8")
P = "C:/Users/kangg/Desktop/网站搭建/ai-news-site/src/build.py"
c = open(P, "r", encoding="utf-8").read()

changes = []

# ===== 1. Replace content_card feature image with SVG =====
# Find the featured-image div and icon selection logic
old_feature = '''    icon_emoji = "\\U0001f4d6"
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

new_feature = '''    # Map tags to Q-version SVG icons
    icon_map = {
        "ai": "ai-brain.svg", "news": "ai-brain.svg", "\\u65b0\\u95fb": "ai-brain.svg", "\\u5927\\u6a21\\u578b": "ai-brain.svg",
        "tool": "ai-tool.svg", "\\u5de5\\u5177": "ai-tool.svg", "framework": "ai-framework.svg", "\\u6846\\u67b6": "ai-framework.svg",
        "github": "ai-github.svg", "skill": "ai-skill.svg",
        "\\u6570\\u636e": "ai-data.svg", "data": "ai-data.svg", "test": "ai-data.svg", "\\u6d4b\\u8bd5": "ai-data.svg",
        "top": "ai-star.svg", "star": "ai-star.svg", "\\u6392\\u884c": "ai-star.svg",
    }
    tag_text = " ".join(tags).lower()
    icon_file = "ai-default.svg"
    for key, val in icon_map.items():
        if key in tag_text:
            icon_file = val
            break
    desc_preview = html_escape(desc[:150])
    return f\'<a href="{link}" class="content-card" style="padding-bottom:0.75rem;">\\n  <div class="flex gap-3">\\n    <div class="featured-image" style="width:70px;height:70px;min-width:70px;border-radius:10px;margin-bottom:0;flex-shrink:0;display:flex;align-items:center;justify-content:center;overflow:hidden;padding:8px;">\\n      <img src="{np}/images/{icon_file}" alt="" style="width:100%;height:100%;object-fit:contain;">\\n    </div>'''

if old_feature in c:
    c = c.replace(old_feature, new_feature)
    changes.append("Updated content_card with Q-version SVG icons")
else:
    changes.append("WARN: content_card feature section not found")

# ===== 2. Update homepage module cards to use module SVGs =====
old_module_card = '''    module_cards.append(f\'''
    <a href="{slug}/index.html" class="block bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg hover:border-primary-300 transition-all duration-200 group">
      <div class="text-3xl mb-3">{icon}</div>
      <h2 class="text-lg font-semibold text-gray-900 group-hover:text-primary-600 transition">{label}</h2>
      <p class="text-sm text-gray-500 mt-1">{desc}</p>
      <p class="text-xs text-primary-500 mt-2">共 {count} 篇文章 &rarr;</p>
    </a>\')'''

new_module_card = '''    module_cards.append(f\'''
    <a href="{slug}/index.html" class="block bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg hover:border-primary-300 transition-all duration-200 group">
      <div class="mb-3" style="display:flex;justify-content:center;"><img src="images/module-{slug}.svg" alt="{label}" style="width:80px;height:80px;border-radius:12px;"></div>
      <h2 class="text-lg font-semibold text-gray-900 group-hover:text-primary-600 transition">{label}</h2>
      <p class="text-sm text-gray-500 mt-1">{desc}</p>
      <p class="text-xs text-primary-500 mt-2">共 {count} 篇文章 &rarr;</p>
    </a>\')'''

if old_module_card in c:
    c = c.replace(old_module_card, new_module_card)
    changes.append("Updated module cards with Q-version SVGs")
else:
    changes.append("WARN: module card section not found")

# ===== 3. Remove old module icons dict (no longer needed) =====
old_icons_dict = '''    icons = {"\\u672c\\u5730 Skills": "\\U0001f4e0", "\\u63d2\\u4ef6 Skills": "\\U0001f4e0", "AI \\u5927\\u6a21\\u578b\\u65b0\\u95fb": "\\U0001f4e0", "GitHub \\u7cbe\\u9009 Skills": "\\U0001f4e0", "GitHub Top 100": "\\U0001f4e0"}'''
# The old icons might be different - let me find the actual line
idx = c.find("icons = {")
if idx > 0:
    end = c.find("\n", idx)
    old_line = c[idx:end]
    new_line = "    icons = {}  # No longer used - module SVGs are embedded in the cards"
    if "module-{slug}" not in c[end:end+200]:
        c = c.replace(old_line, new_line)
        changes.append("Removed old icons dict")

open(P, "w", encoding="utf-8").write(c)
print("\n".join(f"  {ch}" for ch in changes))
print("\n[DONE]")