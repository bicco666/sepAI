async function api(path, opts={}){
  const s = document.getElementById('summary');
  try{
    const res = await fetch(path, {headers:{'Content-Type':'application/json'}, ...opts});
    const data = await res.json().catch(()=> ({}));
    if(!res.ok){ throw new Error(data?.detail || res.statusText); }
    s.classList.add('hidden'); s.textContent=''; return data;
  }catch(e){ s.textContent='Fehler: '+e.message; s.classList.remove('hidden'); throw e; }
}

async function refreshLists(){
  try{
    const ideas = await api('/api/v1/ideas');
    const orders = await api('/api/v1/orders');
    const history = await api('/api/v1/history');
    renderList('ideas', ideas.items.map(i=>`${i.id} • ${i.asset}/${i.chain} • ${i.state}`));
    renderList('orders', orders.items.map(o=>`${o.id} • ${o.asset}/${o.chain} • ${o.state}${o.txid? ' • tx='+o.txid:''}`));
    renderList('history', history.items.map(h=>`${h.ts} • ${h.actor} • ${h.event}${h.ref? ' • '+h.ref:''}`));
  }catch{ /* summary already shows error */ }
}

function renderList(id, lines){
  const el = document.getElementById(id);
  el.innerHTML = (lines && lines.length)
    ? lines.map(l=>`<li class=\"border-b border-gray-700/50 pb-1\">${l}</li>`).join('')
    : '<li class=\"text-gray-500\">–</li>';
}

document.addEventListener('click', async (ev)=>{
  const t = ev.target;
  if(t.id==='btn-system'){
    const r = await api('/api/v1/system/run',{method:'POST'});
    await refreshLists();
    document.getElementById('report-content').textContent = 'Report: '+ r.report_path + '\n\nSchritte:\n- ' + r.steps.join('\n- ');
  }
  if(t.id==='btn-balance'){
    const r = await api('/api/v1/wallet/balance');
    document.getElementById('wallet-balance').textContent = r.balance;
  }
  if(t.id==='btn-last-report'){
    const r = await api('/api/v1/reports/latest');
    document.getElementById('report-content').textContent = r.found ? r.content : 'Kein Report gefunden.';
  }
});

refreshLists();
