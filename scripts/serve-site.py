import logging

import http.server
import os
import runpy
import socketserver
import sys
from pathlib import Path

import lxmsite

LOGGER = logging.getLogger(Path(__file__).stem)
lxmsite.configure_logging()

THISDIR = Path(__file__).parent
BUILDSCRIPT_PATH = THISDIR / "build-site.py"
BUILDSCRIPT = runpy.run_path(str(BUILDSCRIPT_PATH))["main"]
BUILDIR = THISDIR.parent / "site" / ".build"
SERVEFILE = BUILDIR.parent / ".server-active.info"

PORT = 8000
ADRESS = f"http://localhost:{PORT}"

# // site build

LOGGER.info(f"📃 building doc to '{BUILDIR}'")

LOGGER.debug(f"writing '{SERVEFILE}'")
SERVEFILE.write_text(ADRESS)

try:
    BUILDSCRIPT(["--publish", "--target-dir", str(BUILDIR), "--clear"])
except SystemExit as systemexit:
    if systemexit.code != 0:
        raise


# // HTML server


class LxmHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # mimic GitHub pages behavior with redirection
        # https://til.simonwillison.net/github/github-pages#user-content-foo-will-serve-content-from-foohtml-if-it-exists
        translated = super().translate_path(path)
        if not Path(translated).exists():
            new_path = translated + ".html"
            if Path(new_path).exists():
                return new_path
        return translated


os.chdir(BUILDIR)
with socketserver.TCPServer(("", PORT), LxmHTTPRequestHandler) as httpd:
    LOGGER.info(f"🌐 serving to {ADRESS}")
    LOGGER.warning("note this server doesn't actually auto-build on changes")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received, exiting.")

SERVEFILE.unlink(missing_ok=True)
sys.exit(0)
