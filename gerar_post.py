#!/usr/bin/env python3
"""
Gera posts para MEMETRADE usando Claude AI + Web Search.

Uso:
  # Só tema — a IA pesquisa na internet e gera o artigo
  python gerar_post.py -t "Bitcoin crash 2026"

  # Tema + idioma
  python gerar_post.py -t "Elon Musk Mars" --lang pt

  # Com instruções extras
  python gerar_post.py -t "AI regulation EU" -p "tom sarcástico" --lang es

  # Com links de referência manuais (não usa web search)
  python gerar_post.py -t "React 20" --links "https://react.dev/blog/..."

  # Com imagem de capa
  python gerar_post.py -t "OpenAI drama" --cover "https://img.com/foto.jpg"

  # Sem web search (modo offline)
  python gerar_post.py -t "Meu tema" --no-search
"""

import argparse
import json
import re
import urllib.request
from datetime import datetime
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("❌ Instale o SDK: pip install anthropic")
    print("   E defina: export ANTHROPIC_API_KEY='sua-chave'")
    exit(1)

POSTS_DIR = Path(__file__).parent / "_posts"
MODEL = "claude-sonnet-4-20250514"

LANG_PROMPTS = {
    "en": "You are a blog writer for MEMETRADE, a BuzzFeed-style news blog. Write in English.",
    "pt": "Você é redator do MEMETRADE, um blog de notícias estilo BuzzFeed. Escreva em português brasileiro.",
    "es": "Eres redactor de MEMETRADE, un blog de noticias estilo BuzzFeed. Escribe en español.",
}

BASE_PROMPT = """
Write a complete, well-structured blog post with introduction, development and conclusion.
Use ## and ### subtitles to organize content.
Be informative, accessible and direct. Include examples when relevant.
Do NOT include the main title (it goes in the front matter).
Return ONLY the Markdown content, no front matter, no ```markdown``` fences.
Write in a BuzzFeed-like engaging tone: punchy, fun, with personality.
When you have web search results, USE THEM to write a factual, up-to-date article.
Cite sources naturally in the text (e.g. "According to Reuters..." or "As reported by...").
"""


def slugify(text: str) -> str:
    text = text.lower().strip()
    for a, b in [("àáâãä","a"),("èéêë","e"),("ìíîï","i"),("òóôõö","o"),("ùúûü","u"),("ç","c"),("ñ","n")]:
        for ch in a:
            text = text.replace(ch, b)
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s]+", "-", text)
    return text.strip("-")


def fetch_url_content(url: str) -> str:
    try:
        print(f"  📥 Baixando: {url}")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:8000]
    except Exception as e:
        print(f"  ⚠️  Erro ao baixar {url}: {e}")
        return f"[Erro ao acessar: {url}]"


def generate_post_with_search(titulo: str, lang: str, prompt_extra: str = "") -> str:
    """Gera post usando web search — a IA pesquisa sozinha."""
    client = anthropic.Anthropic()
    system = LANG_PROMPTS.get(lang, LANG_PROMPTS["en"]) + BASE_PROMPT

    user_msg = (
        f'Research the topic "{titulo}" using web search to find the latest news and information. '
        f'Then write a complete blog post about it based on what you found. '
        f'Make it current, factual, and engaging.'
    )
    if prompt_extra:
        user_msg += f"\n\nAdditional instructions: {prompt_extra}"

    print(f"  🔍 Pesquisando e gerando com Claude + Web Search...")

    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=system,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": user_msg}],
    )

    # Extrai o texto da resposta (ignora blocos de tool_use)
    text_parts = []
    for block in response.content:
        if block.type == "text":
            text_parts.append(block.text)
    return "\n".join(text_parts)


def generate_post_with_links(titulo: str, lang: str, prompt_extra: str = "", links: list = None) -> str:
    """Gera post usando links fornecidos manualmente (sem web search)."""
    client = anthropic.Anthropic()
    system = LANG_PROMPTS.get(lang, LANG_PROMPTS["en"]) + BASE_PROMPT

    user_msg = f'Write a blog post titled: "{titulo}"\n'
    if links:
        user_msg += "\nUse these as reference:\n"
        for url in links:
            content = fetch_url_content(url)
            user_msg += f"\n--- Content from {url} ---\n{content}\n"
    if prompt_extra:
        user_msg += f"\nAdditional instructions: {prompt_extra}\n"

    print(f"  🤖 Gerando com Claude...")

    response = client.messages.create(
        model=MODEL, max_tokens=4096, system=system,
        messages=[{"role": "user", "content": user_msg}],
    )
    return response.content[0].text


def generate_post_offline(titulo: str, lang: str, prompt_extra: str = "") -> str:
    """Gera post sem internet, só com conhecimento do modelo."""
    client = anthropic.Anthropic()
    system = LANG_PROMPTS.get(lang, LANG_PROMPTS["en"]) + BASE_PROMPT

    user_msg = f'Write a blog post titled: "{titulo}"\n'
    if prompt_extra:
        user_msg += f"\nAdditional instructions: {prompt_extra}\n"

    print(f"  🤖 Gerando com Claude (offline)...")

    response = client.messages.create(
        model=MODEL, max_tokens=4096, system=system,
        messages=[{"role": "user", "content": user_msg}],
    )
    return response.content[0].text


def save_post(titulo: str, content: str, lang: str, cover: str) -> Path:
    POSTS_DIR.mkdir(exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    slug = slugify(titulo)
    filename = f"{date_str}-{slug}.md"
    filepath = POSTS_DIR / filename

    front_matter = f"---\ntitle: {titulo}\ndate: {datetime.now().strftime('%Y-%m-%d %H:%M')}\nlang: {lang}\n"
    if cover:
        front_matter += f"cover: {cover}\n"
    front_matter += "---\n\n"

    filepath.write_text(front_matter + content, encoding="utf-8")
    return filepath


def main():
    parser = argparse.ArgumentParser(description="Gera posts com IA para MEMETRADE")
    parser.add_argument("--titulo", "-t", required=True, help="Título ou tema do post")
    parser.add_argument("--lang", default="en", choices=["en", "pt", "es"], help="Idioma (default: en)")
    parser.add_argument("--cover", "-c", default="", help="URL da imagem de capa")
    parser.add_argument("--prompt", "-p", default="", help="Instruções extras")
    parser.add_argument("--links", "-l", nargs="+", default=[], help="URLs de referência (desativa web search)")
    parser.add_argument("--no-search", action="store_true", help="Não usar web search")
    args = parser.parse_args()

    print(f"\n📝 MEMETRADE [{args.lang.upper()}]: \"{args.titulo}\"\n")

    if args.links:
        # Modo links manuais
        content = generate_post_with_links(args.titulo, args.lang, args.prompt, args.links)
    elif args.no_search:
        # Modo offline
        content = generate_post_offline(args.titulo, args.lang, args.prompt)
    else:
        # Modo padrão: web search + gerar
        content = generate_post_with_search(args.titulo, args.lang, args.prompt)

    filepath = save_post(args.titulo, content, args.lang, args.cover)

    print(f"\n  ✅ Salvo: {filepath}")
    print(f"  Agora: python build.py --serve\n")


if __name__ == "__main__":
    main()