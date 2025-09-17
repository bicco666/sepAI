type ApiResponse = Record<string, any>;

async function api(path: string, opts: RequestInit = {}): Promise<ApiResponse> {
  const summary = document.getElementById("summary")!;
  try {
    const res = await fetch(path, { headers: { "Content-Type": "application/json" }, ...opts });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data?.detail || res.statusText);
    summary.classList.add("hidden");
    summary.textContent = "";
    return data;
  } catch (e: any) {
    summary.textContent = "Fehler: " + e.message;
    summary.classList.remove("hidden");
    throw e;
  }
}

function renderList(id: string, lines: string[]) {
  const el = document.getElementById(id)!;
  el.innerHTML = lines.length
    ? lines.map((l) => `<li class="border-b border-gray-700/50 pb-1">${l}</li>`).join("")
    : '<li class="text-gray-500">–</li>';
}

async function refreshLists() {
  const ideas = await api("/api/v1/ideas");
  const orders = await api("/api/v1/orders");
  const history = await api("/api/v1/history");
  renderList("ideas", ideas.items.map((i: any) => `${i.id} • ${i.asset}/${i.chain} • ${i.state}`));
  renderList("orders", orders.items.map((o: any) => `${o.id} • ${o.asset}/${o.chain} • ${o.state}`));
  renderList("history", history.items.map((h: any) => `${h.ts} • ${h.actor} • ${h.event}`));
}

function setup() {
  document.getElementById("btn-system")!.addEventListener("click", async () => {
    const r = await api("/api/v1/system/run", { method: "POST" });
    await refreshLists();
    (document.getElementById("report-content") as HTMLElement).textContent =
      `Report: ${r.report_path}\n\nSchritte:\n- ${r.steps.join("\n- ")}`;
  });

  document.getElementById("btn-balance")!.addEventListener("click", async () => {
    const r = await api("/api/v1/wallet/balance");
    (document.getElementById("wallet-balance") as HTMLElement).textContent = r.balance;
  });

  document.getElementById("btn-last-report")!.addEventListener("click", async () => {
    const r = await api("/api/v1/reports/latest");
    (document.getElementById("report-content") as HTMLElement).textContent = r.found
      ? r.content
      : "Kein Report gefunden.";
  });

  refreshLists();
}

document.addEventListener("DOMContentLoaded", setup);
