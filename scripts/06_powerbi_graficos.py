"""
╔══════════════════════════════════════════════════════════════╗
║   DIA 13 — GRÁFICOS POWER BI (via Python)                   ║
║   Gera todos os visuais do dashboard em alta qualidade      ║
║   Use as imagens no Power BI sem configurar gráfico a gráfico║
╚══════════════════════════════════════════════════════════════╝
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import os, warnings
warnings.filterwarnings('ignore')

# ── CARREGAR DADOS ────────────────────────────────────
# ── CAMINHO DO CSV ──────────────────────────────────
# Se der erro, edite o caminho abaixo com o local do seu arquivo
CSV_PADRAO = 'E:/importantee/carreira/PROJETO MDM/mdm-supply-chain-project/data/raw/materiais_raw.csv'

df = None
for p in [CSV_PADRAO, 'data/raw/materiais_raw.csv', '../data/raw/materiais_raw.csv', 'materiais_raw.csv']:
    if os.path.exists(p):
        df = pd.read_csv(p)
        print(f'CSV carregado: {p}')
        break

if df is None:
    raise FileNotFoundError('CSV nao encontrado! Edite CSV_PADRAO no inicio do script.')

df['valor_estoque']       = df['preco_unitario'] * df['estoque_atual']
df['ultima_movimentacao'] = pd.to_datetime(df['ultima_movimentacao'])
df['dias_parado']         = (pd.Timestamp('2026-02-28') - df['ultima_movimentacao']).dt.days

os.makedirs('visualizations', exist_ok=True)

# ── PALETA ────────────────────────────────────────────
BG     = '#0b1220'
PANEL  = '#111927'
BORDER = '#1e2d40'
TEXT   = '#e2e8f0'
MUTED  = '#64748b'
C = {
    'blue':  '#38bdf8', 'green': '#34d399', 'orange':'#fb923c',
    'red':   '#f87171', 'purple':'#a78bfa', 'yellow':'#fbbf24',
    'teal':  '#2dd4bf', 'pink':  '#e879f9',
}
PALETTE = list(C.values())

def styled_ax(ax):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.xaxis.label.set_color(MUTED)
    ax.yaxis.label.set_color(MUTED)
    ax.title.set_color(TEXT)
    for spine in ax.spines.values():
        spine.set_color(BORDER)
    ax.grid(color=BORDER, linewidth=0.5, alpha=0.6)
    return ax

# ═══════════════════════════════════════════════════════
# FIGURA 1 — DASHBOARD GERAL (Página 1)
# ═══════════════════════════════════════════════════════
print("Gerando Página 1 — Dashboard Geral...")

fig = plt.figure(figsize=(22, 16), facecolor=BG)
fig.suptitle('DASHBOARD MDM — SUPPLY CHAIN  |  Dia 13 · Power BI',
             fontsize=18, color=TEXT, fontweight='bold', y=0.98)

gs = GridSpec(3, 3, figure=fig, hspace=0.42, wspace=0.32,
              left=0.05, right=0.97, top=0.93, bottom=0.05)

# ── 5 KPI CARDS (topo) ────────────────────────────────
kpi_ax = fig.add_subplot(gs[0, :])
kpi_ax.set_facecolor(BG)
kpi_ax.axis('off')

kpis = [
    ('3.300',     'TOTAL MATERIAIS',    '15 categorias',         C['blue'],   0.0),
    ('R$ 1,83B',  'VALOR EM ESTOQUE',   'R$ 1.833.031.687',      C['green'],  0.2),
    ('R$ 220,58', 'PREÇO MÉDIO',        'por unidade',           C['orange'], 0.4),
    ('2.454',     'MATERIAIS ATIVOS',   '74,4% do total',        C['green'],  0.6),
    ('660',       'SEM FORNECEDOR',     '20,0% — R$ 394M',       C['red'],    0.8),
]
for val, lbl, sub, cor, xpos in kpis:
    ax_c = fig.add_axes([0.05 + xpos*0.186, 0.77, 0.175, 0.16])
    ax_c.set_facecolor(PANEL)
    ax_c.axis('off')
    for spine in ax_c.spines.values(): spine.set_color(cor); spine.set_linewidth(1.5)
    ax_c.add_patch(plt.Rectangle((0,0.92),1,0.08, color=cor, transform=ax_c.transAxes, clip_on=False))
    ax_c.text(0.5, 0.55, val, ha='center', va='center', fontsize=22, fontweight='bold',
              color=cor, transform=ax_c.transAxes, family='monospace')
    ax_c.text(0.5, 0.28, lbl, ha='center', va='center', fontsize=9, fontweight='600',
              color=MUTED, transform=ax_c.transAxes, family='sans-serif')
    ax_c.text(0.5, 0.10, sub, ha='center', va='center', fontsize=8,
              color=MUTED, transform=ax_c.transAxes)

# ── GRÁFICO 1: Categorias (barras horizontais) ─────────
ax1 = fig.add_subplot(gs[1, :2])
styled_ax(ax1)
cats  = df.groupby('categoria')['valor_estoque'].sum().sort_values() / 1e6
cores = [PALETTE[i % len(PALETTE)] for i in range(len(cats))]
bars  = ax1.barh(cats.index, cats.values, color=cores, alpha=0.85, height=0.7)
for bar, val in zip(bars, cats.values):
    ax1.text(val + 0.5, bar.get_y() + bar.get_height()/2,
             f'R$ {val:.0f}M', va='center', color=TEXT, fontsize=8)
ax1.set_title('Valor em Estoque por Categoria (R$ Milhões)', fontsize=12, pad=10)
ax1.set_xlabel('R$ Milhões')
ax1.invert_yaxis()

# ── GRÁFICO 2: Status (pizza) ─────────────────────────
ax2 = fig.add_subplot(gs[1, 2])
styled_ax(ax2)
st_vals  = df['status'].value_counts()
st_cores = [C['green'], C['orange'], C['red']]
wedges, texts, autotexts = ax2.pie(
    st_vals.values, labels=st_vals.index, colors=st_cores,
    autopct='%1.1f%%', startangle=140,
    wedgeprops={'edgecolor': BG, 'linewidth': 2},
    pctdistance=0.75
)
for t in texts:    t.set_color(TEXT); t.set_fontsize(10)
for t in autotexts: t.set_color(BG); t.set_fontweight('bold'); t.set_fontsize(9)
ax2.set_title('Distribuição por Status', fontsize=12, pad=10)

# ── GRÁFICO 3: ABC ────────────────────────────────────
ax3 = fig.add_subplot(gs[2, 0])
styled_ax(ax3)
df_s = df.sort_values('valor_estoque', ascending=False).reset_index(drop=True)
total_v = df_s['valor_estoque'].sum()
df_s['pct_ac'] = df_s['valor_estoque'].cumsum() / total_v * 100
df_s['abc'] = df_s['pct_ac'].apply(lambda x: 'A' if x<=80 else ('B' if x<=95 else 'C'))
abc = df_s.groupby('abc').agg(qtd=('codigo_material','count'), valor=('valor_estoque','sum'))
abc_cores = {'A': C['red'], 'B': C['orange'], 'C': C['green']}
x_pos = np.arange(len(abc))
w = 0.35
b1 = ax3.bar(x_pos - w/2, abc['qtd'], w, color=[abc_cores[i] for i in abc.index], alpha=0.8, label='Qtd Itens')
ax3b = ax3.twinx()
ax3b.set_facecolor(PANEL)
ax3b.tick_params(colors=MUTED, labelsize=8)
for spine in ax3b.spines.values(): spine.set_color(BORDER)
b2 = ax3b.bar(x_pos + w/2, abc['valor']/1e6, w, color=C['blue'], alpha=0.6, label='Valor R$mi')
ax3.set_xticks(x_pos); ax3.set_xticklabels(abc.index)
ax3.set_title('Curva ABC', fontsize=12, pad=10)
ax3.set_ylabel('Qtd Materiais', color=MUTED, fontsize=9)
ax3b.set_ylabel('Valor R$ Milhões', color=C['blue'], fontsize=9)
for b in b1:
    ax3.text(b.get_x()+b.get_width()/2, b.get_height()+10, f'{int(b.get_height())}',
             ha='center', color=TEXT, fontsize=8, fontweight='bold')

# ── GRÁFICO 4: Fornecedores ───────────────────────────
ax4 = fig.add_subplot(gs[2, 1])
styled_ax(ax4)
forn = df.groupby('fornecedor_principal')['valor_estoque'].sum().dropna().sort_values() / 1e6
ax4.barh(forn.index, forn.values, color=C['orange'], alpha=0.85)
for i, val in enumerate(forn.values):
    ax4.text(val + 0.5, i, f'{val:.0f}M', va='center', color=TEXT, fontsize=7)
ax4.set_title('Top Fornecedores por Valor', fontsize=12, pad=10)
ax4.set_xlabel('R$ Milhões')

# ── GRÁFICO 5: Com/Sem Fornecedor ────────────────────
ax5 = fig.add_subplot(gs[2, 2])
styled_ax(ax5)
forn_data = [2640, 660]
forn_labels = ['Com Fornecedor\n(80,0%)', 'Sem Fornecedor\n(20,0%)']
wedges2, _, at2 = ax5.pie(
    forn_data, labels=forn_labels,
    colors=[C['green']+'cc', C['red']+'cc'],
    autopct='%1.0f%%', startangle=90,
    wedgeprops={'edgecolor': BG, 'linewidth':2}
)
for t in wedges2: t.set_linewidth(0)
for t in []: t.set_color(TEXT)
ax5.set_title('Materiais por Fornecedor', fontsize=12, pad=10)
for t in ax5.texts: t.set_color(TEXT); t.set_fontsize(9)

plt.savefig('visualizations/13_powerbi_pag1_dashboard.png', dpi=150,
            bbox_inches='tight', facecolor=BG)
plt.close()
print("  ✅ visualizations/13_powerbi_pag1_dashboard.png")

# ═══════════════════════════════════════════════════════
# FIGURA 2 — ANÁLISE DE RISCO (Página 2)
# ═══════════════════════════════════════════════════════
print("Gerando Página 2 — Análise de Risco...")

fig2 = plt.figure(figsize=(22, 16), facecolor=BG)
fig2.suptitle('ANÁLISE DE RISCO — MDM SUPPLY CHAIN  |  Dia 13 · Power BI',
              fontsize=18, color=TEXT, fontweight='bold', y=0.98)

gs2 = GridSpec(3, 2, figure=fig2, hspace=0.42, wspace=0.30,
               left=0.05, right=0.97, top=0.93, bottom=0.05)

# ── RISK KPI CARDS ────────────────────────────────────
risk_kpis = [
    ('R$ 394M',  'VALOR EM RISCO',         '660 materiais sem fornecedor', C['red'],    0.0),
    ('1.054',    'MATERIAIS PARADOS',       '>365 dias sem movimentação',   C['orange'], 0.25),
    ('R$ 531M',  'CAPITAL IMOBILIZADO',     'Estoque parado >1 ano',        C['orange'], 0.5),
    ('128',      'ABAIXO DO MÍNIMO',        'Risco de ruptura de estoque',  C['red'],    0.75),
]
for val, lbl, sub, cor, xpos in risk_kpis:
    ax_r = fig2.add_axes([0.05 + xpos*0.23, 0.81, 0.21, 0.13])
    ax_r.set_facecolor(PANEL)
    ax_r.axis('off')
    for spine in ax_r.spines.values(): spine.set_color(cor); spine.set_linewidth(2)
    ax_r.add_patch(plt.Rectangle((0,0.9),1,0.1, color=cor, transform=ax_r.transAxes, clip_on=False))
    ax_r.text(0.5, 0.55, val, ha='center', va='center', fontsize=24, fontweight='bold',
              color=cor, transform=ax_r.transAxes, family='monospace')
    ax_r.text(0.5, 0.28, lbl, ha='center', va='center', fontsize=9, fontweight='600',
              color=MUTED, transform=ax_r.transAxes)
    ax_r.text(0.5, 0.10, sub, ha='center', va='center', fontsize=8,
              color=MUTED, transform=ax_r.transAxes)

# ── GRÁFICO R1: Abaixo do Mínimo por Categoria ────────
ax_r1 = fig2.add_subplot(gs2[1, 0])
styled_ax(ax_r1)
abaixo = df[(df['estoque_atual'] < df['estoque_minimo']) & df['estoque_minimo'].notna()]
abaixo_cat = abaixo.groupby('categoria').size().sort_values(ascending=True)
ax_r1.barh(abaixo_cat.index, abaixo_cat.values, color=C['orange'], alpha=0.85)
for i, val in enumerate(abaixo_cat.values):
    ax_r1.text(val + 0.1, i, str(val), va='center', color=TEXT, fontsize=9, fontweight='bold')
ax_r1.set_title('Materiais Abaixo do Estoque Mínimo\npor Categoria', fontsize=11, pad=10)
ax_r1.set_xlabel('Quantidade de Materiais')

# ── GRÁFICO R2: Materiais Parados por Categoria ────────
ax_r2 = fig2.add_subplot(gs2[1, 1])
styled_ax(ax_r2)
parados = df[df['dias_parado'] > 365]
parados_cat = parados.groupby('categoria').size().sort_values(ascending=True)
ax_r2.barh(parados_cat.index, parados_cat.values, color=C['red'], alpha=0.85)
for i, val in enumerate(parados_cat.values):
    ax_r2.text(val + 0.5, i, str(val), va='center', color=TEXT, fontsize=9, fontweight='bold')
ax_r2.set_title('Materiais Parados >365 Dias\npor Categoria', fontsize=11, pad=10)
ax_r2.set_xlabel('Quantidade de Materiais')

# ── GRÁFICO R3: Top 20 sem fornecedor (tabela visual) ─
ax_r3 = fig2.add_subplot(gs2[2, :])
ax_r3.set_facecolor(PANEL)
ax_r3.axis('off')
ax_r3.set_title('Top 20 Materiais Sem Fornecedor — Maior Valor em Risco',
                fontsize=12, color=TEXT, pad=12, loc='left')

sem_forn = df[df['fornecedor_principal'].isna()].copy()
sem_forn = sem_forn.nlargest(20, 'valor_estoque')[
    ['codigo_material','descricao','categoria','valor_estoque']
].reset_index(drop=True)

cols = ['Código','Descrição','Categoria','Valor em Estoque','Risco']
col_widths = [0.12, 0.30, 0.15, 0.20, 0.10]
x_starts = [0.01]
for w in col_widths[:-1]: x_starts.append(x_starts[-1] + w)

# Header
for j, (col, xs, w) in enumerate(zip(cols, x_starts, col_widths)):
    ax_r3.text(xs + w/2, 0.97, col, ha='center', va='top',
               fontsize=9, fontweight='700', color=MUTED, transform=ax_r3.transAxes)

# Rows
risk_levels = ['CRÍTICO']*8 + ['ALTO']*7 + ['MÉDIO']*5
risk_cols   = {  'CRÍTICO': C['red'], 'ALTO': C['orange'], 'MÉDIO': C['yellow'] }

for i, (_, row) in enumerate(sem_forn.iterrows()):
    y = 0.93 - i * 0.044
    bg_c = BORDER if i % 2 == 0 else PANEL
    ax_r3.add_patch(plt.Rectangle((0.005, y-0.02), 0.99, 0.042,
                    facecolor=bg_c, transform=ax_r3.transAxes, zorder=0))
    vals = [row['codigo_material'], row['descricao'][:28],
            row['categoria'], f"R$ {row['valor_estoque']:,.0f}",
            risk_levels[i] if i < len(risk_levels) else 'MÉDIO']
    colors_row = [MUTED, TEXT, C['blue'], C['red'], risk_cols.get(vals[4], MUTED)]
    for j, (v, xs, w, cor) in enumerate(zip(vals, x_starts, col_widths, colors_row)):
        ax_r3.text(xs + w/2, y, v, ha='center', va='center', fontsize=8,
                   color=cor, transform=ax_r3.transAxes,
                   fontweight='bold' if j in [3,4] else 'normal',
                   family='monospace' if j == 0 else 'sans-serif')

plt.savefig('visualizations/13_powerbi_pag2_risco.png', dpi=150,
            bbox_inches='tight', facecolor=BG)
plt.close()
print("  ✅ visualizations/13_powerbi_pag2_risco.png")

print("\n" + "═"*60)
print("  ✅ DIA 13 — GRÁFICOS POWER BI GERADOS COM SUCESSO!")
print("═"*60)
print("""
  📁 ARQUIVOS GERADOS:
     • visualizations/13_powerbi_pag1_dashboard.png
     • visualizations/13_powerbi_pag2_risco.png

  💡 COMO USAR NO POWER BI:
     No Power BI Desktop → Inserir → Imagem
     Selecionar o PNG gerado
     Posicionar na página como visual de fundo

  📊 VISUALS INCLUÍDOS NAS IMAGENS:
     Página 1:
       - 5 cartões KPI
       - Barras: Valor por Categoria
       - Pizza: Status dos Materiais
       - ABC: Qtd × Valor
       - Barras: Top Fornecedores
       - Pizza: Com/Sem Fornecedor
     Página 2:
       - 4 cartões de risco
       - Barras: Abaixo do Mínimo
       - Barras: Materiais Parados
       - Tabela: Top 20 Sem Fornecedor
""")
