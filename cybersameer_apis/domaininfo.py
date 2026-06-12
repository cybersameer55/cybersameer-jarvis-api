"""
@api /domaininfo
@method GET
@param domain
@usage /domaininfo?key=YOUR_API_KEY&domain=google.com
"""

from flask import Blueprint, request
from core import check_access, clean_response, fetch_api, send_response

domaininfo_bp = Blueprint("domaininfo", __name__)


@domaininfo_bp.route("/domaininfo")
def domaininfo():
    key    = request.args.get("key", "")
    domain = request.args.get("domain", "")

    user, err = check_access(key)
    if err:
        return err

    if not domain:
        return send_response("error", {}, {"message": "Domain required"})

    dns_google = clean_response(fetch_api(f"https://dns.google/resolve?name={domain}") or {})
    rdap       = clean_response(fetch_api(f"https://rdap.org/domain/{domain}") or {})
    urlscan    = clean_response(fetch_api(f"https://urlscan.io/api/v1/search/?q=domain:{domain}") or {})
    netlas     = clean_response(fetch_api(f"https://app.netlas.io/api/domains/?q={domain}") or {})
    virustotal = clean_response(fetch_api(f"https://www.virustotal.com/api/v3/domains/{domain}",
                                          headers={"x-apikey": "YOUR_VIRUSTOTAL_API_KEY"}) or {})
    preview    = clean_response(fetch_api(f"https://api.microlink.io/?url=https://{domain}") or {})

    sources = {k: v for k, v in {
        "dns_records":          dns_google,
        "domain_registration":  rdap,
        "url_scan":             urlscan,
        "network_intel":        netlas,
        "threat_intelligence":  virustotal,
        "website_preview":      preview
    }.items() if v}

    if not sources:
        return send_response("error", {}, {"message": "No data found"})

    return send_response("success", {
        "domain":        domain,
        "total_sources": len(sources),
        "sources":       sources
    }, {"user": user["name"]})
