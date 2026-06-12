from flask import request, jsonify
import requests as req
import re
from datetime import datetime

USERS = {
    "BHAI":              {"name": "𝐇𝐀𝐂𝐊𝐄𝐑 𝐇𝐔 𝐁𝐇𝐀𝐈",             "expiry": "unlimited", "status": "active"},
    "BHAIYA":            {"name": "𝐑𝐀𝐃𝐇𝐄 𝐁𝐇𝐀𝐈𝐘𝐀",              "expiry": "unlimited", "status": "active"},
    "MITRO": {"name": "𝐒𝐈𝐑𝐅 𝐃𝐎𝐒𝐓𝐎 𝐊𝐄 𝐋𝐈𝐘𝐄", "expiry": "2026-6-29", "status": "active"},
    "Jarvis4":  {"name": "User 4",  "expiry": "unlimited", "status": "active"},
    "Jarvis5":  {"name": "User 5",  "expiry": "unlimited", "status": "active"},
    "Jarvis6":  {"name": "User 6",  "expiry": "unlimited", "status": "active"},
    "Jarvis7":  {"name": "User 7",  "expiry": "unlimited", "status": "active"},
    "Jarvis8":  {"name": "User 8",  "expiry": "unlimited", "status": "active"},
    "Jarvis9":  {"name": "User 9",  "expiry": "unlimited", "status": "active"},
    "Jarvis10": {"name": "User 10", "expiry": "unlimited", "status": "active"},
    "Jarvis11": {"name": "User 11", "expiry": "unlimited", "status": "active"},
    "Jarvis12": {"name": "User 12", "expiry": "unlimited", "status": "active"},
    "Jarvis13": {"name": "User 13", "expiry": "unlimited", "status": "active"},
    "Jarvis14": {"name": "User 14", "expiry": "unlimited", "status": "active"},
    "Jarvis15": {"name": "User 15", "expiry": "unlimited", "status": "active"},
    "Jarvis16": {"name": "User 16", "expiry": "unlimited", "status": "active"},
    "Jarvis17": {"name": "User 17", "expiry": "unlimited", "status": "active"},
    "Jarvis18": {"name": "User 18", "expiry": "unlimited", "status": "active"},
    "Jarvis19": {"name": "User 19", "expiry": "unlimited", "status": "active"},
    "Jarvis20": {"name": "User 20", "expiry": "unlimited", "status": "active"},
}

DEVELOPER = {
    "developer_name": "𝗗𝗲𝘃𝗲𝗹𝗼𝗽𝗲𝗿 𝗖𝘆𝗯𝗲𝗿𝗦𝗮𝗺𝗲𝗲𝗿",
    "instagram":      "broken_heart_boy_sm",
    "contact":        "+254770650152",
    "bot_name":       "𝗝.𝗔.𝗥.𝗩.𝗜.𝗦",
    "channel":        "@CyberSameer",
    "group_chat": {
        "link":  "https://t.me/+-HBD0IWfpANlOWRl",
        "link":  "https://t.me/CyberSameerAPIs",
        "Hacker": "@DeveloperCyberSameer"
    },
    "notes": "𝗙𝗢𝗖𝗨𝗦 𝗢𝗡 𝗨𝗥𝗚𝗢𝗟𝗔𝗦 𝗡𝗢𝗧 𝗔 𝗙𝗘𝗠𝗔𝗟𝗘 𝗛𝗢𝗟𝗟𝗦"
}

REMOVE_KEYS = [
    "developer_name","developer","credit","credits","made_by","owner","seller",
    "api_sell","dm_to_buy","created_by","channel_name","channel_link","join","support",
    "branding","provider","website","telegram_support","updates_channel",
    "author","creator","admin","administrator","contact","tw","all","whatsapp",
    "telegram","discord","instagram","youtube","apikey","api_key","api-key","token",
    "access_token","auth","secret","client_secret","server","host","ip","port",
    "subscription","plan","pricing","referral","ref_code","invite","promo","note",
    "message","msg","warning","debug","trace","stack","error_details",
    "parameters","timestamp","source","input"
]

REMOVE_VALUES = [
    "gaurav","ngyt","kon_hu_mai","gaurav_cyber","@gaurav_cyber","@kon_hu_mai","@ngyt777gg",
    "anshapi","cyber_ansh","@anshapi","@cyber_ansh","t.me/anshapi","rishuapi",
    "strikerxyash","abbas","prosnal","anmol","api_developer","anonymous","dm to buy access",
    "tech vishal boss api","@techvishalboss","techvishalboss","team_vishal_boss",
    "access forbidden: invalid or missing api-key","key has been revoked",
    "t.me/","telegram.me/","wa.me/","chat.whatsapp.com/",
    "buy","buy now","purchase","premium","upgrade","free trial","limited offer",
    "join now","subscribe","follow","invalid","forbidden","unauthorized",
    "api key","expired key","limit reached","access denied","not allowed",
    "all rights reserved","terms","privacy_policy","license"
]


def clean_response(data):
    if isinstance(data, dict):
        result = {}
        for k, v in data.items():
            if k in REMOVE_KEYS:
                continue
            cleaned = clean_response(v)
            if isinstance(cleaned, str):
                lower = cleaned.lower()
                if any(bad.lower() in lower for bad in REMOVE_VALUES):
                    continue
            if cleaned is not None and cleaned != {} and cleaned != []:
                result[k] = cleaned
        return result
    elif isinstance(data, list):
        return [clean_response(i) for i in data if clean_response(i) is not None]
    return data


def check_access(key):
    if not key or key not in USERS:
        return None, send_response("error", {}, {"message": "Invalid API Key"})
    user = USERS[key]
    if user["status"] != "active":
        return None, send_response("error", {}, {"message": "Key disabled"})
    if user["expiry"] != "unlimited":
        parts = user["expiry"].split("-")
        expiry = datetime(int(parts[0]), int(parts[1]), int(parts[2]))
        if datetime.now() > expiry:
            return None, send_response("expired", {}, {
                "message":     "Key expired",
                "expiry_date": user["expiry"]
            })
    return user, None


def fetch_api(url, headers=None, timeout=15):
    try:
        h = {"User-Agent": "Mozilla/5.0"}
        if headers:
            h.update(headers)
        r = req.get(url, headers=h, timeout=timeout)
        return r.json()
    except Exception:
        return None


def send_response(status, data=None, extra=None):
    if data is None:
        data = {}
    if extra is None:
        extra = {}
    resp = {"status": status, "data": data, "developer": DEVELOPER}
    resp.update(extra)
    return jsonify(resp)


def get_time_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def make_list(data):
    if not data:
        return []
    if isinstance(data, list):
        return data
    return [data]
