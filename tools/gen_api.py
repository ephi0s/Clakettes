#!/usr/bin/env python3
import argparse
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "backend"
ROUTERS = ROOT / "app" / "routers"
MAIN = (ROOT / "app" / "main.py").read_text(encoding="utf-8")
DOCS = Path(__file__).resolve().parents[1] / "docs"

LANGS = {
    "es": {
        "title": "# API — referencia de endpoints",
        "gen": "Generado desde `app/routers/*.py` + prefijos de `app/main.py`.",
        "detail": "Detalle interactivo: `/docs` (Swagger) y `/redoc` con el backend en marcha.",
        "header": "| Método | Ruta | Auth |",
        "yes": "sí",
        "no": "no",
        "optional": "opcional",
        "total": "Total: {n} endpoints en {m} routers.",
    },
    "en": {
        "title": "# API — endpoint reference",
        "gen": "Generated from `app/routers/*.py` + prefixes in `app/main.py`.",
        "detail": "Interactive detail: `/docs` (Swagger) and `/redoc` with the backend running.",
        "header": "| Method | Path | Auth |",
        "yes": "yes",
        "no": "no",
        "optional": "optional",
        "total": "Total: {n} endpoints in {m} routers.",
    },
    "fr": {
        "title": "# API — référence des endpoints",
        "gen": "Généré depuis `app/routers/*.py` + préfixes de `app/main.py`.",
        "detail": "Détail interactif : `/docs` (Swagger) et `/redoc` avec le backend lancé.",
        "header": "| Méthode | Chemin | Auth |",
        "yes": "oui",
        "no": "non",
        "optional": "optionnel",
        "total": "Total : {n} endpoints dans {m} routers.",
    },
    "de": {
        "title": "# API — Endpunktreferenz",
        "gen": "Erzeugt aus `app/routers/*.py` + Präfixen in `app/main.py`.",
        "detail": "Interaktive Details: `/docs` (Swagger) und `/redoc` bei laufendem Backend.",
        "header": "| Methode | Pfad | Auth |",
        "yes": "ja",
        "no": "nein",
        "optional": "optional",
        "total": "Gesamt: {n} Endpunkte in {m} Routern.",
    },
    "it": {
        "title": "# API — riferimento endpoint",
        "gen": "Generato da `app/routers/*.py` + prefissi di `app/main.py`.",
        "detail": "Dettaglio interattivo: `/docs` (Swagger) e `/redoc` col backend avviato.",
        "header": "| Metodo | Percorso | Auth |",
        "yes": "sì",
        "no": "no",
        "optional": "opzionale",
        "total": "Totale: {n} endpoint in {m} router.",
    },
    "ca": {
        "title": "# API — referència d'endpoints",
        "gen": "Generat des de `app/routers/*.py` + prefixos de `app/main.py`.",
        "detail": "Detall interactiu: `/docs` (Swagger) i `/redoc` amb el backend en marxa.",
        "header": "| Mètode | Ruta | Auth |",
        "yes": "sí",
        "no": "no",
        "optional": "opcional",
        "total": "Total: {n} endpoints en {m} routers.",
    },
    "eu": {
        "title": "# API — endpointen erreferentzia",
        "gen": "`app/routers/*.py` + `app/main.py`-ko aurrizkietatik sortua.",
        "detail": "Xehetasun interaktiboa: `/docs` (Swagger) eta `/redoc` backend-a martxan.",
        "header": "| Metodoa | Ibilbidea | Auth |",
        "yes": "bai",
        "no": "ez",
        "optional": "aukerakoa",
        "total": "Guztira: {n} endpoint {m} routerretan.",
    },
    "gl": {
        "title": "# API — referencia de endpoints",
        "gen": "Xerado desde `app/routers/*.py` + prefixos de `app/main.py`.",
        "detail": "Detalle interactivo: `/docs` (Swagger) e `/redoc` co backend en marcha.",
        "header": "| Método | Ruta | Auth |",
        "yes": "si",
        "no": "non",
        "optional": "opcional",
        "total": "Total: {n} endpoints en {m} routers.",
    },
    "oc": {
        "title": "# API — referéncia dels endpoints",
        "gen": "Generat dempuèi `app/routers/*.py` + prefixes de `app/main.py`.",
        "detail": "Datalh interactiu: `/docs` (Swagger) e `/redoc` amb lo backend en marcha.",
        "header": "| Metòde | Camin | Auth |",
        "yes": "òc",
        "no": "non",
        "optional": "opcional",
        "total": "Total: {n} endpoints en {m} routers.",
    },
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", default="es", choices=sorted(LANGS))
    parser.add_argument("--all", action="store_true", help="generate every locale")
    args = parser.parse_args()
    langs = sorted(LANGS) if args.all else [args.lang]

    prefix_of = {}
    for m in re.finditer(r"app\.include_router\(\s*(\w+)\.router,\s*prefix=\"([^\"]+)\"", MAIN):
        prefix_of[m.group(1)] = m.group(2)

    for lang in langs:
        t = LANGS[lang]
        out = [t["title"], "", t["gen"], t["detail"], ""]
        total = 0
        for f in sorted(ROUTERS.glob("*.py")):
            if f.name == "__init__.py":
                continue
            tree = ast.parse(f.read_text(encoding="utf-8"))
            rows = []
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                for dec in node.decorator_list:
                    if not isinstance(dec, ast.Call):
                        continue
                    func = dec.func
                    if not isinstance(func, ast.Attribute) or func.value.id != "router":
                        continue
                    method = func.attr.upper()
                    path = ast.literal_eval(dec.args[0]) if dec.args else ""
                    rows.append((method, path, node.name))
            if not rows:
                continue
            mod = f.stem
            prefix = prefix_of.get(mod, "")
            out.append(f"## `{mod}` → `{prefix or '/'}`")
            out.append("")
            out.append(t["header"])
            out.append("|---|---|---|")
            src = f.read_text(encoding="utf-8")
            for method, path, name in rows:
                m = re.search(
                    rf"(async )?def {name}\(.*?\):(.*?)(?=\n@router|\ndef |\nasync def |\Z)",
                    src,
                    re.S,
                )
                body = m.group(0) if m else ""
                if method == "WEBSOCKET":
                    auth = "token (query)"
                elif "get_current_user_optional" in body:
                    auth = t["optional"]
                elif "get_current_user" in body:
                    auth = t["yes"]
                else:
                    auth = t["no"]
                full = (prefix + path).replace("//", "/")
                out.append(f"| {method} | `{full}` | {auth} |")
                total += 1
            out.append("")
        out.append(t["total"].format(n=total, m=len(prefix_of)))
        target = DOCS / ("API.md" if lang == "es" else f"API.{lang}.md")
        target.write_text("\n".join(out), encoding="utf-8")
        print(lang, "endpoints:", total, "| routers con prefijo:", len(prefix_of))


if __name__ == "__main__":
    main()
