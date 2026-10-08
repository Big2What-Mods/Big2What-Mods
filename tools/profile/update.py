#!/usr/bin/env python3
"""Militech Cynosure profile: live GitHub data and coordinated SVG modules."""
import os,json,datetime,html,urllib.request,pathlib,math
ROOT=pathlib.Path(__file__).resolve().parents[2]
TOKEN=os.getenv("GITHUB_TOKEN","")
USER="Big2What-Mods"
PROJECTS=[
("Cyberpunk-2077-Iconic-ID-Tag-Dumper","ICONIC ID / TAG DUMPER"),
("CP2077-Achievement-Logic","ACHIEVEMENT LOGIC"),
("CP2077-Journal-State-Tracer","JOURNAL STATE TRACER"),
("Cynosure_Terminal_Teaser---H10_Bathroom_Poster","CYNOSURE TEASER / H10"),
("Misty-s_Esoterica_Poster-H10_Bathroom","MISTY'S ESOTERICA"),
("Viktor_Vektor_Ripperdoc_Poster-H10_Bathroom","VIKTOR VEKTOR"),
("El_Coyote_Cojo-_Bar_Poster-H10_Bathroom","EL COYOTE COJO")]
def request(url,body=None):
    h={"User-Agent":"Militech-Cynosure-Profile","Accept":"application/vnd.github+json"}
    if TOKEN:h["Authorization"]="Bearer "+TOKEN
    if body is not None:h["Content-Type"]="application/json"
    q=urllib.request.Request(url,data=json.dumps(body).encode() if body is not None else None,headers=h,method="POST" if body is not None else "GET")
    with urllib.request.urlopen(q,timeout=35) as f:return json.load(f)
def e(x):return html.escape(str(x),quote=True)
def t(x,y,s,size=17,bold=False,color="#222820"):
    return f'<text x="{x}" y="{y}" font-family="Arial,Helvetica,sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{color}">{e(s)}</text>'
def r(x,y,w,h,fill="#f6eaaa",stroke="#272b22",sw=2):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
def svg(h,body,top=False,bottom=False):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="{h}" viewBox="0 0 1100 {h}">
<defs><linearGradient id="p" x2="0" y2="1"><stop stop-color="#fff8bb"/><stop offset="1" stop-color="#ebdea0"/></linearGradient><pattern id="v" width="15" height="20" patternUnits="userSpaceOnUse"><path d="M4 3h7v14H4z" fill="#66715e" stroke="#222820"/></pattern></defs>
<rect width="1100" height="{h}" fill="#111b16"/>
<rect x="15" y="0" width="1070" height="{h}" fill="#26342b"/>
<rect x="45" y="0" width="1010" height="{h}" fill="url(#p)"/>
<rect x="18" y="0" width="19" height="{h}" fill="url(#v)"/><rect x="1063" y="0" width="19" height="{h}" fill="url(#v)"/>
<path d="M45 0V{h}M1055 0V{h}" fill="none" stroke="#212a20" stroke-width="5"/>
{body}
</svg>'''
def save(name,body): (ROOT/"assets"/name).write_text(body,encoding="utf-8")
repos=request(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner")
profile=request(f"https://api.github.com/users/{USER}")
byname={a["name"]:a for a in repos}
stars=sum(a.get("stargazers_count",0) for a in repos)
langs={}
for a in repos:
    if a.get("language"):langs[a["language"]]=langs.get(a["language"],0)+1
languages=", ".join(sorted(langs,key=langs.get,reverse=True)[:4]) or "UNREPORTED"
calendar=[]
try:
    query='query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}'
    d=request("https://api.github.com/graphql",{"query":query,"variables":{"login":USER}})
    c=d["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    calendar=[a for w in c["weeks"] for a in w["contributionDays"]]
    total=c["totalContributions"]
except Exception as exc:
    print("Contribution data not available:",exc)
    total=None
# Every slice shares the same physical chassis; the SVGs stack edge-to-edge in README.
b=r(67,12,966,38,"#eee3a1")+t(85,39,"MILITECH / CYNOSURE  //  CONTROL SYSTEM",20,True)+t(850,39,"ACCESS: VERIFIED",15,True)
b+=r(74,66,950,188)+t(99,95,"OPERATOR IDENTITY / SECURE INTERFACE",16,True)+t(98,170,"Big2What",66,True)+t(103,213,"RETIRED CYBERSECURITY ANALYST",22,True)
b+='<g transform="translate(911 162)"><circle r="73" fill="#e4d693" stroke="#272b22" stroke-width="5"/><circle r="54" fill="none" stroke="#34382b" stroke-width="4" stroke-dasharray="9 7"><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="35s" repeatCount="indefinite"/></circle><path d="M0 -38L34 27H-34Z" fill="none" stroke="#272b22" stroke-width="5"/></g>'
save("header.svg",svg(280,b,top=True))
b=r(73,9,954,42,"#e8da99")+t(91,37,"01  /  EXTERNAL UPLINK // NEXUS MODS",19,True)
b+=r(87,65,926,90)+t(109,104,"NEXUS MODS  /  AUTHOR PROFILE",24,True)+r(817,113,177,31,"#edc34d","none",0)+t(839,135,"UPLINK ACTIVE",16,True)
save("nexus.svg",svg(172,b))
b=r(73,10,954,39,"#e8da99")+t(90,38,"02  /  SYSTEM TELEMETRY",19,True)
values=[("REPOSITORIES",len(repos)),("STARS",stars),("FOLLOWERS",profile.get("followers",0)),("FORKS",sum(a.get("forks_count",0) for a in repos))]
for i,(name,value) in enumerate(values):
    x=83+i*234;b+=r(x,66,221,112)+t(x+13,94,name,15,True)+t(x+14,143,str(value),36,True)+r(x+155,154,51,12,"#edc34d","none",0)
b+=t(95,213,"LANGUAGES / "+languages[:65],17,True)
save("stats.svg",svg(240,b))
b=r(73,9,954,41,"#e8da99")+t(90,38,"03  /  ACTIVITY SENSOR ARRAY",19,True)
b+=r(84,64,932,226)+t(102,95,"ANNUAL CONTRIBUTIONS: "+(str(total) if total is not None else "DATA UNAVAILABLE"),19,True)
if calendar:
    for i,day in enumerate(calendar):
        x=105+(i//7)*16.8;y=112+(i%7)*22
        n=day["contributionCount"]
        color="#e9dda0" if n==0 else "#c5b773" if n<3 else "#ae9a4e" if n<7 else "#ecbc43"
        b+=f'<rect x="{x:.1f}" y="{y:.1f}" width="13" height="17" fill="{color}" stroke="#4e4b34" stroke-width=".5"><title>{e(day["date"])}: {n}</title></rect>'
else:b+=t(105,168,"Contribution calendar will populate when GitHub API data is available.",17)
save("activity.svg",svg(305,b))
b=r(73,8,954,42,"#e8da99")+t(90,37,"04  /  REPOSITORY SUBSYSTEMS",19,True)
b+=t(91,75,"SEVEN LINKED MODULES / AUTOMATED GITHUB REPOSITORY DATA",15,True)
save("projects.svg",svg(93,b))
for i,(name,title) in enumerate(PROJECTS,1):
    a=byname.get(name)
    description=(a.get("description") if a else None) or "Repository data unavailable"
    if len(description)>52:description=description[:49]+"..."
    b=r(61,0,478,166)+r(61,0,478,34,"#e7d998")+t(76,24,f"MODULE 0{i} / DATATERM",16,True)
    b+=t(78,75,title,20,True)+t(78,105,description,14)
    if a:b+=t(78,143,f'STARS {a.get("stargazers_count",0)}   FORKS {a.get("forks_count",0)}   ISSUES {a.get("open_issues_count",0)}',14,True)
    else:b+=t(78,143,"DATA LINK UNAVAILABLE",14,True)
    b+=r(491,123,32,25,"#e9be4c","none",0)
    save(f"project-{i}.svg",svg(166,b))
b=r(73,8,954,39,"#e8da99")+t(90,35,"05  /  SYSTEM TOOLCHAIN",19,True)+t(92,93,"CYBER ENGINE TWEAKS  /  LUA  /  WOLVENKIT",21,True)+t(92,127,"REDMOD  /  HTML  /  AI-ASSISTED DEVELOPMENT",18)
save("tech.svg",svg(151,b))
b=r(73,8,954,37,"#e8da99")+t(90,34,"CYNOSURE // TERMINAL SESSION STATUS",18,True)+t(91,91,"ENCRYPTION MEASURES & DEFENSIVE ICE",19,True)+t(795,91,"LINK STABLE",16,True)
b+='<circle cx="984" cy="85" r="9" fill="#dfad32"><animate attributeName="opacity" values=".2;1;.2" dur="2.4s" repeatCount="indefinite"/></circle>'
save("footer.svg",svg(116,b,bottom=True))
print(f"Updated: {len(repos)} repositories, {stars} stars, {len(calendar)} contribution days, 7 modules")
