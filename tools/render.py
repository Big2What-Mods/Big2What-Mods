#!/usr/bin/env python3
"""Original, data-driven MILITECH/Cynosure GitHub profile SVG renderer.
Every SVG is drawn as a vector interface module, never a reused background image.
All full-width slices share a 960px chassis and align edge-to-edge in README.
"""
import html, math, json, pathlib, datetime
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'assets'; OUT.mkdir(exist_ok=True)
W=960
PAPER='#f5ecaa'; PAPER2='#fff7bb'; INK='#24291e'; MUTED='#64634b'; AMBER='#eec04c'; DARK='#18251d'; FRAME='#29372a'

def E(x):return html.escape(str(x),quote=True)
def rect(x,y,w,h,fill='none',stroke=INK,sw=1):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
def path(d,sw=1.5,stroke=INK,fill='none'):return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="miter"/>'
def txt(x,y,s,size=13,bold=False,color=INK,spacing=None):return f'<text x="{x}" y="{y}" font-family="Arial Narrow, Liberation Sans Narrow, Arial, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{color}"'+(f' letter-spacing="{spacing}"' if spacing else '')+f'>{E(s)}</text>'
def circle(x,y,r,fill='none',stroke=INK,sw=1):return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
def status(x,y,label='ONLINE'):
    return rect(x,y,92,23,AMBER,'none',0)+txt(x+13,y+16,label,12,True)+f'<rect x="{x+78}" y="{y+7}" width="7" height="7" fill="{INK}"><animate attributeName="opacity" values=".35;1;.35" dur="2.7s" repeatCount="indefinite"/></rect>'
def screw(x,y):return circle(x,y,4,'#b0a677',INK,.8)+path(f'M{x-2} {y+2}l4 -4',1)
def rails(h,first=False,last=False):
    # Shared physical housing; only the first/last segment draws the outer end cap.
    out=rect(0,0,W,h,DARK,'none',0)+rect(12,0,W-24,h,FRAME,'none',0)+rect(38,0,W-76,h,'#f7edaf','none',0)
    out+=rect(38,0,W-76,h,'url(#dust)','none',0)
    out+=rect(17,0,15,h,'url(#vent)','none',0)+rect(W-32,0,15,h,'url(#vent)','none',0)
    out+=path(f'M38 0V{h}M{W-38} 0V{h}',3,'#131c17')
    if first:out+=rect(12,0,W-24,13,'#364539','none',0)+path(f'M12 12H{W-12}',2)
    if last:out+=rect(12,h-13,W-24,13,'#364539','none',0)+path(f'M12 {h-13}H{W-12}',2)
    return out

def svg(h,content,first=False,last=False,width=W):
    # Shared original texture primitives, not a static background asset.
    defs=f'''<defs><pattern id="dust" width="83" height="71" patternUnits="userSpaceOnUse"><path d="M9 15l6 1m48 32h-4" stroke="#666145" opacity=".14"/><circle cx="37" cy="23" r=".9" fill="#736d4b" opacity=".19"/></pattern><pattern id="vent" width="15" height="31" patternUnits="userSpaceOnUse"><path d="M3 4l9 -3v24l-9 3z" fill="#82917b" stroke="#29362b" stroke-width="1.2"/></pattern><linearGradient id="screen" x2="0" y2="1"><stop stop-color="{PAPER2}"/><stop offset="1" stop-color="{PAPER}"/></linearGradient></defs>'''
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{h}" viewBox="0 0 {width} {h}">{defs}{rails(h,first,last) if width==W else ""}{content}</svg>'
def bar(y,name):return rect(57,y,846,30,'#f7efb7',INK,1.5)+txt(73,y+21,name,15,True)
def linkport(x,y):
    return rect(x,y,29,38,'#e9dda1',INK,2)+rect(x+5,y+7,19,24,'none',INK,1)+path(f'M{x+8} {y+12}h13M{x+8} {y+17}h13M{x+8} {y+22}h13',1)
def hardware(x,y):
    """Original industrial line-art dataport enclosure with hinges, vents, screw heads."""
    a=rect(x+18,y+12,188,124,'#e4d99b',INK,3)+rect(x+28,y+22,168,104,'#f6ecad',INK,1.6)
    a+=path(f'M{x+18} {y+12}l-12 13v116l12 -5M{x+206} {y+12}l14 13v116l-14 -5',2)
    for side in [x+7,x+192]:
        for i in range(4):a+=rect(side,y+34+i*20,19,10,'#c7bd8a',INK,1)
    for i in range(5):a+=path(f'M{x+60} {y+39+i*15}h92',3,'#65654b')
    a+=rect(x+82,y+54,47,40,'#f1e6a4',INK,1.6)+txt(x+92,y+78,'CN-03',12,True)
    for xx in [x+37,x+184]:
        for yy in [y+29,y+119]:a+=screw(xx,yy)
    a+=txt(x+20,y+155,'MILITECH // INDUSTRIAL DATAPORT',10,True)
    return a

def header():
    h=310;b=rails(h,True)
    b+=rect(56,24,848,33,'#e8dfa2',INK,1)+txt(72,46,'CONTROL PANEL    /    CYNOSURE SYSTEMS',14,True)+txt(776,46,'SECURITY: ACTIVE',11,True)
    b+=bar(70,'OPERATOR IDENTIFICATION   /   DATATERM ACCESS')
    b+=rect(58,113,386,175,'url(#screen)',INK,1.7)+txt(76,139,'IDENTITY VERIFIED',12,True)+txt(74,206,'Big2What',52,True)+txt(77,236,'RETIRED CYBERSECURITY ANALYST',17,True)+status(77,254,'ONLINE')
    b+=hardware(547,112)
    b+=txt(782,140,'REF: 07-A',10,True)+path('M776 143l-28 16',1)+txt(781,259,'ENCRYPTED',12,True)
    return svg(h,b[len(rails(h,True)):],True) # avoid duplicated rails

def uplink():
    h=142;b=bar(8,'NETWORK CONNECTION   /   NEXUS MODS')+rect(57,49,846,75,'url(#screen)',INK,1.4)
    b+=linkport(75,67)+txt(123,80,'NEXUS MODS',22,True)+txt(124,105,'AUTHOR PROFILE  /  EXTERNAL DATAPORT',13)+status(788,74,'LINK UP')
    b+=path('M104 86H118M658 86H786',2.2)
    return svg(h,b)

def telemetry(data):
    h=229;b=bar(8,'GITHUB TELEMETRY   /   ACCOUNT SYSTEM STATUS')
    names=[('REPOSITORIES',data.get('repo_count')),('STARS',data.get('stars')),('FOLLOWERS',data.get('followers')),('FORKS',data.get('forks'))]
    for i,(name,val) in enumerate(names):
        x=58+i*213;b+=rect(x,50,201,126,'url(#screen)',INK,1.4)+rect(x,50,201,27,'#e4d89d',INK,1)
        b+=txt(x+10,69,name,13,True)+txt(x+14,128,'--' if val is None else val,37,True)+rect(x+13,146,175,19,AMBER,'none',0)+txt(x+20,160,'SYSTEM ONLINE',11,True)
    b+=path('M158 177v13H800v-13M478 190v11',2)
    b+=txt(74,215,'LANGUAGE INDEX: '+', '.join(data.get('languages') or ['NO LANGUAGE DATA'])[:80],13,True)
    return svg(h,b)

def activity(data):
    h=253;b=bar(8,'ACTIVITY SENSOR ARRAY   /   CONTRIBUTION HISTORY')
    b+=rect(58,49,845,184,'url(#screen)',INK,1.5)
    total=data.get('total_contributions')
    b+=txt(73,75,'LAST 12 MONTHS   /   '+(str(total)+' CONTRIBUTIONS' if total is not None else 'DATA UNAVAILABLE'),14,True)
    days=data.get('calendar') or []
    if days:
        # Last 371 days, seven rows per week, 53 columns. Data-derived cell illumination.
        days=days[-371:]
        maxn=max([d['count'] for d in days] or [1])
        for i,d in enumerate(days):
            x=77+(i//7)*15.2;y=91+(i%7)*17.5;n=d['count']
            color='#eee3a8' if n==0 else '#c7b77b' if n<3 else '#a59452' if n<7 else '#e7b43f'
            b+=f'<rect x="{x:.1f}" y="{y:.1f}" width="11.6" height="13.5" fill="{color}" stroke="#625d41" stroke-width=".4"><title>{E(d["date"])}: {n} contributions</title></rect>'
        b+=txt(74,222,'CONTRIBUTION SIGNAL / REAL GITHUB ACTIVITY',11,True)
    else:b+=txt(75,135,'NO VERIFIED CONTRIBUTION CALENDAR AVAILABLE',15,True)
    return svg(h,b)

def projects_heading():
    return svg(67,bar(9,'DATATERM ARCHIVE   /   SEVEN VERIFIED REPOSITORY MODULES'))

def card(i,p,width=480):
    h=158
    # Half width has shared left/right industrial rails, no isolated box framing.
    side='left' if i%2==0 else 'right'
    b=rect(0,0,width,h,DARK,'none',0)+rect(6,0,width-12,h,FRAME,'none',0)
    if side=='left':b+=rect(20,0,width-24,h,'url(#screen)','none',0)+path(f'M20 0V{h}',2)
    else:b+=rect(4,0,width-24,h,'url(#screen)','none',0)+path(f'M{width-20} 0V{h}',2)
    x=36 if side=='left' else 20
    b+=rect(x,7,width-56,27,'#e2d69a',INK,1)+txt(x+11,26,f'DATATERM {i+1:02d}  /  SYSTEM FILE',13,True)
    b+=txt(x+12,68,p['label'],19,True)
    desc=(p.get('description') or 'No repository description supplied').strip()
    if len(desc)>54:desc=desc[:51]+'...'
    b+=txt(x+12,93,desc,11)
    b+=rect(x+10,109,width-76,32,'#edc04b',INK,1)+txt(x+18,131,f'STARS {p.get("stars",0)}    FORKS {p.get("forks",0)}    ISSUES {p.get("issues",0)}',12,True)
    b+=circle(x+width-81,125,5,'#303528')+f'<circle cx="{x+width-81}" cy="125" r="5" fill="#f5e9a7"><animate attributeName="opacity" values=".2;1;.2" dur="{2+i%3}s" repeatCount="indefinite"/></circle>'
    return svg(h,b,width=width)

def project_end():
    h=158;w=480
    b=rect(0,0,w,h,DARK,'none',0)+rect(4,0,w-24,h,'url(#screen)','none',0)
    b+=rect(20,7,424,27,'#e2d69a',INK,1)+txt(31,26,'CYNOSURE // CONTROL BUS',13,True)
    # Original schematic: three linked terminal controllers with an active data bus.
    for i in range(3):
        x=47+i*125
        b+=rect(x,59,83,56,'#e8dba0',INK,2)+rect(x+12,69,59,19,'#c7ba84',INK,1)
        b+=txt(x+23,83,f'BUS-0{i+1}',10,True)
        b+=rect(x+16,97,51,9,AMBER,INK,.6)
        if i<2:b+=path(f'M{x+83} 87h42',2.5)
    b+=txt(35,141,'SYSTEM MODULES / SYNCHRONIZED',13,True)
    return svg(h,b,width=w)

def toolchain():
    h=150;b=bar(7,'SYSTEMS   /   DEVELOPMENT TOOLCHAIN')
    b+=rect(58,49,844,80,'url(#screen)',INK,1.3)
    b+=txt(79,81,'CYBER ENGINE TWEAKS  /  LUA  /  WOLVENKIT',18,True)
    b+=txt(79,110,'REDMOD  /  HTML  /  AI-ASSISTED IMPLEMENTATION',15,True)
    return svg(h,b)

def footer():
    h=120;b=bar(7,'CYNOSURE   /   ENCRYPTION MEASURES & DEFENSIVE ICE')
    b+=rect(58,48,844,52,'url(#screen)',INK,1.3)+txt(76,81,'SYSTEM INTEGRITY VERIFIED  /  CONNECTION STABLE',17,True)
    b+=status(782,62,'ONLINE')
    b+=txt(75,114,'CYNOSURE SYSTEMS',10,True)
    return svg(h,b,last=True)

def render(data):
    assets={'header':header(),'nexus':uplink(),'stats':telemetry(data),'activity':activity(data),'projects':projects_heading(),'tech':toolchain(),'footer':footer(),'project-end':project_end()}
    for i,p in enumerate(data['projects']):assets[f'project-{i+1}']=card(i,p)
    for name,content in assets.items():(OUT/f'cynosure-{name}.svg').write_text(content,encoding='utf-8')
    return len(assets)
if __name__=='__main__':
    data=json.loads((ROOT/'tools'/'profile-data.json').read_text(encoding='utf-8'))
    print('Generated',render(data),'new Cynosure assets')