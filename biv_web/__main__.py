"""Usage: python -m biv_web config.toml"""
import json, sys, tomllib
from pathlib import Path
from .gpkg import read_layer
from .build import features, breaks, palette
from .provenance import record


def run(cfg_path):
    base = Path(cfg_path).parent
    cfg = tomllib.loads(Path(cfg_path).read_text())
    src = base / cfg["input"]["gpkg"]
    out = base / cfg["output"]["dir"]
    out.mkdir(parents=True, exist_ok=True)
    recs, srs = read_layer(src, cfg["input"]["layer"])
    valid = [r for r in recs if r["QA_STATUS"] == "VALID"]
    fc, n = features(recs, cfg["geometry"]["simplify_m"], cfg["geometry"]["round_m"])
    pal = palette(recs)
    if cfg["input"].get("legend"):
        leg = json.loads((base / cfg["input"]["legend"]).read_text())
        if pal != {k: v for k, v in leg["colors"].items() if k in pal}:
            print("WARNING: colours in the GeoPackage differ from legend.json")
    else:
        da, db = breaks(valid, "INDEX_A", "CLASS_A"), breaks(valid, "INDEX_B", "CLASS_B")
        fmt = lambda b: [f"< {b[0]['lower_of_upper']:g}", f"{b[0]['lower_of_upper']:g} – {b[1]['lower_of_upper']:g}", f"≥ {b[1]['lower_of_upper']:g}"]
        leg = {"axes": {"a": {"breaks": [x["lower_of_upper"] for x in da], "ranges": fmt(da)},
                        "b": {"breaks": [x["lower_of_upper"] for x in db], "ranges": fmt(db)}},
               "colors": pal, "provenance": None}
        print("no legend.json: breaks derived from the classes in the GeoPackage")
    meta = {"crs": f"EPSG:{srs}", "labels": cfg["labels"], "n_valid": len(valid), "n_a": sum(1 for r in recs if r["INDEX_A"] is not None), "n_b": sum(1 for r in recs if r["INDEX_B"] is not None), "a_unit": cfg["labels"].get("a_unit", ""),
            "breaks_a": leg["axes"]["a"]["breaks"], "breaks_b": leg["axes"]["b"]["breaks"],
            "ranges_a": leg["axes"]["a"]["ranges"], "ranges_b": leg["axes"]["b"]["ranges"],
            "palette": leg["colors"], "bivariate_run": leg.get("provenance"),
            "check_breaks_from_data": {"a": breaks(valid, "INDEX_A", "CLASS_A"), "b": breaks(valid, "INDEX_B", "CLASS_B")},
            "provenance": record(src, cfg)}
    with open(out / "countries.geojson", "w", encoding="utf-8") as f:
        json.dump(fc, f, ensure_ascii=False, separators=(",", ":"))
    with open(out / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    print(f"{len(fc["features"])} features ({len(valid)} with both values), CRS EPSG:{srs} -> {out}")
    print("breaks A", meta["breaks_a"], "breaks B", meta["breaks_b"], "run", (meta["bivariate_run"] or {}).get("run_id"))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    run(sys.argv[1])
