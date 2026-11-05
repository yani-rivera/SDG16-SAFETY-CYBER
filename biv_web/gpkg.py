"""Read features from a GeoPackage with the standard library (no GDAL needed)."""
import sqlite3
import struct
from shapely import wkb

_ENV = {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}


def gpkg_geom(blob):
    """Strip the GeoPackage binary header and return a shapely geometry."""
    if blob is None:
        return None
    if blob[:2] != b"GP":
        raise ValueError("not a GeoPackage geometry blob")
    flags = blob[3]
    env = _ENV[(flags >> 1) & 0b111]
    return wkb.loads(bytes(blob[8 + env:]))


def read_layer(path, layer):
    con = sqlite3.connect(path)
    srs = con.execute("select srs_id from gpkg_contents where table_name=?", (layer,)).fetchone()[0]
    gcol = con.execute("select column_name from gpkg_geometry_columns where table_name=?", (layer,)).fetchone()[0]
    cols = [r[1] for r in con.execute(f"pragma table_info('{layer}')")]
    rows = con.execute(f"select * from '{layer}'").fetchall()
    con.close()
    out = []
    for r in rows:
        rec = dict(zip(cols, r))
        rec["_geom"] = gpkg_geom(rec.pop(gcol))
        out.append(rec)
    return out, srs
