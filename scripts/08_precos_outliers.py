"""
╔══════════════════════════════════════════════════════════════════╗
║         DIA 16 — ANÁLISE DE PREÇOS E OUTLIERS                   ║
║         Semana 3 · Projeto MDM Supply Chain                     ║
╚══════════════════════════════════════════════════════════════════╝

OBJETIVO:
  - Detectar preços zerados (material COM estoque, SEM preço)
  - Identificar outliers por Z-Score (>3 desvios padrões)
  - Identificar outliers por IQR (método robusto)
  - Detectar preços incoerentes dentro de cada categoria
  - Calcular impacto financeiro dos erros de preço
  - Gerar Top 50 prioridades para revisão
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
print("\n" + "="*68)
print("  DIA 16 — ANÁLISE DE PREÇOS E OUTLIERS")
print("  Semana 3 · Projeto MDM Supply Chain")
print("="*68)

CSV = 'E:/importantee/carreira/PROJETO MDM/mdm-supply-chain-project/data/raw/materiais_raw.csv'
df = None
for p in [CSV, 'data/raw/materiais_raw.csv', '../data/raw/materiais_raw.csv', 'materiais_raw.csv']:
    if os.path.exists(p):
        df = pd.read_csv(p)
        print(f"\n✅ CSV carregado: {p} ({len(df):,} registros)")
        break

if df is None:
    raise FileNotFoundError('CSV nao encontrado! Edite a variavel CSV no inicio do script.')

df['valor_estoque'] = df['preco_unitario'] * df['estoque_atual']
os.makedirs('data/processed', exist_ok=True)
os.makedirs('visualizations', exist_ok=True)
total = len(df)

# ─────────────────────────────────────────────────────────────────
# 2. VISÃO GERAL DOS PREÇOS
# ─────────────────────────────────────────────────────────────────
print("\n" + "-"*68)
print("  VISÃO GERAL DA DISTRIBUIÇÃO DE PREÇOS")
print("-"*68)

p = df['preco_unitario']
media  = p.mean()
mediana = p.median()
desvio = p.std()
cv = desvio / media * 100

print(f"""
  Registros analisados:  {total:,}
  -------------------------------------------------
  Minimo:                R$ {p.min():>10.2f}
  1o Quartil (Q1):       R$ {p.quantile(0.25):>10.2f}
  Mediana:               R$ {mediana:>10.2f}
  Media:                 R$ {media:>10.2f}
  3o Quartil (Q3):       R$ {p.quantile(0.75):>10.2f}
  Maximo:                R$ {p.max():>10.2f}
  -------------------------------------------------
  Desvio Padrao:         R$ {desvio:>10.2f}
  Coef. Variacao:        {cv:>9.1f}%
  -------------------------------------------------
  ATENCAO: CV = {cv:.0f}% (>100%) indica distribuicao MUITO dispersa
  ATENCAO: Media ({media:.0f}) >> Mediana ({mediana:.0f}) -> muitos outliers altos
""")

# Distribuicao por faixa
print(f"  {'FAIXA':<22} {'QTD':>6} {'%':>7}  STATUS")
print("  " + "-"*52)
faixas_dados = [
    ('R$ 0 (ZERO)',       df['preco_unitario'] == 0,                                          'CRITICO'),
    ('R$ 0,01 a R$ 1',   (df['preco_unitario'] > 0)  & (df['preco_unitario'] < 1),           'ATENCAO'),
    ('R$ 1 a R$ 10',     (df['preco_unitario'] >= 1)  & (df['preco_unitario'] < 10),          'OK'),
    ('R$ 10 a R$ 50',    (df['preco_unitario'] >= 10) & (df['preco_unitario'] < 50),          'OK'),
    ('R$ 50 a R$ 100',   (df['preco_unitario'] >= 50) & (df['preco_unitario'] < 100),         'OK'),
    ('R$ 100 a R$ 500',  (df['preco_unitario'] >= 100)& (df['preco_unitario'] < 500),         'OK'),
    ('R$ 500 a R$ 1k',   (df['preco_unitario'] >= 500)& (df['preco_unitario'] < 1000),        'ATENCAO'),
    ('R$ 1k a R$ 2k',    df['preco_unitario'] >= 1000,                                        'ATENCAO'),
]
for lbl, mask, status in faixas_dados:
    qtd = mask.sum()
    pct = qtd / total * 100
    print(f"  {lbl:<22} {qtd:>6,} {pct:>6.1f}%  {status}")

# ─────────────────────────────────────────────────────────────────
# 3. MÉTODO 1 — PREÇOS ZERADOS
# ─────────────────────────────────────────────────────────────────
print("\n" + "-"*68)
print("  METODO 1: PRECOS ZERADOS (CRITICO)")
print("-"*68)
print("  Material com preco = R$ 0,00 MAS com estoque fisico real")

df_zero = df[df['preco_unitario'] == 0].copy()

# Estimar valor real pela mediana da categoria
medianas_cat = df[df['preco_unitario'] > 0].groupby('categoria')['preco_unitario'].median()
df_zero['preco_estimado'] = df_zero['categoria'].map(medianas_cat)
df_zero['valor_estimado'] = df_zero['preco_estimado'] * df_zero['estoque_atual']
valor_real_estimado = df_zero['valor_estimado'].sum()

print(f"\n  Materiais com preco zerado: {len(df_zero):,}")
print(f"  Unidades em estoque SEM valor: {df_zero['estoque_atual'].sum():,}")
print(f"  Valor REAL estimado (mediana da cat.): R$ {valor_real_estimado:,.2f}")
print(f"  Balanco SUBAVALIADO em R$ {valor_real_estimado:,.2f}!")

print(f"\n  ZERADOS POR CATEGORIA:")
zero_cat = df_zero.groupby('categoria').agg(
    qtd=('codigo_material','count'),
    estoque=('estoque_atual','sum'),
    valor_est=('valor_estimado','sum')
).sort_values('valor_est', ascending=False)

print(f"  {'CATEGORIA':<16} {'QTD':>5} {'ESTOQUE':>10} {'VALOR EST.':>16}")
print("  " + "-"*52)
for cat, r in zero_cat.iterrows():
    print(f"  {cat:<16} {r['qtd']:>5,} {r['estoque']:>10,} {r['valor_est']:>15,.2f}")

print(f"\n  TOP 10 CRITICOS (maior estoque sem valor):")
print(f"  {'CODIGO':<14} {'DESCRICAO':<26} {'CAT':<14} {'ESTOQUE':>8}")
print("  " + "-"*66)
for _, r in df_zero.nlargest(10, 'estoque_atual').iterrows():
    print(f"  {r['codigo_material']:<14} {str(r['descricao'])[:25]:<26}"
          f" {r['categoria']:<14} {r['estoque_atual']:>8,}")

# ─────────────────────────────────────────────────────────────────
# 4. MÉTODO 2 — Z-SCORE
# ─────────────────────────────────────────────────────────────────
print("\n" + "-"*68)
print("  METODO 2: Z-SCORE (OUTLIERS ESTATISTICOS)")
print("-"*68)
print("  Formula: Z = (preco - media) / desvio_padrao")
print("  Threshold: |Z| > 3  (99,7% dos dados dentro)")

df_valid = df[df['preco_unitario'] > 0].copy()
mean_p = df_valid['preco_unitario'].mean()
std_p  = df_valid['preco_unitario'].std()
df_valid['z_score'] = (df_valid['preco_unitario'] - mean_p) / std_p

out_z3      = df_valid[df_valid['z_score'].abs() > 3]
out_z3_high = df_valid[df_valid['z_score'] > 3]
limiar_z3   = mean_p + 3 * std_p

print(f"\n  Media:      R$ {mean_p:,.2f}")
print(f"  Desvio:     R$ {std_p:,.2f}")
print(f"  Limiar Z>3: R$ {limiar_z3:,.2f}")
print(f"\n  Outliers |Z| > 2: {(df_valid['z_score'].abs() > 2).sum():,}")
print(f"  Outliers |Z| > 3: {len(out_z3):,}")
print(f"  Outliers ALTOS Z>3: {len(out_z3_high):,} materiais")

print(f"\n  TOP 15 OUTLIERS POR Z-SCORE:")
print(f"  {'CODIGO':<14} {'DESCRICAO':<26} {'CAT':<14} {'PRECO':>9} {'Z':>7} {'VALOR':>14}")
print("  " + "-"*88)
for _, r in out_z3.nlargest(15, 'z_score').iterrows():
    print(f"  {r['codigo_material']:<14} {str(r['descricao'])[:25]:<26}"
          f" {r['categoria']:<14} {r['preco_unitario']:>8,.2f}"
          f" {r['z_score']:>6.1f}o {r['valor_estoque']:>13,.0f}")

# ─────────────────────────────────────────────────────────────────
# 5. MÉTODO 3 — IQR
# ─────────────────────────────────────────────────────────────────
print("\n" + "-"*68)
print("  METODO 3: IQR — INTERVALO INTERQUARTILICO (METODO ROBUSTO)")
print("-"*68)
print("  Mais robusto que Z-Score para distribuicoes assimetricas")

Q1  = df_valid['preco_unitario'].quantile(0.25)
Q3  = df_valid['preco_unitario'].quantile(0.75)
IQR = Q3 - Q1
lim_sup = Q3 + 1.5 * IQR
lim_inf = max(0, Q1 - 1.5 * IQR)

out_iqr_alto = df_valid[df_valid['preco_unitario'] > lim_sup]

print(f"\n  Q1: R$ {Q1:.2f}  |  Q3: R$ {Q3:.2f}  |  IQR: R$ {IQR:.2f}")
print(f"  Limite Superior (Q3 + 1.5*IQR): R$ {lim_sup:,.2f}")
print(f"  Outliers acima do limite: {len(out_iqr_alto):,} materiais")

print(f"\n  OUTLIERS IQR POR CATEGORIA:")
print(f"  {'CATEGORIA':<16} {'OUTLIERS':>9} {'% DA CAT':>9} {'VALOR':>16}")
print("  " + "-"*54)
for cat, grp in df_valid.groupby('categoria'):
    n_out = (grp['preco_unitario'] > lim_sup).sum()
    val_out = grp.loc[grp['preco_unitario'] > lim_sup, 'valor_estoque'].sum()
    pct = n_out / len(grp) * 100
    if n_out > 0:
        print(f"  {cat:<16} {n_out:>9,} {pct:>8.1f}% {val_out:>15,.0f}")

# ─────────────────────────────────────────────────────────────────
# 6. MÉTODO 4 — OUTLIERS INTRA-CATEGORIA
# ─────────────────────────────────────────────────────────────────
print("\n" + "-"*68)
print("  METODO 4: OUTLIERS DENTRO DE CADA CATEGORIA")
print("-"*68)
print("  Detecta preco incoerente vs mediana da propria categoria")
print("  Ex: 'Clips PVC R$1.984' em Escritorio (mediana: R$8)")

suspeitos_cat = []
for cat, grp in df_valid.groupby('categoria'):
    med = grp['preco_unitario'].median()
    if med == 0: continue
    for _, row in grp.iterrows():
        ratio = row['preco_unitario'] / med
        if ratio > 10 or ratio < 0.05:
            suspeitos_cat.append({
                'codigo_material': row['codigo_material'],
                'descricao':       row['descricao'],
                'categoria':       cat,
                'preco':           row['preco_unitario'],
                'mediana_cat':     round(med, 2),
                'ratio':           round(ratio, 1),
                'estoque':         row['estoque_atual'],
                'valor_estoque':   row['valor_estoque'],
                'tipo':            'MUITO ALTO' if ratio > 10 else 'MUITO BAIXO',
            })

df_intra = pd.DataFrame(suspeitos_cat).sort_values('valor_estoque', ascending=False)

print(f"\n  Suspeitos intra-categoria: {len(df_intra):,}")
print(f"  MUITO ALTO (>10x mediana):  {(df_intra['tipo']=='MUITO ALTO').sum()}")
print(f"  MUITO BAIXO (<5% mediana):  {(df_intra['tipo']=='MUITO BAIXO').sum()}")

print(f"\n  TOP 15 MAIS SUSPEITOS:")
print(f"  {'CODIGO':<14} {'DESCRICAO':<24} {'CAT':<13} {'PRECO':>9} {'MED':>9} {'RATIO':>7}  TIPO")
print("  " + "-"*90)
for _, r in df_intra.head(15).iterrows():
    print(f"  {r['codigo_material']:<14} {str(r['descricao'])[:23]:<24}"
          f" {r['categoria']:<13} {r['preco']:>8,.2f}"
          f" {r['mediana_cat']:>8,.2f} {r['ratio']:>6.0f}x  {r['tipo']}")

# ─────────────────────────────────────────────────────────────────
# 7. TOP 50 CONSOLIDADO
# ─────────────────────────────────────────────────────────────────
print("\n" + "-"*68)
print("  CONSOLIDACAO: TOP 50 PARA REVISAO PRIORITARIA")
print("-"*68)

codigos_zero  = set(df_zero['codigo_material'])
codigos_z3    = set(out_z3['codigo_material'])
codigos_intra = set(df_intra['codigo_material'])
todos = codigos_zero | codigos_z3 | codigos_intra

df_todos = df[df['codigo_material'].isin(todos)].copy()
df_todos['metodos'] = df_todos['codigo_material'].apply(
    lambda c: ' + '.join(
        (['ZERO']      if c in codigos_zero  else []) +
        (['Z-SCORE']   if c in codigos_z3    else []) +
        (['INTRA-CAT'] if c in codigos_intra else [])
    )
)
def score(row):
    s = 0
    if row['preco_unitario'] == 0:      s += 30
    if row['preco_unitario'] > lim_sup: s += 20
    if abs((row['preco_unitario'] - mean_p) / (std_p + 1)) > 3: s += 15
    s += min(row['valor_estoque'] / 1e6, 10)
    s += min(row['estoque_atual']  / 1000, 5)
    return round(s, 1)

df_todos['score'] = df_todos.apply(score, axis=1)
top50 = df_todos.sort_values('score', ascending=False).head(50)

print(f"\n  Total suspeitos (todos os metodos): {len(todos):,}")
print(f"\n  TOP 20 PARA ACAO IMEDIATA:")
print(f"  {'CODIGO':<14} {'PRECO':>9} {'ESTOQUE':>8} {'VALOR':>14} {'SCORE':>6}  METODOS")
print("  " + "-"*74)
for _, r in top50.head(20).iterrows():
    print(f"  {r['codigo_material']:<14} {r['preco_unitario']:>8,.2f}"
          f" {r['estoque_atual']:>8,} {r['valor_estoque']:>13,.0f}"
          f" {r['score']:>5.1f}  {r['metodos']}")

# ─────────────────────────────────────────────────────────────────
# 8. IMPACTO FINANCEIRO
# ─────────────────────────────────────────────────────────────────
print("\n" + "-"*68)
print("  IMPACTO FINANCEIRO DOS ERROS DE PRECO")
print("-"*68)

custo_compras_erro = len(out_z3_high) * (out_z3_high['preco_unitario'].mean() - mediana) * 2
custo_auditoria    = 4500
custo_correcao_1x  = len(todos) * 4
total_custo_anual  = custo_compras_erro + custo_auditoria

print(f"""
  PROBLEMA 1 - PRECOS ZERADOS:
  -> {len(df_zero):,} materiais com R$ 0,00 mas com estoque fisico
  -> {df_zero['estoque_atual'].sum():,} unidades sem valor contabil
  -> Balanco SUBAVALIADO em R$ {valor_real_estimado:,.2f}

  PROBLEMA 2 - OUTLIERS ALTOS (Z > 3):
  -> {len(out_z3_high):,} materiais com preco muito acima da media
  -> Limiar: R$ {limiar_z3:,.2f}  |  Maximo: R$ {df_valid['preco_unitario'].max():,.2f}

  PROBLEMA 3 - INCOERENCIA INTRA-CATEGORIA:
  -> {len(df_intra):,} materiais com preco incoerente para a categoria
  -> Ex: "Clips PVC R$1.984" enquanto mediana Escritorio = R${df_valid[df_valid['categoria']=='Escritorio']['preco_unitario'].median() if 'Escritorio' in df_valid['categoria'].values else df_valid[df_valid['categoria']=='Escritório']['preco_unitario'].median():.2f}

  +------------------------------------------------------------+
  |         CUSTO ANUAL DOS ERROS DE PRECO                    |
  |                                                            |
  |  Compras com preco incorreto (outliers z>3):              |
  |    R$ {custo_compras_erro:>10,.2f}/ano                              |
  |                                                            |
  |  Auditorias e reconciliacoes extras:                       |
  |    R$ {custo_auditoria:>10,.2f}/ano                              |
  |                                                            |
  |  TOTAL ANUAL:        R$ {total_custo_anual:>10,.2f}                    |
  |  Balanco subavaliado: R$ {valor_real_estimado:>10,.2f} (risco auditoria)|
  |  Custo correcao 1x:  R$ {custo_correcao_1x:>10,.2f}                    |
  |  ROI: paga em menos de 1 mes!                             |
  +------------------------------------------------------------+
""")

# ─────────────────────────────────────────────────────────────────
# 9. GRÁFICOS
# ─────────────────────────────────────────────────────────────────
print("-"*68)
print("  GERANDO GRAFICOS...")
print("-"*68)

BG, PANEL = '#0b1220', '#111927'
BORDER, TEXT, MUTED = '#1e2d40', '#e2e8f0', '#64748b'
C = {'blue':'#38bdf8','green':'#34d399','orange':'#fb923c',
     'red':'#f87171','purple':'#a78bfa','yellow':'#fbbf24','teal':'#2dd4bf'}
PALETTE = list(C.values())

def styled(ax):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.xaxis.label.set_color(MUTED); ax.yaxis.label.set_color(MUTED)
    ax.title.set_color(TEXT)
    for s in ax.spines.values(): s.set_color(BORDER)
    ax.grid(color=BORDER, linewidth=0.5, alpha=0.6)
    return ax

fig = plt.figure(figsize=(22, 16), facecolor=BG)
fig.suptitle('DIA 16 — ANALISE DE PRECOS E OUTLIERS | MDM Supply Chain',
             fontsize=18, color=TEXT, fontweight='bold', y=0.98)
gs = GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.35,
              left=0.05, right=0.97, top=0.93, bottom=0.05)

# G1: Histograma de precos
ax1 = styled(fig.add_subplot(gs[0, :2]))
precos_filtrados = df_valid[df_valid['preco_unitario'] <= 600]['preco_unitario']
n, bins, patches = ax1.hist(precos_filtrados, bins=60, color=C['blue'], alpha=0.7, edgecolor=BG)
for patch in patches:
    if patch.get_x() > lim_sup:
        patch.set_facecolor(C['red']); patch.set_alpha(0.9)
ax1.axvline(mean_p,  color=C['yellow'], lw=2, ls='--', label=f'Media R${mean_p:.0f}')
ax1.axvline(mediana, color=C['green'],  lw=2, ls='--', label=f'Mediana R${mediana:.0f}')
ax1.axvline(lim_sup, color=C['red'],    lw=2, ls=':',  label=f'Limite IQR R${lim_sup:.0f}')
ax1.set_title('Distribuicao de Precos — vermelho = outliers IQR', fontsize=12, pad=10)
ax1.set_xlabel('Preco Unitario (R$)')
ax1.set_ylabel('Frequencia')
ax1.legend(fontsize=9, facecolor=PANEL, labelcolor=TEXT)

# G2: Pizza tipos de problema
ax2 = styled(fig.add_subplot(gs[0, 2]))
prob_data   = [len(df_zero), len(out_z3_high), len(df_intra)]
prob_labels = [f'Zerado\n({len(df_zero)})', f'Outlier Z>3\n({len(out_z3_high)})',
               f'Intra-cat.\n({len(df_intra)})']
wedges, texts, ats = ax2.pie(
    prob_data, labels=prob_labels,
    colors=[C['red'], C['orange'], C['yellow']],
    autopct='%1.1f%%', startangle=90,
    wedgeprops={'edgecolor': BG, 'linewidth': 2},
    textprops={'color': TEXT, 'fontsize': 9})
for at in ats: at.set_color(BG); at.set_fontweight('bold')
ax2.set_title('Tipos de Problema de Preco', fontsize=12, pad=10)

# G3: Zerados por categoria
ax3 = styled(fig.add_subplot(gs[1, 0]))
zc = df_zero.groupby('categoria').size().sort_values()
cores3 = [C['red'] if v > 8 else C['orange'] for v in zc.values]
bars3 = ax3.barh(zc.index, zc.values, color=cores3, alpha=0.85, height=0.7)
for b, v in zip(bars3, zc.values):
    ax3.text(v+0.1, b.get_y()+b.get_height()/2, str(v),
             va='center', color=TEXT, fontsize=9, fontweight='bold')
ax3.set_title('Precos Zerados por Categoria', fontsize=11, pad=10)
ax3.set_xlabel('Quantidade')

# G4: Top 10 precos mais altos
ax4 = styled(fig.add_subplot(gs[1, 1]))
top10 = df_valid.nlargest(10, 'preco_unitario')
y_pos = range(len(top10))
bars4 = ax4.barh(list(y_pos), top10['preco_unitario'].values,
                 color=C['red'], alpha=0.85, height=0.7)
ax4.set_yticks(list(y_pos))
ax4.set_yticklabels([str(r['descricao'])[:18] for _, r in top10.iterrows()],
                    fontsize=8, color=TEXT)
for b, (_, r) in zip(bars4, top10.iterrows()):
    ax4.text(r['preco_unitario']+5, b.get_y()+b.get_height()/2,
             f"R${r['preco_unitario']:.0f}", va='center', color=TEXT, fontsize=8)
ax4.axvline(mediana, color=C['green'], lw=2, ls='--',
            label=f'Mediana R${mediana:.0f}')
ax4.set_title('Top 10 Precos Mais Altos', fontsize=11, pad=10)
ax4.set_xlabel('Preco Unitario (R$)')
ax4.legend(fontsize=8, facecolor=PANEL, labelcolor=TEXT)
ax4.invert_yaxis()

# G5: Outliers intra-categoria por categoria
ax5 = styled(fig.add_subplot(gs[1, 2]))
intra_cat = df_intra.groupby('categoria').size().sort_values()
cores5 = [PALETTE[i % len(PALETTE)] for i in range(len(intra_cat))]
bars5 = ax5.barh(intra_cat.index, intra_cat.values, color=cores5, alpha=0.85, height=0.7)
for b, v in zip(bars5, intra_cat.values):
    ax5.text(v+0.05, b.get_y()+b.get_height()/2, str(v),
             va='center', color=TEXT, fontsize=9, fontweight='bold')
ax5.set_title('Outliers Intra-Categoria', fontsize=11, pad=10)
ax5.set_xlabel('Quantidade')

# G6: Media vs Mediana por categoria
ax6 = styled(fig.add_subplot(gs[2, :2]))
cat_preco = df_valid.groupby('categoria')['preco_unitario'].agg(
    media='mean', mediana='median').sort_values('media', ascending=True)
x_pos = np.arange(len(cat_preco))
w = 0.35
ax6.bar(x_pos - w/2, cat_preco['media'],   width=w, color=C['orange'], alpha=0.8, label='Media')
ax6.bar(x_pos + w/2, cat_preco['mediana'], width=w, color=C['green'],  alpha=0.8, label='Mediana')
ax6.set_xticks(x_pos)
ax6.set_xticklabels(cat_preco.index, rotation=35, ha='right', fontsize=8)
ax6.set_title('Media vs Mediana por Categoria  (gap grande = muitos outliers!)', fontsize=11, pad=10)
ax6.set_ylabel('Preco Unitario (R$)')
ax6.legend(fontsize=9, facecolor=PANEL, labelcolor=TEXT)

# G7: KPIs
ax7 = styled(fig.add_subplot(gs[2, 2]))
ax7.axis('off')
ax7.set_title('KPIs do Dia 16', fontsize=11, pad=10)
kpis = [
    ('Total Materiais',          f'{total:,}',                       C['blue']),
    ('Preco Zerado',             f'{len(df_zero):,} materiais',       C['red']),
    ('Outliers Z>3',             f'{len(out_z3):,} materiais',        C['orange']),
    ('Outliers IQR (altos)',     f'{len(out_iqr_alto):,} materiais',  C['orange']),
    ('Intra-categoria',          f'{len(df_intra):,} materiais',      C['yellow']),
    ('Balanco subavaliado',      f'R$ {valor_real_estimado:,.0f}',    C['red']),
    ('Custo anual estimado',     f'R$ {total_custo_anual:,.0f}',      C['yellow']),
    ('Custo correcao (1x)',      f'R$ {custo_correcao_1x:,.0f}',      C['green']),
]
for i, (lbl, val, cor) in enumerate(kpis):
    y = 0.90 - i * 0.115
    ax7.text(0.03, y,       lbl, transform=ax7.transAxes, fontsize=9,  color=MUTED, va='center')
    ax7.text(0.97, y-0.035, val, transform=ax7.transAxes, fontsize=9,  color=cor,
             va='center', ha='right', fontweight='bold')
    ax7.plot([0.01, 0.99], [y-0.07, y-0.07], color=BORDER, lw=0.6, transform=ax7.transAxes)

plt.savefig('visualizations/08_precos_outliers.png', dpi=150,
            bbox_inches='tight', facecolor=BG)
plt.close()
print("\n  OK: visualizations/08_precos_outliers.png gerado!")

# ─────────────────────────────────────────────────────────────────
# 10. EXPORTAR CSVs
# ─────────────────────────────────────────────────────────────────
df_zero[['codigo_material','descricao','categoria','estoque_atual',
         'preco_estimado','valor_estimado']].to_csv(
    'data/processed/precos_zerados.csv', index=False, encoding='utf-8-sig')

top50[['codigo_material','descricao','categoria','preco_unitario',
       'estoque_atual','valor_estoque','score','metodos']].to_csv(
    'data/processed/precos_outliers_top50.csv', index=False, encoding='utf-8-sig')

df_intra[['codigo_material','descricao','categoria','preco','mediana_cat',
          'ratio','valor_estoque','tipo']].to_csv(
    'data/processed/precos_intra_categoria.csv', index=False, encoding='utf-8-sig')

print("  OK: data/processed/precos_zerados.csv")
print("  OK: data/processed/precos_outliers_top50.csv")
print("  OK: data/processed/precos_intra_categoria.csv")

# ─────────────────────────────────────────────────────────────────
# 11. RESUMO FINAL
# ─────────────────────────────────────────────────────────────────
print("\n" + "="*68)
print("  DIA 16 CONCLUIDO!")
print("="*68)
print(f"""
  RESULTADOS DA ANALISE DE PRECOS E OUTLIERS:

  CRITICO — PRECOS ZERADOS:
  -> {len(df_zero):,} materiais com R$ 0,00 MAS com estoque fisico
  -> {df_zero['estoque_atual'].sum():,} unidades sem valor contabil
  -> Balanco SUBAVALIADO em R$ {valor_real_estimado:,.2f}

  OUTLIERS ESTATISTICOS (Z-SCORE > 3):
  -> {len(out_z3):,} materiais fora de 3 desvios padroes
  -> Limiar: R$ {limiar_z3:,.2f}  |  Maximo: R$ {df_valid['preco_unitario'].max():,.2f}

  OUTLIERS IQR:
  -> {len(out_iqr_alto):,} materiais acima de R$ {lim_sup:,.2f}

  INCOERENCIA INTRA-CATEGORIA:
  -> {len(df_intra):,} materiais com preco >10x ou <5% da mediana da categoria

  IMPACTO FINANCEIRO:
  -> Custo anual: R$ {total_custo_anual:,.2f}
  -> Balanco subavaliado: R$ {valor_real_estimado:,.2f}
  -> Custo correcao 1x: R$ {custo_correcao_1x:,.2f}

  ARQUIVOS GERADOS:
  -> visualizations/08_precos_outliers.png
  -> data/processed/precos_zerados.csv         ({len(df_zero):,} linhas)
  -> data/processed/precos_outliers_top50.csv  (50 linhas)
  -> data/processed/precos_intra_categoria.csv ({len(df_intra):,} linhas)

  PROGRESSO:
  OK Dias  1-14: Semanas 1 e 2
  OK Dia  15: Categorizacao    (R$ 6,3M)
  OK Dia  16: Precos/Outliers  <- VOCE ESTA AQUI
  .. Dia  17: Sazonalidade     (amanha)
  .. Dias 18-19: Implementacao Correcoes
  .. Dia  20: Testes e Validacao
  .. Dia  21: Checkpoint Semana 3
""")
print("="*68)
print("  AMANHA — DIA 17: Analise de Sazonalidade")
print("="*68 + "\n")
