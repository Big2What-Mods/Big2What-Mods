import json,os,urllib.request,pathlib,datetime
HERE=pathlib.Path(__file__).resolve().parent
DATA=HERE/"data";DATA.mkdir(exist_ok=True)
USER="Big2What-Mods"
PROJECTS=["Cyberpunk-2077-Iconic-ID-Tag-Dumper","CP2077-Achievement-Logic","CP2077-Journal-State-Tracer","Cynosure_Terminal_Teaser---H10_Bathroom_Poster","Misty-s_Esoterica_Poster-H10_Bathroom","Viktor_Vektor_Ripperdoc_Poster-H10_Bathroom","El_Coyote_Cojo-_Bar_Poster-H10_Bathroom"]
def request(url,query=None):
 h={"User-Agent":"Cynosure-Profile","Accept":"application/vnd.github+json"}
 if os.getenv("GITHUB_TOKEN"):h["Authorization"]="Bearer "+os.environ["GITHUB_TOKEN"]
 if query is not None:h["Content-Type"]="application/json"
 r=urllib.request.Request(url,data=json.dumps(query).encode() if query is not None else None,headers=h,method="POST" if query is not None else "GET")
 with urllib.request.urlopen(r,timeout=30) as response:return json.load(response)
def cached(name,fn):
 path=DATA/(name+".json")
 try:
  value=fn()
  if value is None:raise ValueError("empty response")
  path.write_text(json.dumps(value,indent=2),encoding="utf-8")
  print("REFRESHED",name)
  return value
 except Exception as exc:
  if path.exists():
   print("CACHED",name,exc);return json.loads(path.read_text())
  raise RuntimeError("No valid "+name+" data: "+str(exc))
def stats():
 account=request("https://api.github.com/users/"+USER)
 repos=request("https://api.github.com/users/"+USER+"/repos?per_page=100")
 language={}
 for repo in repos:
  if repo.get("language"):language[repo["language"]]=language.get(repo["language"],0)+1
 return {"account":USER,"followers":account["followers"],"created":account["created_at"][:10],"repos":len(repos),"stars":sum(x["stargazers_count"] for x in repos),"forks":sum(x["forks_count"] for x in repos),"languages":language,"projects":{p:next(({"stars":r["stargazers_count"],"forks":r["forks_count"],"issues":r["open_issues_count"],"description":r.get("description") or ""} for r in repos if r["name"]==p),None) for p in PROJECTS}}
def calendar():
 q='query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}'
 d=request("https://api.github.com/graphql",{"query":q,"variables":{"login":USER}})
 cal=d["data"]["user"]["contributionsCollection"]["contributionCalendar"]
 return {"total":cal["totalContributions"],"days":[day for week in cal["weeks"] for day in week["contributionDays"]]}
def main():
 cached("stats",stats)
 cached("calendar",calendar)
if __name__=="__main__":main()
