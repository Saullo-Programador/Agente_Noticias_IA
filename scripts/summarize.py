

import json
import os
import re
import sys

import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
)

INPUT_PATH = "collected.json"
OUTPUT_PATH = "summarized.json"
MIN_RELEVANCE = 4
BATCH_SIZE = 12 

PROMPT_TEMPLATE = """Voce e um analista de tecnologia especializado em IA.
Para cada item da lista abaixo (titulo, fonte e resumo original em ingles ou
outro idioma), gere um objeto JSON com:
- "title": titulo traduzido/adaptado para portugues, curto
- "source": mesmo valor recebido
- "link": mesmo valor recebido
- "category": uma de ["Lancamento de modelo", "Pesquisa", "Produto/Ferramenta",
  "Negocios/Investimento", "Politica/Regulacao", "Outro"]
- "relevance": nota de 1 a 5 sobre o quanto isso importa para quem acompanha
  o mercado de IA profissionalmente (5 = muito relevante, 1 = irrelevante/ruido)
- "summary_pt": resumo em portugues, 2 a 4 frases, direto ao ponto

Responda APENAS com um array JSON valido, sem markdown, sem texto antes ou
depois, sem crases.

Itens:
{items}
"""


def call_gemini(batch):
    if not GEMINI_API_KEY:
        print("ERRO: variavel de ambiente GEMINI_API_KEY nao definida.", file=sys.stderr)
        sys.exit(1)

    items_text = json.dumps(
        [
            {
                "title": it["title"],
                "source": it["source"],
                "link": it["link"],
                "summary_raw": it["summary_raw"][:600],
            }
            for it in batch
        ],
        ensure_ascii=False,
    )

    payload = {
        "contents": [{"parts": [{"text": PROMPT_TEMPLATE.format(items=items_text)}]}],
        "generationConfig": {"temperature": 0.2},
    }

    resp = requests.post(GEMINI_URL, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    text = data["candidates"][0]["content"]["parts"][0]["text"]
    # blindagem: remove eventuais crases de markdown caso o modelo desobedeca
    text = re.sub(r"^```json|```$", "", text.strip(), flags=re.MULTILINE).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        print("[aviso] resposta do modelo nao era JSON valido, lote descartado")
        print(text[:500])
        return []


def summarize():
    with open(INPUT_PATH, encoding="utf-8") as f:
        items = json.load(f)

    if not items:
        print("Nenhum item coletado, nada para resumir.")
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)
        return

    results = []
    for i in range(0, len(items), BATCH_SIZE):
        batch = items[i : i + BATCH_SIZE]
        results.extend(call_gemini(batch))

    results = [r for r in results if r.get("relevance", 0) >= MIN_RELEVANCE]
    results.sort(key=lambda r: r.get("relevance", 0), reverse=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"{len(results)} itens com relevancia >= {MIN_RELEVANCE} -> {OUTPUT_PATH}")


if __name__ == "__main__":
    summarize()
