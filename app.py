import os
import importlib
import pkgutil

from flask import Flask, send_from_directory

app = Flask(__name__)


@app.route("/index.html")
@app.route("/home")
def home():
    return send_from_directory(".", "index.html")


# ===== AUTO-DISCOVER & REGISTER ALL BLUEPRINTS =====
# How it works:
#   - Add a new .py file to cybersameer_apis/ → it registers automatically on next start.
#   - Delete a .py file → it disappears automatically. No changes needed here.
#
# Each module just needs to contain at least one Flask Blueprint object.

import cybersameer_apis as _pkg
from flask import Blueprint as _Blueprint

_apis_dir = os.path.dirname(os.path.abspath(_pkg.__file__))

for _mod_info in pkgutil.iter_modules([_apis_dir]):
    try:
        _module = importlib.import_module(f"cybersameer_apis.{_mod_info.name}")
        for _attr in dir(_module):
            _obj = getattr(_module, _attr)
            if isinstance(_obj, _Blueprint):
                app.register_blueprint(_obj)
    except Exception as _e:
        print(f"[WARNING] Skipped cybersameer_apis.{_mod_info.name}: {_e}")

# documentation blueprint (outside cybersameer_apis package)
try:
    from documentation import documentation_bp
    app.register_blueprint(documentation_bp)
except Exception as _e:
    print(f"[WARNING] Skipped documentation: {_e}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
