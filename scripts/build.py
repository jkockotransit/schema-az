#!/usr/bin/env python3
"""Construit la bibliothèque d'icônes officielles Microsoft du dépôt schema-az.

Pour chaque famille déclarée dans sources.json :
  1. trouve le lien de téléchargement officiel (page Microsoft Learn ou lien direct) ;
  2. télécharge le pack, et s'arrête là si son empreinte n'a pas changé ;
  3. extrait les icônes dans icons/<famille>/ (SVG, ou PNG si le pack n'a pas de SVG) ;
  4. génère les bibliothèques draw.io dans drawio/ ;
  5. met à jour index.json (catalogue lu par Claude) et manifest.json (versions).

Usage : python scripts/build.py [--only azure,fabric] [--force] [--zip famille=chemin.zip]
Aucune dépendance hors bibliothèque standard Python 3.9+.
"""
import argparse, base64, datetime, hashlib, html, io, json, os, re, shutil, sys, urllib.request, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ICONS, DRAWIO = ROOT / "icons", ROOT / "drawio"
UA = {"User-Agent": "Mozilla/5.0 (schema-az icon library builder)"}
RAW_BASE = os.environ.get("RAW_BASE", "")  # ex. https://raw.githubusercontent.com/<compte>/schema-az/main


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read(), r.geturl()


def find_zip_url(src):
    if src.get("direct_url"):
        return src["direct_url"], None
    page, _ = fetch(src["page"])
    text = html.unescape(page.decode("utf-8", "replace"))
    m = re.search(src["zip_regex"], text)
    if not m:
        raise RuntimeError(f"lien de téléchargement introuvable sur {src['page']}")
    date = re.search(r'<meta name="ms.date" content="([^"]+)"', text)
    return m.group(0), (date.group(1) if date else None)


def iter_files(zbytes, prefix=""):
    """Parcourt un ZIP, y compris les ZIP imbriqués."""
    with zipfile.ZipFile(io.BytesIO(zbytes)) as z:
        for info in z.infolist():
            if info.is_dir() or "__MACOSX" in info.filename:
                continue
            data = z.read(info)
            name = prefix + info.filename
            if name.lower().endswith(".zip"):
                yield from iter_files(data, name + "/")
            else:
                yield name, data


SIZE_RE = re.compile(r"[_-](\d{2,3})(?=[_-]|$)")


def clean_title(stem):
    s = re.sub(r"^\d+-icon-service-", "", stem)
    s = re.sub(r"[_-](scalable|color|item|regular|filled|non-item)$", "", s, flags=re.I)
    s = SIZE_RE.sub("", s)
    s = re.sub(r"[_-]+", " ", s).strip()
    return s[:1].upper() + s[1:] if s else stem


def select(mode, files):
    """Retourne une liste (catégorie, titre, extension, octets)."""
    svgs = [(n, d) for n, d in files if n.lower().endswith(".svg")]
    pool = svgs or [(n, d) for n, d in files if n.lower().endswith(".png")]
    out = {}
    for name, data in pool:
        p = Path(name)
        stem, ext = p.stem, p.suffix.lower().lstrip(".")
        if mode == "azure":
            if "/Icons/" not in "/" + name:
                continue
            cat = p.parent.name.replace("-", " ").title()
        elif mode == "fabric":
            m = re.match(r"(.+)_(\d+)_(item|color)$", stem)
            if not m:
                continue
            cat = "Workloads" if m.group(3) == "color" else "Items"
            size = int(m.group(2))
            key = (cat, m.group(1))
            if key in out and out[key][0] >= size:
                continue
            out[key] = (size, cat, clean_title(m.group(1)), ext, data)
            continue
        else:
            parts = [x for x in p.parent.parts if x not in (".",)]
            cat = parts[-1] if parts else "General"
            cat = re.sub(r"[_-]+", " ", cat).strip() or "General"
        sizes = [int(x) for x in SIZE_RE.findall(stem)]
        size = max(sizes) if sizes else 0
        title = clean_title(stem)
        key = (cat, title.lower())
        if key in out and out[key][0] >= size:
            continue
        out[key] = (size, cat, title, ext, data)
    return [(c, t, e, d) for (_, c, t, e, d) in out.values()]


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "icone"


def svg_size(data):
    try:
        head = data[:600].decode("utf-8", "replace")
        vb = re.search(r'viewBox="[\d.\-]+\s+[\d.\-]+\s+([\d.]+)\s+([\d.]+)"', head)
        if vb:
            w, h = float(vb.group(1)), float(vb.group(2))
            k = 48 / max(w, h)
            return round(w * k), round(h * k)
    except Exception:
        pass
    return 48, 48


def drawio_library(entries):
    items = []
    for e in entries:
        mime = "image/svg+xml" if e["ext"] == "svg" else "image/png"
        w, h = svg_size(e["bytes"]) if e["ext"] == "svg" else (48, 48)
        items.append({"data": f"data:{mime};base64," + base64.b64encode(e["bytes"]).decode(),
                      "w": w, "h": h, "title": e["title"], "aspect": "fixed"})
    return "<mxlibrary>" + json.dumps(items, ensure_ascii=False) + "</mxlibrary>"


def build_family(key, src, manifest, force, local_zip=None):
    if local_zip:
        zbytes, url, page_date = Path(local_zip).read_bytes(), "local:" + local_zip, None
    else:
        url, page_date = find_zip_url(src)
        zbytes, url = fetch(url)[0], url
    digest = hashlib.sha256(zbytes).hexdigest()
    prev = manifest.get(key, {})
    if not force and prev.get("sha256") == digest:
        print(f"[{key}] inchangé ({prev.get('version')})")
        return False
    files = list(iter_files(zbytes))
    chosen = select(src["mode"], files)
    if not chosen:
        raise RuntimeError(f"[{key}] aucune icône trouvée dans le pack")
    fam_dir = ICONS / key
    shutil.rmtree(fam_dir, ignore_errors=True)
    entries, used = [], set()
    for cat, title, ext, data in sorted(chosen, key=lambda x: (x[0].lower(), x[1].lower())):
        base = f"{slug(cat)}/{slug(title)}"
        n, path = 2, base
        while path in used:
            path, n = f"{base}-{n}", n + 1
        used.add(path)
        dest = fam_dir / f"{path}.{ext}"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        entries.append({"family": key, "category": cat, "title": title, "ext": ext,
                        "path": f"icons/{key}/{path}.{ext}", "bytes": data})
    DRAWIO.mkdir(exist_ok=True)
    for old in DRAWIO.glob(f"{key}*.xml"):
        old.unlink()
    (DRAWIO / f"{key}.xml").write_text(drawio_library(entries), encoding="utf-8")
    if key == "azure":  # bibliothèques par catégorie, plus légères à ouvrir
        cats = sorted({e["category"] for e in entries})
        for c in cats:
            sub = [e for e in entries if e["category"] == c]
            (DRAWIO / f"azure-{slug(c)}.xml").write_text(drawio_library(sub), encoding="utf-8")
    version = Path(url.split("?")[0]).stem if "Azure_Public" in url else (page_date or datetime.date.today().isoformat())
    if key == "fabric":
        vdir = next((n.split("/")[0] for n, _ in files if re.match(r"v\d+\.\d+", n)), None)
        version = vdir or version
    manifest[key] = {"label": src["label"], "version": version, "source_page": src["page"],
                     "download_url": url, "sha256": digest, "icons": len(entries),
                     "built": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                     **({"note": src["note"]} if src.get("note") else {})}
    print(f"[{key}] {len(entries)} icônes, version {version}")
    return entries


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--zip", action="append", default=[], help="famille=chemin.zip (test hors ligne)")
    a = ap.parse_args()
    sources = json.loads((ROOT / "sources.json").read_text(encoding="utf-8"))
    mpath, ipath = ROOT / "manifest.json", ROOT / "index.json"
    manifest = json.loads(mpath.read_text(encoding="utf-8")) if mpath.exists() else {}
    index = json.loads(ipath.read_text(encoding="utf-8")) if ipath.exists() else {"icons": []}
    local = dict(z.split("=", 1) for z in a.zip)
    only = [x for x in a.only.split(",") if x] or list(sources)
    changed, errors = [], []
    for key in only:
        try:
            res = build_family(key, sources[key], manifest, a.force, local.get(key))
        except Exception as ex:  # une famille en échec ne bloque pas les autres
            errors.append(f"{key}: {ex}")
            print(f"[{key}] ERREUR {ex}", file=sys.stderr)
            continue
        if res:
            changed.append(key)
            index["icons"] = [i for i in index["icons"] if i["family"] != key] + [
                {k: v for k, v in e.items() if k != "bytes"} | ({"raw_url": f"{RAW_BASE}/{e['path']}"} if RAW_BASE else {})
                for e in res]
    if changed or not (mpath.exists() and ipath.exists()):
        # index et manifeste réécrits seulement si une famille a changé (EF06 : sinon, aucun commit)
        index["icons"].sort(key=lambda i: (i["family"], i["category"].lower(), i["title"].lower()))
        index["generated"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        index["families"] = {k: {"label": v["label"], "version": v["version"], "icons": v["icons"]} for k, v in manifest.items()}
        mpath.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        ipath.write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    print("Familles mises à jour :", ", ".join(changed) or "aucune (aucun fichier réécrit)")
    if errors:
        print("Erreurs :", "; ".join(errors), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
