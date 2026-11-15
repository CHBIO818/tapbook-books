import json, os, shutil, subprocess, sys, glob, html
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(ROOT, "tapbook", "scripts")
SITE, ZIPS, TMP = [os.path.join(ROOT, d) for d in ("site", "zips", "_tmp")]
for d in (SITE, ZIPS, TMP): os.makedirs(d, exist_ok=True)
def run(*a):
    print("$", " ".join(a), flush=True); subprocess.run(a, check=True)
items = []
for meta_path in sorted(glob.glob(os.path.join(ROOT, "books", "*", "meta.json"))):
    slug = os.path.basename(os.path.dirname(meta_path)); meta = json.load(open(meta_path, encoding="utf-8"))
    work = os.path.join(TMP, slug); shutil.copytree(os.path.join(ROOT, "books", slug, "book"), work)
    run(sys.executable, f"{S}/generate_audio.py", "build", f"{work}/book.json", "--root", work,
        "--voice-en", meta["voiceEn"], "--voice-zh", meta["voiceZh"], f"--rate={meta.get('rate','-10%')}", "--concurrency", "6", "--retries", "4")
    run(sys.executable, f"{S}/validate_book.py", f"{work}/book.json", "--root", work)
    run(sys.executable, f"{S}/package_book.py", work, "--output-dir", f"{SITE}/{slug}", "--zip", f"{ZIPS}/{slug}-tapbook.zip")
    items.append((slug, meta))
lis = "\n".join(f'<li><a href="{s}/"><b>{html.escape(m["title"])}</b><span>{html.escape(m.get("titleZh",""))}</span><small>{html.escape(m.get("credit",""))}</small></a></li>' for s, m in items)
open(f"{SITE}/index.html", "w", encoding="utf-8").write(f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>中英点读绘本</title>
<style>body{{font-family:system-ui,-apple-system,"PingFang SC",sans-serif;background:#fdf6ec;margin:0;padding:24px;color:#3b2f2a}}h1{{font-size:26px}}ul{{list-style:none;padding:0;display:grid;gap:14px}}a{{display:flex;flex-direction:column;gap:4px;padding:18px 20px;background:#fff;border-radius:18px;text-decoration:none;color:inherit;box-shadow:0 2px 10px #0001;font-size:20px}}span{{font-size:18px;color:#c0602a}}small{{color:#8a7a70;font-size:13px}}</style></head>
<body><h1>中英点读绘本</h1><ul>{lis}</ul></body></html>""")
print("built", [s for s, _ in items])
