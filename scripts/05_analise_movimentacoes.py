"""
═══════════════════════════════════════════════════════════════════════════════
PROJETO MDM SUPPLY CHAIN
Script: Análise de Movimentações
Dia 11 - Gestão de Estoque e Movimentações
═══════════════════════════════════════════════════════════════════════════════

OBJETIVO:
Analisar movimentações de estoque para identificar:
- Materiais parados (obsolescência)
- Giro de estoque (otimização)
- Padrões temporais (sazonalidade)
- Capital imobilizado

IMPACTO ESPERADO: R$ 50.000/ano
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

print("\n" + "="*70)
print("📦 DIA 11 — ANÁLISE DE MOVIMENTAÇÕES DE ESTOQUE")
print("="*70 + "\n")

# ═══════════════════════════════════════════════════════════════════════════
# 1. CARREGAR DADOS
# ═══════════════════════════════════════════════════════════════════════════

print("📂 Carregando dados...")
df = pd.read_csv('data/raw/materiais_raw.csv')
print(f"✅ Dados carregados: {len(df):,} materiais\n")

# Converter datas
df['ultima_movimentacao'] = pd.to_datetime(df['ultima_movimentacao'])
df['data_cadastro'] = pd.to_datetime(df['data_cadastro'])

# Data referência (hoje)
data_ref = datetime(2026, 2, 27)  # Data atual do projeto

# Calcular dias sem movimento
df['dias_sem_movimento'] = (data_ref - df['ultima_movimentacao']).dt.days

# Calcular valor em estoque
if 'valor_estoque' not in df.columns:
    df['valor_estoque'] = df['preco_unitario'] * df['estoque_atual']

# ═══════════════════════════════════════════════════════════════════════════
# 2. ESTATÍSTICAS BÁSICAS MOVIMENTAÇÕES
# ═══════════════════════════════════════════════════════════════════════════

print("="*70)
print("📊 ESTATÍSTICAS BÁSICAS - MOVIMENTAÇÕES")
print("="*70 + "\n")

print(f"Média dias sem movimento: {df['dias_sem_movimento'].mean():.0f} dias")
print(f"Mediana dias sem movimento: {df['dias_sem_movimento'].median():.0f} dias")
print(f"Máximo dias sem movimento: {df['dias_sem_movimento'].max():.0f} dias")
print(f"Mínimo dias sem movimento: {df['dias_sem_movimento'].min():.0f} dias\n")

# ═══════════════════════════════════════════════════════════════════════════
# 3. MATERIAIS PARADOS (>365 DIAS)
# ═══════════════════════════════════════════════════════════════════════════

print("="*70)
print("🔴 MATERIAIS PARADOS - SEM MOVIMENTO >365 DIAS")
print("="*70 + "\n")

# Materiais parados
materiais_parados = df[df['dias_sem_movimento'] > 365].copy()
qtd_parados = len(materiais_parados)
perc_parados = (qtd_parados / len(df)) * 100
valor_parado = materiais_parados['valor_estoque'].sum()

print(f"Total materiais parados >365 dias: {qtd_parados:,} ({perc_parados:.1f}%)")
print(f"Capital imobilizado: R$ {valor_parado:,.2f}")
print(f"Custo oportunidade (10% a.a.): R$ {valor_parado * 0.10:,.2f}/ano\n")

# Por categoria
print("Distribuição materiais parados por categoria:\n")
parados_cat = materiais_parados.groupby('categoria').agg({
    'codigo_material': 'count',
    'valor_estoque': 'sum'
}).reset_index()
parados_cat.columns = ['categoria', 'qtd', 'valor_total']
parados_cat = parados_cat.sort_values('valor_total', ascending=False)

for idx, row in parados_cat.head(10).iterrows():
    print(f"{row['categoria']:20s}: {row['qtd']:4d} materiais | R$ {row['valor_total']:,.2f}")

# Top 20 materiais parados por valor
print(f"\n🔴 TOP 20 MATERIAIS PARADOS (maior valor):\n")
top20_parados = materiais_parados.nlargest(20, 'valor_estoque')[
    ['codigo_material', 'descricao', 'categoria', 'dias_sem_movimento', 'valor_estoque']
]
print(top20_parados.to_string(index=False))

# ═══════════════════════════════════════════════════════════════════════════
# 4. FAIXAS DE TEMPO SEM MOVIMENTO
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("📅 DISTRIBUIÇÃO POR FAIXAS DE TEMPO SEM MOVIMENTO")
print("="*70 + "\n")

# Criar faixas
bins = [0, 30, 90, 180, 365, 730, df['dias_sem_movimento'].max()+1]
labels = ['0-30 dias', '31-90 dias', '91-180 dias', '181-365 dias', 
          '366-730 dias', '>730 dias']
df['faixa_movimento'] = pd.cut(df['dias_sem_movimento'], bins=bins, labels=labels, right=False)

# Contar por faixa
faixa_counts = df.groupby('faixa_movimento').agg({
    'codigo_material': 'count',
    'valor_estoque': 'sum'
}).reset_index()
faixa_counts.columns = ['faixa', 'qtd_materiais', 'valor_total']

print("Faixa de Tempo          Qtd Materiais    Valor Total       % Materiais")
print("─"*70)
for idx, row in faixa_counts.iterrows():
    perc = (row['qtd_materiais'] / len(df)) * 100
    print(f"{row['faixa']:20s} {row['qtd_materiais']:6,d}        R$ {row['valor_total']:12,.2f}   {perc:5.1f}%")

# ═══════════════════════════════════════════════════════════════════════════
# 5. GIRO DE ESTOQUE (ESTIMADO)
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("🔄 ANÁLISE DE GIRO DE ESTOQUE")
print("="*70 + "\n")

# Simular giro baseado em tempo sem movimento
# Giro alto: movimento recente (< 30 dias)
# Giro médio: movimento moderado (30-180 dias)
# Giro baixo: movimento lento (> 180 dias)

df['classificacao_giro'] = df['dias_sem_movimento'].apply(
    lambda x: 'Alto' if x < 30 else ('Médio' if x < 180 else 'Baixo')
)

giro_stats = df.groupby('classificacao_giro').agg({
    'codigo_material': 'count',
    'valor_estoque': 'sum'
}).reset_index()
giro_stats.columns = ['giro', 'qtd', 'valor']
giro_stats['perc_qtd'] = (giro_stats['qtd'] / len(df) * 100).round(1)
giro_stats['perc_valor'] = (giro_stats['valor'] / df['valor_estoque'].sum() * 100).round(1)

print("Classificação Giro    Qtd Materiais    % Qtd    Valor Total       % Valor")
print("─"*75)
for idx, row in giro_stats.sort_values('giro').iterrows():
    print(f"{row['giro']:18s} {row['qtd']:6,d}        {row['perc_qtd']:5.1f}%   R$ {row['valor']:12,.2f}   {row['perc_valor']:5.1f}%")

# ═══════════════════════════════════════════════════════════════════════════
# 6. ANÁLISE TEMPORAL - ÚLTIMA MOVIMENTAÇÃO
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("📆 ANÁLISE TEMPORAL - ÚLTIMA MOVIMENTAÇÃO")
print("="*70 + "\n")

# Agrupar por mês de última movimentação
df['mes_ultima_mov'] = df['ultima_movimentacao'].dt.to_period('M')
mov_mensal = df.groupby('mes_ultima_mov').size().reset_index()
mov_mensal.columns = ['mes', 'qtd_materiais']
mov_mensal['mes'] = mov_mensal['mes'].astype(str)

print("Últimos 12 meses - Materiais com última movimentação:\n")
print(mov_mensal.tail(12).to_string(index=False))

# ═══════════════════════════════════════════════════════════════════════════
# 7. MATERIAIS CRÍTICOS (PARADOS + ALTO VALOR)
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("⚠️ MATERIAIS CRÍTICOS - PARADOS E ALTO VALOR")
print("="*70 + "\n")

# Materiais parados >365 dias E valor > mediana
mediana_valor = df['valor_estoque'].median()
criticos = df[
    (df['dias_sem_movimento'] > 365) & 
    (df['valor_estoque'] > mediana_valor)
].copy()

print(f"Total materiais críticos: {len(criticos):,}")
print(f"Valor total crítico: R$ {criticos['valor_estoque'].sum():,.2f}")
print(f"Prioridade: MÁXIMA (alto valor + parado)\n")

if len(criticos) > 0:
    print("Top 15 materiais críticos:\n")
    top15_criticos = criticos.nlargest(15, 'valor_estoque')[
        ['codigo_material', 'descricao', 'categoria', 'dias_sem_movimento', 'valor_estoque']
    ]
    print(top15_criticos.to_string(index=False))

# ═══════════════════════════════════════════════════════════════════════════
# 8. ANÁLISE POR STATUS
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("📋 ANÁLISE DE MOVIMENTAÇÕES POR STATUS")
print("="*70 + "\n")

status_mov = df.groupby('status').agg({
    'codigo_material': 'count',
    'dias_sem_movimento': 'mean',
    'valor_estoque': 'sum'
}).reset_index()
status_mov.columns = ['status', 'qtd', 'dias_med_sem_mov', 'valor_total']

print("Status         Qtd Mat.    Dias Médio    Valor Total")
print("─"*55)
for idx, row in status_mov.iterrows():
    print(f"{row['status']:12s} {row['qtd']:6,d}      {row['dias_med_sem_mov']:6.0f}      R$ {row['valor_total']:,.2f}")

# Materiais inativos com estoque
inativos_estoque = df[
    (df['status'].str.lower() == 'inativo') & 
    (df['estoque_atual'] > 0)
]

if len(inativos_estoque) > 0:
    valor_inativo = inativos_estoque['valor_estoque'].sum()
    print(f"\n⚠️ ALERTA: {len(inativos_estoque):,} materiais INATIVOS com estoque!")
    print(f"   Valor bloqueado: R$ {valor_inativo:,.2f}")
    print(f"   Ação: Liquidar ou reativar urgente\n")

# ═══════════════════════════════════════════════════════════════════════════
# 9. IMPACTO FINANCEIRO
# ═══════════════════════════════════════════════════════════════════════════

print("="*70)
print("💰 IMPACTO FINANCEIRO - MOVIMENTAÇÕES")
print("="*70 + "\n")

# Custos
custo_capital = valor_parado * 0.10  # 10% a.a. custo oportunidade
custo_armazenagem = qtd_parados * 2 * 12  # R$ 2/material/mês
custo_obsolescencia = valor_parado * 0.05  # 5% obsolescência estimada
valor_inativo_bloqueado = inativos_estoque['valor_estoque'].sum() if len(inativos_estoque) > 0 else 0

economia_total = custo_capital + custo_armazenagem + custo_obsolescencia

print("CUSTOS IDENTIFICADOS:")
print(f"   Capital parado (10% a.a.): R$ {custo_capital:,.2f}/ano")
print(f"   Armazenagem materiais parados: R$ {custo_armazenagem:,.2f}/ano")
print(f"   Risco obsolescência (5%): R$ {custo_obsolescencia:,.2f}/ano")
if valor_inativo_bloqueado > 0:
    print(f"   Inativos com estoque bloqueado: R$ {valor_inativo_bloqueado:,.2f}")

print(f"\n─"*70)
print(f"💰 ECONOMIA POTENCIAL ANUAL: R$ {economia_total:,.2f}")
print(f"─"*70)

print(f"\nAÇÕES RECOMENDADAS:")
print(f"   1. Liquidar/doar {qtd_parados:,} materiais parados >365 dias")
print(f"   2. Reduzir estoque materiais giro baixo")
if len(inativos_estoque) > 0:
    print(f"   3. Liquidar {len(inativos_estoque):,} materiais inativos com estoque")
print(f"   4. Implementar política reposição baseada em giro\n")

# ═══════════════════════════════════════════════════════════════════════════
# 10. SALVAR ANÁLISE
# ═══════════════════════════════════════════════════════════════════════════

print("="*70)
print("💾 SALVANDO ANÁLISE DE MOVIMENTAÇÕES")
print("="*70 + "\n")

# CSV análise completa
df_export = df[[
    'codigo_material', 'descricao', 'categoria', 'status',
    'dias_sem_movimento', 'classificacao_giro', 'faixa_movimento',
    'valor_estoque', 'estoque_atual'
]].copy()
df_export = df_export.sort_values('dias_sem_movimento', ascending=False)
df_export.to_csv('data/processed/movimentacoes_analise.csv', index=False, encoding='utf-8-sig')
print("✅ Arquivo salvo: data/processed/movimentacoes_analise.csv")

# CSV materiais críticos
if len(criticos) > 0:
    criticos_export = criticos[[
        'codigo_material', 'descricao', 'categoria', 
        'dias_sem_movimento', 'valor_estoque'
    ]].sort_values('valor_estoque', ascending=False)
    criticos_export.to_csv('data/processed/materiais_criticos_parados.csv', index=False, encoding='utf-8-sig')
    print("✅ Arquivo salvo: data/processed/materiais_criticos_parados.csv")

# ═══════════════════════════════════════════════════════════════════════════
# 11. VISUALIZAÇÕES
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("📊 GERANDO VISUALIZAÇÕES...")
print("="*70 + "\n")

fig = plt.figure(figsize=(16, 12))
gs = GridSpec(4, 2, figure=fig, hspace=0.35, wspace=0.3)

fig.suptitle('DIA 11 — ANÁLISE DE MOVIMENTAÇÕES | Master Data Management', 
             fontsize=16, fontweight='bold', y=0.98)

# 1. Distribuição dias sem movimento (Histograma)
ax1 = fig.add_subplot(gs[0, :])
ax1.hist(df['dias_sem_movimento'], bins=50, color='steelblue', alpha=0.7, edgecolor='black')
ax1.axvline(365, color='red', linestyle='--', linewidth=2, label='365 dias (1 ano)')
ax1.axvline(df['dias_sem_movimento'].mean(), color='orange', linestyle='--', 
           linewidth=2, label=f"Média: {df['dias_sem_movimento'].mean():.0f} dias")
ax1.set_xlabel('Dias Sem Movimento', fontweight='bold')
ax1.set_ylabel('Quantidade de Materiais', fontweight='bold')
ax1.set_title('Distribuição: Dias Sem Movimento', fontweight='bold', fontsize=12)
ax1.legend()
ax1.grid(alpha=0.3)

# 2. Faixas de tempo
ax2 = fig.add_subplot(gs[1, 0])
colors_faixa = ['#27ae60', '#2ecc71', '#f39c12', '#e67e22', '#e74c3c', '#c0392b']
bars = ax2.bar(range(len(faixa_counts)), faixa_counts['qtd_materiais'], 
               color=colors_faixa, alpha=0.7, edgecolor='black')
ax2.set_xticks(range(len(faixa_counts)))
ax2.set_xticklabels(faixa_counts['faixa'], rotation=45, ha='right')
ax2.set_ylabel('Quantidade de Materiais', fontweight='bold')
ax2.set_title('Materiais por Faixa de Tempo', fontweight='bold', fontsize=12)
ax2.grid(axis='y', alpha=0.3)
for i, (bar, val) in enumerate(zip(bars, faixa_counts['qtd_materiais'])):
    ax2.text(bar.get_x() + bar.get_width()/2, val + 20, f'{val:,}', 
            ha='center', fontweight='bold', fontsize=9)

# 3. Classificação Giro
ax3 = fig.add_subplot(gs[1, 1])
giro_order = ['Alto', 'Médio', 'Baixo']
giro_stats_sorted = giro_stats.set_index('giro').reindex(giro_order)
colors_giro = ['#27ae60', '#f39c12', '#e74c3c']
bars = ax3.bar(range(len(giro_stats_sorted)), giro_stats_sorted['qtd'], 
               color=colors_giro, alpha=0.7, edgecolor='black')
ax3.set_xticks(range(len(giro_stats_sorted)))
ax3.set_xticklabels(giro_stats_sorted.index)
ax3.set_ylabel('Quantidade de Materiais', fontweight='bold')
ax3.set_title('Classificação por Giro de Estoque', fontweight='bold', fontsize=12)
ax3.grid(axis='y', alpha=0.3)
for i, (bar, val, perc) in enumerate(zip(bars, giro_stats_sorted['qtd'], giro_stats_sorted['perc_qtd'])):
    ax3.text(bar.get_x() + bar.get_width()/2, val + 30, 
            f'{val:,}\n({perc:.1f}%)', ha='center', fontweight='bold', fontsize=9)

# 4. Top 10 Categorias - Materiais Parados
ax4 = fig.add_subplot(gs[2, 0])
top10_cat_parados = parados_cat.head(10)
y_pos = np.arange(len(top10_cat_parados))
ax4.barh(y_pos, top10_cat_parados['qtd'], color='coral', alpha=0.7, edgecolor='black')
ax4.set_yticks(y_pos)
ax4.set_yticklabels(top10_cat_parados['categoria'])
ax4.set_xlabel('Quantidade de Materiais Parados', fontweight='bold')
ax4.set_title('Top 10 Categorias - Materiais Parados >365 dias', fontweight='bold', fontsize=12)
ax4.invert_yaxis()
ax4.grid(axis='x', alpha=0.3)

# 5. Valor por Faixa de Tempo
ax5 = fig.add_subplot(gs[2, 1])
bars = ax5.bar(range(len(faixa_counts)), faixa_counts['valor_total']/1e6, 
               color=colors_faixa, alpha=0.7, edgecolor='black')
ax5.set_xticks(range(len(faixa_counts)))
ax5.set_xticklabels(faixa_counts['faixa'], rotation=45, ha='right')
ax5.set_ylabel('Valor Total (R$ Milhões)', fontweight='bold')
ax5.set_title('Valor em Estoque por Faixa de Tempo', fontweight='bold', fontsize=12)
ax5.grid(axis='y', alpha=0.3)

# 6. Timeline - Movimentações ao longo do tempo
ax6 = fig.add_subplot(gs[3, 0])
mov_mensal_plot = mov_mensal.tail(12).copy()
mov_mensal_plot['mes_num'] = range(len(mov_mensal_plot))
ax6.plot(mov_mensal_plot['mes_num'], mov_mensal_plot['qtd_materiais'], 
        marker='o', linewidth=2, markersize=6, color='steelblue')
ax6.fill_between(mov_mensal_plot['mes_num'], mov_mensal_plot['qtd_materiais'], 
                 alpha=0.3, color='steelblue')
ax6.set_xticks(mov_mensal_plot['mes_num'])
ax6.set_xticklabels(mov_mensal_plot['mes'], rotation=45, ha='right')
ax6.set_ylabel('Materiais com Movimento', fontweight='bold')
ax6.set_xlabel('Mês (Última Movimentação)', fontweight='bold')
ax6.set_title('Timeline: Movimentações Últimos 12 Meses', fontweight='bold', fontsize=12)
ax6.grid(alpha=0.3)

# 7. KPIs Box
ax7 = fig.add_subplot(gs[3, 1])
ax7.axis('off')

kpis_text = f"""
KPIS MOVIMENTAÇÕES

Materiais Parados >365 dias:
{qtd_parados:,} ({perc_parados:.1f}%)

Capital Imobilizado:
R$ {valor_parado:,.2f}

Giro Alto (<30 dias):
{giro_stats[giro_stats['giro']=='Alto']['qtd'].values[0]:,} materiais

Materiais Críticos:
{len(criticos):,} (parados + alto valor)

ECONOMIA ANUAL:
R$ {economia_total:,.2f}

Custo Capital: R$ {custo_capital:,.2f}
Armazenagem: R$ {custo_armazenagem:,.2f}
Obsolescência: R$ {custo_obsolescencia:,.2f}
"""

ax7.text(0.1, 0.5, kpis_text, fontsize=10, verticalalignment='center',
         bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3), family='monospace')

plt.savefig('visualizations/05_movimentacoes.png', dpi=150, bbox_inches='tight')
print("✅ Dashboard salvo: visualizations/05_movimentacoes.png")
plt.close()

# ═══════════════════════════════════════════════════════════════════════════
# 12. RESUMO EXECUTIVO
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("📊 RESUMO EXECUTIVO - ANÁLISE DE MOVIMENTAÇÕES")
print("="*70 + "\n")

print(f"Total de materiais analisados: {len(df):,}")
print(f"Média dias sem movimento: {df['dias_sem_movimento'].mean():.0f} dias")
print(f"\nMateriais parados >365 dias: {qtd_parados:,} ({perc_parados:.1f}%)")
print(f"Capital imobilizado: R$ {valor_parado:,.2f}")
print(f"\nClassificação Giro:")
for idx, row in giro_stats.iterrows():
    print(f"   {row['giro']:6s}: {row['qtd']:,} materiais ({row['perc_qtd']:.1f}%)")

if len(criticos) > 0:
    print(f"\nMateriais críticos (parados + alto valor): {len(criticos):,}")
    print(f"Valor crítico: R$ {criticos['valor_estoque'].sum():,.2f}")

if len(inativos_estoque) > 0:
    print(f"\nMateriais inativos com estoque: {len(inativos_estoque):,}")
    print(f"Valor bloqueado: R$ {valor_inativo_bloqueado:,.2f}")

print(f"\n💰 ECONOMIA POTENCIAL ANUAL: R$ {economia_total:,.2f}")

print("\n" + "="*70)
print("✅ DIA 11 COMPLETO!")
print("="*70 + "\n")

print("📁 Arquivos gerados:")
print("   • data/processed/movimentacoes_analise.csv")
if len(criticos) > 0:
    print("   • data/processed/materiais_criticos_parados.csv")
print("   • visualizations/05_movimentacoes.png")

print("\n🎯 Próximo: DIA 12 - Análise de Acuracidade (Físico × Sistema)\n")
