import ast, re
from pathlib import Path

ROOT = Path("C:/Users/abdon/Desktop/proyectos/cine/backend")
ROUTERS = ROOT / "app" / "routers"
MAIN = (ROOT / "app" / "main.py").read_text(encoding="utf-8")

prefix_of = {}
for m in re.finditer(r"app\.include_router\(\s*(\w+)\.router,\s*prefix=\"([^\"]+)\"", MAIN):
    prefix_of[m.group(1)] = m.group(2)

out = ["# API — referencia de endpoints", "",
       "Generado desde `app/routers/*.py` + prefijos de `app/main.py`.",
       "Detalle interactivo: `/docs` (Swagger) y `/redoc` con el backend en marcha.", ""]
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
    out.append("| Método | Ruta | Auth |")
    out.append("|---|---|---|")
    src = f.read_text(encoding="utf-8")
    for method, path, name in rows:
        # auth: busca el cuerpo de la función para get_current_user / optional / nada
        m = re.search(rf"(async )?def {name}\(.*?\):(.*?)(?=\n@router|\ndef |\nasync def |\Z)", src, re.S)
        body = m.group(0) if m else ""
        if method == "WEBSOCKET":
            auth = "token (query)"
        elif "get_current_user_optional" in body:
            auth = "opcional"
        elif "get_current_user" in body:
            auth = "sí"
        else:
            auth = "no"
        full = (prefix + path).replace("//", "/")
        out.append(f"| {method} | `{full}` | {auth} |")
        total += 1
    out.append("")

out.append(f"Total: {total} endpoints en {len(prefix_of)} routers.")
Path("C:/Users/abdon/Desktop/proyectos/cine/docs/API.md").write_text("\n".join(out), encoding="utf-8")
print("endpoints:", total, "| routers con prefijo:", len(prefix_of))
