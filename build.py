#!/usr/bin/env python3
"""
Compila os posts Markdown em HTML estático com suporte multi-idioma.

Uso:
  python build.py              # gera HTML em docs/
  python build.py --serve      # gera e abre servidor local em http://localhost:8000
  python build.py --publish    # gera, commit e push
"""

import argparse
import http.server
import os
import re
import subprocess
import functools
from datetime import datetime
from pathlib import Path

try:
    import markdown
except ImportError:
    print("❌ Instale: pip install markdown")
    exit(1)

ROOT = Path(__file__).parent
POSTS_DIR = ROOT / "_posts"
DOCS_DIR = ROOT / "docs"
TEMPLATE_DIR = ROOT / "templates"

# ── Config do blog (edite aqui) ──────────────────────────────
SITE_TITLE = "MEMETRADE"
SITE_DESC = "The Latest Viral News"
SITE_URL = "memetrade.org"  # ← mude para sua URL
LANGUAGES = ["en", "pt", "es"]
DEFAULT_LANG = "en"
POSTS_PER_PAGE = 12
# ──────────────────────────────────────────────────────────────

DEFAULT_COVERS = [
    "https://picsum.photos/seed/meme1/800/450",
    "https://picsum.photos/seed/meme2/800/450",
    "https://picsum.photos/seed/meme3/800/450",
    "https://picsum.photos/seed/meme4/800/450",
    "https://picsum.photos/seed/meme5/800/450",
    "https://picsum.photos/seed/meme6/800/450",
]

I18N = {
    "en": {"back": "← Back to home", "powered": "Powered by <a href=\"https://aithor.ca\">Aithor</a> – Your Blog on Autopilot"},
    "pt": {"back": "← Voltar ao início", "powered": "Powered by <a href=\"https://aithor.ca\">Aithor</a> – Seu Blog no Piloto Automático"},
    "es": {"back": "← Volver al inicio", "powered": "Powered by <a href=\"https://aithor.ca\">Aithor</a> – Tu Blog en Piloto Automático"},
}


def parse_front_matter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    meta = {}
    for line in parts[1].strip().splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            meta[key.strip()] = val.strip()
    return meta, parts[2].strip()


def slugify(text: str) -> str:
    text = text.lower().strip()
    for a, b in [("àáâãä","a"),("èéêë","e"),("ìíîï","i"),("òóôõö","o"),("ùúûü","u"),("ç","c"),("ñ","n")]:
        for ch in a:
            text = text.replace(ch, b)
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s]+", "-", text)
    return text.strip("-")


def read_template(name: str) -> str:
    return (TEMPLATE_DIR / f"{name}.html").read_text(encoding="utf-8")


def render(template: str, **kwargs) -> str:
    for key, val in kwargs.items():
        template = template.replace(f"{{{{ {key} }}}}", str(val))
    return template


def format_date(date_str: str, lang: str = "en") -> str:
    try:
        dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
        if lang in ("pt", "es"):
            return dt.strftime("%d/%m/%Y")
        return dt.strftime("%b %d, %Y")
    except Exception:
        return date_str


def get_post_lang(meta: dict) -> str:
    lang = meta.get("lang", DEFAULT_LANG).strip().lower()
    return lang if lang in LANGUAGES else DEFAULT_LANG


def build_lang_switcher(current_lang: str, base_path: str) -> str:
    """Gera HTML do seletor de idioma. base_path é relativo à raiz do docs."""
    items = []
    for lang in LANGUAGES:
        label = lang.upper()
        if lang == current_lang:
            items.append(f'<span class="lang-active">{label}</span>')
        else:
            # Caminho relativo do arquivo atual até a versão no outro idioma
            href = f"{base_path}{lang}/"
            items.append(f'<a href="{href}">{label}</a>')
    return " ".join(items)


def build():
    print("🔨 Compilando MEMETRADE...\n")

    base_tpl = read_template("base")
    post_tpl = read_template("post")
    index_tpl = read_template("index")
    md = markdown.Markdown(extensions=["fenced_code", "codehilite", "tables"])

    # Processa todos os posts
    all_posts = []
    for filepath in sorted(POSTS_DIR.glob("*.md"), reverse=True):
        raw = filepath.read_text(encoding="utf-8")
        meta, content = parse_front_matter(raw)
        md.reset()
        all_posts.append({
            "title": meta.get("title", filepath.stem),
            "date": meta.get("date", "")[:10],
            "slug": slugify(meta.get("title", filepath.stem)),
            "cover": meta.get("cover", ""),
            "lang": get_post_lang(meta),
            "html": md.convert(content),
        })

    sitemap_entries = []
    css_src = (ROOT / "assets" / "css" / "style.css").read_text(encoding="utf-8")

    for lang in LANGUAGES:
        lang_dir = DOCS_DIR / lang
        posts_dir = lang_dir / "posts"
        posts_dir.mkdir(parents=True, exist_ok=True)

        for f in posts_dir.glob("*.html"):
            f.unlink()

        # CSS por idioma
        css_dir = lang_dir / "assets" / "css"
        css_dir.mkdir(parents=True, exist_ok=True)
        (css_dir / "style.css").write_text(css_src, encoding="utf-8")

        lang_posts = [p for p in all_posts if p["lang"] == lang]
        strings = I18N[lang]
        built_posts = []

        for i, p in enumerate(lang_posts):
            cover = p["cover"] or DEFAULT_COVERS[i % len(DEFAULT_COVERS)]
            out_name = f"{p['date']}-{p['slug']}.html" if p["date"] else f"{p['slug']}.html"

            lang_sw = build_lang_switcher(lang, "../../")

            post_body = render(post_tpl,
                title=p["title"], date=p["date"],
                date_formatted=format_date(p["date"], lang),
                content=p["html"], cover=cover,
                back_text=strings["back"],
            )
            page = render(base_tpl,
                title=f"{p['title']} — {SITE_TITLE}",
                site_title=SITE_TITLE, site_desc=SITE_DESC,
                css_path="../", home_path="../",
                content=post_body, lang=lang,
                lang_switch=lang_sw,
                powered=strings["powered"],
            )
            (posts_dir / out_name).write_text(page, encoding="utf-8")
            print(f"  ✅ /{lang}/posts/{out_name}")

            built_posts.append({
                "title": p["title"], "date": p["date"],
                "date_formatted": format_date(p["date"], lang),
                "url": f"posts/{out_name}", "cover": cover,
            })
            sitemap_entries.append(f"{SITE_URL}/{lang}/posts/{out_name}")

        # Paginação
        total_pages = max(1, -(-len(built_posts) // POSTS_PER_PAGE))  # ceil division

        for page_num in range(1, total_pages + 1):
            start = (page_num - 1) * POSTS_PER_PAGE
            end = start + POSTS_PER_PAGE
            page_posts = built_posts[start:end]

            cards = ""
            for j, bp in enumerate(page_posts):
                size = "card-hero" if j == 0 and page_num == 1 else ""
                # Posts path: from index.html it's "posts/...", from page/N.html it's "../posts/..."
                post_url = bp["url"] if page_num == 1 else f"../{bp['url']}"
                cards += (
                    f'<li class="card {size}">'
                    f'<a href="{post_url}">'
                    f'<img class="card-img" src="{bp["cover"]}" alt="{bp["title"]}">'
                    f'<div class="card-body">'
                    f'<time>{bp["date_formatted"]}</time>'
                    f'<h2>{bp["title"]}</h2>'
                    f'</div></a></li>\n'
                )

            if not cards:
                cards = '<li class="empty">No posts yet.</li>'

            # Navegação entre páginas
            pagination = ""
            if total_pages > 1:
                pagination = '<nav class="pagination">'
                if page_num > 1:
                    prev_href = "../index.html" if page_num == 2 else f"{page_num - 1}.html"
                    pagination += f'<a href="{prev_href}" class="pg-prev">← Prev</a>'
                else:
                    pagination += '<span class="pg-disabled">← Prev</span>'

                pagination += f'<span class="pg-info">{page_num} / {total_pages}</span>'

                if page_num < total_pages:
                    next_href = f"page/{page_num + 1}.html" if page_num == 1 else f"{page_num + 1}.html"
                    pagination += f'<a href="{next_href}" class="pg-next">Next →</a>'
                else:
                    pagination += '<span class="pg-disabled">Next →</span>'

                pagination += '</nav>'

            lang_sw = build_lang_switcher(lang, "../")
            index_body = render(index_tpl, post_list=cards, pagination=pagination)

            # CSS path depends on depth
            if page_num == 1:
                css_p, home_p = "", ""
                out_file = lang_dir / "index.html"
            else:
                css_p, home_p = "../", "../"
                page_dir = lang_dir / "page"
                page_dir.mkdir(exist_ok=True)
                out_file = page_dir / f"{page_num}.html"

            index_page = render(base_tpl,
                title=f"{SITE_TITLE} — {SITE_DESC}",
                site_title=SITE_TITLE, site_desc=SITE_DESC,
                css_path=css_p, home_path=home_p,
                content=index_body, lang=lang,
                lang_switch=lang_sw,
                powered=strings["powered"],
            )
            out_file.write_text(index_page, encoding="utf-8")

            if page_num == 1:
                print(f"  ✅ /{lang}/index.html ({len(page_posts)} posts)")
            else:
                print(f"  ✅ /{lang}/page/{page_num}.html ({len(page_posts)} posts)")

        sitemap_entries.append(f"{SITE_URL}/{lang}/")

    # Root redirect → /en/
    (DOCS_DIR / "index.html").write_text(
        f'<!DOCTYPE html><html><head><meta http-equiv="refresh" content="0;url=/{DEFAULT_LANG}/"></head><body></body></html>',
        encoding="utf-8",
    )

    # Sitemap
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for url in sitemap_entries:
        sitemap += f'  <url><loc>{url}</loc></url>\n'
    sitemap += '</urlset>'
    (DOCS_DIR / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    print(f"  ✅ sitemap.xml ({len(sitemap_entries)} URLs)")

    (DOCS_DIR / ".nojekyll").touch()
    print(f"\n✨ MEMETRADE compilado ({len(all_posts)} posts, {len(LANGUAGES)} idiomas)")


def serve():
    os.chdir(DOCS_DIR)
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(DOCS_DIR))
    server = http.server.HTTPServer(("localhost", 8000), handler)
    print(f"\n🌐 http://localhost:8000")
    print("   Ctrl+C para parar\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋")


def publish():
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"build: {datetime.now().strftime('%Y-%m-%d %H:%M')}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("\n🚀 Publicado!")
    except subprocess.CalledProcessError as e:
        print(f"\n⚠️  Erro no git: {e}")


def main():
    parser = argparse.ArgumentParser(description="Compila e serve o MEMETRADE")
    parser.add_argument("--serve", "-s", action="store_true")
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    build()
    if args.publish:
        publish()
    elif args.serve:
        serve()


if __name__ == "__main__":
    main()