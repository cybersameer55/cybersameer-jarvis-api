"""
@api /gitrepo
@method GET
@param repo
@usage /gitrepo?key=YOUR_API_KEY&repo=torvalds/linux
"""
from flask import Blueprint, request
from core import check_access, send_response, fetch_api

github_repo_bp = Blueprint("github_repo", __name__)

@github_repo_bp.route("/gitrepo")
def gitrepo():
    key  = request.args.get("key","")
    repo = request.args.get("repo","")
    user, err = check_access(key)
    if err: return err
    if not repo or "/" not in repo: return send_response("error",{},{"message":"repo required (format: owner/repo)"})
    data = fetch_api(f"https://api.github.com/repos/{repo}")
    if not data or "message" in data: return send_response("error",{},{"message":"Repository not found"})
    langs = fetch_api(f"https://api.github.com/repos/{repo}/languages") or {}
    return send_response("success",{
        "name":data.get("name",""),"full_name":data.get("full_name",""),
        "description":data.get("description",""),"stars":data.get("stargazers_count",0),
        "forks":data.get("forks_count",0),"watchers":data.get("watchers_count",0),
        "open_issues":data.get("open_issues_count",0),"language":data.get("language",""),
        "languages":langs,"license":(data.get("license") or {}).get("spdx_id",""),
        "created_at":data.get("created_at",""),"updated_at":data.get("updated_at",""),
        "homepage":data.get("homepage",""),"topics":data.get("topics",[]),
        "url":data.get("html_url",""),"default_branch":data.get("default_branch","main"),
        "is_fork":data.get("fork",False)
    },{"user":user["name"]})
