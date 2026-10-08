#!/usr/bin/env python3
"""Generate linked, continuous multi-SVG Cynosure profile and cache-bust artwork URLs."""
import hashlib,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
ASSETS=ROOT/'assets'
slugs=['Cyberpunk-2077-Iconic-ID-Tag-Dumper','CP2077-Achievement-Logic','CP2077-Journal-State-Tracer','Cynosure_Terminal_Teaser---H10_Bathroom_Poster','Misty-s_Esoterica_Poster-H10_Bathroom','Viktor_Vektor_Ripperdoc_Poster-H10_Bathroom','El_Coyote_Cojo-_Bar_Poster-H10_Bathroom']
labels=['Iconic ID and Tag Dumper','Achievement Logic','Journal State Tracer','Cynosure Teaser H10','Misty’s Esoterica','Viktor Vektor','El Coyote Cojo']
assets=list(sorted(ASSETS.glob('cynosure-*.svg')))
if len(assets)!=15:raise RuntimeError(f'Expected 15 fresh SVG modules; got {len(assets)}')
version=hashlib.sha256(b''.join(p.read_bytes() for p in assets)).hexdigest()[:12]
def img(name,alt,width='100%'):
    return f'<img src="./assets/cynosure-{name}.svg?v={version}" width="{width}" align="top" alt="{alt}">'
parts=[img('header','Militech Cynosure operator panel: Big2What, Retired Cybersecurity Analyst'),
       f'<a href="https://www.nexusmods.com/profile/Big2What">{img("nexus","Nexus Mods profile access")}</a>',
       img('stats','Actual GitHub account statistics'),img('activity','Actual daily GitHub contributions'),img('projects','Repository system directory')]
for i in range(0,6,2):
    parts.append(''.join(f'<a href="https://github.com/Big2What-Mods/{slugs[j]}">{img(f"project-{j+1}",labels[j],"50%")}</a>' for j in (i,i+1)))
# Final project occupies half-width to retain identical dimensions; second half is terminal equipment schematic.
parts.append(f'<a href="https://github.com/Big2What-Mods/{slugs[6]}">{img("project-7",labels[6],"50%")}</a>'+img('project-end','Cynosure module diagnostics','50%'))
parts.extend([img('tech','Modding tools and technologies'),img('footer','Cynosure secure session status')])
readme='<p align="center">'+''.join(parts)+'</p>\n'
(ROOT/'README.md').write_text(readme,encoding='utf-8')
print('README refreshed, cache version:',version)