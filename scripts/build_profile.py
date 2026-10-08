#!/usr/bin/env python3
"""Generate original Big2What profile panels from GitHub public API.
No third-party profile data is used. Standard library only.
"""
import json, os, urllib.request, html, datetime
from pathlib import Path

OWNER = "Big2What-Mods"
ROOT = Path("assets")
ROOT.mkdir(exist_ok=True)
TOKEN = os.environ.get("GITHUB_TOKEN", "")
def api(path):
    req = urllib.request.Request("https://api.github.com" + path,
        headers={"Accept":"application/vnd.github+json",
                 "User-Agent":"Big2What-profile-builder",
                 **({"Authorization":"Bearer "+TOKEN} if TOKEN else {})})
    with urllib.request.urlopen(req, timeout=25) as response:
        return json.load(response)
def esc(s):
    return html.escape(str(s), quote=True)
def panel(name, heading, rows, height=None):
    height = height or max(140, 98 + len(rows)*34)
    lines = [
      '<svg xmlns="http://www.w3.org/2000/svg" width="880" height="%d" viewBox="0 0 880 %d">' % (height,height),
      '<rect width="880" height="%d" fill="#090e14"/>' % height,
      '<path d="M0 0 H880 V%d H0 Z" fill="none" stroke="#fcee09" stroke-width="3"/>' % height,
      '<path d="M0 45 H880" stroke="#fcee09" stroke-width="2"/>',
      '<text x="24" y="31" fill="#fcee09" font-family="monospace" font-size="22" font-weight="bold">%s</text>' % esc(heading)]
    for i,row in enumerate(rows):
        lines.append('<text x="28" y="%d" fill="#65e9e0" font-family="monospace" font-size="17">%s</text>' % (80+i*34,esc(row[:83])))
    lines.append('</svg>')
    (ROOT/name).write_text("\n".join(lines)+"\n",encoding="utf-8")
def main():
    user=api("/users/"+OWNER)
    repos=[]
    page=1
    while page<=5:
        batch=api("/users/"+OWNER+"/repos?per_page=100&page="+str(page)+"&type=owner")
        repos.extend(batch)
        if len(batch)<100: break
        page+=1
    repos=[r for r in repos if not r.get("fork") and r["name"]!=OWNER]
    repos.sort(key=lambda r:r.get("pushed_at") or "",reverse=True)
    stars=sum(r.get("stargazers_count",0) for r in repos)
    panel("header.svg","BIG2WHAT // NIGHT CITY MOD DEVELOPMENT",
          ["Cyberpunk 2077 modder  |  GitHub: "+OWNER,
           "Cynosure Terminal  /  Wire Atlas",
           "LIVE PROFILE DATA // "+datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d UTC")],205)
    panel("links.svg","NETWORK CONNECTIONS",
          ["GITHUB  github.com/"+OWNER,
           "NEXUS   nexusmods.com/profile/Big2What"],160)
    panel("stats.svg","GITHUB // VERIFIED PUBLIC STATS",
          ["Public repositories: "+str(user.get("public_repos",len(repos))),
           "Followers: "+str(user.get("followers",0)),
           "Stars across public owned repositories: "+str(stars),
           "Public owned repositories retrieved: "+str(len(repos))],245)
    panel("contribution-city.svg","CONTRIBUTION CITY // STATUS",
          ["Contribution graph is displayed by GitHub below this README.",
           "No fabricated activity counts or generated skyline."],170)
    panel("traffic.svg","REPOSITORY TRAFFIC // STATUS",
          ["Traffic requires repository-specific permissions and API access.",
           "No invented clone counts or visitor metrics."],170)
    project_rows=[r["name"]+"  |  "+str(r.get("stargazers_count",0))+" stars" for r in repos[:12]]
    panel("projects.svg","PROJECT INDEX",project_rows or ["No public projects returned"])
    languages={}
    for r in repos:
        lang=r.get("language")
        if lang: languages[lang]=languages.get(lang,0)+1
    panel("stack.svg","REPOSITORY LANGUAGES",
          [k+": "+str(v)+" repos" for k,v in sorted(languages.items(),key=lambda x:-x[1])[:10]] or ["No language data returned"])
    panel("footer.svg","CONNECTION CLOSED",
          ["BIG2WHAT-MODS // DATA REFRESHED BY GITHUB ACTIONS"],140)
if __name__=="__main__":
    main()
