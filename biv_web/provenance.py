import datetime, hashlib, platform
from . import __version__


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def record(src, cfg):
    return {"script": "biv_web", "version": __version__, "python": platform.python_version(),
            "input": {"file": str(src), "sha256": sha256(src)}, "config": cfg,
            "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
