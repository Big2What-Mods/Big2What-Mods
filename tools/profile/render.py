"""Militech Cynosure SVG slice renderer. Every module uses one continuous chassis."""
import pathlib,json,html,math,hashlib
HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[1];OUT=ROOT/"assets";OUT.mkdir(exist_ok=True)
DATA=HERE/"data"
W,M=960,12
INK="#20251d";PAPER="#f5edb0";AMBER="#e6bb51";CREAM="#fff8c6"
def e(v):return html.escape(str(v),quote=True)
def t(x,y,value,size=16,bold=False,fill=INK,extra=""):
 return f'<text x="{x}" y="{y}" font-family="monospace" font-size="{size}" font-weight="{700 if bold else 400}" fill="{fill}" {extra}>{e(value)}</text>'
def rect(x,y,w,h,fill=PAPER,stroke=INK,sw=1.5):
 return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
def stagger(rows,start=0.3,step=0.13):
 return "".join(f'<g class="appear" style="animation-delay:{start+i*step:.2f}s">{r}</g>' for i,r in enumerate(rows))
def slice_svg(height,body,top=False,bottom=False):
 assert height>0
 end=height-M if bottom else height
 begin=M if top else 0
 css="""<style>
 @keyframes appear{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:translateY(0)}}
 @keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}
 @keyframes scan{from{transform:translateX(-400px)}to{transform:translateX(1200px)}}
 @keyframes type{from{width:0}to{width:100%}}
 .appear{animation:appear .55s ease both}.pulse{animation:pulse 2.5s infinite}
 .scan{animation:scan 12s linear infinite}
 @media(prefers-reduced-motion:reduce){*{animation:none!important}}
 </style>"""
 frame=rect(M,begin,W-2*M,end-begin,CREAM,INK,3)
 rails=f'<path d="M{M+24} {begin}V{end}M{W-M-24} {begin}V{end}" stroke="#4b5140" stroke-width="6"/>'
 defs='<defs><pattern id="hatch" width="13" height="16" patternUnits="userSpaceOnUse"><path d="M3 2h7v12H3z" fill="#59604d" stroke="#24291f"/></pattern></defs>'
 side=f'<rect x="{M+6}" y="{begin}" width="14" height="{end-begin}" fill="url(#hatch)"/><rect x="{W-M-20}" y="{begin}" width="14" height="{end-begin}" fill="url(#hatch)"/>'
 return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}">{css}{defs}{frame}{rails}{side}{body}</svg>'
def heading(title):
 return rect(53,12,854,36,"#e5d89b")+t(69,37,title,17,True)
def save(name,body): (OUT/name).write_text(body,encoding="utf-8")
def build_header():
 b=heading("MILITECH  //  CYNOSURE  //  OPERATOR INTERFACE")
 b+=rect(66,61,827,212,CREAM)
 b+=t(88,93,"IDENTIFICATION VERIFIED  /  SESSION ACTIVE",15,True)
 name="Big2What"
 for i,ch in enumerate(name):
  b+=t(90+i*44,173,ch,55,True,extra=f'class="appear" style="animation-delay:{.5+i*.2:.2f}s"')
 b+=f'<rect x="447" y="125" width="5" height="52" fill="{INK}" class="pulse"/>'
 b+=stagger([t(91,218,"Retired Cybersecurity Analyst",22,True),t(91,247,"CYNOSURE // SYSTEM CLEARANCE",14)],2.4,.25)
 # Exact reference emblem, preserved as an embedded alpha-masked image; only opacity animates.
 b+='<g transform="translate(777 162)"><image href="data:image/png;base64,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" x="-76" y="-74" width="152" height="148" preserveAspectRatio="xMidYMid meet"><animate attributeName="opacity" values=".85;1;.85" dur="3s" repeatCount="indefinite"/></image></g>'

 save("header.svg",slice_svg(300,b,top=True))
def build_link():
 b=heading("01 / EXTERNAL DATAPORT")
 b+=rect(67,63,827,91)+t(92,104,"NEXUS MODS  /  AUTHOR PROFILE",25,True)+rect(706,113,169,30,AMBER)+t(726,134,"UPLINK READY",15,True)
 save("nexus.svg",slice_svg(160,b))
def build_stats(s):
 b=heading("02 / TELEMETRY MONITOR  //  GITHUB ACCOUNT")
 values=[("REPOSITORIES",s["repos"]),("STARS",s["stars"]),("FOLLOWERS",s["followers"]),("FORKS",s["forks"])]
 for i,(name,value) in enumerate(values):
  x=67+i*210;b+=rect(x,65,197,104)+t(x+12,92,name,15,True)+stagger([t(x+12,141,value,35,True)],.4+i*.2)
 b+=t(80,201,"LANGUAGES / "+(", ".join(sorted(s["languages"],key=s["languages"].get,reverse=True)[:4]) or "UNREPORTED"),16,True)
 save("stats.svg",slice_svg(240,b))
def build_activity(c):
 b=heading("03 / CONTRIBUTION SENSOR ARRAY")
 b+=rect(67,65,827,211)+stagger([t(84,92,"ANNUAL CONTRIBUTIONS / "+str(c["total"]),17,True)])
 for i,d in enumerate(c["days"]):
  x=88+(i//7)*14.5;y=111+(i%7)*20
  n=d["contributionCount"]
  fill="#e8dda0" if n==0 else "#b7a76c" if n<3 else "#988548" if n<7 else AMBER
  b+=f'<rect x="{x:.1f}" y="{y:.1f}" width="11" height="15" fill="{fill}" stroke="#55533a" stroke-width=".5"><title>{e(d["date"])}: {n} contributions</title><animate attributeName="opacity" values=".5;1;.5" dur="{2+i%6}s" repeatCount="indefinite"/></rect>'
 b+=t(84,260,"DAILY SIGNAL // REAL GITHUB CONTRIBUTION HISTORY",12)
 save("activity.svg",slice_svg(280,b))
PROJECTS=[("Cyberpunk-2077-Iconic-ID-Tag-Dumper","ICONIC ID / TAG DUMPER"),("CP2077-Achievement-Logic","ACHIEVEMENT LOGIC"),("CP2077-Journal-State-Tracer","JOURNAL STATE TRACER"),("Cynosure_Terminal_Teaser---H10_Bathroom_Poster","CYNOSURE TEASER / H10"),("Misty-s_Esoterica_Poster-H10_Bathroom","MISTY'S ESOTERICA"),("Viktor_Vektor_Ripperdoc_Poster-H10_Bathroom","VIKTOR VEKTOR"),("El_Coyote_Cojo-_Bar_Poster-H10_Bathroom","EL COYOTE COJO")]
def build_projects(s):
 save("projects.svg",slice_svg(80,heading("04 / REPOSITORY SUBSYSTEMS  //  SEVEN MODULES")))
 for i,(key,title) in enumerate(PROJECTS):
  p=s["projects"][key]
  if p is None:raise ValueError("Missing actual repository: "+key)
  b=rect(53,0,854,120,CREAM)+rect(66,9,828,33,"#e5d89b")+t(80,33,f"MODULE {i+1:02d}  /  {title}",18,True)
  b+=stagger([t(82,72,f'STARS {p["stars"]}   FORKS {p["forks"]}   OPEN ISSUES {p["issues"]}',16,True)],.3)
  b+=rect(714,83,160,27,AMBER)+t(736,103,"LINK AVAILABLE",13,True)
  save(f"project-{i+1}.svg",slice_svg(120,b))
def build_tech():
 b=heading("05 / SYSTEM TOOLCHAIN")+stagger([t(80,98,"CYBER ENGINE TWEAKS / LUA / WOLVENKIT",20,True),t(80,137,"REDMOD / HTML / AI-ASSISTED DEVELOPMENT",17)],.3,.3)
 save("tech.svg",slice_svg(160,b))
def build_footer():
 b=heading("CYNOSURE SYSTEMS / SESSION STATUS")+t(79,101,"ENCRYPTION MEASURES & DEFENSIVE ICE",17,True)+t(728,101,"LINK STABLE",15,True)+f'<circle cx="869" cy="95" r="8" fill="{AMBER}" class="pulse"/>'
 save("footer.svg",slice_svg(120,b,bottom=True))
def main():
 s=json.loads((DATA/"stats.json").read_text())
 c=json.loads((DATA/"calendar.json").read_text())
 build_header();build_link();build_stats(s);build_activity(c);build_projects(s);build_tech();build_footer()
 print("Rendered",len(list(OUT.glob("*.svg"))),"data-driven animated slices")
if __name__=="__main__":main()
