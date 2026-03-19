# 🤖 Blog com IA — python3 + GitHub Pages

Blog 100% python3. Sem Ruby, sem Jekyll. Gera posts com IA, compila Markdown → HTML, testa local e publica no GitHub Pages.

## Setup (Mac)

```bash
pip install anthropic markdown
export ANTHROPIC_API_KEY="sk-ant-sua-chave-aqui"
```

## Uso

```bash
# 1. Gerar post com IA
python3 gerar_post.py -t "Introdução ao python3"
python3 gerar_post.py -t "Docker Prático" -p "Use analogias, foque em comandos"
python3 gerar_post.py -t "Resumo React 19" -l "https://react.dev/blog/..."

# 2. Compilar HTML e testar local
python3 build.py --serve
# Abre http://localhost:8000

# 3. Publicar
python3 build.py --publish
```

## Estrutura

```
blog/
├── gerar_post.py       ← gera posts com IA (Markdown)
├── build.py            ← compila HTML + serve local + publica
├── _posts/             ← posts em Markdown (fonte)
├── docs/               ← HTML gerado (GitHub Pages serve daqui)
├── templates/          ← templates HTML
└── assets/css/         ← estilos
```

## GitHub Pages

1. Crie um repo no GitHub
2. Push o código
3. Settings → Pages → Source: **Deploy from a branch**
4. Branch: `main`, Folder: `/docs`
5. Pronto! Acesse `https://seuusuario.github.io/nome-do-repo`
