#!/usr/bin/env python3
"""Update Cynosure Terminal GitHub telemetry SVGs from real GitHub data."""
import json, os, urllib.request, datetime, html, pathlib
ROOT=pathlib.Path(__file__).resolve().parents[2]
TOKEN=os.environ.get("GITHUB_TOKEN","")
USER="Big2What-Mods"
def api(url,method="GET",body=None):
    headers={"Accept":"application/vnd.github+json","User-Agent":"Cynosure-Profile-Updater"}
    if TOKEN: headers["Authorization"]="Bearer "+TOKEN
    if body is not None: headers["Content-Type"]="application/json"
    req=urllib.request.Request(url,data=json.dumps(body).encode() if body is not None else None,headers=headers,method=method)
    with urllib.request.urlopen(req,timeout=30) as response:return json.load(response)
def e(s):return html.escape(str(s),quote=True)
def svg(w,h,content):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="{w}" height="{h}" fill="#0b1420"/><rect x="8" y="8" width="{w-16}" height="{h-16}" fill="none" stroke="#43858a" stroke-width="2"/><path d="M8 44H{w-8}" stroke="#43858a"/>{content}</svg>'
def t(x,y,s,size=18,color="#dff8f3"):
    return f'<text x="{x}" y="{y}" font-family="monospace" font-size="{size}" fill="{color}">{e(s)}</text>'
def save(path,content):
    target=ROOT/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(content,encoding="utf-8")
repos=api("https://api.github.com/users/"+USER+"/repos?per_page=100&type=owner")
profile=api("https://api.github.com/users/"+USER)
repo_map={r["name"]:r for r in repos}
stars=sum(r.get("stargazers_count",0) for r in repos)
forks=sum(r.get("forks_count",0) for r in repos)
lang={}
for r in repos:
    if r.get("language"):lang[r["language"]]=lang.get(r["language"],0)+1
languages=", ".join(k for k,v in sorted(lang.items(),key=lambda kv:-kv[1])[:4]) or "NOT REPORTED"
# GraphQL contribution calendar is queried using the workflow token; do not invent missing data.
calendar=[];total=None
try:
    q='query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}'
    data=api("https://api.github.com/graphql","POST",{"query":q,"variables":{"login":USER}})
    cal=data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    total=cal["totalContributions"]
    calendar=[d for w in cal["weeks"] for d in w["contributionDays"]]
except Exception as exc:
    print("Contribution calendar unavailable; leaving previous activity image intact:",exc)
c=t(30,31,"TELEMETRY // LIVE GITHUB DATA",17,"#f1c274")
c+=t(32,89,f'REPOSITORIES {len(repos)}    STARS {stars}    FORKS {forks}',23,"#5de3d7")
c+=t(32,125,f'FOLLOWERS {profile.get("followers",0)}    MEMBER SINCE {profile.get("created_at","")[:10]}',19)
c+=t(32,160,"LANGUAGES: "+languages,17)
if total is not None:c+=t(740,126,f'YEARLY ACTIVITY {total}',16,"#f1c274")
save("assets/stats.svg",svg(1100,190,c))
if calendar:
    # One illuminated cell per contribution day, arranged in calendar weeks.
    cells=t(24,32,"ACTIVITY GRID // ACTUAL GITHUB CONTRIBUTIONS",16,"#f1c274")
    cells+=t(24,68,f'{total} CONTRIBUTIONS / LAST 12 MONTHS',20,"#5de3d7")
    for i,d in enumerate(calendar):
        col=i//7;row=i%7;count=d["contributionCount"]
        fill="#19353e" if count==0 else ("#337a81" if count<3 else "#56b7b0" if count<7 else "#f1c274")
        x=25+col*19.6;y=88+row*19.6
        cells+=f'<rect x="{x:.1f}" y="{y:.1f}" width="15" height="15" rx="2" fill="{fill}"><title>{e(d["date"])}: {count} contributions</title></rect>'
    save("assets/activity.svg",svg(1100,250,cells))
projects=[
("Cyberpunk-2077-Iconic-ID-Tag-Dumper","ICONIC ID / TAG DUMPER"),
("CP2077-Achievement-Logic","ACHIEVEMENT LOGIC"),
("CP2077-Journal-State-Tracer","JOURNAL STATE TRACER"),
("Cynosure_Terminal_Teaser---H10_Bathroom_Poster","CYNOSURE TEASER"),
("Misty-s_Esoterica_Poster-H10_Bathroom","MISTY'S ESOTERICA"),
("Viktor_Vektor_Ripperdoc_Poster-H10_Bathroom","VIKTOR VEKTOR"),
("El_Coyote_Cojo-_Bar_Poster-H10_Bathroom","EL COYOTE COJO")]
for i,(name,title) in enumerate(projects,1):
    r=repo_map.get(name)
    if r is None:
        print("Repository not returned, retaining existing card:",name);continue
    description=(r.get("description") or "Cyberpunk 2077 modding repository").strip()
    if len(description)>61:description=description[:58]+"..."
    c=t(25,32,f'ARCHIVE {i:02d} // REPOSITORY',15,"#f1c274")
    c+=t(25,83,title,22)
    c+=t(25,115,description,13,"#a4c1c6")
    c+=t(25,149,f'STARS {r.get("stargazers_count",0)}   FORKS {r.get("forks_count",0)}   OPEN ISSUES {r.get("open_issues_count",0)}',14,"#5de3d7")
    c+=f'<circle cx="500" cy="145" r="7" fill="#5de3d7"><animate attributeName="opacity" values=".2;1;.2" dur="{2+i%3}s" repeatCount="indefinite"/></circle>'
    save(f"assets/project-{i}.svg",svg(540,180,c))
print("Telemetry updated from GitHub API")
