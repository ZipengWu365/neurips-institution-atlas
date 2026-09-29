import json,math,re,html,csv,zipfile,ast,shutil
from pathlib import Path
from collections import defaultdict
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data';POSTERS=ROOT/'posters';POSTERS.mkdir(exist_ok=True)
REPO=ROOT;REPO.mkdir(exist_ok=True)
(REPO/'assets').mkdir(exist_ok=True);(REPO/'data').mkdir(exist_ok=True)
data=json.loads((OUT/'institutions_clean.json').read_text(encoding='utf-8'))
BASE={'Asia':(34,100,162),'Europe':(113,72,155),'Americas':(17,119,98),'Oceania':(194,121,29)}
regions={'China':'Asia','Japan':'Asia','South Korea':'Asia','India':'Asia','Singapore':'Asia','United Arab Emirates':'Asia','Israel':'Asia','Saudi Arabia':'Asia','United States':'Americas','Canada':'Americas','Australia':'Oceania'}
COUNTRIES=['China','United Kingdom','United States','Germany','France','Italy','Australia','South Korea','India','Japan']
for d in data:d['region']=regions.get(d['country'],'Europe')
# Reuse the already validated area-preserving layout functions without running the old builders.
tree=ast.parse((ROOT/'scripts/layout.py').read_text(encoding='utf-8'))
keep=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['square_layout','binary_layout','split_layout']]
exec(compile(ast.Module(body=keep,type_ignores=[]),'layout','exec'))
def font(sz,bold=False):return ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf',int(sz))
def hx(c):return '#%02x%02x%02x'%tuple(c)
KNOWN={
 'Massachusetts Institute of Technology':'MIT','Korea Advanced Institute of Science and Technology':'KAIST','Mohamed bin Zayed University of Artificial Intelligence':'MBZUAI','Korea Institute for Advanced Study':'KIAS','University of California, Berkeley':'UC Berkeley','University of California, Los Angeles':'UCLA','University of California, San Diego':'UC San Diego','University of California, Santa Barbara':'UC Santa Barbara','University of California, Santa Cruz':'UC Santa Cruz','University of California, Irvine':'UC Irvine','University of California, Davis':'UC Davis','University of California, Riverside':'UC Riverside','University of California, Merced':'UC Merced','University of California, San Francisco':'UC San Francisco','Hong Kong University of Science and Technology':'HKUST','Hong Kong University of Science and Technology (Guangzhou)':'HKUST (Guangzhou)','Chinese University of Hong Kong':'CUHK','Chinese University of Hong Kong, Shenzhen':'CUHK (Shenzhen)','National University of Singapore':'NUS','Nanyang Technological University':'NTU Singapore','University of Science and Technology of China':'USTC','University of Electronic Science and Technology of China':'UESTC','Beijing University of Posts and Telecommunications':'BUPT','Georgia Institute of Technology':'Georgia Tech','California Institute of Technology':'Caltech','University of New South Wales':'UNSW','Australian National University':'ANU','University of Technology Sydney':'UTS','Université Claude Bernard (Lyon I)':'Claude Bernard Lyon 1','Institut national de la santé et de la recherche médicale':'Inserm','National Institute of Advanced Industrial Science and Technology':'AIST','National Institute of Information and Communications Technology (NICT)':'NICT','ASIAN INSTITUTE OF GASTROENTEROLOGY':'Asian Inst. of Gastroenterology','Università degli Studi di Milano':'University of Milan','Università degli Studi di Salerno':'University of Salerno','Università di Roma Tor Vergata':'Tor Vergata University of Rome','Royal Holloway and Bedford New College':'Royal Holloway, University of London','Google':'Google / DeepMind','Indraprastha Institute of Information Technology Delhi':'IIIT Delhi','International Institute of Information Technology Hyderabad':'IIIT Hyderabad','National Institute of Informatics':'NII','Electronics and Telecommunications Research Institute':'ETRI','Kalinga Institute of Industrial Technology (KIIT) Bhubaneswar India':'KIIT','Defence Science and Technology Group (DSTG)':'DSTG','CAS Center for Excellence in Brain Science and Intelligence Technology':'CAS Brain Science Center','Intelligent Science & Technology Academy of CASIC':'CASIC Intelligent Science & Technology Academy','Institute of Science and Technology Austria':'ISTA'
}
def display_name(n):
 if n=='Beijing Institute of Mathematical Sciences and Applications (BIMSA)':return 'BIMSA'
 if n=='Information Technology Service Center of People\'s Court':return "People's Court IT Service Center"
 if n=='Guangdong Laboratory of Artificial Intelligence and Digital Economy (SZ)':return 'Guangdong AI & Digital Economy Lab (SZ)'
 if n=='National University of Defense Technology':return 'NUDT'
 if n=='Institute of Microelectronics of the Chinese Academy of Sciences':return 'CAS Microelectronics'
 if n in KNOWN:return KNOWN[n]
 n=n.replace('Indian Institute of Technology','IIT').replace('Indian Institute of Management','IIM')
 n=n.replace(', Chinese Academy of Sciences',' (CAS)').replace('of the Chinese Academy of Sciences','(CAS)')
 n=n.replace('University','Univ.').replace('Institute','Inst.').replace('Technology','Tech.').replace('Technological','Technol.').replace('Information','Info.').replace('International','Intl.').replace('Laboratory','Lab').replace('Laboratories','Labs').replace('Artificial Intelligence','AI').replace(' and ',' & ')
 return n
W,H=7200,9600
views=[('world-regions','Worldwide','region',data[:200]),('world-countries','Worldwide','country',data[:200])]
views += [(c.lower().replace(' ','-'),c,None,[d for d in data if d['country']==c][:200]) for c in COUNTRIES]
manifest=[]
for slug,country,mode,selected in views:
 im=Image.new('RGB',(W,H),'#f7f9fc');dr=ImageDraw.Draw(im);parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" fill="#f7f9fc"/>']
 def rect(x,y,w,h,fill,stroke=None,sw=0):
  dr.rectangle((round(x),round(y),round(x+w),round(y+h)),fill=fill,outline=stroke,width=int(sw) if stroke else 1)
  parts.append(f'<rect x="{x:.4f}" y="{y:.4f}" width="{w:.4f}" height="{h:.4f}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{sw}"' if stroke else '')+'/>')
 def text(x,y,s,size,color='#102c44',bold=False,center=False):
  dr.text((x,y),s,font=font(size,bold),fill=color,anchor='mt' if center else 'lt')
  parts.append(f'<text x="{x}" y="{y}" dominant-baseline="text-before-edge" text-anchor="{"middle" if center else "start"}" font-family="Arial,sans-serif" font-weight="{700 if bold else 400}" font-size="{size}" fill="{color}">{html.escape(s)}</text>')
 def wrap(s,size,width):
  words=[]
  for word in s.split():
   while size<=34 and dr.textlength(word,font=font(size,True))>width and len(word)>1:
    k=len(word)-1
    while k>1 and dr.textlength(word[:k]+'-',font=font(size,True))>width:k-=1
    words.append(word[:k]+'-');word=word[k:]
   words.append(word)
  lines=[];line=''
  for word in words:
   new=(line+' '+word).strip()
   if line and dr.textlength(new,font=font(size,True))>width:lines.append(line);line=word
   else:line=new
  if line:lines.append(line)
  return lines
 theme=BASE[selected[0]['region']] if not mode else BASE['Asia']
 text(160,145,'NEURIPS 2026',180,hx(theme),True)
 text(150,405,country.upper(),285,bold=True)
 subtitle=('TOP 200 INSTITUTIONS' if len(selected)==200 else f'{len(selected)} INSTITUTIONS')+'  /  PAPER PARTICIPATION'
 text(160,790,subtitle,89,'#4a647b',True)
 X,Y,CW,CH=150,1090,6900,7850
 if mode:
  buckets=defaultdict(list)
  for d in selected:buckets[d[mode]].append(d)
  groups=[{'label':k,'members':v,'value':sum(d['value'] for d in v)} for k,v in buckets.items()]
  groups.sort(key=lambda x:-x['value'])
  outer=split_layout(groups,X,Y,CW,CH)
 else:outer=[({'label':country,'members':selected,'value':sum(d['value'] for d in selected)},X,Y,CW,CH)]
 ratios=[];smallest=999;leafcount=0
 for g,x,y,w,h in outer:
  hh=h*(.075 if mode=='region' else .16) if mode else 0
  if mode:
   region=g['members'][0]['region'];rect(x,y,w,hh,hx(BASE[region]))
   for fs in range(132,7,-1):
    ls=wrap(g['label'],fs,w-22)
    if len(ls)*(fs+4)<hh-8 and all(dr.textlength(s,font=font(fs,True))<w-22 for s in ls):break
   assert len(ls)*(fs+4)<hh-8,(slug,g['label'])
   ty=y+(hh-len(ls)*(fs+4))/2
   for s in ls:text(x+w/2,ty,s,fs,'white',True,True);ty+=fs+4
  for d,rx,ry,rw,rh in split_layout(g['members'],x,y+hh,w,h-hh):
   ratios.append(rw*rh/d['value']);leafcount+=1
   strength=.22+.61*math.sqrt(d['value']/selected[0]['value'])
   base=BASE[d['region']] if mode else theme
   fill=tuple(round(255*(1-strength)+v*strength) for v in base)
   parts.append(f'<g class="institution" data-name="{html.escape(d["name"],quote=True)}" data-country="{html.escape(d["country"] or "Unassigned",quote=True)}"><title>{html.escape(d["name"])} — {d["value"]} papers</title>')
   rect(rx,ry,rw,rh,hx(fill),'white',5)
   label=display_name(d['name']);pad=min(16,max(4,rw*.04));ypad=min(25,max(4,rh*.04))
   for fs in range(220 if mode else 280,11,-1):
    ls=wrap(label,fs,rw-pad*2);ms=max(12,int(fs*.85));metric=str(d['value']);gap=max(2,int(fs*.1));mgap=max(5,int(fs*.15));needed=len(ls)*(fs+gap)+ms+mgap
    if needed<rh-ypad*2 and all(dr.textlength(s,font=font(fs,True))<rw-pad*2 for s in ls) and dr.textlength(metric,font=font(ms))<rw-pad*2:break
   assert needed<rh-ypad*2 and all(dr.textlength(s,font=font(fs,True))<rw-pad*2 for s in ls),(slug,label,rw,rh,fs)
   smallest=min(smallest,fs)
   fg='white' if strength>.78 else '#12344b';ty=ry+(rh-needed)/2
   for s in ls:text(rx+rw/2,ty,s,fs,fg,True,True);ty+=fs+gap
   text(rx+rw/2,ty+mgap,metric,ms,fg,False,True)
   parts.append('</g>')
  if mode:
   dr.rectangle((round(x),round(y),round(x+w),round(y+h)),outline='white',width=12)
   parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="white" stroke-width="12" pointer-events="none"/>')
 assert leafcount==len(selected)
 assert max(ratios)-min(ratios)<1e-6
 rect(150,9150,6900,7,'#dbe3ed')
 text(W/2,9270,'github.com/ZipengWu365',235,'#102c44',True,True)
 parts.append('</svg>');svg='\n'.join(parts)
 assert not re.search(r'[\u4e00-\u9fff]',svg)
 filename=f'NeurIPS_2026_{slug}_EN'
 im.save(POSTERS/f'{filename}.png',dpi=(300,300))
 (POSTERS/f'{filename}.svg').write_text(svg,encoding='utf-8')
 (REPO/'assets'/f'{slug}.svg').write_text(svg,encoding='utf-8')
 preview=im.copy();preview.thumbnail((900,1200));preview.save(POSTERS/f'{filename}_preview.jpg',quality=90)
 with (REPO/'data'/f'{slug}.csv').open('w',newline='',encoding='utf-8-sig') as f:
  wr=csv.writer(f);wr.writerow(['Displayed position','Institution','Country','Associated papers','Original source labels'])
  for i,d in enumerate(selected):wr.writerow([i+1,d['name'],d['country'],d['value'],'; '.join(d['aliases'])])
 manifest.append({'id':slug,'title':country+(' by '+mode if mode else ''),'count':len(selected),'filename':filename,'minimum_font_pixels':smallest,'svg':svg})
 print(slug,len(selected),'minimum font',smallest,flush=True)
 del im

htmlpage='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NeurIPS 2026 Institution Atlas — Zipeng Wu</title><meta name="description" content="Explore institutional participation at NeurIPS 2026 through regional and country treemaps."><style>*{box-sizing:border-box}body{font:16px Arial,sans-serif;color:#173249;background:#f7f9fc;margin:0}header{padding:28px;max-width:1300px;margin:auto}h1{font-size:32px}a{color:#245b86}.links,.controls{display:flex;gap:16px;flex-wrap:wrap;align-items:center}.controls{padding-top:24px}select,input,button{font:inherit;padding:10px;border:1px solid #bdcdd9;border-radius:5px;background:white;color:#173249}.frame{overflow:auto;padding:20px}.chart{width:1200px;margin:auto}.chart svg{width:100%;height:auto}.institution.dim{opacity:.15}.institution:hover rect{stroke:#eb9b35;stroke-width:12}footer{max-width:1200px;margin:28px auto;padding:24px;line-height:1.6}#detail{padding:18px;background:#e6eef4;margin:0 28px}summary{cursor:pointer;font-weight:bold}</style>
<header><h1>NeurIPS 2026 Institution Atlas</h1><p>Explore paper participation across institutions, regions and countries.</p><div class="links"><a href="https://github.com/ZipengWu365">GitHub · ZipengWu365</a><a href="https://zipengwu365.github.io/">Academic homepage</a><a href="README.md">Methods and data notes</a></div><div class="controls"><label>View <select id="view"></select></label><label>Zoom <select id="zoom"><option value="1200">Fit overview</option><option value="2400">2×</option><option value="4800">4×</option><option value="7200">Original</option></select></label><input id="search" placeholder="Search an institution" aria-label="Search an institution"><button id="clear">Clear</button><a id="download">Download SVG</a><a id="csv">Download data</a></div></header><div id="detail">Select a view, then click an institution for its full name and paper count.</div><div class="frame"><div class="chart" id="chart"></div></div><footer><details><summary>How to interpret the charts</summary><p>Areas show institution–paper counts. Each paper counts once for each associated institution; a collaborative paper may contribute to several institutions. These charts are not official conference rankings.</p><p>Countries use institutional or corporate operational bases, not individual author locations. China includes mainland China, Hong Kong, Macao and Taiwan. ByteDance is assigned to China by convention. Unresolved country assignments are excluded from country-specific charts.</p><p>At most 200 institutions are displayed in each view. Equal counts at the cutoff are ordered alphabetically. Source labels with confirmed aliases were merged using the union of paper IDs. Original labels and merge records are retained in the data files. Short display names are used on posters; full names are available here and in the CSV files.</p><p>Source: supplied NeurIPS 2026 institution statistics workbook, snapshot 26 September 2026, covering 9,006 poster records. Missing and unverified affiliations remain; country assignment is a curated working classification.</p></details></footer><script>const views=VIEWS_JSON;const select=document.querySelector('#view'),chart=document.querySelector('#chart'),input=document.querySelector('#search');for(const v of views){const o=document.createElement('option');o.value=v.id;o.textContent=v.title+' ('+v.count+')';select.append(o)}function search(){const q=input.value.trim().toLowerCase();chart.querySelectorAll('.institution').forEach(g=>g.classList.toggle('dim',!g.dataset.name.toLowerCase().includes(q)))}function render(){const v=views.find(v=>v.id===select.value);chart.innerHTML=v.svg;document.querySelector('#download').href='assets/'+v.id+'.svg';document.querySelector('#download').download=v.filename+'.svg';document.querySelector('#csv').href='data/'+v.id+'.csv';chart.querySelectorAll('.institution').forEach(g=>{g.onclick=()=>document.querySelector('#detail').textContent=g.querySelector('title').textContent});search()}select.onchange=render;input.oninput=search;document.querySelector('#zoom').onchange=e=>chart.style.width=e.target.value+'px';document.querySelector('#clear').onclick=()=>{input.value='';search()};render();</script></html>'''
htmlpage=htmlpage.replace('VIEWS_JSON',json.dumps(manifest,ensure_ascii=False).replace('<','\\u003c'))
(REPO/'index.html').write_text(htmlpage,encoding='utf-8')
(REPO/'.nojekyll').write_text('',encoding='utf-8')
# The included data files already reside in data/.
summary=[{k:v for k,v in m.items() if k!='svg'} for m in manifest]
(OUT/'manifest.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
# A visual index for checking every poster without opening twelve large files.
sheet=Image.new('RGB',(1800,4*850),'white');sd=ImageDraw.Draw(sheet)
for i,m in enumerate(manifest):
 thumb=Image.open(POSTERS/(m['filename']+'_preview.jpg'));thumb.thumbnail((570,760))
 x=(i%3)*600+15;y=(i//3)*850
 sheet.paste(thumb,(x,y));sd.text((x,y+770),m['title'],font=font(22,True),fill='#173249')
sheet.save(POSTERS/'series_overview.jpg',quality=92)
