# Memetrade - Predict Market

> Mercados preditivos para o Brasil. Aposte no futuro com odds definidas pela inteligência coletiva — não pela casa.

Plataforma brasileira de mercados preditivos no estilo **Polymarket** e **Kalshi**, com foco em eventos relevantes para o público nacional: eleições, futebol, economia, cripto e cultura pop. Marca do produto: **afax** ([afax.online](https://afax.online)).

---

## Sobre

Cada mercado é uma pergunta com resultado verificável. Traders compram contratos **SIM** ou **NÃO** com preço entre R$ 0,01 e R$ 0,99 — o preço *é* a probabilidade implícita do evento. Quando o evento se resolve, os contratos vencedores pagam exatamente R$ 1,00.

Sem casa. Sem house edge. Sem mistério. As odds são definidas pelo mercado em tempo real.

---

## Features atuais

- Mercados binários (SIM/NÃO) e categóricos (múltiplas opções)
- Card de destaque com gráfico multi-temporal e notícias contextuais
- Ticker ao vivo dos mercados em movimento
- Sidebar com últimas notícias e tópicos quentes
- Categorias: Política, Esportes, Cripto, Economia, Cultura, Geopolítica
- Layout responsivo (desktop, tablet, mobile)

---

## Stack

### Frontend
- HTML5 + CSS3 vanilla (sem framework — por enquanto)
- Google Fonts: Instrument Serif, DM Sans, JetBrains Mono
- SVG inline para gráficos, sparklines e ícones

### Backend (planejado)
- Node.js + Fastify
- PostgreSQL + Redis
- WebSocket para preços em tempo real
- Integração PIX via Bacen
- Oráculos para resolução de mercados

---

## Estrutura

```
memetrade/
├── public/
│   ├── index.html            # Homepage
│   ├── market/[id].html      # Página individual de mercado
│   ├── portfolio.html        # Carteira do usuário
│   └── assets/
├── api/
│   ├── markets/
│   ├── orders/
│   ├── users/
│   └── webhooks/
├── docs/
└── README.md
```

---

## Setup

```bash
git clone https://github.com/your-org/memetrade
cd memetrade

# Para a versão atual (HTML estático):
python -m http.server 8000
# acesse http://localhost:8000
```

---

## Como funciona

1. **Escolha um mercado** — mais de 300 abertos sobre tudo, do próximo gol à próxima eleição
2. **Compre SIM ou NÃO** — cada contrato custa R$ 0,01 a R$ 0,99 e paga R$ 1,00 se você acertar
3. **Receba via PIX quando acertar** — liquidação automática assim que o evento se resolve

---

## Todo

### MVP — Q3 2026
- [ ] Página individual de mercado (order book + chart histórico)
- [ ] Order book + matching engine
- [ ] Autenticação (email + magic link)
- [ ] KYC básico (CPF + selfie)
- [ ] Carteira interna em BRL
- [ ] Depósito e saque via PIX

### v1.0 — Q4 2026
- [ ] Apps nativos iOS + Android
- [ ] WebSocket para preços em tempo real
- [ ] Notificações push (resolução, movimentos do mercado)
- [ ] Painel admin para criação e curadoria de mercados
- [ ] Resolução automatizada via oráculo
- [ ] Ranking público de traders e perfis individuais

### v2.0 — 2027
- [ ] Mercados categóricos com mais de 2 opções (eleições com N candidatos)
- [ ] AMM como camada de liquidez secundária
- [ ] API pública para desenvolvedores
- [ ] Programa de afiliados
- [ ] Trading social (copy trade)
- [ ] Mercados privados (empresas / influenciadores)

### Compliance & Operações
- [ ] Aprovação regulatória SECAP/MF (Lei 14.790/23)
- [ ] Integração direta com Bacen para PIX automático
- [ ] Programa de jogo responsável (limites, autoexclusão)
- [ ] Auditoria SOC 2

### Engenharia
- [ ] Migrar frontend para Next.js + React + TypeScript
- [ ] Design system formal (tokens + componentes)
- [ ] Testes E2E (Playwright)
- [ ] CI/CD (GitHub Actions)
- [ ] Observabilidade (Sentry + Grafana + Loki)
- [ ] Caching agressivo (Redis + CDN)
- [ ] Rate limiting e proteção DDoS

### Frontend (curto prazo)
- [ ] Página de detalhe do mercado
- [ ] Modal de compra com ajuste de quantidade
- [ ] Página de portfólio do trader
- [ ] Filtros avançados na lista de mercados
- [ ] Modo claro
- [ ] Internacionalização (PT-BR / EN)

---

## Disclaimer

Apostas exclusivamente para maiores de 18 anos. Aposte com responsabilidade. Em caso de necessidade, busque ajuda em [jogadoresanonimos.com.br](https://jogadoresanonimos.com.br).

---

## License

MIT © 2026 Memetrade Tech