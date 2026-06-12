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


CSS_STYLE = r"""    :root {
      --bg-primary: #0a0a1a; --bg-secondary: #12122a;
      --bg-card: rgba(255,255,255,0.04);
      --border-color: rgba(99,102,241,0.15);
      --border-glow: rgba(6,182,212,0.3);
      --text-primary: #e2e8f0; --text-secondary: #94a3b8;
      --text-muted: #64748b;
      --accent-1: #818cf8; --accent-2: #22d3ee; --accent-3: #a78bfa;
      --gradient-2: linear-gradient(135deg, #06b6d4 0%, #6366f1 50%, #a78bfa 100%);
      --glass-bg: rgba(18,18,42,0.6);
      --glass-border: rgba(255,255,255,0.08);
    }
    * { margin:0; padding:0; box-sizing:border-box; }
    body { font-family:"Noto Sans SC",system-ui,sans-serif; background:var(--bg-primary); color:var(--text-primary); min-height:100vh; overflow-x:hidden; }
    body::before { content:""; position:fixed; inset:0; background:radial-gradient(ellipse 80% 60% at 50% -20%,rgba(99,102,241,0.15) 0%,transparent 60%),radial-gradient(ellipse 60% 50% at 80% 80%,rgba(6,182,212,0.1) 0%,transparent 50%),radial-gradient(ellipse 50% 40% at 20% 90%,rgba(167,139,250,0.08) 0%,transparent 50%); pointer-events:none; z-index:0; }
    body::after { content:""; position:fixed; inset:0; background-image:linear-gradient(rgba(99,102,241,0.03) 1px,transparent 1px),linear-gradient(90deg,rgba(99,102,241,0.03) 1px,transparent 1px); background-size:60px 60px; pointer-events:none; z-index:0; }
    @keyframes float { 0%{transform:translateY(100vh) scale(1);opacity:0;} 10%{opacity:.6;} 90%{opacity:.6;} 100%{transform:translateY(-10vh) scale(.5);opacity:0;} }
    .glass-nav { position:sticky; top:0; z-index:100; backdrop-filter:blur(20px) saturate(1.8); -webkit-backdrop-filter:blur(20px) saturate(1.8); background:rgba(10,10,26,.75); border-bottom:1px solid var(--glass-border); }
    .glass-nav .nav-link { position:relative; color:var(--text-secondary); text-decoration:none; padding:.25rem 0; font-size:.875rem; letter-spacing:.3px; transition:color .3s; }
    .glass-nav .nav-link::after { content:""; position:absolute; bottom:-2px; left:0; width:0; height:2px; background:var(--gradient-2); transition:width .3s ease; border-radius:2px; }
    .glass-nav .nav-link:hover { color:var(--accent-2); }
    .glass-nav .nav-link:hover::after { width:100%; }
    .site-logo { font-family:"Orbitron",sans-serif; font-weight:700; font-size:1.1rem; background:var(--gradient-2); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; text-decoration:none; letter-spacing:1px; }
    .glass-card { background:var(--glass-bg); backdrop-filter:blur(16px) saturate(1.4); -webkit-backdrop-filter:blur(16px) saturate(1.4); border:1px solid var(--glass-border); border-radius:16px; transition:all .4s cubic-bezier(.25,.46,.45,.94); position:relative; overflow:hidden; }
    .glass-card::before { content:""; position:absolute; top:0; left:-100%; width:100%; height:100%; background:linear-gradient(90deg,transparent,rgba(255,255,255,.03),transparent); transition:left .6s ease; }
    .glass-card:hover::before { left:100%; }
    .glass-card:hover { transform:translateY(-4px); border-color:var(--border-glow); box-shadow:0 8px 32px rgba(99,102,241,.15),0 0 60px rgba(6,182,212,.05); }
    .glass-card .card-icon { font-size:2.2rem; line-height:1; margin-bottom:.5rem; }
    .glass-card h2 { font-family:"Orbitron",sans-serif; font-size:.95rem; font-weight:600; letter-spacing:.5px; color:var(--text-primary); margin-bottom:.4rem; }
    .content-card { background:var(--glass-bg); backdrop-filter:blur(12px) saturate(1.3); -webkit-backdrop-filter:blur(12px) saturate(1.3); border:1px solid var(--glass-border); border-radius:12px; padding:1.25rem; transition:all .35s ease; position:relative; overflow:hidden; display:block; text-decoration:none; }
    .content-card::before { content:""; position:absolute; top:0; left:0; width:3px; height:0; background:var(--gradient-2); transition:height .4s ease; border-radius:0 2px 2px 0; }
    .content-card:hover::before { height:100%; }
    .content-card:hover { border-color:var(--border-glow); transform:translateY(-2px); box-shadow:0 4px 24px rgba(99,102,241,.12); }
    .content-card h3 { font-size:1rem; font-weight:600; color:var(--text-primary); line-height:1.4; }
    .tag { display:inline-block; padding:.15rem .55rem; border-radius:20px; font-size:.7rem; font-weight:500; background:rgba(99,102,241,.12); color:var(--accent-1); border:1px solid rgba(99,102,241,.2); letter-spacing:.3px; }
    .prose { max-width:65ch; line-height:1.9; color:#cbd5e1; }
    .prose h1 { font-family:"Orbitron",sans-serif; font-size:1.6rem; font-weight:700; letter-spacing:1px; margin-top:1.5rem; margin-bottom:1rem; background:var(--gradient-2); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
    .prose h2 { font-size:1.25rem; font-weight:600; margin-top:1.5rem; margin-bottom:.6rem; color:#e2e8f0; padding-bottom:.4rem; border-bottom:1px solid rgba(99,102,241,.15); }
    .prose h3 { font-size:1.05rem; font-weight:600; margin-top:1.2rem; margin-bottom:.5rem; color:#cbd5e1; }
    .prose p { margin-bottom:.9rem; }
    .prose ul,.prose ol { margin-bottom:.9rem; padding-left:1.5rem; }
    .prose li { margin-bottom:.3rem; }
    .prose code { font-family:"JetBrains Mono",monospace; background:rgba(99,102,241,.12); padding:.15rem .45rem; border-radius:4px; font-size:.85em; color:#67e8f9; }
    .prose pre { background:rgba(10,10,26,.8); border:1px solid rgba(99,102,241,.15); color:#e2e8f0; padding:1rem; border-radius:12px; overflow-x:auto; margin-bottom:1rem; }
    .prose pre code { background:none; color:inherit; padding:0; }
    .prose a { color:#22d3ee; text-decoration:none; border-bottom:1px solid rgba(34,211,238,.3); transition:border-color .2s; }
    .prose a:hover { border-color:#22d3ee; }
    .prose blockquote { border-left:3px solid var(--accent-1); padding-left:1rem; color:var(--text-muted); margin-bottom:.9rem; background:rgba(99,102,241,.05); border-radius:0 8px 8px 0; padding:.6rem 1rem; }
    .prose img { max-width:100%; border-radius:12px; margin:1rem 0; border:1px solid var(--glass-border); }
    .prose table { width:100%; border-collapse:collapse; margin-bottom:1rem; border-radius:12px; overflow:hidden; }
    .prose th,.prose td { border:1px solid rgba(99,102,241,.12); padding:.5rem .75rem; text-align:left; }
    .prose th { background:rgba(99,102,241,.1); font-weight:600; color:#e2e8f0; }
    .prose td { color:#cbd5e1; }
    .source-footer { margin-top:2.5rem; padding:1.25rem; background:rgba(99,102,241,.06); border:1px solid var(--glass-border); border-radius:12px; }
    .source-footer h3 { font-family:"Orbitron",sans-serif; font-size:.75rem; font-weight:600; letter-spacing:1px; color:var(--accent-2); text-transform:uppercase; margin-bottom:.5rem; }
    .source-footer a { color:#22d3ee; text-decoration:none; border-bottom:1px solid rgba(34,211,238,.2); transition:border-color .2s; word-break:break-all; }
    .source-footer a:hover { border-color:#22d3ee; }
    .page-footer { border-top:1px solid var(--glass-border); margin-top:3rem; padding:1.5rem 0; text-align:center; position:relative; z-index:1; }
    .page-footer p { color:var(--text-muted); font-size:.78rem; }
    ::-webkit-scrollbar { width:6px; }
    ::-webkit-scrollbar-track { background:var(--bg-primary); }
    ::-webkit-scrollbar-thumb { background:rgba(99,102,241,.3); border-radius:3px; }
    ::-webkit-scrollbar-thumb:hover { background:rgba(99,102,241,.5); }
    @keyframes fadeInUp { from{opacity:0;transform:translateY(20px);} to{opacity:1;transform:translateY(0);} }
    .animate-in { animation:fadeInUp .6s ease forwards; opacity:0; }
    .hero-section { text-align:center; padding:3rem 1rem 2rem; }
    .hero-section h1 { font-family:"Orbitron",sans-serif; font-size:clamp(1.6rem,4vw,2.5rem); font-weight:800; letter-spacing:2px; background:var(--gradient-2); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; margin-bottom:.6rem; }
    .hero-section .subtitle { color:var(--text-secondary); font-size:.95rem; max-width:500px; margin:0 auto; line-height:1.6; }
    .back-btn { display:inline-flex; align-items:center; gap:.4rem; color:var(--text-secondary); font-size:.85rem; text-decoration:none; transition:color .3s; }
    .back-btn:hover { color:var(--accent-2); }
    .module-badge { display:inline-block; font-family:"Orbitron",sans-serif; font-size:.7rem; font-weight:600; letter-spacing:1.5px; text-transform:uppercase; padding:.3rem .8rem; border-radius:20px; background:rgba(99,102,241,.12); border:1px solid rgba(99,102,241,.2); color:var(--accent-1); }
    .glow-text { text-shadow:0 0 20px rgba(6,182,212,.3); }
    .line-clamp-2 { display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }
    .back-to-top { position:fixed; bottom:2rem; right:2rem; z-index:99; width:44px; height:44px; border-radius:50%; background:var(--glass-bg); backdrop-filter:blur(12px); border:1px solid var(--glass-border); color:var(--accent-2); font-size:1.3rem; cursor:pointer; display:none; align-items:center; justify-content:center; transition:all .3s ease; }
    .back-to-top:hover { transform:translateY(-3px); box-shadow:0 0 20px rgba(6,182,212,.2); border-color:var(--border-glow); }
    .back-to-top.visible { display:flex; }
    .theme-toggle { position:fixed; bottom:2rem; right:5rem; z-index:99; width:44px; height:44px; border-radius:50%; background:var(--glass-bg); backdrop-filter:blur(12px); border:1px solid var(--glass-border); color:var(--accent-2); font-size:1.2rem; cursor:pointer; display:flex; align-items:center; justify-content:center; transition:all .3s ease; }
    .theme-toggle:hover { transform:translateY(-3px); box-shadow:0 0 20px rgba(6,182,212,.2); border-color:var(--border-glow); }
    .share-btn { display:inline-flex; align-items:center; gap:.4rem; padding:.4rem .9rem; border-radius:8px; font-size:.78rem; font-weight:500; cursor:pointer; background:rgba(99,102,241,.1); border:1px solid var(--glass-border); color:var(--text-secondary); transition:all .3s ease; text-decoration:none; }
    .share-btn:hover { background:rgba(99,102,241,.2); color:var(--accent-1); border-color:var(--border-glow); transform:translateY(-1px); }
    .breadcrumb { display:flex; align-items:center; gap:.4rem; font-size:.78rem; color:var(--text-muted); margin-bottom:.5rem; }
    .breadcrumb a { color:var(--text-secondary); text-decoration:none; transition:color .3s; }
    .breadcrumb a:hover { color:var(--accent-2); }
    .breadcrumb span { color:var(--text-muted); }
    .filter-pills { display:flex; gap:.5rem; flex-wrap:wrap; margin-bottom:1rem; }
    .filter-pill { padding:.25rem .7rem; border-radius:20px; font-size:.75rem; cursor:pointer; background:rgba(99,102,241,.08); border:1px solid var(--glass-border); color:var(--text-secondary); transition:all .3s ease; text-decoration:none; display:inline-block; }
    .filter-pill:hover,.filter-pill.active { background:rgba(99,102,241,.2); color:var(--accent-2); border-color:var(--border-glow); }
    .featured-image { width:100%; height:180px; border-radius:12px; margin-bottom:1rem; background:var(--gradient-2); opacity:.15; display:flex; align-items:center; justify-content:center; overflow:hidden; position:relative; }
    body.light-theme { --bg-primary: #f1f5f9; --bg-secondary: #e2e8f0; --text-primary: #1e293b; --text-secondary: #475569; --text-muted: #94a3b8; --glass-bg: rgba(255,255,255,0.7); --glass-border: rgba(0,0,0,0.08); }
        @media (max-width:640px) { .glass-nav .nav-links { gap:.6rem; font-size:.75rem; overflow-x:auto; } .glass-nav .nav-link { font-size:.75rem; white-space:nowrap; } .prose h1 { font-size:1.2rem; } }
"""

CSS_STYLE = r"""    :root {
      --bg-primary: #0a0a1a; --bg-secondary: #12122a;
      --bg-card: rgba(255,255,255,0.04);
      --border-color: rgba(99,102,241,0.15);
      --border-glow: rgba(6,182,212,0.3);
      --text-primary: #e2e8f0; --text-secondary: #94a3b8;
      --text-muted: #64748b;
      --accent-1: #818cf8; --accent-2: #22d3ee; --accent-3: #a78bfa;
      --gradient-2: linear-gradient(135deg, #06b6d4 0%, #6366f1 50%, #a78bfa 100%);
      --glass-bg: rgba(18,18,42,0.6);
      --glass-border: rgba(255,255,255,0.08);
    }
    * { margin:0; padding:0; box-sizing:border-box; }
    body { font-family:"Noto Sans SC",system-ui,sans-serif; background:var(--bg-primary); color:var(--text-primary); min-height:100vh; overflow-x:hidden; }
    body::before { content:""; position:fixed; inset:0; background:radial-gradient(ellipse 80% 60% at 50% -20%,rgba(99,102,241,0.15) 0%,transparent 60%),radial-gradient(ellipse 60% 50% at 80% 80%,rgba(6,182,212,0.1) 0%,transparent 50%),radial-gradient(ellipse 50% 40% at 20% 90%,rgba(167,139,250,0.08) 0%,transparent 50%); pointer-events:none; z-index:0; }
    body::after { content:""; position:fixed; inset:0; background-image:linear-gradient(rgba(99,102,241,0.03) 1px,transparent 1px),linear-gradient(90deg,rgba(99,102,241,0.03) 1px,transparent 1px); background-size:60px 60px; pointer-events:none; z-index:0; }
    @keyframes float { 0%{transform:translateY(100vh) scale(1);opacity:0;} 10%{opacity:.6;} 90%{opacity:.6;} 100%{transform:translateY(-10vh) scale(.5);opacity:0;} }
    .glass-nav { position:sticky; top:0; z-index:100; backdrop-filter:blur(20px) saturate(1.8); -webkit-backdrop-filter:blur(20px) saturate(1.8); background:rgba(10,10,26,.75); border-bottom:1px solid var(--glass-border); }
    .glass-nav .nav-link { position:relative; color:var(--text-secondary); text-decoration:none; padding:.25rem 0; font-size:.875rem; letter-spacing:.3px; transition:color .3s; }
    .glass-nav .nav-link::after { content:""; position:absolute; bottom:-2px; left:0; width:0; height:2px; background:var(--gradient-2); transition:width .3s ease; border-radius:2px; }
    .glass-nav .nav-link:hover { color:var(--accent-2); }
    .glass-nav .nav-link:hover::after { width:100%; }
    .site-logo { font-family:"Orbitron",sans-serif; font-weight:700; font-size:1.1rem; background:var(--gradient-2); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; text-decoration:none; letter-spacing:1px; }
    .glass-card { background:var(--glass-bg); backdrop-filter:blur(16px) saturate(1.4); -webkit-backdrop-filter:blur(16px) saturate(1.4); border:1px solid var(--glass-border); border-radius:16px; transition:all .4s cubic-bezier(.25,.46,.45,.94); position:relative; overflow:hidden; }
    .glass-card::before { content:""; position:absolute; top:0; left:-100%; width:100%; height:100%; background:linear-gradient(90deg,transparent,rgba(255,255,255,.03),transparent); transition:left .6s ease; }
    .glass-card:hover::before { left:100%; }
    .glass-card:hover { transform:translateY(-4px); border-color:var(--border-glow); box-shadow:0 8px 32px rgba(99,102,241,.15),0 0 60px rgba(6,182,212,.05); }
    .glass-card .card-icon { font-size:2.2rem; line-height:1; margin-bottom:.5rem; }
    .glass-card h2 { font-family:"Orbitron",sans-serif; font-size:.95rem; font-weight:600; letter-spacing:.5px; color:var(--text-primary); margin-bottom:.4rem; }
    .content-card { background:var(--glass-bg); backdrop-filter:blur(12px) saturate(1.3); -webkit-backdrop-filter:blur(12px) saturate(1.3); border:1px solid var(--glass-border); border-radius:12px; padding:1.25rem; transition:all .35s ease; position:relative; overflow:hidden; display:block; text-decoration:none; }
    .content-card::before { content:""; position:absolute; top:0; left:0; width:3px; height:0; background:var(--gradient-2); transition:height .4s ease; border-radius:0 2px 2px 0; }
    .content-card:hover::before { height:100%; }
    .content-card:hover { border-color:var(--border-glow); transform:translateY(-2px); box-shadow:0 4px 24px rgba(99,102,241,.12); }
    .content-card h3 { font-size:1rem; font-weight:600; color:var(--text-primary); line-height:1.4; }
    .tag { display:inline-block; padding:.15rem .55rem; border-radius:20px; font-size:.7rem; font-weight:500; background:rgba(99,102,241,.12); color:var(--accent-1); border:1px solid rgba(99,102,241,.2); letter-spacing:.3px; }
    .prose { max-width:65ch; line-height:1.9; color:#cbd5e1; }
    .prose h1 { font-family:"Orbitron",sans-serif; font-size:1.6rem; font-weight:700; letter-spacing:1px; margin-top:1.5rem; margin-bottom:1rem; background:var(--gradient-2); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
    .prose h2 { font-size:1.25rem; font-weight:600; margin-top:1.5rem; margin-bottom:.6rem; color:#e2e8f0; padding-bottom:.4rem; border-bottom:1px solid rgba(99,102,241,.15); }
    .prose h3 { font-size:1.05rem; font-weight:600; margin-top:1.2rem; margin-bottom:.5rem; color:#cbd5e1; }
    .prose p { margin-bottom:.9rem; }
    .prose ul,.prose ol { margin-bottom:.9rem; padding-left:1.5rem; }
    .prose li { margin-bottom:.3rem; }
    .prose code { font-family:"JetBrains Mono",monospace; background:rgba(99,102,241,.12); padding:.15rem .45rem; border-radius:4px; font-size:.85em; color:#67e8f9; }
    .prose pre { background:rgba(10,10,26,.8); border:1px solid rgba(99,102,241,.15); color:#e2e8f0; padding:1rem; border-radius:12px; overflow-x:auto; margin-bottom:1rem; }
    .prose pre code { background:none; color:inherit; padding:0; }
    .prose a { color:#22d3ee; text-decoration:none; border-bottom:1px solid rgba(34,211,238,.3); transition:border-color .2s; }
    .prose a:hover { border-color:#22d3ee; }
    .prose blockquote { border-left:3px solid var(--accent-1); padding-left:1rem; color:var(--text-muted); margin-bottom:.9rem; background:rgba(99,102,241,.05); border-radius:0 8px 8px 0; padding:.6rem 1rem; }
    .prose img { max-width:100%; border-radius:12px; margin:1rem 0; border:1px solid var(--glass-border); }
    .prose table { width:100%; border-collapse:collapse; margin-bottom:1rem; border-radius:12px; overflow:hidden; }
    .prose th,.prose td { border:1px solid rgba(99,102,241,.12); padding:.5rem .75rem; text-align:left; }
    .prose th { background:rgba(99,102,241,.1); font-weight:600; color:#e2e8f0; }
    .prose td { color:#cbd5e1; }
    .source-footer { margin-top:2.5rem; padding:1.25rem; background:rgba(99,102,241,.06); border:1px solid var(--glass-border); border-radius:12px; }
    .source-footer h3 { font-family:"Orbitron",sans-serif; font-size:.75rem; font-weight:600; letter-spacing:1px; color:var(--accent-2); text-transform:uppercase; margin-bottom:.5rem; }
    .source-footer a { color:#22d3ee; text-decoration:none; border-bottom:1px solid rgba(34,211,238,.2); transition:border-color .2s; word-break:break-all; }
    .source-footer a:hover { border-color:#22d3ee; }
    .page-footer { border-top:1px solid var(--glass-border); margin-top:3rem; padding:1.5rem 0; text-align:center; position:relative; z-index:1; }
    .page-footer p { color:var(--text-muted); font-size:.78rem; }
    ::-webkit-scrollbar { width:6px; }
    ::-webkit-scrollbar-track { background:var(--bg-primary); }
    ::-webkit-scrollbar-thumb { background:rgba(99,102,241,.3); border-radius:3px; }
    ::-webkit-scrollbar-thumb:hover { background:rgba(99,102,241,.5); }
    @keyframes fadeInUp { from{opacity:0;transform:translateY(20px);} to{opacity:1;transform:translateY(0);} }
    .animate-in { animation:fadeInUp .6s ease forwards; opacity:0; }
    .hero-section { text-align:center; padding:3rem 1rem 2rem; }
    .hero-section h1 { font-family:"Orbitron",sans-serif; font-size:clamp(1.6rem,4vw,2.5rem); font-weight:800; letter-spacing:2px; background:var(--gradient-2); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; margin-bottom:.6rem; }
    .hero-section .subtitle { color:var(--text-secondary); font-size:.95rem; max-width:500px; margin:0 auto; line-height:1.6; }
    .back-btn { display:inline-flex; align-items:center; gap:.4rem; color:var(--text-secondary); font-size:.85rem; text-decoration:none; transition:color .3s; }
    .back-btn:hover { color:var(--accent-2); }
    .module-badge { display:inline-block; font-family:"Orbitron",sans-serif; font-size:.7rem; font-weight:600; letter-spacing:1.5px; text-transform:uppercase; padding:.3rem .8rem; border-radius:20px; background:rgba(99,102,241,.12); border:1px solid rgba(99,102,241,.2); color:var(--accent-1); }
    .glow-text { text-shadow:0 0 20px rgba(6,182,212,.3); }
    .line-clamp-2 { display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }
    .back-to-top { position:fixed; bottom:2rem; right:2rem; z-index:99; width:44px; height:44px; border-radius:50%; background:var(--glass-bg); backdrop-filter:blur(12px); border:1px solid var(--glass-border); color:var(--accent-2); font-size:1.3rem; cursor:pointer; display:none; align-items:center; justify-content:center; transition:all .3s ease; }
    .back-to-top:hover { transform:translateY(-3px); box-shadow:0 0 20px rgba(6,182,212,.2); border-color:var(--border-glow); }
    .back-to-top.visible { display:flex; }
    .theme-toggle { position:fixed; bottom:2rem; right:5rem; z-index:99; width:44px; height:44px; border-radius:50%; background:var(--glass-bg); backdrop-filter:blur(12px); border:1px solid var(--glass-border); color:var(--accent-2); font-size:1.2rem; cursor:pointer; display:flex; align-items:center; justify-content:center; transition:all .3s ease; }
    .theme-toggle:hover { transform:translateY(-3px); box-shadow:0 0 20px rgba(6,182,212,.2); border-color:var(--border-glow); }
    .share-btn { display:inline-flex; align-items:center; gap:.4rem; padding:.4rem .9rem; border-radius:8px; font-size:.78rem; font-weight:500; cursor:pointer; background:rgba(99,102,241,.1); border:1px solid var(--glass-border); color:var(--text-secondary); transition:all .3s ease; text-decoration:none; }
    .share-btn:hover { background:rgba(99,102,241,.2); color:var(--accent-1); border-color:var(--border-glow); transform:translateY(-1px); }
    .breadcrumb { display:flex; align-items:center; gap:.4rem; font-size:.78rem; color:var(--text-muted); margin-bottom:.5rem; }
    .breadcrumb a { color:var(--text-secondary); text-decoration:none; transition:color .3s; }
    .breadcrumb a:hover { color:var(--accent-2); }
    .breadcrumb span { color:var(--text-muted); }
    .filter-pills { display:flex; gap:.5rem; flex-wrap:wrap; margin-bottom:1rem; }
    .filter-pill { padding:.25rem .7rem; border-radius:20px; font-size:.75rem; cursor:pointer; background:rgba(99,102,241,.08); border:1px solid var(--glass-border); color:var(--text-secondary); transition:all .3s ease; text-decoration:none; display:inline-block; }
    .filter-pill:hover,.filter-pill.active { background:rgba(99,102,241,.2); color:var(--accent-2); border-color:var(--border-glow); }
    .featured-image { width:100%; height:180px; border-radius:12px; margin-bottom:1rem; background:var(--gradient-2); opacity:.15; display:flex; align-items:center; justify-content:center; overflow:hidden; position:relative; }
    body.light-theme { --bg-primary: #f1f5f9; --bg-secondary: #e2e8f0; --text-primary: #1e293b; --text-secondary: #475569; --text-muted: #94a3b8; --glass-bg: rgba(255,255,255,0.7); --glass-border: rgba(0,0,0,0.08); }
        @media (max-width:640px) { .glass-nav .nav-links { gap:.6rem; font-size:.75rem; overflow-x:auto; } .glass-nav .nav-link { font-size:.75rem; white-space:nowrap; } .prose h1 { font-size:1.2rem; } }
"""

def page_frame(title, body_html, nav_depth=0, og_desc=None, og_image=None):
    if og_desc is None:
        og_desc = SITE_DESC
    np = nav_prefix(nav_depth)
    og_url_path = "." if nav_depth == 0 else "../" * nav_depth
    scroll_js = "window.scrollTo({top:0,behavior:'smooth'})"
    theme_js = "document.body.classList.toggle('light-theme');localStorage.setItem('theme',document.body.classList.contains('light-theme')?'light':'dark')"
    scroll_event_js = "window.addEventListener('scroll',function(){document.getElementById('backToTop').classList.toggle('visible',window.scrollY>300)})"
    theme_init_js = "if(localStorage.getItem('theme')==='light')document.body.classList.add('light-theme')"
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html_escape(title)} - {SITE_NAME}</title>
  <meta name="description" content="{og_desc}">
  <meta name="keywords" content="AI,大模型,GPT,Claude,DeepSeek,GitHub,开源,机器学习,深度学习,人工智能">
  <meta property="og:title" content="{html_escape(title)} - {SITE_NAME}">
  <meta property="og:description" content="{og_desc}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{og_url_path}/index.html">
  <meta property="og:image" content="{og_image or og_url_path + '/images/hero.svg'}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html_escape(title)} - {SITE_NAME}">
  <meta name="twitter:description" content="{og_desc}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;600;700&family=Orbitron:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  <style>{CSS_STYLE}</style>
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
        <a href="{np}/index.html" class="site-logo">🦢 AI 资讯站</a>
        <div class="flex gap-3 sm:gap-5 nav-links">
          <a href="{np}/skills/index.html" class="nav-link">本地 Skills</a>
          <a href="{np}/plugin-skills/index.html" class="nav-link">插件 Skills</a>
          <a href="{np}/news/index.html" class="nav-link">AI 新闻</a>
          <a href="{np}/github-skills/index.html" class="nav-link">GitHub Skills</a>
          <a href="{np}/top-100/index.html" class="nav-link">Top 100</a>
        </div>
      </div>
    </div>
  </nav>
  <main class="max-w-5xl mx-auto px-4 sm:px-6 py-6 relative" style="z-index:1;">
    {body_html}
  </main>
  <button onclick="{scroll_js}" class="back-to-top" id="backToTop" aria-label="回到顶部">↑</button>
  <button onclick="{theme_js}" class="theme-toggle" id="themeToggle" aria-label="切换主题">☀</button>
  <script>{scroll_event_js}; {theme_init_js};</script>
  <footer class="page-footer">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 text-center">
      <p>&copy; {NOW.year} {SITE_NAME} &middot; 由 Codex 构建与维护</p>
      <p style="color:var(--text-muted);font-size:0.72rem;margin-top:0.25rem;">数据来源标注于各文章底部 &middot; 探索 AI 的无限可能</p>
    </div>
  </footer>
</body>
</html>"""


def content_card(title, desc, link, tags, date_str):
    tag_badges = "".join(f'<span class="tag">{html_escape(t)}</span>' for t in tags)
    date_html = ""
    if date_str:
        date_html = f'<span style="color:var(--text-muted);font-size:0.72rem;">{html_escape(date_str)}</span>'
    icon_emoji = "\U0001f4d6"
    tag_text = " ".join(tags).lower()
    if any(x in tag_text for x in ["news", "ai", "\u65b0\u95fb", "\u5927\u6a21\u578b"]):
        icon_emoji = "\U0001f9e0"
    elif any(x in tag_text for x in ["\u5de5\u5177", "\u6846\u67b6", "tool", "framework"]):
        icon_emoji = "\U0001f527"
    elif "github" in tag_text:
        icon_emoji = "\U0001f525"
    elif "skill" in tag_text:
        icon_emoji = "\U0001f4bb"
    desc_preview = html_escape(desc[:150])
    return f'<a href="{link}" class="content-card" style="padding-bottom:0.75rem;">\n  <div class="flex gap-3">\n    <div class="featured-image" style="width:70px;height:70px;min-width:70px;border-radius:10px;margin-bottom:0;flex-shrink:0;display:flex;align-items:center;justify-content:center;">\n      <span style="font-size:1.8rem;opacity:0.4;">{icon_emoji}</span>\n    </div>\n    <div class="flex-1 min-w-0">\n      <h3 class="line-clamp-2" style="font-size:0.92rem;">{html_escape(title)}</h3>\n      <p style="color:var(--text-muted);font-size:0.75rem;line-height:1.45;margin-top:0.3rem;" class="line-clamp-2">{desc_preview}</p>\n      <div class="flex flex-wrap items-center gap-2 mt-2">\n        {tag_badges}\n        {date_html}\n      </div>\n    </div>\n  </div>\n</a>'



def list_page(title, desc, cards_html, nav_d=1):
    np = nav_prefix(nav_d)
    filter_js = "function filterCards(el,cat){document.querySelectorAll(\".filter-pill\").forEach(function(p){p.classList.remove(\"active\")});el.classList.add(\"active\");document.querySelectorAll(\"#cardList .content-card\").forEach(function(c){if(cat===\"all\"){c.style.display=\"\"}else{c.style.display=c.textContent.includes(cat)?\"\":\"none\"}})}"
    body = f'''<div class="mb-6 animate-in">
  <nav class="breadcrumb">
    <a href="{np}/index.html">首页</a>
    <span>/</span>
    <span>{html_escape(title)}</span>
  </nav>
  <h1 style="font-family:'Orbitron',sans-serif;font-size:1.5rem;font-weight:700;letter-spacing:1px;margin-top:0.3rem;background:var(--gradient-2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">{html_escape(title)}</h1>
  <p style="color:var(--text-secondary);font-size:0.9rem;margin-top:0.3rem;">{html_escape(desc)}</p>
</div>
<div class="filter-pills" style="margin-bottom:1rem;">
  <a href="javascript:void(0)" class="filter-pill active" onclick="filterCards(this,'all')">全部</a>
  <a href="javascript:void(0)" class="filter-pill" onclick="filterCards(this,'新闻')">新闻</a>
  <a href="javascript:void(0)" class="filter-pill" onclick="filterCards(this,'工具')">工具</a>
  <a href="javascript:void(0)" class="filter-pill" onclick="filterCards(this,'框架')">框架</a>
  <a href="javascript:void(0)" class="filter-pill" onclick="filterCards(this,'开源')">开源</a>
</div>
<div class="space-y-3" id="cardList">
  {cards_html}
</div>
<script>
{filter_js}
</script>'''
    return page_frame(title, body, nav_depth=nav_d)



def detail_page(title, content_html, source="", nav_d=1):
    np = nav_prefix(nav_d)
    body = f'''<div class="mb-6 animate-in">
  <nav class="breadcrumb">
    <a href="{np}/index.html">首页</a>
    <span>/</span>
    <span>{html_escape(title)}</span>
  </nav>
  <div class="flex items-center justify-between gap-3" style="margin-top:0.5rem;">
    <div class="flex items-center gap-2">
      <a href="javascript:history.back()" class="back-btn">&larr; 返回</a>
      <span style="color:var(--text-muted);font-size:0.78rem;">|</span>
      <a href="{np}/index.html" class="back-btn">首页</a>
    </div>
    <div class="flex gap-2">
      <a href="https://twitter.com/intent/tweet?text={html_escape(title)}&url=https://ckang2927-commits.github.io/ai-news-site/{np}/index.html" target="_blank" rel="noopener" class="share-btn" aria-label="分享到Twitter">⌘ Twitter</a>
      <a href="javascript:void(0)" onclick="navigator.clipboard.writeText(window.location.href);alert('链接已复制！')" class="share-btn" aria-label="复制链接">📋 复制链接</a>
    </div>
  </div>
</div>
<article class="prose glass-card" style="padding:1.5rem 2rem;animation:fadeInUp 0.6s ease forwards;">
  <h1>{html_escape(title)}</h1>
  {content_html}
</article>
<div class="source-footer animate-in" style="animation-delay:0.15s;">
  <h3>💡 数据来源</h3>
  <div style="color:var(--text-secondary);font-size:0.85rem;line-height:1.7;">{html_escape(source)}</div>
  <p style="color:var(--text-muted);font-size:0.75rem;margin-top:0.5rem;border-top:1px solid var(--glass-border);padding-top:0.5rem;">更新时间：{NOW.strftime('%Y-%m-%d')}</p>
</div>
<div class="flex justify-center gap-3 mt-6 animate-in" style="animation-delay:0.2s;">
  <a href="javascript:history.back()" class="cyber-btn">&larr; 返回</a>
  <a href="{np}/index.html" class="cyber-btn">🏠 首页</a>
</div>'''
    return page_frame(title, body, nav_depth=nav_d, og_desc=title)



def index_page(module_cards):
    nav_d = 0
    body = f'''<div class="hero-section animate-in">
  <div class="module-badge" style="margin-bottom:1rem;">⚡ LIVE &middot; 2026</div>
  <h1 class="glow-text">🦢 {SITE_NAME}</h1>
  <p class="subtitle">追踪 AI 前沿动态 &middot; 收录实用 Skills &middot; 打造你的 AI 知识库</p>
</div>
<div class="grid gap-5 sm:grid-cols-2 mb-8">
  {module_cards}
</div>
<div class="glass-card" style="padding:1.5rem;margin-top:1rem;animation:fadeInUp 0.6s ease forwards;animation-delay:0.3s;opacity:0;">
  <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.6rem;">
    <span style="font-size:1.2rem;">💡</span>
    <span style="font-family:'Orbitron',sans-serif;font-size:0.8rem;font-weight:600;letter-spacing:1px;color:var(--accent-2);">ABOUT</span>
  </div>
  <p style="color:var(--text-secondary);font-size:0.85rem;line-height:1.7;">
    这是一个由 Codex AI 与人类协作打造的 AI 内容资讯站。所有内容均标注数据来源，确保信息的可追溯性。网站持续更新中。
  </p>
  <p style="color:var(--text-muted);font-size:0.72rem;margin-top:0.8rem;border-top:1px solid var(--glass-border);padding-top:0.6rem;">最后更新：{NOW.strftime('%Y-%m-%d')}</p>
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
