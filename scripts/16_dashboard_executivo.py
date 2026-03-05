"""
╔══════════════════════════════════════════════════════════════════╗
║         DIA 28 — DASHBOARD EXECUTIVO INTERATIVO                 ║
║         Semana 5 · Projeto MDM Supply Chain                     ║
╚══════════════════════════════════════════════════════════════════╝

OBJETIVO:
  - Gerar dashboard executivo em HTML interativo
  - Consolidar todos os KPIs e métricas do projeto
  - Criar visualização navegável para apresentar a gestores
  - Exportar também PNG de alta resolução para relatórios

📖 CONCEITO RÁPIDO — DASHBOARD vs RELATÓRIO
─────────────────────────────────────────────────────
  Relatório (PDF/PPTX): fotografia de um momento.
  Você olha, entende, arquivo.

  Dashboard (HTML/Power BI): painel vivo.
  Você navega, filtra, explora.

  Um gestor prefere o dashboard porque consegue
  responder suas próprias perguntas sem depender
  de você para gerar um novo relatório.
─────────────────────────────────────────────────────
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import os, json, warnings
from datetime import datetime
warnings.filterwarnings('ignore')

print("\n" + "="*68)
print("  DIA 28 — DASHBOARD EXECUTIVO")
print("  Semana 5 · Projeto MDM Supply Chain")
print("="*68)

# ─────────────────────────────────────────────────────────────────
# 1. CARREGAR E PREPARAR DADOS
# ─────────────────────────────────────────────────────────────────
CSV = 'E:/importantee/carreira/PROJETO MDM/mdm-supply-chain-project/data/raw/materiais_raw.csv'
df = None
for p in [CSV, 'data/raw/materiais_raw.csv', '../data/raw/materiais_raw.csv']:
    if os.path.exists(p):
        df = pd.read_csv(p)
        print(f"\n✅ CSV: {p} ({len(df):,} registros)")
        break
if df is None:
    raise FileNotFoundError('CSV não encontrado!')

os.makedirs('data/processed', exist_ok=True)
os.makedirs('visualizations', exist_ok=True)
ts   = datetime.now().strftime('%Y%m%d_%H%M%S')
HOJE = pd.Timestamp('2026-03-04')

df['valor']       = df['preco_unitario'] * df['estoque_atual']
df['ultima_dt']   = pd.to_datetime(df['ultima_movimentacao'])
df['dias_parado'] = (HOJE - df['ultima_dt']).dt.days.fillna(9999).astype(int)
df['ncm_str']     = df['ncm'].apply(
    lambda x: str(int(x)) if pd.notna(x) and x != 0 else '')
df['ncm_ok']      = df['ncm_str'].apply(lambda x: len(x) == 8 and x.isdigit())

CATS = {'Acessórios','EPI','Eletrônico','Elétrico','Embalagem','Escritório',
        'Ferramentas','Fixação','Hidráulico','Limpeza','Lubrificante',
        'Mecânico','Peças','Pneumático','Químico'}

# ABC
df_abc = df.drop_duplicates('codigo_material').sort_values('valor', ascending=False).copy()
df_abc['pct'] = df_abc['valor'].cumsum() / df_abc['valor'].sum() * 100
df_abc['abc'] = df_abc['pct'].apply(lambda x: 'A' if x <= 80 else ('B' if x <= 95 else 'C'))
df = df.merge(df_abc[['codigo_material','abc']], on='codigo_material', how='left')
df['abc'] = df['abc'].fillna('C')

abc_counts   = df['abc'].value_counts()
status_counts = df['status'].value_counts()
cat_valor    = df.groupby('categoria')['valor'].sum().sort_values(ascending=False)
cat_count    = df.groupby('categoria').size()
cat_ncm_pct  = df.groupby('categoria')['ncm_ok'].mean() * 100

# KPIs
kpis = {
    'completude':  100.0,
    'ncm':         round(df['ncm_ok'].mean() * 100, 1),
    'preco':       round((df['preco_unitario'] > 0).mean() * 100, 1),
    'fornecedor':  round(df['fornecedor_principal'].notna().mean() * 100, 1),
    'est_min':     round(df['estoque_minimo'].notna().mean() * 100, 1),
    'score_pond':  92.8,
}

savings = {
    'Semana 1': 18.06,
    'Semana 2': 20.70,
    'Semana 3':  6.74,
    'Semana 4':  0.00,
}

pipeline = {
    'entrada':   len(df),
    'aprovados': int(df['ncm_ok'].sum() & (df['preco_unitario'] > 0).sum()),
    'retidos':   0,
}
pipeline['aprovados'] = int((df['ncm_ok'] & (df['preco_unitario'] > 0)).sum())
pipeline['retidos']   = pipeline['entrada'] - pipeline['aprovados']

print(f"\n  KPIs calculados:")
for k, v in kpis.items():
    print(f"    {k:15} {v:.1f}")

# ─────────────────────────────────────────────────────────────────
# 2. DASHBOARD PNG — MATPLOTLIB
# ─────────────────────────────────────────────────────────────────
print("\n" + "-"*68)
print("  GERANDO DASHBOARD PNG...")

BG, PANEL = '#0B1220', '#111927'
BORDER, TEXT, MUTED = '#1E2D40', '#E2E8F0', '#64748B'
C = {
    'teal':   '#00C9B1', 'blue':   '#4A9EDB',
    'green':  '#34D399', 'red':    '#F87171',
    'amber':  '#FBB124', 'purple': '#A78BFA',
}

fig = plt.figure(figsize=(24, 16), facecolor=BG)
fig.suptitle('MDM Supply Chain — Dashboard Executivo  |  Março 2026',
             fontsize=19, color=TEXT, fontweight='bold', y=0.98)
gs  = GridSpec(3, 4, figure=fig, hspace=0.52, wspace=0.38,
               left=0.04, right=0.97, top=0.93, bottom=0.04)

def stl(ax):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=MUTED, labelsize=9)
    for sp in ax.spines.values(): sp.set_color(BORDER)
    ax.grid(color=BORDER, lw=0.5, alpha=0.6)
    ax.title.set_color(TEXT)
    ax.xaxis.label.set_color(MUTED)
    ax.yaxis.label.set_color(MUTED)
    return ax

# ── G1: Indicadores-chave (linha 1, 4 gauges) ────────────────────
gauge_data = [
    ('Completude\nGeral',  kpis['completude'], 95,  C['green']),
    ('NCM\nVálido',        kpis['ncm'],        100, C['red']),
    ('Acuracidade\nPreço', kpis['preco'],       95,  C['teal']),
    ('Score\nPonderado',   kpis['score_pond'],  85,  C['teal']),
]
for i, (lbl, val, meta, cor) in enumerate(gauge_data):
    ax = fig.add_subplot(gs[0, i])
    ax.set_facecolor(PANEL)
    ax.set_xlim(-1.2, 1.2); ax.set_ylim(-0.35, 1.25)
    ax.axis('off')
    theta = np.linspace(np.pi, 0, 200)
    ax.plot(np.cos(theta), np.sin(theta), color=BORDER, lw=14, solid_capstyle='round')
    pct = min(max(val / (meta * 1.05), 0), 1)
    tv  = np.linspace(np.pi, np.pi - pct * np.pi, 200)
    ax.plot(np.cos(tv), np.sin(tv), color=cor, lw=14, solid_capstyle='round')
    ax.text(0, 0.10, f'{val:.1f}%', ha='center', fontsize=21,
            fontweight='bold', color=cor, family='monospace')
    ax.text(0, -0.12, f'meta {meta:.0f}%', ha='center', fontsize=9, color=MUTED)
    ax.set_title(lbl, fontsize=11, pad=6)
    for sp in ax.spines.values(): sp.set_color(cor); sp.set_lw(1.5)

# ── G2: Savings por semana (linha 2, col 0-1) ────────────────────
ax2 = stl(fig.add_subplot(gs[1, :2]))
sem_labels = list(savings.keys())
sem_vals   = list(savings.values())
cum_vals   = np.cumsum(sem_vals)
cores_s    = [C['teal'], C['blue'], C['amber'], MUTED]
bars = ax2.bar(sem_labels, sem_vals, color=cores_s, alpha=0.85, width=0.55, zorder=3)
ax2_r = ax2.twinx()
ax2_r.plot(sem_labels, cum_vals, color=C['green'], marker='o',
           lw=2, ms=7, zorder=4, label='Acumulado')
ax2_r.set_ylabel('Acumulado R$M', color=C['green'], fontsize=9)
ax2_r.tick_params(colors=C['green'], labelsize=9)
ax2_r.set_ylim(0, 60)
for sp in ax2_r.spines.values(): sp.set_color(BORDER)
for b, v in zip(bars, sem_vals):
    if v > 0:
        ax2.text(b.get_x()+b.get_width()/2, v+0.3, f'R${v:.1f}M',
                 ha='center', color=TEXT, fontsize=9, fontweight='bold')
ax2.set_title('Savings por Semana  (R$ Milhões/ano)', fontsize=12, pad=8)
ax2.set_ylabel('Savings R$M')
ax2.set_ylim(0, 26)
ax2_r.legend(fontsize=9, facecolor=PANEL, labelcolor=TEXT, loc='upper left')

# ── G3: Status materiais (pizza) ─────────────────────────────────
ax3 = stl(fig.add_subplot(gs[1, 2]))
pv = [status_counts.get('Ativo', 0),
      status_counts.get('Bloqueado', 0),
      status_counts.get('Inativo', 0)]
pl = [f'Ativo\n{pv[0]:,}', f'Bloqueado\n{pv[1]:,}', f'Inativo\n{pv[2]:,}']
pc = [C['green'], C['red'], MUTED]
ax3.pie(pv, labels=pl, colors=pc, startangle=90, autopct='%1.0f%%',
        wedgeprops={'edgecolor': BG, 'lw': 2},
        textprops={'color': TEXT, 'fontsize': 9})
ax3.set_title('Status dos Materiais', fontsize=12, pad=8)
ax3.set_facecolor(PANEL)

# ── G4: Pipeline funil ───────────────────────────────────────────
ax4 = stl(fig.add_subplot(gs[1, 3]))
stages = ['Entrada', 'Aprovados', 'Auto', 'Supervisor', 'MDO']
vals4  = [3300, 2428, 1056, 1019, 353]
cores4 = [C['blue'], C['teal'], C['green'], C['amber'], C['amber']]
bars4  = ax4.barh(stages, vals4, color=cores4, alpha=0.85, height=0.6)
for b, v in zip(bars4, vals4):
    ax4.text(v+30, b.get_y()+b.get_height()/2, f'{v:,}',
             va='center', color=TEXT, fontsize=9, fontweight='bold')
ax4.set_xlim(0, 3800)
ax4.set_title('Pipeline de Aprovação', fontsize=12, pad=8)
ax4.invert_yaxis()

# ── G5: Valor por categoria (linha 3, col 0-1) ───────────────────
ax5 = stl(fig.add_subplot(gs[2, :2]))
top8_cats  = cat_valor.head(8)
cores_cat  = [C['teal'] if cat_ncm_pct.get(c, 0) >= 80 else
              (C['amber'] if cat_ncm_pct.get(c, 0) >= 70 else C['red'])
              for c in top8_cats.index]
bars5 = ax5.barh(range(len(top8_cats)), top8_cats.values / 1e6,
                 color=cores_cat, alpha=0.85, height=0.65)
ax5.set_yticks(range(len(top8_cats)))
ax5.set_yticklabels(top8_cats.index, fontsize=9)
ax5.invert_yaxis()
for b, v in zip(bars5, top8_cats.values):
    ax5.text(v/1e6+1, b.get_y()+b.get_height()/2,
             f'R${v/1e6:.0f}M', va='center', color=TEXT, fontsize=9)
ax5.set_title('Valor de Estoque por Categoria  (cor = % NCM OK)', fontsize=12, pad=8)
ax5.set_xlabel('R$ Milhões')
patches = [mpatches.Patch(color=C['teal'], label='NCM ≥80%'),
           mpatches.Patch(color=C['amber'],label='NCM 70-79%'),
           mpatches.Patch(color=C['red'],  label='NCM <70%')]
ax5.legend(handles=patches, fontsize=8, facecolor=PANEL, labelcolor=TEXT)

# ── G6: Curva ABC ────────────────────────────────────────────────
ax6 = stl(fig.add_subplot(gs[2, 2]))
abc_labels = ['A', 'B', 'C']
abc_vals   = [int(abc_counts.get(l, 0)) for l in abc_labels]
abc_pct    = [v/sum(abc_vals)*100 for v in abc_vals]
abc_cores  = [C['red'], C['amber'], C['green']]
bars6 = ax6.bar(abc_labels, abc_vals, color=abc_cores, alpha=0.85, width=0.55)
for b, v, p in zip(bars6, abc_vals, abc_pct):
    ax6.text(b.get_x()+b.get_width()/2, v+8, f'{v:,}\n({p:.0f}%)',
             ha='center', color=TEXT, fontsize=9, fontweight='bold')
ax6.set_title('Curva ABC — Materiais', fontsize=12, pad=8)
ax6.set_ylabel('Quantidade')

# ── G7: KPI gap chart ────────────────────────────────────────────
ax7 = stl(fig.add_subplot(gs[2, 3]))
kpi_names  = ['NCM\nVálido', 'Desc.\nPadron.', 'Fornecedor', 'Est.\nMínimo', 'Preço\nOK']
kpi_vals   = [kpis['ncm'], 73.0, kpis['fornecedor'], kpis['est_min'], kpis['preco']]
kpi_metas  = [100, 95, 90, 90, 95]
gaps       = [m - v for m, v in zip(kpi_metas, kpi_vals)]
cores_gap  = [C['red'] if g > 15 else (C['amber'] if g > 5 else C['green']) for g in gaps]
bars7 = ax7.bar(kpi_names, gaps, color=cores_gap, alpha=0.85, width=0.55)
for b, g, v in zip(bars7, gaps, kpi_vals):
    ax7.text(b.get_x()+b.get_width()/2, g+0.3, f'–{g:.0f}pp\n({v:.0f}%)',
             ha='center', color=TEXT, fontsize=8, fontweight='bold')
ax7.set_title('Gap para Meta (percentual pts)', fontsize=12, pad=8)
ax7.set_ylabel('Gap (pp)')

# Anotação total
fig.text(0.5, 0.005,
         f'Total R$ 1,83B  ·  3.300 materiais  ·  R$ 45,5M/ano savings  ·  Score Ponderado: 92,8/100  ·  Pipeline: 2.428 aprovados (73,6%)',
         ha='center', fontsize=9, color=MUTED)

out_png = f'visualizations/16_dashboard_executivo.png'
plt.savefig(out_png, dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print(f"\n  ✅ {out_png}")

# ─────────────────────────────────────────────────────────────────
# 3. GERAR DASHBOARD HTML INTERATIVO
# ─────────────────────────────────────────────────────────────────
print("-"*68)
print("  GERANDO DASHBOARD HTML INTERATIVO...")

# Preparar dados para o HTML
cat_data = []
for cat in cat_valor.head(12).index:
    cat_data.append({
        'nome':    cat,
        'valor':   round(float(cat_valor.get(cat, 0)) / 1e6, 1),
        'qtd':     int(cat_count.get(cat, 0)),
        'ncm_pct': round(float(cat_ncm_pct.get(cat, 0)), 1),
    })

abc_data = [{'curva': l, 'qtd': int(abc_counts.get(l, 0))} for l in ['A', 'B', 'C']]

sav_data = [{'semana': k, 'valor': v} for k, v in savings.items() if v > 0]

html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MDM Supply Chain — Dashboard Executivo</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;700&display=swap');

  :root {{
    --bg:      #0b1220;
    --panel:   #111927;
    --border:  #1e2d40;
    --text:    #e2e8f0;
    --muted:   #64748b;
    --teal:    #00c9b1;
    --blue:    #4a9edb;
    --green:   #34d399;
    --red:     #f87171;
    --amber:   #fbb124;
  }}

  * {{ margin:0; padding:0; box-sizing:border-box; }}

  body {{
    background: var(--bg);
    color: var(--text);
    font-family: 'DM Sans', sans-serif;
    min-height: 100vh;
    padding: 24px;
  }}

  /* TOP BAR */
  .topbar {{
    display: flex; justify-content: space-between; align-items: center;
    border-bottom: 1px solid var(--border);
    padding-bottom: 16px; margin-bottom: 28px;
  }}
  .topbar h1 {{ font-size: 1.15rem; font-weight: 700; letter-spacing: .05em; }}
  .topbar h1 span {{ color: var(--teal); }}
  .topbar .meta {{ font-size: .8rem; color: var(--muted); font-family: 'Space Mono', monospace; }}
  .topbar .live {{ display:flex; align-items:center; gap:6px; font-size:.8rem; color:var(--green); }}
  .topbar .live::before {{ content:''; width:8px; height:8px; border-radius:50%; background:var(--green); animation: pulse 1.8s infinite; }}
  @keyframes pulse {{ 0%,100%{{opacity:1}} 50%{{opacity:.3}} }}

  /* KPI ROW */
  .kpi-row {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; margin-bottom: 22px; }}

  .kpi-card {{
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 18px 20px 14px;
    position: relative;
    overflow: hidden;
    transition: transform .18s, box-shadow .18s;
    cursor: default;
  }}
  .kpi-card:hover {{ transform: translateY(-3px); box-shadow: 0 12px 32px rgba(0,0,0,.4); }}
  .kpi-card::before {{
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: var(--accent, var(--teal));
  }}
  .kpi-label {{ font-size: .72rem; color: var(--muted); letter-spacing: .08em; text-transform: uppercase; margin-bottom: 8px; }}
  .kpi-value {{ font-size: 2rem; font-weight: 700; font-family: 'Space Mono', monospace; color: var(--accent, var(--teal)); line-height: 1; }}
  .kpi-meta  {{ font-size: .75rem; color: var(--muted); margin-top: 6px; }}
  .kpi-bar   {{ margin-top: 10px; height: 4px; background: var(--border); border-radius: 2px; overflow: hidden; }}
  .kpi-bar-fill {{ height: 100%; border-radius: 2px; background: var(--accent, var(--teal)); transition: width .6s ease; }}

  .ok  {{ --accent: var(--green); }}
  .warn{{ --accent: var(--amber); }}
  .bad {{ --accent: var(--red);   }}

  /* CHARTS GRID */
  .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-bottom: 18px; }}
  .grid-3 {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 18px; margin-bottom: 18px; }}
  .grid-32 {{ display: grid; grid-template-columns: 2fr 1fr; gap: 18px; margin-bottom: 18px; }}

  .chart-card {{
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px;
  }}
  .chart-card h3 {{
    font-size: .82rem; font-weight: 600; color: var(--muted);
    letter-spacing: .06em; text-transform: uppercase; margin-bottom: 16px;
  }}
  .chart-card canvas {{ max-height: 240px; }}

  /* FUNIL */
  .funnel {{ display: flex; flex-direction: column; gap: 6px; padding: 8px 0; }}
  .funnel-bar {{
    display: flex; align-items: center; gap: 12px;
  }}
  .funnel-label {{ font-size: .8rem; color: var(--muted); width: 90px; text-align: right; flex-shrink: 0; }}
  .funnel-track {{ flex: 1; height: 32px; background: var(--border); border-radius: 4px; overflow: hidden; }}
  .funnel-fill  {{ height: 100%; border-radius: 4px; display: flex; align-items: center; padding: 0 10px;
                   font-size: .82rem; font-weight: 700; color: #0b1220; transition: width .6s ease; }}
  .funnel-count {{ font-size: .82rem; color: var(--text); width: 60px; font-family: 'Space Mono', monospace; }}

  /* TABELA CATEGORIAS */
  table {{ width: 100%; border-collapse: collapse; font-size: .83rem; }}
  th {{ text-align: left; padding: 8px 10px; color: var(--muted); font-weight: 500;
        border-bottom: 1px solid var(--border); font-size: .72rem; letter-spacing: .06em; text-transform: uppercase; }}
  td {{ padding: 8px 10px; border-bottom: 1px solid var(--border); }}
  tr:last-child td {{ border-bottom: none; }}
  tr:hover td {{ background: rgba(255,255,255,.02); }}
  .pill {{
    display: inline-block; padding: 2px 8px; border-radius: 20px;
    font-size: .7rem; font-weight: 600;
  }}
  .pill-ok   {{ background: rgba(52,211,153,.15); color: var(--green); }}
  .pill-warn {{ background: rgba(251,177,36,.15);  color: var(--amber); }}
  .pill-bad  {{ background: rgba(248,113,113,.15); color: var(--red);   }}

  /* FOOTER */
  footer {{
    margin-top: 28px; padding-top: 16px; border-top: 1px solid var(--border);
    display: flex; justify-content: space-between; align-items: center;
    font-size: .75rem; color: var(--muted);
  }}
  footer strong {{ color: var(--teal); }}
</style>
</head>
<body>

<!-- TOP BAR -->
<div class="topbar">
  <h1>MDM <span>Supply Chain</span> — Dashboard Executivo</h1>
  <div class="live">AO VIVO</div>
  <div class="meta">Base: 3.300 materiais · R$ 1,83B · Março 2026</div>
</div>

<!-- KPI ROW -->
<div class="kpi-row">
  <div class="kpi-card ok">
    <div class="kpi-label">Completude Geral</div>
    <div class="kpi-value">100%</div>
    <div class="kpi-meta">meta 95% · ✅ atingido</div>
    <div class="kpi-bar"><div class="kpi-bar-fill" style="width:100%"></div></div>
  </div>
  <div class="kpi-card bad">
    <div class="kpi-label">NCM Válido</div>
    <div class="kpi-value">{kpis['ncm']:.0f}%</div>
    <div class="kpi-meta">meta 100% · ❌ gap 24pp</div>
    <div class="kpi-bar"><div class="kpi-bar-fill" style="width:{kpis['ncm']}%"></div></div>
  </div>
  <div class="kpi-card ok">
    <div class="kpi-label">Acuracidade Preço</div>
    <div class="kpi-value">{kpis['preco']:.0f}%</div>
    <div class="kpi-meta">meta 95% · ✅ atingido</div>
    <div class="kpi-bar"><div class="kpi-bar-fill" style="width:{kpis['preco']}%"></div></div>
  </div>
  <div class="kpi-card warn">
    <div class="kpi-label">Fornecedor Cadastrado</div>
    <div class="kpi-value">{kpis['fornecedor']:.0f}%</div>
    <div class="kpi-meta">meta 90% · ⚠️ gap 10pp</div>
    <div class="kpi-bar"><div class="kpi-bar-fill" style="width:{kpis['fornecedor']}%"></div></div>
  </div>
  <div class="kpi-card ok" style="--accent:var(--teal)">
    <div class="kpi-label">Score Ponderado</div>
    <div class="kpi-value">{kpis['score_pond']:.0f}</div>
    <div class="kpi-meta">meta 85 · ✅ atingido</div>
    <div class="kpi-bar"><div class="kpi-bar-fill" style="width:{kpis['score_pond']}%"></div></div>
  </div>
</div>

<!-- ROW 2: Savings + Pipeline -->
<div class="grid-2">
  <div class="chart-card">
    <h3>Savings Acumulados por Semana (R$ M/ano)</h3>
    <canvas id="chartSavings"></canvas>
  </div>
  <div class="chart-card">
    <h3>Pipeline de Integração — Funil de Aprovação</h3>
    <div class="funnel">
      <div class="funnel-bar">
        <div class="funnel-label">Entrada</div>
        <div class="funnel-track">
          <div class="funnel-fill" style="width:100%;background:#4a9edb">3.300</div>
        </div>
        <div class="funnel-count">3.300</div>
      </div>
      <div class="funnel-bar">
        <div class="funnel-label">Stage 1</div>
        <div class="funnel-track">
          <div class="funnel-fill" style="width:100%;background:#00c9b1">3.300</div>
        </div>
        <div class="funnel-count">3.300</div>
      </div>
      <div class="funnel-bar">
        <div class="funnel-label">Stage 2</div>
        <div class="funnel-track">
          <div class="funnel-fill" style="width:73.6%;background:#fbb124">2.428</div>
        </div>
        <div class="funnel-count">2.428</div>
      </div>
      <div class="funnel-bar">
        <div class="funnel-label">Auto ⚡</div>
        <div class="funnel-track">
          <div class="funnel-fill" style="width:32%;background:#34d399">1.056</div>
        </div>
        <div class="funnel-count">1.056</div>
      </div>
      <div class="funnel-bar">
        <div class="funnel-label">Supervisor</div>
        <div class="funnel-track">
          <div class="funnel-fill" style="width:30.9%;background:#4a9edb">1.019</div>
        </div>
        <div class="funnel-count">1.019</div>
      </div>
      <div class="funnel-bar">
        <div class="funnel-label">Retidos ❌</div>
        <div class="funnel-track">
          <div class="funnel-fill" style="width:26.4%;background:#f87171">872</div>
        </div>
        <div class="funnel-count">872</div>
      </div>
    </div>
  </div>
</div>

<!-- ROW 3: Categorias + ABC + Status -->
<div class="grid-3">
  <div class="chart-card" style="grid-column: span 2;">
    <h3>Valor por Categoria vs % NCM OK</h3>
    <canvas id="chartCategorias" style="max-height:220px"></canvas>
  </div>
  <div class="chart-card">
    <h3>Curva ABC</h3>
    <canvas id="chartAbc" style="max-height:220px"></canvas>
  </div>
</div>

<!-- ROW 4: Tabela categorias -->
<div class="chart-card" style="margin-bottom:18px">
  <h3>Detalhamento por Categoria</h3>
  <table>
    <thead>
      <tr>
        <th>Categoria</th>
        <th>Valor Estoque</th>
        <th>Materiais</th>
        <th>NCM OK</th>
        <th>Status NCM</th>
      </tr>
    </thead>
    <tbody>
      {''.join(f"""
      <tr>
        <td><strong>{d['nome']}</strong></td>
        <td>R$ {d['valor']:.1f}M</td>
        <td>{d['qtd']:,}</td>
        <td>{d['ncm_pct']:.1f}%</td>
        <td><span class="pill {'pill-ok' if d['ncm_pct']>=80 else ('pill-warn' if d['ncm_pct']>=70 else 'pill-bad')}">{
            '✅ OK' if d['ncm_pct']>=80 else ('⚠️ Atenção' if d['ncm_pct']>=70 else '❌ Crítico')
        }</span></td>
      </tr>""" for d in cat_data)}
    </tbody>
  </table>
</div>

<footer>
  <div>MDM Supply Chain Project · Dias 1–28 de 49 · Score QA: 97%</div>
  <div><strong>R$ 45,5M/ano</strong> em savings identificados · Pipeline: 2.428 aprovados (73,6%)</div>
  <div>Gerado: {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>
</footer>

<script>
Chart.defaults.color = '#64748b';
Chart.defaults.borderColor = '#1e2d40';
Chart.defaults.font.family = "'DM Sans', sans-serif";

// Savings
new Chart(document.getElementById('chartSavings'), {{
  type: 'bar',
  data: {{
    labels: {json.dumps([d['semana'] for d in sav_data])},
    datasets: [
      {{
        label: 'Savings R$M',
        data: {json.dumps([d['valor'] for d in sav_data])},
        backgroundColor: ['#00c9b1','#4a9edb','#fbb124'],
        borderRadius: 6,
        order: 2
      }},
      {{
        label: 'Acumulado R$M',
        data: {json.dumps(list(np.cumsum([d['valor'] for d in sav_data]).round(1)))},
        type: 'line',
        borderColor: '#34d399',
        backgroundColor: 'transparent',
        pointBackgroundColor: '#34d399',
        borderWidth: 2.5,
        pointRadius: 5,
        tension: 0.3,
        order: 1,
        yAxisID: 'y2'
      }}
    ]
  }},
  options: {{
    plugins: {{ legend: {{ labels: {{ color: '#94a3b8' }} }} }},
    scales: {{
      y:  {{ grid: {{ color: '#1e2d40' }}, ticks: {{ callback: v => 'R$'+v+'M' }} }},
      y2: {{ position: 'right', grid: {{ drawOnChartArea: false }},
             ticks: {{ callback: v => 'R$'+v+'M' }}, max: 60 }}
    }}
  }}
}});

// Categorias
new Chart(document.getElementById('chartCategorias'), {{
  type: 'bar',
  data: {{
    labels: {json.dumps([d['nome'] for d in cat_data])},
    datasets: [
      {{
        label: 'Valor R$M',
        data: {json.dumps([d['valor'] for d in cat_data])},
        backgroundColor: {json.dumps(['#34d399' if d['ncm_pct']>=80 else ('#fbb124' if d['ncm_pct']>=70 else '#f87171') for d in cat_data])},
        borderRadius: 4, yAxisID: 'y'
      }},
      {{
        label: 'NCM OK %',
        data: {json.dumps([d['ncm_pct'] for d in cat_data])},
        type: 'line',
        borderColor: '#4a9edb',
        backgroundColor: 'transparent',
        pointBackgroundColor: '#4a9edb',
        borderWidth: 2, pointRadius: 4,
        tension: 0.3, yAxisID: 'y2'
      }}
    ]
  }},
  options: {{
    plugins: {{ legend: {{ labels: {{ color: '#94a3b8' }} }} }},
    scales: {{
      y:  {{ grid: {{ color: '#1e2d40' }}, ticks: {{ callback: v => 'R$'+v+'M' }} }},
      y2: {{ position: 'right', min: 60, max: 100, grid: {{ drawOnChartArea: false }},
             ticks: {{ callback: v => v+'%' }} }}
    }}
  }}
}});

// ABC
new Chart(document.getElementById('chartAbc'), {{
  type: 'doughnut',
  data: {{
    labels: ['Curva A', 'Curva B', 'Curva C'],
    datasets: [{{
      data: {json.dumps(abc_vals)},
      backgroundColor: ['#f87171','#fbb124','#34d399'],
      borderColor: '#0b1220', borderWidth: 3
    }}]
  }},
  options: {{
    cutout: '65%',
    plugins: {{
      legend: {{ position: 'bottom', labels: {{ color: '#94a3b8', padding: 12 }} }}
    }}
  }}
}});
</script>
</body>
</html>"""

out_html = f'visualizations/DIA28_Dashboard_Executivo.html'
with open(out_html, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"  ✅ {out_html}")

# ─────────────────────────────────────────────────────────────────
# 4. SALVAR JSON COM TODOS OS DADOS DO DASHBOARD
# ─────────────────────────────────────────────────────────────────
dados_dash = {
    'gerado_em': ts,
    'kpis': kpis,
    'savings_total_M': 45.5,
    'savings_por_semana': savings,
    'pipeline': pipeline,
    'abc': {k: int(v) for k, v in abc_counts.items()},
    'status': {k: int(v) for k, v in status_counts.items()},
    'top_categorias': cat_data[:5],
}
with open(f'data/processed/dashboard_dados_{ts}.json', 'w', encoding='utf-8') as f:
    json.dump(dados_dash, f, ensure_ascii=False, indent=2)
print(f"  ✅ data/processed/dashboard_dados_{ts}.json")

# ─────────────────────────────────────────────────────────────────
# 5. RESUMO FINAL
# ─────────────────────────────────────────────────────────────────
print("\n" + "="*68)
print("  ✅ DIA 28 CONCLUÍDO — DASHBOARD EXECUTIVO!")
print("="*68)
print(f"""
  📊 DASHBOARD PNG:  visualizations/16_dashboard_executivo.png
  🌐 DASHBOARD HTML: visualizations/DIA28_Dashboard_Executivo.html
  📄 DADOS JSON:     data/processed/dashboard_dados_{ts}.json

  COMO USAR O HTML:
  ├─ Abra no Chrome/Firefox (duplo clique no arquivo)
  ├─ Funciona sem internet (Chart.js via CDN — precisa de conexão)
  └─ Para apresentar: modo tela cheia no navegador (F11)

  PRÓXIMO: DIA 29 — Análise de ROI Detalhada
""")
print("="*68 + "\n")
