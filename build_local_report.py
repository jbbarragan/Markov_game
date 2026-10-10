"""Renderizador mínimo para la copia local del reporte; GitHub usa Jekyll."""
from pathlib import Path
import re
import html
root=Path(__file__).resolve().parent
pages=['index','modelo','aprendizaje','laboratorio']
titles=['Reporte','Modelo matemático','Aprendizaje en Python','Laboratorio']
def inline(s):
    s=re.sub(r'\{\{\s*[\'\"]([^\'\"]+)[\'\"]\s*\|\s*relative_url\s*\}\}',lambda m:'docs/game-v5/index.html' if '/game-v5/' in m[1] else '#'+m[1].strip('/'),s)
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
css=(root/'docs/report-v5.css').read_text()
nav=''.join(f'<a href="#{p}">{i+1:02} &nbsp; {t}</a>' for i,(p,t) in enumerate(zip(pages,titles)))
body=''.join(f'<section id="{p}">'+render((root/'docs'/f'{p}.md').read_text())+'</section>' for p in pages)
script=(root/'docs/report-v5.js').read_text()
(root/'reporte-local.html').write_text(f'<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Can Finder 5000 · Reporte</title><style>{css}</style></head><body><nav><span class="badge">IBERO / PRÁCTICA 05</span><strong>CAN FINDER<br>5000</strong>{nav}</nav><main>{body}</main><script>{script}</script></body></html>',encoding='utf-8')
print('reporte-local.html actualizado')
