"""Simplify geometry, keep the attributes the page needs, compute breaks and ranks."""
from shapely.geometry import mapping


def simplify(geom, tol, rnd):
    if geom is None or geom.is_empty:
        return None
    g = geom.simplify(tol, preserve_topology=True)
    if g.is_empty:
        g = geom.buffer(0)
    m = mapping(g)

    def r(c):
        return [round(c[0] / rnd) * rnd, round(c[1] / rnd) * rnd] if isinstance(c[0], (int, float)) else [r(x) for x in c]
    return {"type": m["type"], "coordinates": r(m["coordinates"])}


def breaks(recs, idx, cls):
    """Break between classes = midpoint of class k max and class k+1 min (as classified by the run)."""
    out = []
    for k in (1, 2):
        hi = max(r[idx] for r in recs if r[cls] == k)
        lo = min(r[idx] for r in recs if r[cls] == k + 1)
        out.append({"between": [k, k + 1], "upper_of_lower": hi, "lower_of_upper": lo, "line": round((hi + lo) / 2, 3)})
    return out


def ranks(recs, idx):
    """Competition ranking, 1 = highest value; ties share a rank."""
    import bisect
    srt = sorted(r[idx] for r in recs if r[idx] is not None)
    n = len(srt)
    return {id(r): (n - bisect.bisect_right(srt, r[idx]) + 1) if r[idx] is not None else None for r in recs}, n


def features(recs, tol, rnd):
    ra, n = ranks(recs, "INDEX_A")
    rb, nb = ranks(recs, "INDEX_B")
    feats = []
    for r in recs:
        g = simplify(r["_geom"], tol, rnd)
        if g is None:
            continue
        feats.append({"type": "Feature", "geometry": g, "properties": {
            "iso3": r["iso3"], "name": r["name_en"] or r["ne_name"], "region": r["subregion"],
            "a": r["INDEX_A"], "b": r["INDEX_B"], "ca": r["CLASS_A"], "cb": r["CLASS_B"],
            "cls": r["BIV_CLASS"], "color": r["BIV_COLOR"], "qa": r["QA_STATUS"],
            "rank_a": ra[id(r)], "rank_b": rb[id(r)], "n_a": n, "n_b": nb}})
    return {"type": "FeatureCollection", "features": feats}, n


def palette(recs):
    pal = {}
    for r in recs:
        if r["BIV_CLASS"]:
            pal.setdefault(r["BIV_CLASS"], r["BIV_COLOR"])
    return dict(sorted(pal.items()))
