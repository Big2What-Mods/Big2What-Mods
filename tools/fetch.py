#!/usr/bin/env python3
"""Fetch real public GitHub telemetry. No synthetic statistics or contributions."""
import os,json,pathlib,urllib.request,urllib.error,datetime,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
CACHE=ROOT/'tools'/'profile-data.json'
LOGIN='Big2What-Mods'
PROJECTS=[
('Cyberpunk-2077-Iconic-ID-Tag-Dumper','ICONIC ID / TAG DUMPER'),
('CP2077-Achievement-Logic','ACHIEVEMENT LOGIC'),
('CP2077-Journal-State-Tracer','JOURNAL STATE TRACER'),
('Cynosure_Terminal_Teaser---H10_Bathroom_Poster','CYNOSURE TEASER / H10'),
('Misty-s_Esoterica_Poster-H10_Bathroom',"MISTY'S ESOTERICA"),
('Viktor_Vektor_Ripperdoc_Poster-H10_Bathroom','VIKTOR VEKTOR'),
('El_Coyote_Cojo-_Bar_Poster-H10_Bathroom','EL COYOTE COJO')]
TOKEN=os.getenv('GITHUB_TOKEN') or os.getenv('GH_TOKEN')
def api(url,payload=None):
    headers={'Accept':'application/vnd.github+json','User-Agent':'Cynosure-Profile/4','X-GitHub-Api-Version':'2022-11-28'}
    if TOKEN:headers['Authorization']='Bearer '+TOKEN
    if payload is not None:headers['Content-Type']='application/json'
    req=urllib.request.Request(url,data=json.dumps(payload).encode() if payload is not None else None,headers=headers,method='POST' if payload is not None else 'GET')
    with urllib.request.urlopen(req,timeout=30) as response:return json.load(response)
def streaks(days):
    days=sorted(days,key=lambda x:x['date']); longest=cur=0
    for day in days:
        if day['count']>0:cur+=1;longest=max(longest,cur)
        else:cur=0
    current=0
    # The current streak may end yesterday when the current day has no contributions yet.
    for day in reversed(days):
        if day['count']==0 and current==0 and day==days[-1]:continue
        if day['count']>0:current+=1
        else:break
    return current,longest
def fetch():
    old=json.loads(CACHE.read_text()) if CACHE.exists() else {}
    user=api('https://api.github.com/users/'+LOGIN)
    repos=[];page=1
    while True:
        batch=api(f'https://api.github.com/users/{LOGIN}/repos?per_page=100&page={page}&type=owner')
        repos.extend(batch)
        if len(batch)<100:break
        page+=1
    byname={r['name']:r for r in repos}
    languages={}
    for r in repos:
        if r.get('fork'):continue
        if r.get('language'):languages[r['language']]=languages.get(r['language'],0)+1
    projects=[]
    for slug,label in PROJECTS:
        r=byname.get(slug)
        if r is None:raise RuntimeError(f'Required featured repository not returned by GitHub: {slug}')
        projects.append({'slug':slug,'label':label,'description':r.get('description') or '', 'stars':r['stargazers_count'],'forks':r['forks_count'],'issues':r['open_issues_count']})
    days=[];total=None;calendar_status='unavailable'
    try:
        q='query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}'
        result=api('https://api.github.com/graphql',{'query':q,'variables':{'login':LOGIN}})
        if result.get('errors'):raise RuntimeError(str(result['errors']))
        calendar=result['data']['user']['contributionsCollection']['contributionCalendar']
        days=[{'date':d['date'],'count':d['contributionCount']} for w in calendar['weeks'] for d in w['contributionDays']]
        total=calendar['totalContributions'];calendar_status='fresh'
    except Exception as exc:
        print('WARNING: contribution calendar fetch failed:',exc,file=sys.stderr)
        if old.get('calendar'):
            days=old['calendar'];total=old.get('total_contributions');calendar_status='cached'
    current,longest=streaks(days) if days else (None,None)
    data={'account':LOGIN,'updated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'repo_count':user['public_repos'],'stars':sum(r['stargazers_count'] for r in repos),
          'forks':sum(r['forks_count'] for r in repos),'followers':user['followers'],
          'languages':sorted(languages,key=languages.get,reverse=True)[:5],
          'calendar':days,'total_contributions':total,'calendar_status':calendar_status,
          'current_streak':current,'longest_streak':longest,'projects':projects}
    CACHE.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f'FETCH VERIFIED: {len(repos)} repositories, {len(projects)} project records, {len(days)} contribution days; calendar={calendar_status}')
    return data
if __name__=='__main__':fetch()