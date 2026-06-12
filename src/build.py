import os, re, markdown
from datetime import datetime

SITE_NAME = "AI 大模型资讯站"
SITE_DESC = "AI 大模型与 Codex Skills 知识库"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT_DIR = os.path.join(BASE_DIR, "content")
OUTPUT_DIR = os.path.join(BASE_DIR, "docs")
NOW = datetime.now()

def parse_frontmatter(text):
    text = text.lstrip("\ufeff")
    m = re.match(r"^---\n(.*?)\n---\n(.*)", text, re.DOTALL)
    if not m:
        return {}, text
    fm = {}
    for line in m.group(1).split("\n"):
        kv = re.match(r"(\w+):\s*(.+?)$", line)
        if kv:
            val = kv.group(2).strip()
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            fm[kv[1]] = val
    return fm, m.group(2)

def html_escape(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

# Navigation depth: 0=homepage, 1=module pages (all pages in skills/, news/, etc.)
# Detail pages are in the SAME directory as list pages, so nav_depth=1 for both
def nav_prefix(nav_depth):
    if nav_depth == 0:
        return "."
    return ("../" * nav_depth).rstrip("/")

def page_frame(title, body_html, nav_depth=0):
    np = nav_prefix(nav_depth)
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html_escape(title)} - {SITE_NAME}</title>
  <meta name="description" content="{SITE_DESC}">
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    @import url("https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;600;700&display=swap");
    * {{ font-family: "Noto Sans SC", system-ui, sans-serif; }}
    body {{ background: #f8fafc; }}
    .prose {{ max-width: 65ch; line-height: 1.8; color: #334155; }}
    .prose h1 {{ font-size: 1.75rem; font-weight: 700; margin-top: 1.5rem; margin-bottom: 0.75rem; color: #1e293b; }}
    .prose h2 {{ font-size: 1.35rem; font-weight: 600; margin-top: 1.25rem; margin-bottom: 0.5rem; color: #334155; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.3rem; }}
    .prose h3 {{ font-size: 1.1rem; font-weight: 600; margin-top: 1rem; margin-bottom: 0.4rem; color: #475569; }}
    .prose p {{ margin-bottom: 0.75rem; }}
    .prose ul, .prose ol {{ margin-bottom: 0.75rem; padding-left: 1.5rem; }}
    .prose li {{ margin-bottom: 0.3rem; }}
    .prose code {{ background: #f1f5f9; padding: 0.15rem 0.4rem; border-radius: 4px; font-size: 0.9em; color: #e11d48; }}
    .prose pre {{ background: #1e293b; color: #e2e8f0; padding: 1rem; border-radius: 8px; overflow-x: auto; margin-bottom: 1rem; }}
    .prose pre code {{ background: none; color: inherit; padding: 0; }}
    .prose a {{ color: #2563eb; text-decoration: underline; }}
    .prose blockquote {{ border-left: 4px solid #3b82f6; padding-left: 1rem; color: #64748b; margin-bottom: 0.75rem; }}
    .prose img {{ max-width: 100%; border-radius: 8px; margin: 1rem 0; }}
    .prose table {{ width: 100%; border-collapse: collapse; margin-bottom: 1rem; }}
    .prose th, .prose td {{ border: 1px solid #e2e8f0; padding: 0.5rem 0.75rem; text-align: left; }}
    .prose th {{ background: #f1f5f9; font-weight: 600; }}
    @media (max-width: 640px) {{ .container {{ padding-left: 1rem; padding-right: 1rem; }} }}
    .line-clamp-2 {{ display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
  </style>
</head>
<body class="min-h-screen">
  <nav class="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
    <div class="max-w-6xl mx-auto px-4 sm:px-6">
      <div class="flex items-center justify-between h-14">
        <a href="{np}/index.html" class="text-lg font-bold text-primary-600 hover:text-primary-700 transition">{SITE_NAME}</a>
        <div class="flex gap-4 text-sm">
          <a href="{np}/skills/index.html" class="text-gray-600 hover:text-primary-600 transition">本地 Skills</a>
          <a href="{np}/plugin-skills/index.html" class="text-gray-600 hover:text-primary-600 transition">插件 Skills</a>
          <a href="{np}/news/index.html" class="text-gray-600 hover:text-primary-600 transition">AI 新闻</a>
          <a href="{np}/github-skills/index.html" class="text-gray-600 hover:text-primary-600 transition">GitHub Skills</a>
          <a href="{np}/top-100/index.html" class="text-gray-600 hover:text-primary-600 transition">Top 100</a>
        </div>
      </div>
    </div>
  </nav>
  <main class="max-w-4xl mx-auto px-4 sm:px-6 py-6">
    {body_html}
  </main>
  <footer class="bg-white border-t border-gray-200 mt-12 py-6">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 text-center text-sm text-gray-500">
      <p>&copy; {NOW.year} {SITE_NAME} | 由 Codex 构建与维护</p>
      <p class="mt-1">数据来源标注于各文章底部</p>
    </div>
  </footer>
</body>
</html>'''

def content_card(title, desc, link, tags=None, date=""):
    if tags is None:
        tags = []
    tag_html = " ".join(
        [f'<span class="inline-block bg-primary-50 text-primary-600 text-xs px-2 py-0.5 rounded-full">{html_escape(t)}</span>' for t in tags]
    )
    date_html = f'<span class="text-xs text-gray-400 ml-auto">{html_escape(date)}</span>' if date else ""
    return f'''
  <a href="{html_escape(link)}" class="block bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md hover:border-primary-300 transition-all duration-200 group">
    <div class="flex items-start justify-between gap-3">
      <div class="flex-1 min-w-0">
        <h3 class="font-semibold text-gray-900 group-hover:text-primary-600 transition text-base truncate">{html_escape(title)}</h3>
        <p class="text-sm text-gray-500 mt-1 line-clamp-2">{html_escape(desc[:200])}</p>
      </div>
      <svg class="w-5 h-5 text-gray-300 group-hover:text-primary-400 shrink-0 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
    </div>
    <div class="flex items-center gap-2 mt-2 flex-wrap">
      {tag_html}
      {date_html}
    </div>
  </a>'''

def list_page(title, desc, cards_html):
    nav_d = 1
    np = nav_prefix(nav_d)
    body = f'''
    <div class="mb-6">
      <a href="{np}/index.html" class="text-sm text-primary-600 hover:text-primary-700 inline-flex items-center gap-1">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
        返回首页
      </a>
    </div>
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-gray-900">{html_escape(title)}</h1>
      <p class="text-gray-500 mt-1">{html_escape(desc)}</p>
    </div>
    <div class="grid gap-4 sm:grid-cols-2">
      {cards_html}
    </div>'''
    return page_frame(title, body, nav_depth=nav_d)

def detail_page(title, content_html, source_info):
    nav_d = 1
    np = nav_prefix(nav_d)
    body = f'''
    <div class="mb-6 flex gap-4 text-sm">
      <a href="javascript:history.back()" class="text-primary-600 hover:text-primary-700 inline-flex items-center gap-1">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
        返回
      </a>
      <a href="{np}/index.html" class="text-gray-400 hover:text-primary-600 inline-flex items-center gap-1">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>
        首页
      </a>
    </div>
    <article class="bg-white rounded-xl border border-gray-200 p-6 sm:p-8 shadow-sm">
      <h1 class="text-2xl font-bold text-gray-900 mb-6">{html_escape(title)}</h1>
      <div class="prose">{content_html}</div>
      <div class="mt-10 pt-6 border-t border-gray-200">
        <div class="bg-gray-50 rounded-lg p-4 text-sm text-gray-500">
          <p class="font-medium text-gray-700">&#128203; 数据来源</p>
          <p class="mt-1">{html_escape(source_info)}</p>
          <p class="mt-1">更新时间：{NOW.strftime("%Y-%m-%d")}</p>
        </div>
      </div>
    </article>'''
    return page_frame(title, body, nav_depth=nav_d)

def index_page(module_cards):
    nav_d = 0
    body = f'''
    <div class="text-center py-8 sm:py-12">
      <h1 class="text-3xl sm:text-4xl font-bold text-gray-900">&#129302; {SITE_NAME}</h1>
      <p class="text-gray-500 mt-3 text-base max-w-lg mx-auto">追踪 AI 大模型最新动态 - 收录实用的 Codex Skills - 打造你的 AI 知识库</p>
    </div>
    <div class="grid gap-6 sm:grid-cols-2 mb-8">
      {module_cards}
    </div>
    <div class="bg-gradient-to-r from-primary-50 to-blue-50 rounded-xl p-6 border border-primary-100 mt-8">
      <h2 class="text-lg font-semibold text-gray-800">&#128161; 关于本站</h2>
      <p class="text-sm text-gray-600 mt-2 leading-relaxed">
        这是一个由 Codex AI 与人类协作打造的 AI 内容资讯站。所有内容均标注数据来源，确保信息的可追溯性。网站持续更新中。
      </p>
      <p class="text-xs text-gray-400 mt-3">最后更新：{NOW.strftime("%Y-%m-%d")}</p>
    </div>'''
    return page_frame("首页", body, nav_depth=nav_d)

def build():
    print("开始构建站点...\n")
    modules = [
        ("skills", "本地 Skills", "Codex 系统中已安装的 17 个本体 Skill"),
        ("plugin-skills", "插件 Skills", "Codex 插件提供的 17 个扩展 Skill"),
        ("news", "AI 大模型新闻", "Claude、GPT、开源模型等重要动态"),
        ("github-skills", "GitHub 精选 Skills", "GitHub 上热门的 AI 相关项目"),
        ("top-100", "GitHub Top 100", "GitHub 上最受欢迎的 AI Skills 排行榜"),
    ]
    module_infos = []
    for slug, label, desc in modules:
        content_dir = os.path.join(CONTENT_DIR, slug)
        out_dir = os.path.join(OUTPUT_DIR, slug)
        os.makedirs(out_dir, exist_ok=True)
        if not os.path.isdir(content_dir):
            module_infos.append((label, desc, 0, slug))
            continue
        files = sorted([f for f in os.listdir(content_dir) if f.endswith(".md")])
        entries = []
        for fname in files:
            filepath = os.path.join(content_dir, fname)
            with open(filepath, "r", encoding="utf-8") as f:
                raw = f.read()
            fm, content = parse_frontmatter(raw)
            html = markdown.markdown(content, extensions=["fenced_code", "codehilite", "tables"])
            slug_name = os.path.splitext(fname)[0]
            entries.append({**fm, "slug": slug_name, "html": html, "content": content})
        cards = []
        for e in entries:
            tags_str = e.get("tags", label)
            tags = [t.strip() for t in tags_str.split(",") if t.strip()]
            link = f"{e['slug']}.html"
            date_str = e.get("date", "")
            title = e.get("title", e.get("name", "未命名"))
            desc_text = e.get("description", "暂无描述")
            cards.append(content_card(title, desc_text, link, tags, date_str))
        list_html = list_page(label, desc, "\n".join(cards))
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(list_html)
        for e in entries:
            title = e.get("title", e.get("name", "未命名"))
            source = e.get("source", f"{label} 本地内容")
            detail_html = detail_page(title, e["html"], source)
            detail_path = os.path.join(out_dir, f"{e['slug']}.html")
            with open(detail_path, "w", encoding="utf-8") as f:
                f.write(detail_html)
        module_infos.append((label, desc, len(entries), slug))
        print(f"  [OK] {label}: {len(entries)} 篇文章已生成")
    icons = {"本地 Skills": "&#128187;", "插件 Skills": "&#128268;", "AI 大模型新闻": "&#129504;", "GitHub 精选 Skills": "&#128293;", "GitHub Top 100": "&#127942;"}
    module_cards = []
    for label, desc, count, slug in module_infos:
        icon = icons.get(label, "&#128196;")
        module_cards.append(f'''
    <a href="{slug}/index.html" class="block bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg hover:border-primary-300 transition-all duration-200 group">
      <div class="text-3xl mb-3">{icon}</div>
      <h2 class="text-lg font-semibold text-gray-900 group-hover:text-primary-600 transition">{label}</h2>
      <p class="text-sm text-gray-500 mt-1">{desc}</p>
      <p class="text-xs text-primary-500 mt-2">共 {count} 篇文章 &rarr;</p>
    </a>''')
    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_page("\n".join(module_cards)))
    total = sum(m[2] for m in module_infos)
    print(f"\n[Done] 站点构建完成！")
    print(f"  [Folder] docs/ 目录")
    print(f"  [Stats] 总计: {total} 篇文章, {len(module_infos)} 个模块")
    print(f"  [Web] 打开 docs/index.html 即可预览\n")

if __name__ == "__main__":
    build()
