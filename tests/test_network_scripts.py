"""fetch_templates.py and fetch_image.py without real internet: local server + canned API answers."""
from __future__ import annotations

import functools
import http.server
import io
import json
import sys
import threading
from pathlib import Path

import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "skills" / "make-clean-pptx" / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(ROOT / "tests"))

import fetch_image  # noqa: E402
import fetch_templates  # noqa: E402
from make_fixtures import make  # noqa: E402


# ----------------------------------------------------------------- templates
@pytest.fixture()
def server(tmp_path):
    """Serve a folder over http://127.0.0.1:<port>/ and return (folder, base_url)."""
    web = tmp_path / "web"
    web.mkdir()
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(web))
    handler.log_message = lambda *a, **k: None
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield web, f"http://127.0.0.1:{httpd.server_port}"
    httpd.shutdown()


def test_fetch_templates_download_cache_and_lfs_pointer(server, tmp_path, monkeypatch):
    web, base = server
    make(web)  # writes layouts.pptx, visuals.pptx and both indexes into the served folder
    monkeypatch.setenv("MAKE_CLEAN_PPTX_CACHE", str(tmp_path / "cache"))
    monkeypatch.setattr(fetch_templates, "_urls", lambda repo, ref, path, name: [f"{base}/{name}"])

    assert fetch_templates.ensure_templates()["source"] == "bundled"  # default: no network
    res = fetch_templates.ensure_templates(remote=True)
    assert res["source"] == "github"
    for kind in ("layouts", "visuals", "design", "shapes"):
        assert Path(res[kind]["pptx"]).is_file() and Path(res[kind]["index"]).is_file()

    # second call is served from the cache (server may even be down)
    assert fetch_templates.ensure_templates(remote=True)["source"] == "cache"

    # a Git-LFS pointer instead of a file is detected and reported
    (web / "layouts.pptx").write_text("version https://git-lfs.github.com/spec/v1\noid sha256:abc\nsize 123\n")
    with pytest.raises(fetch_templates.FetchError, match="LFS"):
        fetch_templates._fetch_one("r", "main", "p", "layouts.pptx", tmp_path / "x.pptx")


def test_fetch_templates_local_dir(tmp_path):
    make(tmp_path / "tpl")
    res = fetch_templates.ensure_templates(local_dir=str(tmp_path / "tpl"))
    assert res["source"] == "local" and res["layouts"]["pptx"].endswith("layouts.pptx")
    assert res["design"] == res["layouts"]  # old name kept as an alias
    with pytest.raises(fetch_templates.FetchError):
        fetch_templates.ensure_templates(local_dir=str(tmp_path / "empty"))


# -------------------------------------------------------------------- images
OPENVERSE_REPLY = {"results": [
    {"title": "Tiny", "url": "https://x/tiny.jpg", "license": "by", "width": 400, "height": 300, "attribution": "tiny"},
    {"title": "Portrait", "url": "https://x/p.jpg", "license": "cc0", "width": 1800, "height": 2400, "attribution": "p"},
    {"title": "Solar roof", "creator": "Ann", "url": "https://x/solar.jpg", "license": "by", "license_url": "https://cc/by/4.0",
     "foreign_landing_url": "https://flickr/1", "width": 3000, "height": 2000,
     "attribution": '"Solar roof" by Ann is licensed under CC BY 4.0.'},
]}
COMMONS_REPLY = {"query": {"pages": {
    "1": {"index": 2, "title": "File:Good.jpg", "imageinfo": [{"url": "https://c/good.jpg", "width": 2600, "height": 1700, "mime": "image/jpeg",
          "descriptionurl": "https://commons/Good", "extmetadata": {"LicenseShortName": {"value": "CC BY-SA 4.0"}, "Artist": {"value": "<a href='#'>Bob</a>"}}}]},
    "2": {"index": 1, "title": "File:Fair.jpg", "imageinfo": [{"url": "https://c/fair.jpg", "width": 3000, "height": 2000, "mime": "image/jpeg",
          "extmetadata": {"LicenseShortName": {"value": "Fair use"}}}]},
    "3": {"index": 3, "title": "File:Anim.gif", "imageinfo": [{"url": "https://c/a.gif", "width": 3000, "height": 2000, "mime": "image/gif",
          "extmetadata": {"LicenseShortName": {"value": "CC0"}}}]},
}}}


def test_image_candidates_filter_licence_size_orientation(monkeypatch):
    def fake(url):
        return OPENVERSE_REPLY if "openverse" in url else COMMONS_REPLY
    monkeypatch.setattr(fetch_image, "_get_json", fake)
    cands, errors = fetch_image.candidates("solar", "auto", ["cc0", "by"], "wide", 1600)
    assert not errors
    assert [c["title"] for c in cands] == ["Solar roof", "Good.jpg"]  # tiny, portrait, fair-use and gif dropped
    assert cands[0]["credit"].startswith('"Solar roof" by Ann')
    assert "Bob" in cands[1]["credit"] and "<a" not in cands[1]["credit"]


def test_image_unreachable_reports_errors(monkeypatch):
    def boom(url):
        raise fetch_image.ImageError("blocked")
    monkeypatch.setattr(fetch_image, "_get_json", boom)
    cands, errors = fetch_image.candidates("x", "auto", ["cc0"], "any", 100)
    assert cands == [] and len(errors) == 2


def test_image_download_validates_and_reencodes(monkeypatch, tmp_path):
    buf = io.BytesIO()
    Image.new("RGB", (3200, 1800), (10, 20, 30)).save(buf, "PNG")

    class Resp(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(fetch_image.urllib.request, "urlopen", lambda req, timeout=0: Resp(buf.getvalue()))
    info = fetch_image.download({"url": "https://x/a.png"}, tmp_path / "out.png", 1600, 25)
    assert info["path"].endswith(".jpg") and max(info["width"], info["height"]) == 1600
    assert Image.open(info["path"]).format == "JPEG"

    monkeypatch.setattr(fetch_image.urllib.request, "urlopen", lambda req, timeout=0: Resp(b"<html>not an image</html>"))
    with pytest.raises(fetch_image.ImageError, match="not a valid image"):
        fetch_image.download({"url": "https://x/a.png"}, tmp_path / "bad.jpg", 1600, 25)

    with pytest.raises(fetch_image.ImageError, match="non-http"):
        fetch_image.download({"url": "file:///etc/passwd"}, tmp_path / "x.jpg", 1600, 25)


def test_image_cli_exit_code_when_blocked(monkeypatch, capsys):
    monkeypatch.setattr(fetch_image, "_get_json", lambda url: (_ for _ in ()).throw(fetch_image.ImageError("blocked")))
    assert fetch_image.main(["-q", "x", "--list"]) == 3
    assert "unreachable" in json.loads(capsys.readouterr().out)["error"]
