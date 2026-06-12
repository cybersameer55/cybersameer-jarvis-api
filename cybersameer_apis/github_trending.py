"""
@api /gittrending
@method GET
@param language, period
@usage /gittrending?key=YOUR_API_KEY&language=python&period=daily
"""
from flask import Blueprint, request
from core import check_access, send_response, fetch_api

github_trending_bp = Blueprint("github_trending", __name__)

@github_trending_bp.route("/gittrending")
def gittrending():
    key      = request.args.get("key","")
    language = request.args.get("language","")
    period   = request.args.get("period","daily").lower()
    user, err= check_access(key)
    if err: return err
    url = "https://api.gitterapp.com/repositories"
    params = []
    if language: params.append(f"language={language}")
    if period in ["daily","weekly","monthly"]: params.append(f"since={period}")
    if params: url += "?" + "&".join(params)
    data = fetch_api(url)
    if not data or not isinstance(data, list):
        q = f"+language:{language}" if language else ""
        data2 = fetch_api(f"https://api.github.com/search/repositories?q=stars:>100{q}&sort=stars&order=desc&per_page=10")
        if data2:
            items = [{"name":r.get("full_name",""),"description":r.get("description",""),"stars":r.get("stargazers_count",0),"url":r.get("html_url",""),"language":r.get("language","")} for r in data2.get("items",[])[:10]]
            return send_response("success",{"period":period,"language":language,"count":len(items),"repos":items},{"user":user["name"]})
        return send_response("error",{},{"message":"Could not fetch trending repos"})
    repos = [{"name":r.get("fullname",r.get("name","")),"description":r.get("description",""),"stars":r.get("stars",""),"language":r.get("language",""),"url":r.get("url","")} for r in data[:15]]
    return send_response("success",{"period":period,"language":language,"count":len(repos),"repos":repos},{"user":user["name"]})
