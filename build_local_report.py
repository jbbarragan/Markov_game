"""Renderizador mínimo para la copia local del reporte; GitHub usa Jekyll."""
from pathlib import Path
import re
import html
root=Path(__file__).resolve().parent
pages=['index','modelo','aprendizaje','laboratorio','instalacion']
titles=['Reporte','Modelo matemático','Aprendizaje en Python','Laboratorio','Publicación']
def inline(s):
    s=re.sub(r'\{\{\s*[\'\"]([^\'\"]+)[\'\"]\s*\|\s*relative_url\s*\}\}',lambda m:'docs/game/index.html' if '/game/' in m[1] else '#'+m[1].strip('/'),s)
    s=re.sub(r'\{:[^}]+\}','',s)
    s=re.sub(r'`([^`]+)`',lambda m:'<code>'+html.escape(m[1])+'</code>',s)
    s=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',s)
    s=re.sub(r'\[([^]]+)\]\(([^)]+)\)',r'<a href="\2">\1</a>',s)
    return s

def render(text):
    text=re.sub(r'^---\n.*?\n---\n','',text,flags=re.S)
    out=[];code=False;table=False;listing=False
    for line in text.splitlines():
        if line.startswith('```'):
            if code:out.append('</code></pre>')
            else:out.append('<pre><code>')
            code=not code;continue
        if code:out.append(html.escape(line)+'\n');continue
        if table and not line.startswith('|'):out.append('</tbody></table></div>');table=False
        if listing and not re.match(r'^(?:- |\d+\. )',line):out.append('</ul>');listing=False
        if not line.strip():continue
        if line.startswith('|'):
            if re.match(r'^\|[\s:|\-]+$',line):continue
            cells=line.strip('|').split('|')
            if not table:out.append('<div class="table-wrap"><table><tbody>');table=True
            out.append('<tr>'+''.join('<td>'+inline(c.strip())+'</td>' for c in cells)+'</tr>');continue
        h=re.match(r'^(#{1,6}) (.*)',line)
        if h:out.append(f'<h{len(h[1])}>{inline(h[2])}</h{len(h[1])}>');continue
        li=re.match(r'^(?:- |\d+\. )(.*)',line)
        if li:
            if not listing:out.append('<ul>');listing=True
            out.append('<li>'+inline(li[1])+'</li>');continue
        if line.startswith('<'):out.append(inline(line));continue
        out.append('<p>'+inline(line)+'</p>')
    if listing:out.append('</ul>')
    if table:out.append('</tbody></table></div>')
    return '\n'.join(out)
css='''*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#fafaf7;color:#273b40;font:16px/1.75 system-ui,sans-serif}nav{position:fixed;width:245px;height:100vh;background:#eeefe8;padding:35px 25px;border-right:1px solid #d5dbd2}nav strong{font:700 22px monospace;display:block;margin:20px 0 35px}nav a{display:block;font-size:14px;text-decoration:none;margin:14px 0;color:inherit}main{margin-left:245px;max-width:1180px;padding:40px 55px}section{padding:5px 0 45px;border-bottom:1px solid #d3dcd6;scroll-margin-top:20px}h1{font-size:42px;line-height:1.2;letter-spacing:-1.5px;margin-bottom:18px}h2{font-size:26px;line-height:1.35;margin:25px 0 18px}h3{font-size:20px;margin-top:32px}a{color:#1c786f}pre{padding:20px;background:#eaf0ea;overflow:auto;font-size:13px;border-radius:6px}code{font-size:13px}table{border-collapse:collapse;width:100%;font-size:14px}td{border:1px solid #ccd7d0;padding:10px 12px;vertical-align:top}tr:first-child{font-weight:700;background:#e6eee6}.table-wrap{overflow:auto}.cf-kicker{font:12px monospace;letter-spacing:2px;color:#687d6c}.cf-hero{padding:25px;border:1px solid #b9c8bc;border-left:5px solid #bd9139;background:linear-gradient(120deg,#f1eddd,#dfebe2);margin:30px 0;border-radius:7px}.cf-tags{font:12px monospace;color:#516b5b}.cf-game{width:100%;height:2000px;border:0;border-radius:8px}.badge{font:12px monospace;color:#98742b}button{border:1px solid #86958a;background:transparent;padding:10px 14px;border-radius:5px;color:inherit;cursor:pointer}body.dark{background:#152129;color:#e1e7df}body.dark nav{background:#1c2b33;border-color:#43555a}body.dark a{color:#8fd0b8}body.dark pre,body.dark tr:first-child{background:#243840}body.dark .cf-hero{background:#293d3c}body.dark td{border-color:#516263}body.dark .cf-tags,body.dark .cf-kicker{color:#b1c4b4}@media(max-width:850px){nav{position:static;width:100%;height:auto;padding:15px 22px}nav strong{margin:5px 0}nav a{display:inline-block;margin:5px 12px 5px 0}main{margin:0;padding:25px 20px}h1{font-size:34px}}@media print{nav,iframe,button{display:none!important}main{margin:0;padding:0;max-width:none}body{font-size:11px}section{break-before:page}section:first-child{break-before:auto}pre,table,.cf-hero{break-inside:avoid}}'''
nav=''.join(f'<a href="#{p}">{i+1:02} &nbsp; {t}</a>' for i,(p,t) in enumerate(zip(pages,titles)))
body=''.join(f'<section id="{p}">'+render((root/'docs'/f'{p}.md').read_text())+'</section>' for p in pages)
script="""document.getElementById('theme').onclick=()=>{document.body.classList.toggle('dark');document.querySelectorAll('iframe').forEach(f=>f.contentWindow.postMessage({theme:document.body.classList.contains('dark')?'dark':'light'},location.origin));};"""
(root/'reporte-local.html').write_text(f'<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Can Finder 5000 · Reporte</title><style>{css}</style><link rel="stylesheet" href="docs/retro.css?v=4"></head><body><nav><span class="badge">IBERO / PRÁCTICA 05</span><strong>CAN FINDER<br>5000</strong>{nav}<button id="theme">☀ / ☾ Cambiar tema</button></nav><main>{body}</main><script>{script}</script></body></html>',encoding='utf-8')
print('reporte-local.html actualizado')
