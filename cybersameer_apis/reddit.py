"""
@api /reddit
@method GET
@param subreddit, sort, limit
@usage /reddit?key=YOUR_API_KEY&subreddit=india&sort=hot&limit=10
"""
from flask import Blueprint, request
from core import check_access, send_response, fetch_api

reddit_bp = Blueprint("reddit", __name__)

@reddit_bp.route("/reddit")
def reddit():
    key       = request.args.get("key","")
    subreddit = request.args.get("subreddit","popular")
    sort      = request.args.get("sort","hot").lower()
    limit     = int(request.args.get("limit",10))
    user, err = check_access(key)
    if err: return err
    if limit > 25: limit = 25
    headers = {"User-Agent":"CyberSameer-API/1.0"}
    data = fetch_api(f"https://www.reddit.com/r/{subreddit}/{sort}.json?limit={limit}", headers=headers)
    if not data: return send_response("error",{},{"message":"Subreddit not found or rate limited"})
    posts = []
    for p in (data.get("data",{}).get("children") or []):
        d = p.get("data",{})
        posts.append({"title":d.get("title",""),"author":d.get("author",""),"score":d.get("score",0),"url":d.get("url",""),"comments":d.get("num_comments",0),"upvote_ratio":d.get("upvote_ratio",0),"nsfw":d.get("over_18",False),"flair":d.get("link_flair_text","")})
    return send_response("success",{"subreddit":subreddit,"sort":sort,"count":len(posts),"posts":posts},{"user":user["name"]})
