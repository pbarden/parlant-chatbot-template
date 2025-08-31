/*
  Web Component: <parlant-chat>
  - Talks to YOUR FastAPI backend, not Parlant directly
  - Backend exposes:
      POST   /api/v1/public/sessions/{client_slug}
      POST   /api/v1/public/sessions/resume/{client_slug}
      POST   /api/v1/public/events/send/{public_token}
      GET    /api/v1/public/events/stream/{public_token}?min_offset=0
*/

function _qs(root, sel) { return root.querySelector(sel); }
function _escape(s) { const d=document.createElement('div'); d.textContent=String(s); return d.innerHTML; }
function _debounce(fn, wait){ let t; return (...a)=>{ clearTimeout(t); t=setTimeout(()=>fn(...a), wait); }; }

class ParlantChatWc extends HTMLElement {
  static get observedAttributes(){ return ['server','client-slug','agent-id','open','float','position','title']; }
  constructor(){
    super();
    this.attachShadow({mode:'open'});
    this._server=''; this._clientSlug=''; this._agentId='';
    this._publicToken=null; this._sessionId=null; this._lastOffset=0;
    this._open=false; this._float=false; this._position='bottom-right'; this._title='Chat';
    this._building=false; this._polling=false;
    this._render();
  }
  connectedCallback(){
    this._readAttrs();
    this._bind();
    this._autostart();
  }
  disconnectedCallback(){ this._stop(); }
  attributeChangedCallback(n,o,v){ if(o===v) return; this._readAttrs(); this._applyState(); }

  _readAttrs(){
    this._server=this.getAttribute('server')||this._server;
    this._clientSlug=this.getAttribute('client-slug')||this._clientSlug;
    this._agentId=this.getAttribute('agent-id')||this._agentId;
    this._open=this.hasAttribute('open');
    this._float=this.hasAttribute('float');
    this._position=this.getAttribute('position')||this._position;
    this._title=this.getAttribute('title')||this._title;
  }

  _render(){
    const style=document.createElement('style');
    style.textContent = `@import url('/static/chatbot.css');`;
    const wrap=document.createElement('div');
    wrap.className='parlant-wrapper';
    wrap.innerHTML=`
      <button class="parlant-popup">Chat</button>
      <div class="parlant-chat hidden">
        <div class="parlant-header">
          <div class="parlant-title"></div>
          <button class="parlant-popup" data-action="min">–</button>
        </div>
        <div class="parlant-status" id="status"></div>
        <div class="parlant-msgs" id="msgs"></div>
        <div class="parlant-compose">
          <textarea class="parlant-input" id="input" rows="1" placeholder="Type a message…"></textarea>
          <button class="parlant-send" id="send">Send</button>
        </div>
      </div>`;
    this.shadowRoot.append(style, wrap);
  }

  _bind(){
    this._btn=this.shadowRoot.querySelector('.parlant-popup');
    this._chat=this.shadowRoot.querySelector('.parlant-chat');
    this._titleEl=this.shadowRoot.querySelector('.parlant-title');
    this._status=this.shadowRoot.querySelector('#status');
    this._msgs=this.shadowRoot.querySelector('#msgs');
    this._input=this.shadowRoot.querySelector('#input');
    this._send=this.shadowRoot.querySelector('#send');

    this._btn.addEventListener('click', ()=>{ this._open=true; this._applyState(); });
    this.shadowRoot.querySelector('[data-action="min"]').addEventListener('click', ()=>{ this._open=false; this._applyState(); });
    this._send.addEventListener('click', ()=> this._sendMsg());
    this._input.addEventListener('keydown', (e)=>{ if(e.key==='Enter'&&!e.shiftKey){ e.preventDefault(); this._sendMsg(); }});

    const autoresize=_debounce(()=>{ this._input.style.height='auto'; this._input.style.height=Math.min(this._input.scrollHeight,140)+'px'; },0);
    this._input.addEventListener('input', autoresize);
  }

  _applyState(){
    this._titleEl.textContent=this._title;
    if(this._open){ this._chat.classList.remove('hidden'); this._btn.classList.add('hidden'); }
    else { this._chat.classList.add('hidden'); this._btn.classList.remove('hidden'); }
  }

  async _autostart(){
    if(!this._server || !this._clientSlug || !this._agentId) return;
    const persisted=JSON.parse(localStorage.getItem(this._storageKey())||'null');
    if(persisted){ this._publicToken=persisted.public_token; this._sessionId=persisted.session_id; this._lastOffset=persisted.last_offset||0; }
    if(!this._publicToken){ await this._createSession(); }
    this._loop();
  }

  _storageKey(){ return `parlant:public:${this._server}:${this._clientSlug}:${this._agentId}`; }

  async _createSession(){
    const userId = this._getOrSetAnonUserId();
    const r = await fetch(`${this._server}/public/sessions/${encodeURIComponent(this._clientSlug)}`, {
      method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ agent_id: this._agentId, user_id: userId })
    });
    if(!r.ok) throw new Error('session_create_failed');
    const data = await r.json();
    this._publicToken=data.public_token; this._sessionId=data.session_id; this._persist();
  }

  _persist(){ localStorage.setItem(this._storageKey(), JSON.stringify({ public_token:this._publicToken, session_id:this._sessionId, last_offset:this._lastOffset })); }

  _getOrSetAnonUserId(){
    const k=`parlant:user`; let v=localStorage.getItem(k); if(!v){ v=crypto.randomUUID(); localStorage.setItem(k,v); } return v;
  }

  async _sendMsg(){
    const text=this._input.value.trim(); if(!text) return;
    this._input.value=''; this._input.style.height='38px';
    const r = await fetch(`${this._server}/public/events/send/${encodeURIComponent(this._publicToken)}`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ message: text }) });
    if(!r.ok){ this._status.textContent='Send failed'; return; }
  }

  async _loop(){
    if(this._polling) return; this._polling=true;
    while(this._polling){
      try {
        const url = `${this._server}/public/events/stream/${encodeURIComponent(this._publicToken)}?min_offset=${this._lastOffset}`;
        const r = await fetch(url);
        if(!r.ok){ this._status.textContent='Reconnecting…'; await new Promise(r=>setTimeout(r,1200)); continue; }
        const evs = await r.json();
        let maxOff=this._lastOffset;
        for(const ev of evs){
          if(ev.kind==='status'){ this._status.textContent=(ev?.data?.status)||''; }
          else if(ev.kind==='message'){ this._append(ev); }
          const n=(typeof ev.offset==='number'?ev.offset:0)+1; maxOff=Math.max(maxOff,n);
        }
        if(maxOff>this._lastOffset){ this._lastOffset=maxOff; this._persist(); }
      } catch(e){ this._status.textContent='Reconnecting…'; await new Promise(r=>setTimeout(r,1200)); }
    }
  }

  _append(ev){
    const atBottom=Math.abs(this._msgs.scrollHeight - this._msgs.scrollTop - this._msgs.clientHeight) < 8;
    const div=document.createElement('div');
    div.className='parlant-msg';
    const role=ev.source;
    if(role==='customer') div.classList.add('customer');
    else div.classList.add('agent');
    div.innerHTML=_escape(ev?.data?.message||'');
    this._msgs.appendChild(div);
    if(atBottom) this._msgs.scrollTop=this._msgs.scrollHeight;
  }

  _stop(){ this._polling=false; }
}

customElements.define('parlant-chat', ParlantChatWc);