"""
╔══════════════════════════════════════════════════════════════════╗
║         DIA 17 — ANÁLISE DE SAZONALIDADE                        ║
║         Semana 3 · Projeto MDM Supply Chain                     ║
╚══════════════════════════════════════════════════════════════════╝

OBJETIVO:
  - Identificar padrões temporais de movimentação/consumo
  - Detectar sazonalidade por categoria
  - Gerar heatmap categoria × mês
  - Forecast básico (Moving Average) para próximos 3 meses
  - Calcular impacto financeiro do planejamento sazonal
  - Recomendar ajustes no estoque_minimo por sazonalidade
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import seaborn as sns
from datetime import datetime, timedelta
import calendar
import os, warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────────
# 1. CARREGAR DADOS
# ─────────────────────────────────────────────────────────────────
print("\n" + "="*68)
print("  DIA 17 — ANÁLISE DE SAZONALIDADE")
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
    raise FileNotFoundError('CSV não encontrado! Edite a variável CSV no início do script.')

# Converter datas
df['ultima_movimentacao'] = pd.to_datetime(df['ultima_movimentacao'])
df['data_cadastro'] = pd.to_datetime(df['data_cadastro'])
df['valor_estoque'] = df['preco_unitario'] * df['estoque_atual']

# Criar colunas temporais
df['mes_mov'] = df['ultima_movimentacao'].dt.month
df['mes_nome'] = df['ultima_movimentacao'].dt.month_name()
df['trimestre'] = df['ultima_movimentacao'].dt.quarter
df['ano'] = df['ultima_movimentacao'].dt.year

# Data referência (hoje simulado: 06/03/2026)
data_ref = datetime(2026, 3, 6)
df['dias_desde_mov'] = (data_ref - df['ultima_movimentacao']).dt.days

os.makedirs('data/processed', exist_ok=True)
os.makedirs('visualizations', exist_ok=True)
total = len(df)

# ─────────────────────────────────────────────────────────────────
# 2. ANÁLISE TEMPORAL GERAL
# ─────────────────────────────────────────────────────────────────
print("\n" + "-"*68)
print("  VISÃO GERAL — DISTRIBUIÇÃO TEMPORAL")
print("-"*68)

# Estatísticas gerais
mov_min = df['ultima_movimentacao'].min()
mov_max = df['ultima_movimentacao'].max()
mov_range = (mov_max - mov_min).days

print(f"""
  Período de dados:
  -------------------------------------------------
  Data mais antiga:      {mov_min.strftime('%d/%m/%Y')}
  Data mais recente:     {mov_max.strftime('%d/%m/%Y')}
  Range (dias):          {mov_range:,} dias
  Média dias desde mov:  {df['dias_desde_mov'].mean():.0f} dias
  Mediana dias:          {df['dias_desde_mov'].median():.0f} dias
""")

# Movimentações por mês
print("  MOVIMENTAÇÕES POR MÊS (últimos 12 meses):")
print(f"  {'MÊS':<12} {'QTD MATERIAIS':>15} {'%':>7}  {'VALOR (R$ Mi)':>14}")
print("  " + "-"*54)

mov_mes = df.groupby('mes_mov').agg({
    'codigo_material': 'count',
    'valor_estoque': 'sum'
}).rename(columns={'codigo_material': 'qtd'})
mov_mes['pct'] = mov_mes['qtd'] / total * 100
mov_mes['valor_mi'] = mov_mes['valor_estoque'] / 1e6

meses_ordem = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']
meses_pt = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

# Criar mapeamento correto
mes_map = df.groupby('mes_mov')['mes_nome'].first().to_dict()

for mes_num in range(1, 13):
    if mes_num in mov_mes.index:
        row = mov_mes.loc[mes_num]
        mes_pt = meses_pt[mes_num - 1]
        print(f"  {mes_pt:<12} {row['qtd']:>15,} {row['pct']:>6.1f}%  {row['valor_mi']:>13.2f}")
    else:
        mes_pt = meses_pt[mes_num - 1]
        print(f"  {mes_pt:<12} {0:>15,} {0:>6.1f}%  {0:>13.2f}")

# Identificar picos e vales
mes_pico = mov_mes['qtd'].idxmax()
mes_vale = mov_mes['qtd'].idxmin()
print(f"\n  🔴 Mês PICO: {meses_pt[mes_pico-1]} ({mov_mes.loc[mes_pico, 'qtd']:,} movimentações)")
print(f"  🔵 Mês VALE: {meses_pt[mes_vale-1]} ({mov_mes.loc[mes_vale, 'qtd']:,} movimentações)")
print(f"  📊 Variação pico/vale: {(mov_mes.loc[mes_pico, 'qtd'] / mov_mes.loc[mes_vale, 'qtd'] - 1) * 100:.1f}%")

# ─────────────────────────────────────────────────────────────────
# 3. PADRÕES TRIMESTRAIS
# ─────────────────────────────────────────────────────────────────
print("\n" + "-"*68)
print("  ANÁLISE TRIMESTRAL")
print("-"*68)

trim = df.groupby('trimestre').agg({
    'codigo_material': 'count',
    'valor_estoque': 'sum'
}).rename(columns={'codigo_material': 'qtd'})
trim['valor_mi'] = trim['valor_estoque'] / 1e6

print(f"\n  {'TRIMESTRE':<12} {'QTD':>8} {'%':>7}  {'VALOR (R$ Mi)':>14}")
print("  " + "-"*46)
for q in [1, 2, 3, 4]:
    if q in trim.index:
        row = trim.loc[q]
        pct = row['qtd'] / total * 100
        print(f"  Q{q} ({['Jan-Mar','Abr-Jun','Jul-Set','Out-Dez'][q-1]:<9}) {row['qtd']:>8,} {pct:>6.1f}%  {row['valor_mi']:>13.2f}")

# Variação entre trimestres
if len(trim) > 1:
    cv_trim = trim['qtd'].std() / trim['qtd'].mean() * 100
    print(f"\n  Coeficiente de Variação (CV) trimestral: {cv_trim:.1f}%")
    if cv_trim < 10:
        print(f"  ✅ Baixa sazonalidade (CV < 10%)")
    elif cv_trim < 25:
        print(f"  ⚠️ Sazonalidade moderada (CV 10-25%)")
    else:
        print(f"  🔴 Alta sazonalidade (CV > 25%)")

# ─────────────────────────────────────────────────────────────────
# 4. SAZONALIDADE POR CATEGORIA
# ─────────────────────────────────────────────────────────────────
print("\n" + "-"*68)
print("  SAZONALIDADE POR CATEGORIA")
print("-"*68)
print("  Analisando variação mensal dentro de cada categoria...")

# Criar matriz categoria × mês
cat_mes = df.groupby(['categoria', 'mes_mov']).size().unstack(fill_value=0)

# Calcular CV (coeficiente de variação) por categoria
cv_categorias = []
for cat in cat_mes.index:
    valores = cat_mes.loc[cat].values
    if valores.mean() > 0:
        cv = (valores.std() / valores.mean()) * 100
        pico_mes = valores.argmax() + 1
        vale_mes = valores.argmin() + 1
        cv_categorias.append({
            'categoria': cat,
            'cv': cv,
            'pico_mes': pico_mes,
            'vale_mes': vale_mes,
            'qtd_media': valores.mean(),
            'pico_qtd': valores.max(),
            'vale_qtd': valores.min()
        })

df_cv = pd.DataFrame(cv_categorias).sort_values('cv', ascending=False)

print(f"\n  TOP 10 CATEGORIAS COM MAIOR SAZONALIDADE:")
print(f"  {'CATEGORIA':<16} {'CV%':>6} {'PICO':>6} {'VALE':>6}  {'MÉDIA/MÊS':>10}")
print("  " + "-"*52)
for _, row in df_cv.head(10).iterrows():
    print(f"  {row['categoria']:<16} {row['cv']:>5.1f}% {meses_pt[int(row['pico_mes'])-1][:3]:>6}"
          f" {meses_pt[int(row['vale_mes'])-1][:3]:>6}  {row['qtd_media']:>9.1f}")

print(f"\n  📊 Interpretação CV (Coeficiente de Variação):")
print(f"     CV < 20%:  Sazonalidade BAIXA (comportamento estável)")
print(f"     CV 20-40%: Sazonalidade MODERADA (planejamento recomendado)")
print(f"     CV > 40%:  Sazonalidade ALTA (ajuste crítico estoque)")

# Contar categorias por nível de sazonalidade
baixa = (df_cv['cv'] < 20).sum()
moderada = ((df_cv['cv'] >= 20) & (df_cv['cv'] < 40)).sum()
alta = (df_cv['cv'] >= 40).sum()

print(f"\n  Distribuição:")
print(f"  • Baixa sazonalidade:    {baixa} categorias")
print(f"  • Moderada sazonalidade: {moderada} categorias")
print(f"  • Alta sazonalidade:     {alta} categorias")

# ─────────────────────────────────────────────────────────────────
# 5. FORECAST BÁSICO (MOVING AVERAGE)
# ─────────────────────────────────────────────────────────────────
print("\n" + "-"*68)
print("  FORECAST — PRÓXIMOS 3 MESES (Abr-Mai-Jun 2026)")
print("-"*68)
print("  Método: Moving Average (Média Móvel) 3 meses")

# Forecast simples por categoria (Top 5 mais movimentadas)
top5_cats = df['categoria'].value_counts().head(5).index

forecast_results = []
for cat in top5_cats:
    df_cat = df[df['categoria'] == cat]
    mov_cat_mes = df_cat.groupby('mes_mov').size()
    
    # Moving Average 3 meses (últimos 3 meses disponíveis)
    if len(mov_cat_mes) >= 3:
        ultimos_3 = mov_cat_mes.tail(3).values
        ma3 = ultimos_3.mean()
        
        forecast_results.append({
            'categoria': cat,
            'ma3': ma3,
            'abr_forecast': ma3,
            'mai_forecast': ma3,
            'jun_forecast': ma3,
            'q2_forecast': ma3 * 3
        })

df_forecast = pd.DataFrame(forecast_results)

print(f"\n  {'CATEGORIA':<16} {'ABR':>6} {'MAI':>6} {'JUN':>6}  {'TOTAL Q2':>10}")
print("  " + "-"*50)
for _, row in df_forecast.iterrows():
    print(f"  {row['categoria']:<16} {row['abr_forecast']:>6.0f} {row['mai_forecast']:>6.0f}"
          f" {row['jun_forecast']:>6.0f}  {row['q2_forecast']:>10,.0f}")

print(f"\n  ⚠️ ATENÇÃO: Forecast usa média simples 3 meses")
print(f"     Para produção, considerar:")
print(f"     • Exponential Smoothing (peso maior meses recentes)")
print(f"     • ARIMA (captura tendências e sazonalidade complexa)")
print(f"     • Machine Learning (múltiplas variáveis)")

# ─────────────────────────────────────────────────────────────────
# 6. RECOMENDAÇÕES DE ESTOQUE_MINIMO
# ─────────────────────────────────────────────────────────────────
print("\n" + "-"*68)
print("  RECOMENDAÇÕES — AJUSTE ESTOQUE_MINIMO SAZONAL")
print("-"*68)

# Para categorias com alta sazonalidade (CV > 40%)
cats_alta_saz = df_cv[df_cv['cv'] > 40]['categoria'].tolist()

if len(cats_alta_saz) > 0:
    print(f"\n  {len(cats_alta_saz)} categorias com ALTA sazonalidade (CV > 40%):")
    print(f"  Recomendação: Ajustar estoque_minimo por mês\n")
    
    for cat in cats_alta_saz[:5]:  # Top 5
        row = df_cv[df_cv['categoria'] == cat].iloc[0]
        pico_mes = int(row['pico_mes'])
        vale_mes = int(row['vale_mes'])
        
        print(f"  📦 {cat}:")
        print(f"     • Mês PICO: {meses_pt[pico_mes-1]} → estoque_minimo +30%")
        print(f"     • Mês VALE: {meses_pt[vale_mes-1]} → estoque_minimo -20%")
        print(f"     • Outros meses: estoque_minimo padrão")
        print()

print(f"  💡 AÇÃO SUGERIDA:")
print(f"     1. Criar campo 'estoque_minimo_sazonal' no cadastro")
print(f"     2. Implementar regra: estoque_min = base × fator_sazonal")
print(f"     3. Fator sazonal: 1.3 (pico), 1.0 (normal), 0.8 (vale)")

# ─────────────────────────────────────────────────────────────────
# 7. IMPACTO FINANCEIRO
# ─────────────────────────────────────────────────────────────────
print("\n" + "-"*68)
print("  IMPACTO FINANCEIRO DO PLANEJAMENTO SAZONAL")
print("-"*68)

# Estimar custos
n_cats_alta_saz = len(cats_alta_saz)
n_cats_mod_saz = len(df_cv[(df_cv['cv'] >= 20) & (df_cv['cv'] < 40)])

# CUSTO 1: Estoque excessivo fora de pico
# Assumindo que 15% do estoque poderia ser reduzido em meses vale
valor_estoque_total = df['valor_estoque'].sum()
economia_estoque = valor_estoque_total * 0.02  # 2% de redução média
custo_capital = economia_estoque * 0.12  # 12% a.a. custo capital
custo_est_ano = custo_capital

# CUSTO 2: Ruptura em picos (pedidos emergenciais)
# Estimando 5 rupturas/ano em categorias alta sazonalidade
custo_ruptura = n_cats_alta_saz * 5 * 50  # R$ 50 por pedido emergencial

# CUSTO 3: Inventários extras
# 2 inventários/ano desnecessários em meses baixa movimentação
custo_inventarios = 2 * 250

# Total
total_custo_anual = custo_est_ano + custo_ruptura + custo_inventarios

print(f"""
  PROBLEMA 1 - ESTOQUE EXCESSIVO FORA DE PICO:
  -> Categorias mantêm estoque constante o ano todo
  -> {n_cats_alta_saz} categorias com alta sazonalidade
  -> Potencial redução 2% estoque em meses vale
  -> Economia: R$ {economia_estoque:,.2f} capital liberado
  -> Custo capital (12% a.a.): R$ {custo_est_ano:,.2f}/ano

  PROBLEMA 2 - RUPTURA EM PERÍODOS DE PICO:
  -> Não antecipar demanda sazonal = falta produto
  -> Estimativa: {n_cats_alta_saz * 5} rupturas/ano (R$ 50/pedido emergencial)
  -> Custo: R$ {custo_ruptura:,.2f}/ano

  PROBLEMA 3 - INVENTÁRIOS DESNECESSÁRIOS:
  -> Contagem completa em meses baixa movimentação
  -> Custo: R$ {custo_inventarios:,.2f}/ano (2 inventários extras)

  +------------------------------------------------------------+
  |         ECONOMIA ANUAL PLANEJAMENTO SAZONAL               |
  |                                                            |
  |  Redução custo capital (estoque otimizado):               |
  |    R$ {custo_est_ano:>10,.2f}/ano                                     |
  |                                                            |
  |  Evitar rupturas e pedidos emergenciais:                  |
  |    R$ {custo_ruptura:>10,.2f}/ano                                     |
  |                                                            |
  |  Inventários otimizados:                                   |
  |    R$ {custo_inventarios:>10,.2f}/ano                                     |
  |                                                            |
  |  TOTAL ANUAL:        R$ {total_custo_anual:>10,.2f}                           |
  |  Custo implementação: R$ {800:>10,.2f} (1× config sistema)    |
  |  ROI: {12 * 800 / (total_custo_anual + 1):.1f} meses                                         |
  +------------------------------------------------------------+
""")

# ─────────────────────────────────────────────────────────────────
# 8. SALVAR ANÁLISE
# ─────────────────────────────────────────────────────────────────
print("-"*68)
print("  SALVANDO ANÁLISE...")
print("-"*68)

# CSV com análise de sazonalidade por categoria
df_cv.to_csv('data/processed/sazonalidade_por_categoria.csv', index=False, encoding='utf-8-sig')
print("✅ Arquivo salvo: data/processed/sazonalidade_por_categoria.csv")

# CSV com forecast
if len(df_forecast) > 0:
    df_forecast.to_csv('data/processed/forecast_q2_2026.csv', index=False, encoding='utf-8-sig')
    print("✅ Arquivo salvo: data/processed/forecast_q2_2026.csv")

# ─────────────────────────────────────────────────────────────────
# 9. VISUALIZAÇÕES
# ─────────────────────────────────────────────────────────────────
print("\n" + "-"*68)
print("  GERANDO DASHBOARD...")
print("-"*68)

BG, PANEL = '#0b1220', '#111927'
BORDER, TEXT, MUTED = '#1e2d40', '#e2e8f0', '#64748b'
C = {'blue':'#38bdf8','green':'#34d399','orange':'#fb923c',
     'red':'#f87171','purple':'#a78bfa','yellow':'#fbbf24','teal':'#2dd4bf'}

def styled(ax):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.xaxis.label.set_color(MUTED); ax.yaxis.label.set_color(MUTED)
    ax.title.set_color(TEXT)
    for s in ax.spines.values(): s.set_color(BORDER)
    ax.grid(color=BORDER, linewidth=0.5, alpha=0.6)
    return ax

fig = plt.figure(figsize=(22, 16), facecolor=BG)
fig.suptitle('DIA 17 — ANÁLISE DE SAZONALIDADE | MDM Supply Chain',
             fontsize=18, color=TEXT, fontweight='bold', y=0.98)
gs = GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.35,
              left=0.05, right=0.97, top=0.93, bottom=0.05)

# G1: Movimentações por mês (linha)
ax1 = styled(fig.add_subplot(gs[0, :2]))
meses_labels = [meses_pt[i] for i in range(12)]
qtd_por_mes = [mov_mes.loc[i+1, 'qtd'] if i+1 in mov_mes.index else 0 for i in range(12)]
ax1.plot(meses_labels, qtd_por_mes, marker='o', linewidth=2.5, 
         markersize=8, color=C['blue'], label='Movimentações')
ax1.axhline(np.mean(qtd_por_mes), color=C['yellow'], linestyle='--', 
            linewidth=2, label=f"Média: {np.mean(qtd_por_mes):.0f}")
ax1.fill_between(range(12), qtd_por_mes, alpha=0.3, color=C['blue'])
ax1.set_title('Movimentações por Mês — Últimos 12 meses', fontsize=12, pad=10)
ax1.set_xlabel('Mês')
ax1.set_ylabel('Quantidade de Materiais')
ax1.legend(fontsize=10, facecolor=PANEL, labelcolor=TEXT)
ax1.tick_params(axis='x', rotation=45)

# G2: Heatmap categoria × mês (Top 10 categorias)
ax2 = styled(fig.add_subplot(gs[0, 2]))
top10_cats = df['categoria'].value_counts().head(10).index
cat_mes_top10 = cat_mes.loc[top10_cats]
sns.heatmap(cat_mes_top10, cmap='YlOrRd', annot=False, fmt='d',
            cbar_kws={'label': 'Movimentações'}, ax=ax2, 
            linewidths=0.5, linecolor=BORDER)
ax2.set_title('Heatmap: Top 10 Categorias × Mês', fontsize=12, pad=10)
ax2.set_xlabel('Mês')
ax2.set_ylabel('Categoria')
ax2.tick_params(colors=TEXT)
cbar = ax2.collections[0].colorbar
cbar.ax.tick_params(colors=TEXT)
cbar.ax.yaxis.label.set_color(TEXT)

# G3: Top 5 categorias com maior sazonalidade (CV)
ax3 = styled(fig.add_subplot(gs[1, 0]))
top5_saz = df_cv.head(5).sort_values('cv')
cores3 = [C['red'] if v > 40 else C['orange'] if v > 20 else C['green'] for v in top5_saz['cv']]
bars3 = ax3.barh(top5_saz['categoria'], top5_saz['cv'], color=cores3, alpha=0.85, height=0.6)
for b, v in zip(bars3, top5_saz['cv']):
    ax3.text(v+1, b.get_y()+b.get_height()/2, f'{v:.1f}%',
             va='center', color=TEXT, fontsize=9, fontweight='bold')
ax3.set_title('Top 5 Categorias — Maior Sazonalidade (CV%)', fontsize=11, pad=10)
ax3.set_xlabel('Coeficiente de Variação (%)')
ax3.axvline(20, color=C['yellow'], linestyle='--', alpha=0.5, label='CV=20%')
ax3.axvline(40, color=C['red'], linestyle='--', alpha=0.5, label='CV=40%')
ax3.legend(fontsize=8, facecolor=PANEL, labelcolor=TEXT)

# G4: Padrões trimestrais
ax4 = styled(fig.add_subplot(gs[1, 1]))
trims = ['Q1\n(Jan-Mar)', 'Q2\n(Abr-Jun)', 'Q3\n(Jul-Set)', 'Q4\n(Out-Dez)']
qtd_trim = [trim.loc[i, 'qtd'] if i in trim.index else 0 for i in [1,2,3,4]]
cores4 = [C['blue'], C['green'], C['orange'], C['purple']]
bars4 = ax4.bar(trims, qtd_trim, color=cores4, alpha=0.85, width=0.6)
for b, v in zip(bars4, qtd_trim):
    ax4.text(b.get_x() + b.get_width()/2, v + 20, f'{v:,}',
             ha='center', va='bottom', color=TEXT, fontsize=10, fontweight='bold')
ax4.set_title('Distribuição por Trimestre', fontsize=11, pad=10)
ax4.set_ylabel('Quantidade de Materiais')
ax4.axhline(np.mean(qtd_trim), color=C['yellow'], linestyle='--', linewidth=2)

# G5: Forecast próximos 3 meses (Top 5)
ax5 = styled(fig.add_subplot(gs[1, 2]))
if len(df_forecast) > 0:
    meses_forecast = ['Abr', 'Mai', 'Jun']
    x = np.arange(len(meses_forecast))
    width = 0.15
    for i, (_, row) in enumerate(df_forecast.iterrows()):
        ax5.bar(x + i*width, [row['abr_forecast'], row['mai_forecast'], row['jun_forecast']],
                width, label=row['categoria'][:12], alpha=0.85)
    ax5.set_title('Forecast Q2 2026 — Top 5 Categorias', fontsize=11, pad=10)
    ax5.set_ylabel('Movimentações Previstas')
    ax5.set_xticks(x + width * 2)
    ax5.set_xticklabels(meses_forecast)
    ax5.legend(fontsize=8, facecolor=PANEL, labelcolor=TEXT, loc='upper left')
else:
    ax5.text(0.5, 0.5, 'Dados insuficientes\npara forecast',
             ha='center', va='center', transform=ax5.transAxes,
             fontsize=12, color=MUTED)
    ax5.set_title('Forecast Q2 2026', fontsize=11, pad=10)

# G6: Distribuição categorias por nível sazonalidade (pizza)
ax6 = styled(fig.add_subplot(gs[2, 0]))
saz_dist = [baixa, moderada, alta]
saz_labels = [f'Baixa\n({baixa})', f'Moderada\n({moderada})', f'Alta\n({alta})']
cores_saz = [C['green'], C['orange'], C['red']]
wedges, texts, autotexts = ax6.pie(saz_dist, labels=saz_labels, colors=cores_saz,
                                     autopct='%1.1f%%', startangle=90,
                                     wedgeprops={'edgecolor': BG, 'linewidth': 2},
                                     textprops={'color': TEXT, 'fontsize': 10})
for autotext in autotexts:
    autotext.set_color(BG)
    autotext.set_fontweight('bold')
ax6.set_title('Distribuição Nível de Sazonalidade', fontsize=11, pad=10)

# G7: Comparação pico vs vale (barras agrupadas Top 5)
ax7 = styled(fig.add_subplot(gs[2, 1]))
top5_pico_vale = df_cv.head(5)
x7 = np.arange(len(top5_pico_vale))
width7 = 0.35
bars_pico = ax7.bar(x7 - width7/2, top5_pico_vale['pico_qtd'], width7,
                    label='Mês Pico', color=C['red'], alpha=0.85)
bars_vale = ax7.bar(x7 + width7/2, top5_pico_vale['vale_qtd'], width7,
                    label='Mês Vale', color=C['blue'], alpha=0.85)
ax7.set_title('Pico vs Vale — Top 5 Categorias Sazonais', fontsize=11, pad=10)
ax7.set_ylabel('Movimentações/Mês')
ax7.set_xticks(x7)
ax7.set_xticklabels([c[:12] for c in top5_pico_vale['categoria']], rotation=45, ha='right')
ax7.legend(fontsize=9, facecolor=PANEL, labelcolor=TEXT)

# G8: KPIs
ax8 = styled(fig.add_subplot(gs[2, 2]))
ax8.axis('off')

kpis_text = f"""
╔══════════════════════════════════════════════╗
║         KPIs SAZONALIDADE — DIA 17          ║
╚══════════════════════════════════════════════╝

📊 ANÁLISE TEMPORAL:
   Total materiais: {total:,}
   Período analisado: {mov_range:,} dias
   
📈 PADRÕES MENSAIS:
   Mês PICO: {meses_pt[mes_pico-1]} ({mov_mes.loc[mes_pico, 'qtd']:,} mov.)
   Mês VALE: {meses_pt[mes_vale-1]} ({mov_mes.loc[mes_vale, 'qtd']:,} mov.)
   Variação: {(mov_mes.loc[mes_pico, 'qtd'] / mov_mes.loc[mes_vale, 'qtd'] - 1) * 100:.1f}%

🎯 SAZONALIDADE CATEGORIAS:
   Baixa (CV<20%):    {baixa} categorias
   Moderada (20-40%): {moderada} categorias
   Alta (CV>40%):     {alta} categorias

💰 ECONOMIA PLANEJAMENTO SAZONAL:
   Custo capital:     R$ {custo_est_ano:,.0f}/ano
   Rupturas evitadas: R$ {custo_ruptura:,.0f}/ano
   Inventários:       R$ {custo_inventarios:,.0f}/ano
   ═════════════════════════════════════════
   TOTAL:             R$ {total_custo_anual:,.0f}/ano
   
🔮 FORECAST Q2 2026:
   Categorias previstas: {len(df_forecast)}
   Método: Moving Average 3 meses
"""

ax8.text(0.05, 0.5, kpis_text, fontsize=9, verticalalignment='center',
         fontfamily='monospace', color=TEXT,
         bbox=dict(boxstyle='round', facecolor=PANEL, edgecolor=BORDER, linewidth=2))

# Salvar
plt.savefig('visualizations/09_sazonalidade.png', dpi=150, bbox_inches='tight', facecolor=BG)
print("\n✅ Dashboard salvo: visualizations/09_sazonalidade.png")
plt.close()

# ─────────────────────────────────────────────────────────────────
# 10. RESUMO EXECUTIVO
# ─────────────────────────────────────────────────────────────────
print("\n" + "="*68)
print("  RESUMO EXECUTIVO — DIA 17")
print("="*68)

print(f"""
✅ ANÁLISE TEMPORAL COMPLETA:
   • {total:,} materiais analisados
   • Período: {mov_range:,} dias de histórico
   • {len(df_cv)} categorias avaliadas

📊 SAZONALIDADE IDENTIFICADA:
   • {alta} categorias com ALTA sazonalidade (CV > 40%)
   • {moderada} categorias com sazonalidade MODERADA (20-40%)
   • {baixa} categorias com BAIXA sazonalidade (CV < 20%)
   
🎯 PADRÕES DETECTADOS:
   • Mês pico: {meses_pt[mes_pico-1]} ({(mov_mes.loc[mes_pico, 'qtd'] / total * 100):.1f}% movimentações)
   • Mês vale: {meses_pt[mes_vale-1]} ({(mov_mes.loc[mes_vale, 'qtd'] / total * 100):.1f}% movimentações)
   • Variação pico/vale: {(mov_mes.loc[mes_pico, 'qtd'] / mov_mes.loc[mes_vale, 'qtd'] - 1) * 100:.1f}%

💰 ECONOMIA IDENTIFICADA: R$ {total_custo_anual:,.2f}/ano
   • Otimização estoque por sazonalidade
   • Prevenção rupturas em períodos pico
   • Inventários direcionados

🔮 FORECAST GERADO:
   • {len(df_forecast)} categorias previstas para Q2 2026
   • Método: Moving Average 3 meses
   
📋 RECOMENDAÇÕES:
   1. Ajustar estoque_minimo por sazonalidade ({alta} categorias prioritárias)
   2. Antecipar compras para mês {meses_pt[mes_pico-1]} (pico)
   3. Reduzir estoque em {meses_pt[mes_vale-1]} (vale)
   4. Implementar forecast automatizado (ARIMA ou ML)
""")

print("="*68)
print("✅ DIA 17 COMPLETO!")
print("="*68)

print(f"""
📁 Arquivos gerados:
   • data/processed/sazonalidade_por_categoria.csv
   • data/processed/forecast_q2_2026.csv
   • visualizations/09_sazonalidade.png

🎯 Próximo: DIA 18-19 — Implementação de Correções Automatizadas
""")
