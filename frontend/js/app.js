// frontend/app.js
async function api(path, opts={}) {
  const s = document.getElementById('summary');
  try {
    const res = await fetch(path, {headers:{'Content-Type':'application/json'}, ...opts});
    const data = await res.json().catch(()=> ({}));
    if(!res.ok) throw new Error(data?.detail || res.statusText);
    s.classList.add('hidden'); s.textContent=''; return data;
  } catch(e){ s.textContent='Fehler: '+e.message; s.classList.remove('hidden'); throw e; }
}

async function refreshIdeas(){
  const {items} = await api('/api/v1/ideas?limit=20&order=desc');
  const tbody = document.getElementById('tbl-ideas');
  if (tbody) {
    tbody.innerHTML = items.map(it => `<tr><td>${it.id}</td><td>${it.chain}</td><td>${it.amount}</td><td>${it.state}</td><td><button id="btn-strategy" data-id="${it.id}">Strategie</button> <button id="btn-schedule" data-id="${it.id}">Einplanen</button></td></tr>`).join('');
  }
}

document.addEventListener('click', async (ev)=>{
  const t = ev.target;
  if(t.matches('#btn-idea')){ await api('/api/v1/ideas/generate',{method:'POST',body:JSON.stringify({risk:3,asset:'SOL'})}); await refreshIdeas(); }
  if(t.matches('#btn-test1')){ const r=await api('/api/v1/tests/run/basic_flow',{method:'POST'}); alert('Report: '+r.report_path); }
  if(t.matches('#btn-balance')){ const r=await api('/api/v1/wallet/balance'); document.querySelector('#wallet-balance').textContent=r.balance; }
  if(t.matches('#btn-strategy')){ const id = t.getAttribute('data-id'); await api(`/api/v1/ideas/${id}/analyze`,{method:'POST'}); await refreshIdeas(); }
  if(t.matches('#btn-schedule')){ const id = t.getAttribute('data-id'); await api(`/api/v1/ideas/${id}/to_orders`,{method:'POST'}); await refreshIdeas(); }
});