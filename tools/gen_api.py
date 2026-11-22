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
        "gen": (
            "Generado desde `app/routers/*.py` (prefijo de cada `APIRouter` más el de "
            "`app/main.py`) y dependencias de cada endpoint."
        ),
        "detail": "Detalle interactivo: `/docs` (Swagger) y `/redoc` con el backend en marcha.",
        "media": (
            "Todas las subidas devuelven una ruta relativa `/uploads/<carpeta>/<archivo>`, "
            "nunca una URL absoluta. El cliente la resuelve con `resolveMediaUrl()`, que "
            "antepone el servidor activo; las URLs `http(s)` se dejan intactas. Los campos "
            "de medios (`logo_url`, `banner_url`, `video_url`, `thumbnail_url`) aceptan "
            "ambos formatos."
        ),
        "header": "| Método | Ruta | Auth |",
        "yes": "sí",
        "no": "no",
        "optional": "opcional",
        "yes_admin": "sí (admin)",
        "federation": "JWT de federación",
        "token_query": "token (query, obligatorio)",
        "deprecated": "obsoleto",
        "total": "Total: {n} endpoints en {r} routers ({m} con prefijo en `main.py`).",
    },
    "en": {
        "title": "# API — endpoint reference",
        "gen": (
            "Generated from `app/routers/*.py` (each `APIRouter` prefix plus the one in "
            "`app/main.py`) and each endpoint's dependencies."
        ),
        "detail": "Interactive detail: `/docs` (Swagger) and `/redoc` with the backend running.",
        "media": (
            "All uploads return a relative `/uploads/<folder>/<file>` path, never an "
            "absolute URL. The client resolves it with `resolveMediaUrl()`, which prepends "
            "the active server; `http(s)` URLs are left unchanged. Media fields "
            "(`logo_url`, `banner_url`, `video_url`, `thumbnail_url`) accept both formats."
        ),
        "header": "| Method | Path | Auth |",
        "yes": "yes",
        "no": "no",
        "optional": "optional",
        "yes_admin": "yes (admin)",
        "federation": "federation JWT",
        "token_query": "token (query, required)",
        "deprecated": "deprecated",
        "total": "Total: {n} endpoints in {r} routers ({m} with a prefix in `main.py`).",
    },
    "fr": {
        "title": "# API — référence des endpoints",
        "gen": (
            "Généré depuis `app/routers/*.py` (préfixe de chaque `APIRouter` plus celui de "
            "`app/main.py`) et des dépendances de chaque endpoint."
        ),
        "detail": "Détail interactif : `/docs` (Swagger) et `/redoc` avec le backend lancé.",
        "media": (
            "Tous les téléversements renvoient un chemin relatif `/uploads/<dossier>/<fichier>`, "
            "jamais une URL absolue. Le client le résout avec `resolveMediaUrl()`, qui "
            "préfixe le serveur actif ; les URL `http(s)` restent inchangées. Les champs "
            "de médias (`logo_url`, `banner_url`, `video_url`, `thumbnail_url`) acceptent "
            "les deux formats."
        ),
        "header": "| Méthode | Chemin | Auth |",
        "yes": "oui",
        "no": "non",
        "optional": "optionnel",
        "yes_admin": "oui (admin)",
        "federation": "JWT de fédération",
        "token_query": "jeton (query, obligatoire)",
        "deprecated": "obsolète",
        "total": "Total : {n} endpoints dans {r} routers ({m} avec un préfixe dans `main.py`).",
    },
    "de": {
        "title": "# API — Endpunktreferenz",
        "gen": (
            "Erzeugt aus `app/routers/*.py` (Präfix jedes `APIRouter` plus dem in "
            "`app/main.py`) und den Abhängigkeiten jedes Endpunkts."
        ),
        "detail": "Interaktive Details: `/docs` (Swagger) und `/redoc` bei laufendem Backend.",
        "media": (
            "Alle Uploads geben einen relativen Pfad `/uploads/<ordner>/<datei>` zurück, "
            "nie eine absolute URL. Der Client löst ihn mit `resolveMediaUrl()` auf, das "
            "den aktiven Server voranstellt; `http(s)`-URLs bleiben unverändert. "
            "Medienfelder (`logo_url`, `banner_url`, `video_url`, `thumbnail_url`) "
            "akzeptieren beide Formate."
        ),
        "header": "| Methode | Pfad | Auth |",
        "yes": "ja",
        "no": "nein",
        "optional": "optional",
        "yes_admin": "ja (Admin)",
        "federation": "Föderations-JWT",
        "token_query": "Token (Query, Pflicht)",
        "deprecated": "veraltet",
        "total": "Gesamt: {n} Endpunkte in {r} Routern ({m} mit Präfix in `main.py`).",
    },
    "it": {
        "title": "# API — riferimento endpoint",
        "gen": (
            "Generato da `app/routers/*.py` (prefissi di ogni `APIRouter` più quello in "
            "`app/main.py`) e dalle dipendenze di ogni endpoint."
        ),
        "detail": "Dettaglio interattivo: `/docs` (Swagger) e `/redoc` col backend avviato.",
        "media": (
            "Tutti i caricamenti restituiscono un percorso relativo `/uploads/<cartella>/<file>`, "
            "mai un URL assoluto. Il client lo risolve con `resolveMediaUrl()`, che prepone "
            "il server attivo; gli URL `http(s)` restano invariati. I campi multimediali "
            "(`logo_url`, `banner_url`, `video_url`, `thumbnail_url`) accettano entrambi "
            "i formati."
        ),
        "header": "| Metodo | Percorso | Auth |",
        "yes": "sì",
        "no": "no",
        "optional": "opzionale",
        "yes_admin": "sì (admin)",
        "federation": "JWT di federazione",
        "token_query": "token (query, obbligatorio)",
        "deprecated": "deprecato",
        "total": "Totale: {n} endpoint in {r} router ({m} con prefisso in `main.py`).",
    },
    "ca": {
        "title": "# API — referència d'endpoints",
        "gen": (
            "Generat des de `app/routers/*.py` (prefix de cada `APIRouter` més el de "
            "`app/main.py`) i les dependències de cada endpoint."
        ),
        "detail": "Detall interactiu: `/docs` (Swagger) i `/redoc` amb el backend en marxa.",
        "media": (
            "Totes les pujades retornen una ruta relativa `/uploads/<carpeta>/<fitxer>`, "
            "mai una URL absoluta. El client la resol amb `resolveMediaUrl()`, que anteposa "
            "el servidor actiu; les URL `http(s)` es deixen intactes. Els camps de mitjans "
            "(`logo_url`, `banner_url`, `video_url`, `thumbnail_url`) accepten ambdós "
            "formats."
        ),
        "header": "| Mètode | Ruta | Auth |",
        "yes": "sí",
        "no": "no",
        "optional": "opcional",
        "yes_admin": "sí (admin)",
        "federation": "JWT de federació",
        "token_query": "token (query, obligatori)",
        "deprecated": "obsolet",
        "total": "Total: {n} endpoints en {r} routers ({m} amb prefix en `main.py`).",
    },
    "eu": {
        "title": "# API — endpointen erreferentzia",
        "gen": (
            "`app/routers/*.py`-tik sortua (APIRouter bakoitzaren aurrizkia gehi "
            "`app/main.py`-koa) eta endpoint bakoitzaren mendekotasunetatik."
        ),
        "detail": "Xehetasun interaktiboa: `/docs` (Swagger) eta `/redoc` backend-a martxan.",
        "media": (
            "Karga guztiek `/uploads/<karpeta>/<fitxategia>` bide erlatiboa itzultzen dute, "
            "inoiz ez URL absolutua. Bezeroak `resolveMediaUrl()`-rekin ebazten du, "
            "zerbitzari aktiboa aurrezten duena; `http(s)` URLak ukitu gabe uzten dira. "
            "Media eremuek (`logo_url`, `banner_url`, `video_url`, `thumbnail_url`) bi "
            "formatuak onartzen dituzte."
        ),
        "header": "| Metodoa | Ibilbidea | Auth |",
        "yes": "bai",
        "no": "ez",
        "optional": "aukerakoa",
        "yes_admin": "bai (admin)",
        "federation": "federazio JWT",
        "token_query": "tokena (query, derrigorrezkoa)",
        "deprecated": "zaharkituta",
        "total": "Guztira: {n} endpoint {r} routerretan ({m} `main.py`-n aurrizkiarekin).",
    },
    "gl": {
        "title": "# API — referencia de endpoints",
        "gen": (
            "Xerado desde `app/routers/*.py` (prefixo de cada `APIRouter` máis o de "
            "`app/main.py`) e das dependencias de cada endpoint."
        ),
        "detail": "Detalle interactivo: `/docs` (Swagger) e `/redoc` co backend en marcha.",
        "media": (
            "Todas as subidas devolven unha ruta relativa `/uploads/<carpeta>/<ficheiro>`, "
            "nunca unha URL absoluta. O cliente résolvea con `resolveMediaUrl()`, que "
            "antepón o servidor activo; as URL `http(s)` déixanse intactas. Os campos de "
            "medios (`logo_url`, `banner_url`, `video_url`, `thumbnail_url`) aceptan ambos "
            "formatos."
        ),
        "header": "| Método | Ruta | Auth |",
        "yes": "si",
        "no": "non",
        "optional": "opcional",
        "yes_admin": "si (admin)",
        "federation": "JWT de federación",
        "token_query": "token (query, obrigatorio)",
        "deprecated": "obsoleto",
        "total": "Total: {n} endpoints en {r} routers ({m} con prefixo en `main.py`).",
    },
    "oc": {
        "title": "# API — referéncia dels endpoints",
        "gen": (
            "Generat dempuèi `app/routers/*.py` (prefixe de cada `APIRouter` plus aquel de "
            "`app/main.py`) e las dependéncias de cada endpoint."
        ),
        "detail": "Datalh interactiu: `/docs` (Swagger) e `/redoc` amb lo backend en marcha.",
        "media": (
            "Totes las pujadas retornan un camin relatiu `/uploads/<dossièr>/<fichièr>`, "
            "jamai una URL absoluda. Lo client lo resòlv amb `resolveMediaUrl()`, que apond "
            "lo servidor actiu; las URL `http(s)` demoran intactas. Los camps de mèdia "
            "(`logo_url`, `banner_url`, `video_url`, `thumbnail_url`) acceptan ambedos "
            "formats."
        ),
        "header": "| Metòde | Camin | Auth |",
        "yes": "òc",
        "no": "non",
        "optional": "opcional",
        "yes_admin": "òc (admin)",
        "federation": "JWT de federacion",
        "token_query": "jeton (query, obligatòri)",
        "deprecated": "depreciat",
        "total": "Total : {n} endpoints dins {r} routers ({m} amb un prefixe dins `main.py`).",
    },
}


LOCALE_CODES = ["ES", "EN", "FR", "DE", "IT", "CA", "EU", "GL", "OC"]


def langs_bar(current: str) -> str:
    parts = []
    for code in LOCALE_CODES:
        lang = code.lower()
        target = "API.md" if lang == current else f"../{lang}/API.md"
        parts.append(f"[{code}]({target})")
    return " · ".join(parts)


def router_prefix(src: str) -> str:
    m = re.search(r'router\s*=\s*APIRouter\(\s*prefix\s*=\s*"([^"]+)"', src, re.DOTALL)
    return m.group(1) if m else ""


def join_paths(*parts: str) -> str:
    cleaned = [p.strip("/") for p in parts if p and p.strip("/")]
    return "/" + "/".join(cleaned) if cleaned else "/"


def auth_label(body: str, method: str, t: dict) -> str:
    if method == "WEBSOCKET":
        return t["token_query"]
    if "get_current_federation_peer" in body:
        return t["federation"]
    if "validate_access_token" in body:
        return t["token_query"]
    if "_admin_user" in body or "require_admin" in body:
        return t["yes_admin"]
    if "get_current_user_optional" in body:
        return t["optional"]
    if "get_current_user" in body:
        return t["yes"]
    return t["no"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", default="es", choices=sorted(LANGS))
    parser.add_argument("--all", action="store_true", help="generate every locale")
    args = parser.parse_args()
    langs = sorted(LANGS) if args.all else [args.lang]

    prefix_of = {}
    for node in ast.walk(ast.parse(MAIN)):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if (
            not isinstance(func, ast.Attribute)
            or func.attr != "include_router"
            or not node.args
        ):
            continue
        arg = node.args[0]
        if not isinstance(arg, ast.Attribute) or not isinstance(arg.value, ast.Name):
            continue
        prefix = ""
        for kw in node.keywords:
            if kw.arg == "prefix" and isinstance(kw.value, ast.Constant):
                prefix = kw.value.value
                break
        prefix_of[arg.value.id] = prefix

    for lang in langs:
        t = LANGS[lang]
        out = [
            t["title"],
            "",
            langs_bar(lang),
            "",
            t["gen"],
            t["detail"],
            "",
            t["media"],
            "",
        ]
        total = 0
        sections = 0
        for f in sorted(ROUTERS.glob("*.py")):
            if f.name == "__init__.py":
                continue
            src = f.read_text(encoding="utf-8")
            tree = ast.parse(src)
            constants = {}
            for stmt in tree.body:
                if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1:
                    target = stmt.targets[0]
                    value = stmt.value
                    if (
                        isinstance(target, ast.Name)
                        and isinstance(value, (ast.List, ast.Tuple))
                        and all(
                            isinstance(e, ast.Constant) and isinstance(e.value, str)
                            for e in value.elts
                        )
                    ):
                        constants[target.id] = [e.value for e in value.elts]
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
                    if method == "API_ROUTE":
                        for kw in dec.keywords:
                            if kw.arg != "methods":
                                continue
                            if isinstance(kw.value, (ast.List, ast.Tuple)):
                                method = "/".join(
                                    v.value.upper()
                                    for v in kw.value.elts
                                    if isinstance(v, ast.Constant)
                                )
                            elif (
                                isinstance(kw.value, ast.Name)
                                and kw.value.id in constants
                            ):
                                method = "/".join(
                                    v.upper() for v in constants[kw.value.id]
                                )
                            break
                    deprecated = any(
                        kw.arg == "deprecated"
                        and isinstance(kw.value, ast.Constant)
                        and kw.value.value is True
                        for kw in dec.keywords
                    )
                    rows.append((method, path, node.name, deprecated))
            if not rows:
                continue
            sections += 1
            mod = f.stem
            prefix = join_paths(prefix_of.get(mod, ""), router_prefix(src))
            out.append(f"## `{mod}` → `{prefix}`")
            out.append("")
            out.append(t["header"])
            out.append("|---|---|---|")
            for method, path, name, deprecated in rows:
                m = re.search(
                    rf"(async )?def {name}\(.*?\):(.*?)(?=\n@router|\ndef |\nasync def |\Z)",
                    src,
                    re.DOTALL,
                )
                body = m.group(0) if m else ""
                suffix = f" ({t['deprecated']})" if deprecated else ""
                out.append(
                    f"| {method} | `{join_paths(prefix, path)}`{suffix} | {auth_label(body, method, t)} |"
                )
                total += 1
            out.append("")
        out.append(
            t["total"].format(
                n=total, r=sections, m=sum(1 for p in prefix_of.values() if p)
            )
        )
        target = DOCS / lang / "API.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("\n".join(out), encoding="utf-8")
        print(lang, "endpoints:", total, "| routers:", sections)


if __name__ == "__main__":
    main()
