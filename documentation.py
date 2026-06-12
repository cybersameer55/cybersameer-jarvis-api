"""
@api /documentation
@method GET
@usage /documentation?key=YOUR_API_KEY
"""
import os, ast
from flask import Blueprint, request, current_app
from core import DEVELOPER, check_access

documentation_bp = Blueprint("documentation", __name__)
SKIP_ROUTES = {"/", "/home", "/index.html", "/api-list", "/documentation"}

def _scan():
    apis_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)),"cybersameer_apis")
    docs=[]
    for fname in sorted(os.listdir(apis_dir)):
        if not fname.endswith(".py") or fname=="__init__.py": continue
        try:
            with open(os.path.join(apis_dir,fname),encoding="utf-8") as f: source=f.read()
            tree=ast.parse(source); ds=ast.get_docstring(tree)
            if not ds: continue
            route=""; method="GET"; params=""; usage=""
            for line in ds.splitlines():
                line=line.strip()
                if line.startswith("@api"):    route=line.replace("@api","").strip()
                elif line.startswith("@method"):method=line.replace("@method","").strip()
                elif line.startswith("@param"): params=line.replace("@param","").strip()
                elif line.startswith("@usage"): usage=line.replace("@usage","").strip()
            if route: docs.append({"endpoint":route,"method":method,"parameter":params or "none","usage":usage})
        except Exception: pass
    return docs

@documentation_bp.route("/documentation")
def documentation():
    key=request.args.get("key","")
    user,err=check_access(key)
    if err: return err
    all_routes=set()
    for rule in current_app.url_map.iter_rules():
        if "GET" in (rule.methods or []):
            route=str(rule)
            if route not in SKIP_ROUTES and not route.startswith("/static"): all_routes.add(route)
    docs=[d for d in _scan() if d["endpoint"] in all_routes]
    return {"status":"success","total_apis":len(docs),"endpoints":docs,"developer":{"developer_name":DEVELOPER["developer_name"],"channel":DEVELOPER["channel"],"instagram":DEVELOPER["instagram"],"contact":DEVELOPER["contact"]},"user_info":{"name":user["name"],"api_key":key}}
