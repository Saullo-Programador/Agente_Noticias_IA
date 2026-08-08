# radar-ia 🤖📰

Agente que roda **todo dia de manhã**, sozinho, sem servidor nenhum:

1. Coleta as notícias mais recentes de fontes de tecnologia/IA (RSS)
2. Usa a API do Gemini (free tier) para resumir e classificar cada item em português
3. Filtra só o que é realmente relevante (nota 4-5 de 5)
4. Gera um relatório em Markdown e **commita no próprio repositório**, em `reports/`
5. Opcionalmente envia o relatório por e-mail

Tudo roda via **GitHub Actions** — 100% gratuito, sem precisar de servidor, Docker ou conta em nuvem paga. Veja a aba **Actions** deste repositório para o histórico de execuções, e a pasta **[reports/](./reports)** para o histórico dos relatórios.

## Como testar você mesmo (leva ~3 minutos)

1. **Fork** este repositório.
2. Consiga uma chave grátis do Gemini em [aistudio.google.com/apikey](https://aistudio.google.com/apikey) (sem cartão de crédito).
3. No seu fork, vá em **Settings → Secrets and variables → Actions → New repository secret** e adicione:
   - `GEMINI_API_KEY` = sua chave
4. Vá na aba **Actions**, abra o workflow **"Radar diario de IA"** e clique em **Run workflow** para rodar na hora (não precisa esperar o horário agendado).
5. Em ~1-2 minutos, um novo arquivo aparece em `reports/AAAA-MM-DD.md` com o relatório do dia.

### Envio por e-mail (opcional)

Se quiser receber por e-mail também, adicione mais estes secrets (exemplo com Gmail):

| Secret | Valor |
|---|---|
| `SMTP_HOST` | `smtp.gmail.com` |
| `SMTP_PORT` | `587` |
| `SMTP_USER` | seu e-mail |
| `SMTP_PASS` | uma [App Password](https://myaccount.google.com/apppasswords) do Gmail (não a senha normal) |
| `EMAIL_TO` | e-mail de destino |

Se esses secrets não forem configurados, essa etapa é simplesmente pulada — o relatório continua sendo gerado e commitado normalmente.

## Como funciona por dentro

```
scripts/
  feeds.py           # lista de fontes RSS (edite à vontade)
  collect_news.py     # coleta itens das últimas ~26h
  summarize.py         # resume/classifica cada item via Gemini API
  build_report.py     # monta o markdown final, agrupado por categoria
  send_email.py        # envio opcional por SMTP
.github/workflows/
  daily.yml            # agenda diária (cron) + execução manual
reports/
  AAAA-MM-DD.md        # histórico diário
  latest.md            # sempre igual ao relatório mais recente
```

Agendamento: todo dia às 07:00 (horário de Brasília), via `cron` no GitHub Actions. Pode rodar manualmente a qualquer momento pelo botão **Run workflow**.

## Rodando localmente (opcional)

```bash
pip install -r requirements.txt
export GEMINI_API_KEY=sua_chave
python scripts/collect_news.py
python scripts/summarize.py
python scripts/build_report.py
```

## Por que Markdown + GitHub Actions em vez de n8n?

Este é um projeto pensado para ser aberto, gratuito e testável por qualquer pessoa sem infraestrutura própria. Um workflow visual (n8n, Zapier etc.) exigiria uma instância rodando 24/7. Aqui, o GitHub já fornece o agendador, o histórico de execuções e o hospedeiro do resultado — de graça.

## Licença

MIT — use, copie, modifique à vontade.
#
