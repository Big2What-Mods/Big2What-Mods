#!/usr/bin/env python3
"""Refresh unified Militech Cynosure Terminal SVG using GitHub data."""
import os,json,html,pathlib,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[2]
USER="Big2What-Mods"
TOKEN=os.getenv("GITHUB_TOKEN","")
def api(url,body=None):
    headers={"Accept":"application/vnd.github+json","User-Agent":"Cynosure-Profile"}
    if TOKEN:headers["Authorization"]="Bearer "+TOKEN
    if body is not None:headers["Content-Type"]="application/json"
    req=urllib.request.Request(url,data=json.dumps(body).encode() if body is not None else None,headers=headers,method="POST" if body is not None else "GET")
    with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)
def esc(v):return html.escape(str(v),quote=True)
def text(x,y,value,size=14,color="#f0c4bd"):
    return f'<text x="{x}" y="{y}" font-family="monospace" font-size="{size}" fill="{color}">{esc(value)}</text>'
repos=api(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner")
profile=api(f"https://api.github.com/users/{USER}")
byname={r["name"]:r for r in repos}
languages={}
for r in repos:
    k=r.get("language")
    if k:languages[k]=languages.get(k,0)+1
lang=", ".join(sorted(languages,key=languages.get,reverse=True)[:4]) or "NOT REPORTED"
total="UNAVAILABLE"
grid=""
try:
    query='query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}'
    response=api("https://api.github.com/graphql",{"query":query,"variables":{"login":USER}})
    calendar=response["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    total=str(calendar["totalContributions"])
    days=[d for w in calendar["weeks"] for d in w["contributionDays"]]
    # 53 weeks x 7 days: a genuine GitHub contribution matrix.
    for i,d in enumerate(days):
        count=d["contributionCount"]
        x=45+(i//7)*19
        y=750+(i%7)*20
        fill="#29272b" if count==0 else "#70343d" if count<3 else "#b55a62" if count<7 else "#f2b0a3"
        grid+=f'<rect x="{x}" y="{y}" width="15" height="15" rx="2" fill="{fill}"><title>{esc(d["date"])}: {count}</title></rect>'
except Exception as ex:
    # Preserve the last valid activity visualization on transient API failures.
    previous=ROOT/"assets/terminal.svg"
    if previous.exists():
        import re
        old=previous.read_text(encoding="utf-8")
        m=re.search(r'<g id="calendar">(.*?)</g>',old,re.S)
        if m:grid=m.group(1)
    print("Calendar query unavailable:",ex)
names=["Cyberpunk-2077-Iconic-ID-Tag-Dumper","CP2077-Achievement-Logic","CP2077-Journal-State-Tracer","Cynosure_Terminal_Teaser---H10_Bathroom_Poster","Misty-s_Esoterica_Poster-H10_Bathroom","Viktor_Vektor_Ripperdoc_Poster-H10_Bathroom","El_Coyote_Cojo-_Bar_Poster-H10_Bathroom"]
values={
"REPOS":str(len(repos)),
"STARS":str(sum(r.get("stargazers_count",0) for r in repos)),
"FOLLOWERS":str(profile.get("followers",0)),
"LANGUAGES":lang[:55],
"TOTAL":total,
"GRID":grid
}
for i,name in enumerate(names,1):
    r=byname.get(name)
    if r:values[f"CARD{i}"]=f'STARS {r.get("stargazers_count",0)}   FORKS {r.get("forks_count",0)}   ISSUES {r.get("open_issues_count",0)}'
    else:values[f"CARD{i}"]="REPOSITORY DATA UNAVAILABLE"
template=(ROOT/"assets/terminal-template.svg").read_text(encoding="utf-8")
for k,v in values.items():
    template=template.replace("{{"+k+"}}",v if k=="GRID" else esc(v))
(ROOT/"assets/terminal.svg").write_text(template,encoding="utf-8")
print("Unified terminal telemetry refreshed.")
