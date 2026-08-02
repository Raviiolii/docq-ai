#!/usr/bin/env python3
"""DocQ — Self-hosted AI Document Q&A.
One-time fee, no SaaS. Live demo: https://fair-rats-wait.loca.lt
Usage: export DEEPSEEK_KEY="sk-..." && python3 demo.py
"""
import json, os, sys
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from openai import OpenAI

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_KEY", "")
if not DEEPSEEK_KEY:
    print("ERROR: Set DEEPSEEK_KEY environment variable")
    print("Get your free key: https://platform.deepseek.com")
    sys.exit(1)

client = OpenAI(api_key=DEEPSEEK_KEY, base_url="https://api.deepseek.com")
DOC = """ACME CORP - EMPLOYEE HANDBOOK
CORE VALUES: Innovation First, Customer Obsession, Radical Transparency.
VACATION: 25 days PTO/year, unlimited sick leave, no approval for <3 days.
REMOTE WORK: Hybrid-first (2 office/3 remote), $2000/year home office stipend.
BENEFITS: 100% health coverage, 401k 6% match, $5000/year learning budget.
CONTACT: hr@acmecorp.com"""

DOC_QA_HTML = r"""<!DOCTYPE html><html lang="en" data-theme="signal">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>DocQ - AI Document Assistant</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Instrument+Serif:ital@1&display=swap" rel="stylesheet">
<style>
:root{--font:"Space Grotesk",system-ui,sans-serif;--font-accent:"Instrument Serif",serif;--bg:#edf3f8;--surface:rgba(252,253,255,0.84);--surface-glass:rgba(248,251,255,0.78);--line:rgba(46,73,104,0.12);--text:#18222d;--text2:#5f6f7f;--text3:#8a99aa;--accent:#1f5a8b;--accent-soft:#80abd8;--shadow:0 26px 90px rgba(27,48,73,0.14);--radius:28px;--radius-sm:14px;--gap:32px;--gap-sm:18px;--ease:320ms cubic-bezier(0.22,1,0.36,1)}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:var(--font);background:linear-gradient(175deg,#f5f9fd,#dfeaf3);color:var(--text);min-height:100vh;line-height:1.6}
.app{max-width:1180px;margin:0 auto;padding:40px 32px 60px}
.nav{display:flex;align-items:center;justify-content:space-between;padding:20px 28px;margin-bottom:var(--gap);background:var(--surface-glass);backdrop-filter:blur(24px);border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow)}
.nav-brand{display:flex;align-items:center;gap:10px;font-weight:700;font-size:1.1rem}
.nav-status{font-size:.75rem;font-weight:600;color:#2d7d5f;padding:6px 14px;border-radius:999px;background:rgba(45,125,95,.1)}
.hero{margin-bottom:var(--gap)}
.hero h1{font-size:clamp(2rem,5vw,3.2rem);font-weight:700;line-height:1.15;letter-spacing:-.03em;margin-bottom:12px}
.hero h1 em{font-family:var(--font-accent);font-style:italic;color:var(--accent);font-weight:400}
.hero p{font-size:1.1rem;color:var(--text2);max-width:520px}
.grid{display:grid;grid-template-columns:340px 1fr;gap:var(--gap);align-items:start}
@media(max-width:900px){.grid{grid-template-columns:1fr}}
.sidebar{position:sticky;top:32px}
.doc-card{padding:28px;background:var(--surface-glass);backdrop-filter:blur(24px);border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow)}
.doc-card .label{font-size:.65rem;font-weight:700;text-transform:uppercase;letter-spacing:.15em;color:var(--accent);margin-bottom:16px}
.doc-card .doctitle{font-size:.95rem;font-weight:600;margin-bottom:18px}
.doc-card .docbody{font-size:.8rem;line-height:1.75;color:var(--text2);white-space:pre-wrap;max-height:50vh;overflow-y:auto}
.chat-card{padding:32px;background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow)}
.chat-messages{display:flex;flex-direction:column;gap:var(--gap-sm);min-height:300px;max-height:55vh;overflow-y:auto;margin-bottom:var(--gap-sm)}
.msg{max-width:85%;animation:in .4s var(--ease)}
@keyframes in{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.msg.assistant .bubble{padding:18px 22px;background:#fff;border:1px solid var(--line);border-radius:20px 20px 20px 4px;font-size:.9rem;line-height:1.6}
.msg.assistant .bubble strong{color:var(--accent)}
.msg.user{align-self:flex-end}
.msg.user .bubble{padding:16px 22px;background:var(--accent);color:#fff;border-radius:20px 20px 4px 20px;font-size:.9rem}
.typing{padding:18px 22px;background:#fff;border:1px solid var(--line);border-radius:20px 20px 20px 4px;width:fit-content;display:flex;gap:5px}
.typing span{width:6px;height:6px;border-radius:50%;background:var(--accent-soft);animation:wave 1.4s ease infinite}
.typing span:nth-child(2){animation-delay:.2s}.typing span:nth-child(3){animation-delay:.4s}
@keyframes wave{0%,60%,100%{transform:translateY(0);opacity:.3}30%{transform:translateY(-5px);opacity:1}}
.chips{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:14px}
.chips button{padding:7px 16px;font-size:.75rem;font-weight:500;border-radius:999px;border:1px solid var(--line);background:transparent;color:var(--text2);cursor:pointer;font-family:inherit;transition:all .2s var(--ease)}
.chips button:hover{border-color:var(--accent);color:var(--accent)}
.input-row{display:flex;gap:10px}
.input-row input{flex:1;padding:14px 18px;border-radius:var(--radius-sm);border:1px solid var(--line);background:#fff;color:var(--text);font-size:.9rem;font-family:inherit;outline:none;transition:border-color .2s var(--ease)}
.input-row input:focus{border-color:var(--accent);box-shadow:0 0 0 4px rgba(31,90,139,.08)}
.input-row button{padding:14px 24px;border-radius:var(--radius-sm);border:none;background:var(--accent);color:#fff;font-weight:600;font-size:.9rem;cursor:pointer;font-family:inherit;transition:all .2s var(--ease)}
.input-row button:hover{background:#1a4f7a;transform:translateY(-1px)}
.empty{display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:60px 20px;gap:14px;color:var(--text3)}
.empty .icon{font-size:2.5rem;opacity:.7}
.empty h3{font-size:1.1rem;font-weight:600;color:var(--text)}
</style></head><body>
<div class="app">
<nav class="nav"><div class="nav-brand">DocQ - Portfolio Demo</div><div class="nav-status">Live</div></nav>
<div class="hero"><h1>Your documents, <em>intelligent.</em></h1><p>Ask anything. Get answers grounded in your own knowledge base.</p></div>
<div class="grid">
<aside class="sidebar"><div class="doc-card"><div class="label">Sample Document</div><div class="doctitle">Company Policy</div><div class="docbody">{doc}</div></div></aside>
<main><div class="chat-card"><div class="chat-messages" id="chat"><div class="empty"><div class="icon">+</div><h3>Ask anything</h3><p>Try the suggested questions below.</p></div></div>
<div class="chips"><button onclick="askThis('What is the vacation policy?')">Vacation</button><button onclick="askThis('How does remote work function?')">Remote Work</button><button onclick="askThis('What are the core values?')">Values</button><button onclick="askThis('Summarize the document')">Summarize</button></div>
<div class="input-row"><input id="q" placeholder="Ask about the document..." onkeydown="if(event.key==='Enter')ask()" autofocus><button onclick="ask()">Ask</button></div></div></main>
</div></div>
<script>
function askThis(t){document.getElementById('q').value=t;ask()}
async function ask(){const q=document.getElementById('q').value.trim();if(!q)return;const chat=document.getElementById('chat'),w=chat.querySelector('.empty');if(w)w.remove();chat.innerHTML+='<div class="msg user"><div class="bubble">'+q+'</div></div>';chat.innerHTML+='<div class="typing"><span></span><span></span><span></span></div>';document.getElementById('q').value='';chat.scrollTop=chat.scrollHeight;try{const r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});const d=await r.json();chat.removeChild(chat.lastChild);const a=d.answer.replace(/\\n/g,'<br>').replace(/\\*\\*(.*?)\\*\\*/g,'<strong>$1</strong>');chat.innerHTML+='<div class="msg assistant"><div class="bubble">'+a+'</div></div>'}catch(e){chat.removeChild(chat.lastChild);chat.innerHTML+='<div class="msg assistant"><div class="bubble">Error connecting.</div></div>'}chat.scrollTop=chat.scrollHeight}
</script></body></html>"""

class DocQHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.end_headers()
        self.wfile.write(DOC_QA_HTML.replace("{doc}", DOC).encode())
    def do_POST(self):
        if self.path == "/ask":
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length",0))))
            q = body.get("question","")
            try:
                r = client.chat.completions.create(model="deepseek-chat", messages=[
                    {"role":"system","content":f"Answer based ONLY on this document. Be concise. Use **bold** for key terms.\n\nDOCUMENT:\n{DOC}"},
                    {"role":"user","content":q}], temperature=0.2, max_tokens=500)
                a = r.choices[0].message.content
            except Exception as e: a = f"Error: {e}"
            self.send_response(200); self.send_header("Content-Type","application/json"); self.end_headers()
            self.wfile.write(json.dumps({"answer":a}).encode())
    def log_message(self,f,*a): pass

def serve(port, handler):
    s = ThreadingHTTPServer(("0.0.0.0", port), handler)
    print(f"  http://localhost:{port}")
    s.serve_forever()

if __name__ == "__main__":
    print("=" * 44)
    print("  DocQ - AI Document Q&A")
    print("  http://localhost:8080")
    print("=" * 44)
    serve(8080, DocQHandler)
