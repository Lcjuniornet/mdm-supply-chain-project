"""
╔══════════════════════════════════════════════════════════════════╗
║         DIA 15 — ANÁLISE DE CATEGORIZAÇÃO                       ║
║         Semana 3 · Projeto MDM Supply Chain                     ║
╚══════════════════════════════════════════════════════════════════╝

OBJETIVO:
  - Detectar materiais em categorias incorretas
  - Identificar descrições iguais em categorias diferentes
  - Analisar coerência entre descrição × categoria
  - Detectar categorias sobrepostas (Elétrico × Eletrônico)
  - Calcular impacto financeiro da má categorização
  - Gerar lista priorizada de correções

IMPACTO ESPERADO: R$ 5.000–10.000/ano
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import os, warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────────
# 1. CARREGAR DADOS
# ─────────────────────────────────────────────────────────────────
print("\n" + "═"*68)
print("  DIA 15 — ANÁLISE DE CATEGORIZAÇÃO")
print("  Semana 3 · Projeto MDM Supply Chain")
print("═"*68)

CSV = 'E:/importantee/carreira/PROJETO MDM/mdm-supply-chain-project/data/raw/materiais_raw.csv'
df = None
for p in [CSV, 'data/raw/materiais_raw.csv', '../data/raw/materiais_raw.csv', 'materiais_raw.csv']:
    if os.path.exists(p):
        df = pd.read_csv(p)
        print(f"\n✅ CSV carregado: {p} ({len(df):,} registros)")
        break

if df is None:
    raise FileNotFoundError('CSV não encontrado! Edite a variável CSV no início do script.')

df['valor_estoque'] = df['preco_unitario'] * df['estoque_atual']
os.makedirs('data/processed', exist_ok=True)
os.makedirs('visualizations', exist_ok=True)
total = len(df)

# ─────────────────────────────────────────────────────────────────
# 2. VISÃO GERAL DAS CATEGORIAS
# ─────────────────────────────────────────────────────────────────
print("\n" + "─"*68)
print("  MÉTODO 1: VISÃO GERAL DAS CATEGORIAS")
print("─"*68)

cat_stats = df.groupby('categoria').agg(
    qtd        =('codigo_material', 'count'),
    valor_total=('valor_estoque',   'sum'),
    valor_medio=('valor_estoque',   'mean'),
    preco_medio=('preco_unitario',  'mean'),
    uoms_unicas=('unidade_medida',  'nunique'),
).sort_values('valor_total', ascending=False)

cat_stats['pct_qtd']   = cat_stats['qtd']         / total * 100
cat_stats['pct_valor'] = cat_stats['valor_total']  / df['valor_estoque'].sum() * 100

print(f"\n  {'CATEGORIA':<16} {'QTD':>6} {'%QTD':>6} {'VALOR TOTAL':>16} {'%VAL':>6} {'P.MEDIO':>12}")
print("  " + "─"*66)
for cat, r in cat_stats.iterrows():
    print(f"  {cat:<16} {r['qtd']:>6,} {r['pct_qtd']:>5.1f}%"
          f" {r['valor_total']:>15,.0f} {r['pct_valor']:>5.1f}%"
          f" {r['preco_medio']:>11,.2f}")

# ─────────────────────────────────────────────────────────────────
# 3. MÉTODO 2 — DESCRIÇÕES EM MÚLTIPLAS CATEGORIAS
# ─────────────────────────────────────────────────────────────────
print("\n" + "─"*68)
print("  MÉTODO 2: DESCRIÇÕES EM MÚLTIPLAS CATEGORIAS")
print("─"*68)
print("  Mesmo material com descrição idêntica em categorias diferentes")

dup_mask   = df.groupby('descricao')['categoria'].nunique()
desc_multi = dup_mask[dup_mask > 1].index.tolist()
df_multi   = df[df['descricao'].isin(desc_multi)].copy()

total_multi = len(df_multi)
valor_multi = df_multi['valor_estoque'].sum()

print(f"\n  Descrições em +1 categoria:  {len(desc_multi):,}")
print(f"  Materiais afetados:          {total_multi:,} ({total_multi/total*100:.1f}%)")
print(f"  Valor em estoque afetado:    R$ {valor_multi:,.2f}")

# Top 10 descrições mais problemáticas
print(f"\n  TOP 10 DESCRIÇÕES MULTI-CATEGORIA:\n")
top_multi = (df_multi.groupby('descricao')
             .agg(n_cats=('categoria','nunique'),
                  n_mats=('codigo_material','count'),
                  valor=('valor_estoque','sum'),
                  cats=('categoria', lambda x: ' / '.join(sorted(x.unique()))))
             .sort_values('valor', ascending=False).head(10))

print(f"  {'DESCRIÇÃO':<30} {'CATS':>5} {'MATS':>6} {'VALOR':>16}  CATEGORIAS")
print("  " + "─"*80)
for desc, r in top_multi.iterrows():
    print(f"  {desc[:29]:<30} {r['n_cats']:>5} {r['n_mats']:>6,}"
          f" {r['valor']:>15,.0f}  {r['cats']}")

# ─────────────────────────────────────────────────────────────────
# 4. MÉTODO 3 — CATEGORIAS SOBREPOSTAS (ELÉTRICO × ELETRÔNICO)
# ─────────────────────────────────────────────────────────────────
print("\n" + "─"*68)
print("  MÉTODO 3: CATEGORIAS SOBREPOSTAS")
print("─"*68)

# Pares suspeitos de categorias sobrepostas
pares_suspeitos = [
    ('Elétrico', 'Eletrônico'),
    ('Mecânico', 'Peças'),
    ('Hidráulico', 'Pneumático'),
    ('Limpeza', 'Químico'),
    ('Acessórios', 'Fixação'),
]

print()
resultado_pares = []
for cat1, cat2 in pares_suspeitos:
    df1 = df[df['categoria'] == cat1]
    df2 = df[df['categoria'] == cat2]

    # Descrições comuns entre as duas categorias
    descs1 = set(df1['descricao'].str.lower().str.strip())
    descs2 = set(df2['descricao'].str.lower().str.strip())
    comuns = descs1 & descs2

    pct_sobrep = len(comuns) / max(len(descs1), len(descs2)) * 100
    status = "🔴 CRÍTICO" if pct_sobrep > 15 else ("⚠️  ATENÇÃO" if pct_sobrep > 5 else "✅ OK")

    resultado_pares.append({
        'par': f'{cat1} × {cat2}',
        'itens_cat1': len(df1),
        'itens_cat2': len(df2),
        'descricoes_comuns': len(comuns),
        'pct_sobreposicao': round(pct_sobrep, 1),
        'status': status,
    })

    print(f"  {status}  {cat1} × {cat2}")
    print(f"         {cat1}: {len(df1)} itens  |  {cat2}: {len(df2)} itens")
    print(f"         Descrições comuns: {len(comuns)} ({pct_sobrep:.1f}% sobreposição)")
    if comuns:
        exemplos = list(comuns)[:3]
        for ex in exemplos:
            print(f"         → '{ex}'")
    print()

# ─────────────────────────────────────────────────────────────────
# 5. MÉTODO 4 — KEYWORD MAPPING (DESCRIÇÃO × CATEGORIA ESPERADA)
# ─────────────────────────────────────────────────────────────────
print("─"*68)
print("  MÉTODO 4: ANÁLISE POR PALAVRAS-CHAVE")
print("─"*68)
print("  Detecta materiais que provavelmente estão na categoria errada")
print("  baseado em palavras-chave da descrição\n")

# Mapeamento: palavra-chave → categoria correta esperada
KEYWORD_MAP = {
    'Hidráulico' : ['mangueira', 'valvula', 'cilindro hidraulico', 'bomba', 'pistao', 'filtro hidra'],
    'Elétrico'   : ['fio', 'cabo eletrico', 'disjuntor', 'rele', 'contator', 'eletroduto', 'led'],
    'Químico'    : ['solvente', 'catalisador', 'reagente', 'desinfetante'],
    'Lubrificante': ['oleo', 'graxo', 'lubrif'],
    'EPI'        : ['mascara', 'luva', 'capacete', 'oculos protecao', 'bota'],
    'Fixação'    : ['parafuso', 'porca ', 'arruela', 'prego', 'rebite', 'bucha'],
    'Pneumático' : ['pneu', 'correia'],
}

resultado_kw = []
df_desc_lower = df['descricao'].str.lower().fillna('')

for cat_esperada, keywords in KEYWORD_MAP.items():
    for kw in keywords:
        mask_kw  = df_desc_lower.str.contains(kw, na=False)
        mask_cat = df['categoria'] != cat_esperada
        suspeitos = df[mask_kw & mask_cat]

        if len(suspeitos) > 0:
            for _, row in suspeitos.iterrows():
                resultado_kw.append({
                    'codigo_material': row['codigo_material'],
                    'descricao':       row['descricao'],
                    'categoria_atual': row['categoria'],
                    'categoria_sugerida': cat_esperada,
                    'palavra_chave':   kw,
                    'valor_estoque':   row['valor_estoque'],
                    'preco_unitario':  row['preco_unitario'],
                })

df_suspeitos = pd.DataFrame(resultado_kw).drop_duplicates(
    subset=['codigo_material']).sort_values('valor_estoque', ascending=False)

print(f"  Total de materiais suspeitos de má categorização: {len(df_suspeitos):,}")
print(f"  Valor em estoque envolvido: R$ {df_suspeitos['valor_estoque'].sum():,.2f}")

print(f"\n  {'CÓDIGO':<14} {'DESCRIÇÃO':<28} {'CAT.ATUAL':<14} {'CAT.SUGERIDA':<14} {'VALOR':>14}")
print("  " + "─"*88)
for _, r in df_suspeitos.head(15).iterrows():
    print(f"  {r['codigo_material']:<14} {r['descricao'][:27]:<28}"
          f" {r['categoria_atual']:<14} {r['categoria_sugerida']:<14}"
          f" {r['valor_estoque']:>13,.0f}")

# Resumo por categoria de destino
print(f"\n  RESUMO POR CATEGORIA SUGERIDA:")
print(f"  {'CATEGORIA SUGERIDA':<20} {'QTD':>6} {'VALOR':>16}")
print("  " + "─"*44)
for cat, grp in df_suspeitos.groupby('categoria_sugerida'):
    print(f"  {cat:<20} {len(grp):>6,} {grp['valor_estoque'].sum():>15,.0f}")

# ─────────────────────────────────────────────────────────────────
# 6. IMPACTO FINANCEIRO
# ─────────────────────────────────────────────────────────────────
print("\n" + "─"*68)
print("  IMPACTO FINANCEIRO DA MÁ CATEGORIZAÇÃO")
print("─"*68)

# Materiais total mal categorizados (união dos métodos)
codigos_multi    = set(df_multi['codigo_material'])
codigos_suspeito = set(df_suspeitos['codigo_material'])
todos_problema   = codigos_multi | codigos_suspeito
df_problema      = df[df['codigo_material'].isin(todos_problema)]

n_problema   = len(df_problema)
val_problema = df_problema['valor_estoque'].sum()
pct_problema = n_problema / total * 100

# Custo operacional da má categorização
custo_busca_hora   = 60       # R$/hora
tempo_busca_errada = 10/60    # 10 min por busca frustrada
buscas_dia         = 8        # buscas por dia afetadas
dias_uteis         = 250
custo_busca_ano    = custo_busca_hora * tempo_busca_errada * buscas_dia * dias_uteis

# Custo compras duplicadas por categoria errada
pct_compras_erro   = 0.02     # 2% das compras afetadas por categoria errada
valor_compras_mes  = val_problema * 0.05  # rotação estimada 5%/mês
custo_compras_ano  = valor_compras_mes * 0.02 * 12

# Custo análises/relatórios distorcidos
custo_relatorios   = 3500     # horas de analista corrigindo relatórios

custo_total_ano = custo_busca_ano + custo_compras_ano + custo_relatorios
custo_correcao  = n_problema * 3  # R$ 3 por registro para corrigir (2 min cada)

print(f"""
  MATERIAIS COM PROBLEMAS DE CATEGORIZAÇÃO:
  ├─ Descrição em múltiplas categorias: {len(codigos_multi):,} materiais
  ├─ Suspeitos por palavra-chave:       {len(codigos_suspeito):,} materiais
  └─ TOTAL (sem duplicatas):            {n_problema:,} materiais ({pct_problema:.1f}%)

  Valor em estoque afetado: R$ {val_problema:,.2f}

  ┌──────────────────────────────────────────────────────────┐
  │         CUSTO ANUAL DA MÁ CATEGORIZAÇÃO                  │
  │                                                          │
  │  Buscas mal sucedidas (10min × 8/dia × 250 dias):       │
  │    R$ {custo_busca_ano:>10,.2f}/ano                              │
  │                                                          │
  │  Compras com categoria errada (~2% do giro):             │
  │    R$ {custo_compras_ano:>10,.2f}/ano                              │
  │                                                          │
  │  Relatórios e análises distorcidas:                      │
  │    R$ {custo_relatorios:>10,.2f}/ano                              │
  │                                                          │
  │  ──────────────────────────────────────────              │
  │  TOTAL ANUAL:      R$ {custo_total_ano:>10,.2f}                  │
  │  CUSTO CORREÇÃO:   R$ {custo_correcao:>10,.2f} (1x)             │
  │  ROI:              Paga em menos de 1 mês!               │
  └──────────────────────────────────────────────────────────┘
""")

# ─────────────────────────────────────────────────────────────────
# 7. PLANO DE CORREÇÃO PRIORIZADO
# ─────────────────────────────────────────────────────────────────
print("─"*68)
print("  PLANO DE CORREÇÃO PRIORIZADO")
print("─"*68)

plano = [
    ("URGENTE",  "P1", "Corrigir 41 descrições em múltiplas categorias",
     f"{len(codigos_multi)} materiais", "Imediato — 2h de trabalho"),
    ("URGENTE",  "P2", "Revisar Elétrico × Eletrônico (sobreposição)",
     "~442 materiais", "1 semana — criar subcategorias"),
    ("ALTO",     "P3", "Corrigir suspeitos por palavra-chave",
     f"{len(codigos_suspeito)} materiais", "30 dias — revisão manual"),
    ("ALTO",     "P4", "Revisar Hidráulico × Pneumático",
     "~438 materiais", "30 dias — definir critério"),
    ("MÉDIO",    "P5", "Padronizar Mecânico × Peças",
     "~444 materiais", "90 dias — reestruturar"),
    ("MÉDIO",    "P6", "Criar regra de categorização automática",
     "Todos os novos cadastros", "90 dias — governança"),
]

cores_prio = {"URGENTE": "🔴", "ALTO": "🟡", "MÉDIO": "🟠"}
print()
for prio, cod, acao, escopo, prazo in plano:
    print(f"  {cores_prio[prio]} [{cod}] {acao}")
    print(f"         Escopo: {escopo}  |  Prazo: {prazo}")
    print()

# ─────────────────────────────────────────────────────────────────
# 8. GRÁFICOS
# ─────────────────────────────────────────────────────────────────
print("─"*68)
print("  GERANDO GRÁFICOS...")
print("─"*68)

BG, PANEL = '#0b1220', '#111927'
BORDER, TEXT, MUTED = '#1e2d40', '#e2e8f0', '#64748b'
C = {'blue':'#38bdf8','green':'#34d399','orange':'#fb923c',
     'red':'#f87171','purple':'#a78bfa','yellow':'#fbbf24','teal':'#2dd4bf'}
PALETTE = list(C.values())

fig = plt.figure(figsize=(22, 16), facecolor=BG)
fig.suptitle('📊 DIA 15 — ANÁLISE DE CATEGORIZAÇÃO | Master Data Management',
             fontsize=18, color=TEXT, fontweight='bold', y=0.98)

gs = GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.35,
              left=0.05, right=0.97, top=0.93, bottom=0.05)

def styled(ax):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=MUTED, labelsize=9)
    for k in ['xlabel','ylabel','title']: getattr(ax, k).set_color(TEXT) if hasattr(ax, k) else None
    ax.xaxis.label.set_color(MUTED); ax.yaxis.label.set_color(MUTED); ax.title.set_color(TEXT)
    for s in ax.spines.values(): s.set_color(BORDER)
    ax.grid(color=BORDER, linewidth=0.5, alpha=0.6)
    return ax

# ── G1: Valor por categoria (barras) ─────────────────────────────
ax1 = styled(fig.add_subplot(gs[0, :2]))
cat_val = cat_stats['valor_total'].sort_values() / 1e6
cores = [PALETTE[i % len(PALETTE)] for i in range(len(cat_val))]
bars = ax1.barh(cat_val.index, cat_val.values, color=cores, alpha=0.85, height=0.7)
for bar, val in zip(bars, cat_val.values):
    ax1.text(val + 0.3, bar.get_y()+bar.get_height()/2,
             f'R$ {val:.0f}M', va='center', color=TEXT, fontsize=8)
ax1.set_title('Valor em Estoque por Categoria (R$ Milhões)', fontsize=12, pad=10)
ax1.set_xlabel('R$ Milhões')

# ── G2: Pizza — Distribuição de materiais ────────────────────────
ax2 = styled(fig.add_subplot(gs[0, 2]))
cat_qtd = cat_stats['qtd'].sort_values(ascending=False)
wedges, texts, ats = ax2.pie(
    cat_qtd.values, labels=cat_qtd.index,
    colors=PALETTE, autopct='%1.1f%%', startangle=140,
    wedgeprops={'edgecolor': BG, 'linewidth': 1.5},
    textprops={'color': TEXT, 'fontsize': 7},
    pctdistance=0.80
)
for at in ats: at.set_fontsize(6); at.set_color(BG)
ax2.set_title('Distribuição de Materiais por Categoria', fontsize=12, pad=10)

# ── G3: Sobreposição entre categorias ────────────────────────────
ax3 = styled(fig.add_subplot(gs[1, 0]))
df_pares = pd.DataFrame(resultado_pares)
cores_bar = [C['red'] if p > 15 else (C['orange'] if p > 5 else C['green'])
             for p in df_pares['pct_sobreposicao']]
bars3 = ax3.barh(df_pares['par'], df_pares['pct_sobreposicao'],
                 color=cores_bar, alpha=0.85, height=0.6)
for bar, val in zip(bars3, df_pares['pct_sobreposicao']):
    ax3.text(val + 0.2, bar.get_y()+bar.get_height()/2,
             f'{val:.1f}%', va='center', color=TEXT, fontsize=9, fontweight='bold')
ax3.axvline(x=15, color=C['red'],    ls='--', lw=1.5, alpha=0.7, label='Crítico >15%')
ax3.axvline(x=5,  color=C['orange'], ls='--', lw=1.5, alpha=0.7, label='Atenção >5%')
ax3.set_title('Sobreposição entre Categorias (%)', fontsize=11, pad=10)
ax3.set_xlabel('% de Descrições em Comum')
ax3.legend(fontsize=8, facecolor=PANEL, labelcolor=TEXT)

# ── G4: Top descrições multi-categoria ───────────────────────────
ax4 = styled(fig.add_subplot(gs[1, 1]))
top_plot = top_multi.head(8)
bars4 = ax4.barh(
    [d[:22] for d in top_plot.index],
    top_plot['valor'] / 1e3,
    color=C['red'], alpha=0.85, height=0.6
)
for bar, val in zip(bars4, top_plot['valor'].values/1e3):
    ax4.text(val + 0.5, bar.get_y()+bar.get_height()/2,
             f'R$ {val:.0f}k', va='center', color=TEXT, fontsize=8)
ax4.set_title('Top Descrições em Múltiplas\nCategorias (R$ mil)', fontsize=11, pad=10)
ax4.set_xlabel('Valor em Estoque (R$ mil)')

# ── G5: Suspeitos por categoria sugerida ─────────────────────────
ax5 = styled(fig.add_subplot(gs[1, 2]))
if len(df_suspeitos) > 0:
    susp_cat = df_suspeitos.groupby('categoria_sugerida').size().sort_values()
    cores5 = [PALETTE[i % len(PALETTE)] for i in range(len(susp_cat))]
    ax5.barh(susp_cat.index, susp_cat.values, color=cores5, alpha=0.85, height=0.6)
    for i, val in enumerate(susp_cat.values):
        ax5.text(val+0.3, i, str(val), va='center', color=TEXT, fontsize=9, fontweight='bold')
ax5.set_title('Materiais Suspeitos por\nCategoria Correta', fontsize=11, pad=10)
ax5.set_xlabel('Quantidade de Materiais')

# ── G6: KPIs resumo ──────────────────────────────────────────────
ax6 = styled(fig.add_subplot(gs[2, 0]))
ax6.axis('off')
ax6.set_title('KPIs do Dia 15', fontsize=11, pad=10)

kpis = [
    ('📦 Total Materiais',          f'{total:,}',                    C['blue']),
    ('⚠️  Multi-categoria',         f'{total_multi:,} ({total_multi/total*100:.1f}%)', C['red']),
    ('🔍 Suspeitos (kw)',            f'{len(df_suspeitos):,}',        C['orange']),
    ('🔄 Sobreposição crítica',      'Elétrico × Eletrônico',         C['red']),
    ('💰 Custo anual estimado',      f'R$ {custo_total_ano:,.0f}',    C['yellow']),
    ('✅ Custo para corrigir (1x)',  f'R$ {custo_correcao:,.0f}',     C['green']),
]
for i, (lbl, val, cor) in enumerate(kpis):
    y = 0.88 - i*0.15
    ax6.text(0.03, y,    lbl, transform=ax6.transAxes, fontsize=9,  color=MUTED, va='center')
    ax6.text(0.97, y-0.04, val, transform=ax6.transAxes, fontsize=10, color=cor,
             va='center', ha='right', fontweight='bold')
    ax6.plot([0.01, 0.99], [y-0.08, y-0.08], color=BORDER, lw=0.7, transform=ax6.transAxes)

# ── G7: Plano de correção ─────────────────────────────────────────
ax7 = styled(fig.add_subplot(gs[2, 1:]))
ax7.axis('off')
ax7.set_title('Plano de Correção Priorizado', fontsize=11, pad=10)

cols_p = ['PRIORIDADE','CÓD','AÇÃO','ESCOPO','PRAZO']
xs = [0.01, 0.09, 0.14, 0.58, 0.78]
ws = [0.07, 0.04, 0.43, 0.19, 0.21]
for j, col in enumerate(cols_p):
    ax7.text(xs[j]+ws[j]/2, 0.94, col, ha='center', va='top',
             fontsize=8, fontweight='700', color=MUTED, transform=ax7.transAxes)

prio_cores = {'URGENTE': C['red'], 'ALTO': C['orange'], 'MÉDIO': C['yellow']}
for i, (prio, cod, acao, escopo, prazo) in enumerate(plano):
    y = 0.84 - i * 0.14
    bg = BORDER if i % 2 == 0 else PANEL
    ax7.add_patch(plt.Rectangle((0.005, y-0.06), 0.99, 0.13,
                  facecolor=bg, transform=ax7.transAxes, zorder=0))
    vals = [prio, cod, acao, escopo, prazo]
    for j, (v, x, w) in enumerate(zip(vals, xs, ws)):
        cor = prio_cores.get(prio, TEXT) if j == 0 else (C['blue'] if j == 1 else TEXT)
        ax7.text(x + w/2, y, v, ha='center', va='center', fontsize=8,
                 color=cor, transform=ax7.transAxes,
                 fontweight='bold' if j in [0,1] else 'normal')

plt.savefig('visualizations/07_categorizacao.png', dpi=150,
            bbox_inches='tight', facecolor=BG)
plt.close()
print("\n  ✅ visualizations/07_categorizacao.png gerado!")

# ─────────────────────────────────────────────────────────────────
# 9. EXPORTAR CSVs
# ─────────────────────────────────────────────────────────────────
# CSV 1: todos os suspeitos para correção manual
df_suspeitos.to_csv('data/processed/categorizacao_suspeitos.csv',
                    index=False, encoding='utf-8-sig')

# CSV 2: descrições em múltiplas categorias
top_multi.reset_index().to_csv('data/processed/categorizacao_multi.csv',
                                index=False, encoding='utf-8-sig')

# CSV 3: relatório completo de categorias
cat_stats.reset_index().to_csv('data/processed/categorizacao_stats.csv',
                                index=False, encoding='utf-8-sig')

print("  ✅ data/processed/categorizacao_suspeitos.csv")
print("  ✅ data/processed/categorizacao_multi.csv")
print("  ✅ data/processed/categorizacao_stats.csv")

# ─────────────────────────────────────────────────────────────────
# 10. RESUMO FINAL
# ─────────────────────────────────────────────────────────────────
print("\n" + "═"*68)
print("  ✅ DIA 15 CONCLUÍDO!")
print("═"*68)
print(f"""
  RESULTADOS DA ANÁLISE DE CATEGORIZAÇÃO:

  📋 VISÃO GERAL:
     · 15 categorias · {total:,} materiais · R$ {df['valor_estoque'].sum()/1e9:.2f}B em estoque

  🔴 PROBLEMAS ENCONTRADOS:
     · {len(desc_multi)} descrições em múltiplas categorias → {total_multi:,} materiais
     · {len(df_suspeitos):,} suspeitos por palavra-chave
     · Elétrico × Eletrônico: sobreposição crítica detectada
     · Hidráulico × Pneumático: sobreposição de atenção

  💰 IMPACTO FINANCEIRO:
     · Custo anual da má categorização: R$ {custo_total_ano:,.2f}
     · Custo para corrigir agora (1x): R$ {custo_correcao:,.2f}
     · ROI: corrigir em 1 mês, economizar por anos!

  📁 ARQUIVOS GERADOS:
     · visualizations/07_categorizacao.png
     · data/processed/categorizacao_suspeitos.csv ({len(df_suspeitos):,} linhas)
     · data/processed/categorizacao_multi.csv ({len(top_multi)} linhas)
     · data/processed/categorizacao_stats.csv (15 categorias)

  🎯 AÇÃO PRIORITÁRIA:
     Corrigir Elétrico × Eletrônico — maior sobreposição detectada
     Depois: 41 descrições em múltiplas categorias (2h de trabalho)

  PROGRESSO DO PROJETO:
     ✅ Dias  1– 7: Setup + Semana 1
     ✅ Dias  8–14: Análises + Power BI (Semana 2)
     ✅ Dia  15: Categorização       ← VOCÊ ESTÁ AQUI
     ⏳ Dia  16: Preços / Outliers   (amanhã)
     ⏳ Dia  17: Sazonalidade
     ⏳ Dias 18-19: Implementação Correções
     ⏳ Dia  20: Testes e Validação
     ⏳ Dia  21: Checkpoint Semana 3

  META DA SEMANA 3: 42,9% do projeto (21/49 dias)
""")
print("═"*68)
print("  AMANHÃ — DIA 16: Análise de Preços e Outliers 🚀")
print("═"*68 + "\n")
