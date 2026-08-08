"""
Le summarized.json e gera reports/AAAA-MM-DD.md, agrupado por categoria.
"""

import json
from collections import defaultdict
from datetime import date

INPUT_PATH = "summarized.json"
CATEGORY_ORDER = [
    "Lancamento de modelo",
    "Pesquisa",
    "Produto/Ferramenta",
    "Negocios/Investimento",
    "Politica/Regulacao",
    "Outro",
]


def build():
    with open(INPUT_PATH, encoding="utf-8") as f:
        items = json.load(f)

    today = date.today().isoformat()
    report_path = f"reports/{today}.md"

    lines = [f"# Radar de IA - {today}", ""]

    if not items:
        lines.append("_Nenhuma noticia relevante encontrada hoje._")
    else:
        by_category = defaultdict(list)
        for item in items:
            by_category[item.get("category", "Outro")].append(item)

        for category in CATEGORY_ORDER:
            entries = by_category.get(category)
            if not entries:
                continue
            lines.append(f"## {category}")
            lines.append("")
            for item in entries:
                stars = "★" * int(item.get("relevance", 0))
                lines.append(
                    f"- **[{item['title']}]({item['link']})** "
                    f"({item['source']}, {stars})  \n  {item['summary_pt']}"
                )
            lines.append("")

    lines.append("---")
    lines.append("_Gerado automaticamente por agente-noticias-ia._")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # tambem grava/atualiza um "latest.md" fixo, util pro README e pro e-mail
    with open("reports/latest.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # versao JSON do dia, consumida pela pagina (index.html / GitHub Pages)
    with open(f"reports/{today}.json", "w", encoding="utf-8") as f:
        json.dump({"date": today, "items": items}, f, ensure_ascii=False, indent=2)

    print(f"Relatorio gerado em {report_path}")


if __name__ == "__main__":
    build()
