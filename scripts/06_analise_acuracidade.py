"""
═══════════════════════════════════════════════════════════════════════════════
PROJETO MDM SUPPLY CHAIN
Script: Análise de Acuracidade de Estoque
Dia 12 - Físico × Sistema (Inventory Accuracy)
═══════════════════════════════════════════════════════════════════════════════

OBJETIVO:
Analisar acuracidade do estoque comparando saldo sistema vs físico:
- Simular divergências realistas
- Calcular score de acuracidade
- Identificar categorias críticas
- Quantificar impacto financeiro (shrinkage)

IMPACTO ESPERADO: R$ 80.000/ano
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

print("\n" + "="*70)
print("📊 DIA 12 — ANÁLISE DE ACURACIDADE DE ESTOQUE")
print("="*70 + "\n")

# ═══════════════════════════════════════════════════════════════════════════
# 1. CARREGAR DADOS
# ═══════════════════════════════════════════════════════════════════════════

print("📂 Carregando dados...")
df = pd.read_csv('data/raw/materiais_raw.csv')
print(f"✅ Dados carregados: {len(df):,} materiais\n")

# Calcular valor em estoque sistema
if 'valor_estoque' not in df.columns:
    df['valor_estoque'] = df['preco_unitario'] * df['estoque_atual']

# ═══════════════════════════════════════════════════════════════════════════
# 2. SIMULAR CONTAGEM FÍSICA (COM DIVERGÊNCIAS REALISTAS)
# ═══════════════════════════════════════════════════════════════════════════

print("="*70)
print("🔄 SIMULANDO CONTAGEM FÍSICA COM DIVERGÊNCIAS REALISTAS")
print("="*70 + "\n")

np.random.seed(42)

# Copiar estoque sistema
df['estoque_sistema'] = df['estoque_atual'].copy()

# Simular estoque físico com divergências
def simular_estoque_fisico(row):
    sistema = row['estoque_sistema']
    categoria = row['categoria']
    
    # Probabilidade de divergência por categoria (algumas mais problemáticas)
    categorias_problematicas = ['Ferramentas', 'Eletronico', 'Escritório']
    
    if categoria in categorias_problematicas:
        # 30% chance divergência significativa
        if np.random.random() < 0.30:
            # Divergência -20% a +10% (mais perdas que sobras)
            divergencia = np.random.uniform(-0.20, 0.10)
        else:
            # Divergência pequena -5% a +5%
            divergencia = np.random.uniform(-0.05, 0.05)
    else:
        # 15% chance divergência
        if np.random.random() < 0.15:
            divergencia = np.random.uniform(-0.15, 0.05)
        else:
            divergencia = np.random.uniform(-0.03, 0.03)
    
    fisico = int(sistema * (1 + divergencia))
    # Estoque físico não pode ser negativo
    fisico = max(0, fisico)
    
    return fisico

df['estoque_fisico'] = df.apply(simular_estoque_fisico, axis=1)

# Calcular divergência
df['divergencia_qtd'] = df['estoque_fisico'] - df['estoque_sistema']
df['divergencia_valor'] = df['divergencia_qtd'] * df['preco_unitario']
df['divergencia_perc'] = ((df['estoque_fisico'] - df['estoque_sistema']) / 
                          df['estoque_sistema'].replace(0, 1) * 100).round(2)

# Valor estoque físico
df['valor_estoque_fisico'] = df['estoque_fisico'] * df['preco_unitario']

print("Simulação de contagem física concluída!")
print(f"Total materiais contados: {len(df):,}\n")

# ═══════════════════════════════════════════════════════════════════════════
# 3. ESTATÍSTICAS GERAIS DE ACURACIDADE
# ═══════════════════════════════════════════════════════════════════════════

print("="*70)
print("📊 ESTATÍSTICAS GERAIS - ACURACIDADE DE ESTOQUE")
print("="*70 + "\n")

# Divergências
total_sistema = df['estoque_sistema'].sum()
total_fisico = df['estoque_fisico'].sum()
divergencia_total_qtd = df['divergencia_qtd'].sum()
divergencia_total_valor = df['divergencia_valor'].sum()

# Acuracidade em quantidade
acuracidade_qtd = (1 - abs(divergencia_total_qtd) / total_sistema) * 100

# Acuracidade em valor
acuracidade_valor = (1 - abs(divergencia_total_valor) / df['valor_estoque'].sum()) * 100

print(f"Estoque Sistema (total): {total_sistema:,} unidades")
print(f"Estoque Físico (total): {total_fisico:,} unidades")
print(f"Divergência Total: {divergencia_total_qtd:,} unidades ({divergencia_total_qtd/total_sistema*100:.2f}%)")
print(f"\nValor Sistema: R$ {df['valor_estoque'].sum():,.2f}")
print(f"Valor Físico: R$ {df['valor_estoque_fisico'].sum():,.2f}")
print(f"Divergência Valor: R$ {divergencia_total_valor:,.2f}")
print(f"\n🎯 ACURACIDADE GERAL:")
print(f"   Quantidade: {acuracidade_qtd:.2f}%")
print(f"   Valor: {acuracidade_valor:.2f}%\n")

# ═══════════════════════════════════════════════════════════════════════════
# 4. ANÁLISE DE DIVERGÊNCIAS POSITIVAS E NEGATIVAS
# ═══════════════════════════════════════════════════════════════════════════

print("="*70)
print("📈 ANÁLISE DE DIVERGÊNCIAS - POSITIVAS × NEGATIVAS")
print("="*70 + "\n")

# Classificar divergências
df['tipo_divergencia'] = df['divergencia_qtd'].apply(
    lambda x: 'Sobra' if x > 0 else ('Falta' if x < 0 else 'OK')
)

# Materiais sem divergência (±2%)
df['acurado'] = df['divergencia_perc'].abs() <= 2

# Estatísticas por tipo
div_stats = df.groupby('tipo_divergencia').agg({
    'codigo_material': 'count',
    'divergencia_valor': 'sum'
}).reset_index()
div_stats.columns = ['tipo', 'qtd_materiais', 'valor_divergencia']

print("Tipo Divergência     Qtd Materiais     Valor Divergência")
print("─"*60)
for idx, row in div_stats.iterrows():
    print(f"{row['tipo']:18s} {row['qtd_materiais']:6,d}          R$ {row['valor_divergencia']:,.2f}")

# Materiais acurados (±2%)
qtd_acurados = df['acurado'].sum()
perc_acurados = (qtd_acurados / len(df)) * 100

print(f"\n✅ Materiais ACURADOS (±2%): {qtd_acurados:,} ({perc_acurados:.1f}%)")
print(f"❌ Materiais COM DIVERGÊNCIA: {len(df) - qtd_acurados:,} ({100-perc_acurados:.1f}%)\n")

# ═══════════════════════════════════════════════════════════════════════════
# 5. SCORE DE ACURACIDADE POR MATERIAL
# ═══════════════════════════════════════════════════════════════════════════

print("="*70)
print("🎯 SCORE DE ACURACIDADE POR MATERIAL")
print("="*70 + "\n")

# Calcular score (100 = perfeito, 0 = muito ruim)
# Score = 100 - abs(divergência%)
df['score_acuracidade'] = 100 - df['divergencia_perc'].abs()
df['score_acuracidade'] = df['score_acuracidade'].clip(lower=0)

# Classificação por score
def classificar_acuracidade(score):
    if score >= 98:
        return 'A'  # Excelente (±2%)
    elif score >= 95:
        return 'B'  # Bom (±5%)
    elif score >= 90:
        return 'C'  # Regular (±10%)
    elif score >= 80:
        return 'D'  # Ruim (±20%)
    else:
        return 'F'  # Crítico (>20%)

df['classe_acuracidade'] = df['score_acuracidade'].apply(classificar_acuracidade)

# Estatísticas por classe
classe_stats = df.groupby('classe_acuracidade').agg({
    'codigo_material': 'count',
    'valor_estoque': 'sum',
    'divergencia_valor': 'sum'
}).reset_index()
classe_stats.columns = ['classe', 'qtd_materiais', 'valor_estoque', 'divergencia']
classe_stats['perc_materiais'] = (classe_stats['qtd_materiais'] / len(df) * 100).round(1)

print("Classe   Qtd Mat.    % Mat.    Valor Estoque       Divergência")
print("─"*70)
for idx, row in classe_stats.sort_values('classe').iterrows():
    print(f"  {row['classe']:3s}    {row['qtd_materiais']:5,d}     {row['perc_materiais']:5.1f}%   R$ {row['valor_estoque']:12,.2f}   R$ {row['divergencia']:12,.2f}")

# ═══════════════════════════════════════════════════════════════════════════
# 6. ANÁLISE POR CATEGORIA
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("📦 ANÁLISE DE ACURACIDADE POR CATEGORIA")
print("="*70 + "\n")

cat_stats = df.groupby('categoria').agg({
    'codigo_material': 'count',
    'score_acuracidade': 'mean',
    'divergencia_valor': lambda x: abs(x).sum(),
    'valor_estoque': 'sum'
}).reset_index()
cat_stats.columns = ['categoria', 'qtd_materiais', 'score_medio', 
                     'divergencia_abs', 'valor_estoque']
cat_stats = cat_stats.sort_values('score_medio')

print("Categoria            Score Médio   Divergência Abs      Valor Estoque")
print("─"*75)
for idx, row in cat_stats.iterrows():
    print(f"{row['categoria']:18s}    {row['score_medio']:6.2f}%    R$ {row['divergencia_abs']:13,.2f}   R$ {row['valor_estoque']:12,.2f}")

# Top 5 piores categorias
print(f"\n🔴 TOP 5 CATEGORIAS COM PIOR ACURACIDADE:\n")
top5_piores = cat_stats.head(5)
for idx, row in top5_piores.iterrows():
    print(f"   {row['categoria']:20s}: Score {row['score_medio']:.2f}% | Div R$ {row['divergencia_abs']:,.2f}")

# ═══════════════════════════════════════════════════════════════════════════
# 7. MATERIAIS CRÍTICOS (ALTO VALOR + BAIXA ACURACIDADE)
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("⚠️ MATERIAIS CRÍTICOS - ALTO VALOR + BAIXA ACURACIDADE")
print("="*70 + "\n")

# Materiais críticos: Score < 90% E Valor > mediana
mediana_valor = df['valor_estoque'].median()
criticos = df[
    (df['score_acuracidade'] < 90) & 
    (df['valor_estoque'] > mediana_valor)
].copy()

print(f"Total materiais críticos: {len(criticos):,}")
print(f"Valor total envolvido: R$ {criticos['valor_estoque'].sum():,.2f}")
print(f"Divergência total: R$ {criticos['divergencia_valor'].abs().sum():,.2f}\n")

if len(criticos) > 0:
    print("Top 20 materiais críticos (prioridade auditoria):\n")
    top20_criticos = criticos.nlargest(20, 'valor_estoque')[
        ['codigo_material', 'descricao', 'categoria', 'score_acuracidade', 
         'divergencia_qtd', 'divergencia_valor']
    ]
    print(top20_criticos.to_string(index=False))

# ═══════════════════════════════════════════════════════════════════════════
# 8. SHRINKAGE (PERDA) - ANÁLISE FINANCEIRA
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("💰 SHRINKAGE - ANÁLISE DE PERDAS")
print("="*70 + "\n")

# Shrinkage = perdas (divergências negativas)
perdas = df[df['divergencia_valor'] < 0]['divergencia_valor'].sum()
sobras = df[df['divergencia_valor'] > 0]['divergencia_valor'].sum()
shrinkage_liquido = perdas + sobras  # Perdas são negativas

print(f"Perdas (faltas): R$ {abs(perdas):,.2f}")
print(f"Sobras (excesso): R$ {sobras:,.2f}")
print(f"Shrinkage Líquido: R$ {abs(shrinkage_liquido):,.2f}")
print(f"\n% Shrinkage: {abs(shrinkage_liquido) / df['valor_estoque'].sum() * 100:.2f}%")

# Shrinkage por categoria
shrink_cat = df.groupby('categoria')['divergencia_valor'].sum().sort_values()
print(f"\nTop 5 categorias com maior shrinkage:\n")
for cat, valor in shrink_cat.head(5).items():
    print(f"   {cat:20s}: R$ {abs(valor):,.2f}")

# ═══════════════════════════════════════════════════════════════════════════
# 9. IMPACTO FINANCEIRO E PLANO DE AÇÃO
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("💰 IMPACTO FINANCEIRO - ACURACIDADE")
print("="*70 + "\n")

# Custos
custo_shrinkage = abs(shrinkage_liquido)  # Perda direta
custo_contagem = len(df) * 2  # R$ 2 por material contado (custo inventário)
custo_ajustes = len(df[~df['acurado']]) * 5  # R$ 5 por ajuste necessário
custo_indisponibilidade = abs(perdas) * 0.05  # 5% do valor perdido em vendas perdidas

economia_total = custo_shrinkage + custo_ajustes + custo_indisponibilidade

print("CUSTOS IDENTIFICADOS:")
print(f"   Shrinkage (perdas): R$ {custo_shrinkage:,.2f}")
print(f"   Ajustes sistema: R$ {custo_ajustes:,.2f}")
print(f"   Indisponibilidade: R$ {custo_indisponibilidade:,.2f}")
print(f"   Custo inventário anual: R$ {custo_contagem * 12:,.2f}")

print(f"\n─"*70)
print(f"💰 ECONOMIA POTENCIAL (MELHORAR ACURACIDADE): R$ {economia_total:,.2f}/ano")
print(f"─"*70)

print(f"\n📋 PLANO DE AÇÃO RECOMENDADO:")
print(f"   1. Inventário cíclico semanal - Classe A (críticos)")
print(f"   2. Auditoria imediata Top 20 materiais críticos")
print(f"   3. Investigar causas shrinkage top 5 categorias")
print(f"   4. Implementar contagem dupla materiais alto valor")
print(f"   5. Treinar equipe registro movimentações")
print(f"   6. Meta: Acuracidade >95% em 90 dias\n")

# ═══════════════════════════════════════════════════════════════════════════
# 10. SALVAR ANÁLISE
# ═══════════════════════════════════════════════════════════════════════════

print("="*70)
print("💾 SALVANDO ANÁLISE DE ACURACIDADE")
print("="*70 + "\n")

# CSV análise completa
df_export = df[[
    'codigo_material', 'descricao', 'categoria',
    'estoque_sistema', 'estoque_fisico', 'divergencia_qtd', 'divergencia_perc',
    'divergencia_valor', 'score_acuracidade', 'classe_acuracidade',
    'valor_estoque', 'valor_estoque_fisico'
]].copy()
df_export = df_export.sort_values('score_acuracidade')
df_export.to_csv('data/processed/acuracidade_analise.csv', index=False, encoding='utf-8-sig')
print("✅ Arquivo salvo: data/processed/acuracidade_analise.csv")

# CSV materiais críticos
if len(criticos) > 0:
    criticos_export = criticos[[
        'codigo_material', 'descricao', 'categoria',
        'estoque_sistema', 'estoque_fisico', 'divergencia_qtd',
        'score_acuracidade', 'divergencia_valor', 'valor_estoque'
    ]].sort_values('valor_estoque', ascending=False)
    criticos_export.to_csv('data/processed/materiais_criticos_acuracidade.csv', 
                          index=False, encoding='utf-8-sig')
    print("✅ Arquivo salvo: data/processed/materiais_criticos_acuracidade.csv")

# ═══════════════════════════════════════════════════════════════════════════
# 11. VISUALIZAÇÕES
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("📊 GERANDO VISUALIZAÇÕES...")
print("="*70 + "\n")

fig = plt.figure(figsize=(16, 12))
gs = GridSpec(4, 2, figure=fig, hspace=0.35, wspace=0.3)

fig.suptitle('DIA 12 — ANÁLISE DE ACURACIDADE DE ESTOQUE | Physical × System', 
             fontsize=16, fontweight='bold', y=0.98)

# 1. Distribuição Score Acuracidade
ax1 = fig.add_subplot(gs[0, :])
ax1.hist(df['score_acuracidade'], bins=50, color='steelblue', alpha=0.7, edgecolor='black')
ax1.axvline(98, color='green', linestyle='--', linewidth=2, label='Meta 98% (Classe A)')
ax1.axvline(df['score_acuracidade'].mean(), color='red', linestyle='--', 
           linewidth=2, label=f"Média: {df['score_acuracidade'].mean():.1f}%")
ax1.set_xlabel('Score de Acuracidade (%)', fontweight='bold')
ax1.set_ylabel('Quantidade de Materiais', fontweight='bold')
ax1.set_title('Distribuição: Score de Acuracidade', fontweight='bold', fontsize=12)
ax1.legend()
ax1.grid(alpha=0.3)

# 2. Classificação A/B/C/D/F
ax2 = fig.add_subplot(gs[1, 0])
classe_plot = classe_stats.sort_values('classe')
colors_classe = ['#27ae60', '#2ecc71', '#f39c12', '#e67e22', '#e74c3c']
bars = ax2.bar(range(len(classe_plot)), classe_plot['qtd_materiais'], 
               color=colors_classe, alpha=0.7, edgecolor='black')
ax2.set_xticks(range(len(classe_plot)))
ax2.set_xticklabels(classe_plot['classe'])
ax2.set_ylabel('Quantidade de Materiais', fontweight='bold')
ax2.set_title('Distribuição por Classe (A=Excelente, F=Crítico)', 
              fontweight='bold', fontsize=12)
ax2.grid(axis='y', alpha=0.3)
for i, (bar, val, perc) in enumerate(zip(bars, classe_plot['qtd_materiais'], 
                                          classe_plot['perc_materiais'])):
    ax2.text(bar.get_x() + bar.get_width()/2, val + 20, 
            f'{val:,}\n({perc:.1f}%)', ha='center', fontweight='bold', fontsize=9)

# 3. Divergências Positivas × Negativas
ax3 = fig.add_subplot(gs[1, 1])
div_plot = div_stats.set_index('tipo')
colors_div = {'Falta': '#e74c3c', 'OK': '#27ae60', 'Sobra': '#3498db'}
bars = ax3.bar(range(len(div_plot)), div_plot['qtd_materiais'],
               color=[colors_div.get(idx, 'gray') for idx in div_plot.index],
               alpha=0.7, edgecolor='black')
ax3.set_xticks(range(len(div_plot)))
ax3.set_xticklabels(div_plot.index)
ax3.set_ylabel('Quantidade de Materiais', fontweight='bold')
ax3.set_title('Tipo de Divergência', fontweight='bold', fontsize=12)
ax3.grid(axis='y', alpha=0.3)

# 4. Top 10 Categorias - Pior Acuracidade
ax4 = fig.add_subplot(gs[2, 0])
top10_cat = cat_stats.head(10)
y_pos = np.arange(len(top10_cat))
ax4.barh(y_pos, top10_cat['score_medio'], color='coral', alpha=0.7, edgecolor='black')
ax4.set_yticks(y_pos)
ax4.set_yticklabels(top10_cat['categoria'])
ax4.set_xlabel('Score Médio de Acuracidade (%)', fontweight='bold')
ax4.set_title('Top 10 Categorias - Pior Acuracidade', fontweight='bold', fontsize=12)
ax4.axvline(95, color='green', linestyle='--', alpha=0.5, label='Meta 95%')
ax4.invert_yaxis()
ax4.grid(axis='x', alpha=0.3)
ax4.legend()

# 5. Shrinkage por Categoria (Top 10)
ax5 = fig.add_subplot(gs[2, 1])
shrink_cat_plot = shrink_cat.head(10).abs().sort_values(ascending=True)
y_pos = np.arange(len(shrink_cat_plot))
ax5.barh(y_pos, shrink_cat_plot.values/1e6, color='#e74c3c', alpha=0.7, edgecolor='black')
ax5.set_yticks(y_pos)
ax5.set_yticklabels(shrink_cat_plot.index)
ax5.set_xlabel('Shrinkage (R$ Milhões)', fontweight='bold')
ax5.set_title('Top 10 Categorias - Maior Shrinkage', fontweight='bold', fontsize=12)
ax5.invert_yaxis()
ax5.grid(axis='x', alpha=0.3)

# 6. Scatter: Score × Valor
ax6 = fig.add_subplot(gs[3, 0])
scatter = ax6.scatter(df['score_acuracidade'], df['valor_estoque']/1e6,
                     c=df['divergencia_qtd'], cmap='RdYlGn', 
                     alpha=0.6, s=30, edgecolors='black', linewidth=0.3)
ax6.set_xlabel('Score de Acuracidade (%)', fontweight='bold')
ax6.set_ylabel('Valor em Estoque (R$ Milhões)', fontweight='bold')
ax6.set_title('Score × Valor (cor = divergência qtd)', fontweight='bold', fontsize=12)
ax6.axvline(95, color='red', linestyle='--', alpha=0.5)
ax6.grid(alpha=0.3)
plt.colorbar(scatter, ax=ax6, label='Divergência Qtd')

# 7. KPIs Box
ax7 = fig.add_subplot(gs[3, 1])
ax7.axis('off')

kpis_text = f"""
KPIS ACURACIDADE

Acuracidade Geral:
Qtd: {acuracidade_qtd:.2f}%
Valor: {acuracidade_valor:.2f}%

Materiais Acurados (±2%):
{qtd_acurados:,} ({perc_acurados:.1f}%)

Classe A (≥98%):
{classe_stats[classe_stats['classe']=='A']['qtd_materiais'].values[0]:,} materiais

Materiais Críticos:
{len(criticos):,} (alto valor + baixa acur.)

SHRINKAGE:
R$ {abs(shrinkage_liquido):,.2f}
({abs(shrinkage_liquido) / df['valor_estoque'].sum() * 100:.2f}% do estoque)

ECONOMIA POTENCIAL:
R$ {economia_total:,.2f}/ano
"""

ax7.text(0.1, 0.5, kpis_text, fontsize=10, verticalalignment='center',
         bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3), family='monospace')

plt.savefig('visualizations/06_acuracidade.png', dpi=150, bbox_inches='tight')
print("✅ Dashboard salvo: visualizations/06_acuracidade.png")
plt.close()

# ═══════════════════════════════════════════════════════════════════════════
# 12. RESUMO EXECUTIVO
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("📊 RESUMO EXECUTIVO - ANÁLISE DE ACURACIDADE")
print("="*70 + "\n")

print(f"Acuracidade Geral: {acuracidade_qtd:.2f}% (quantidade) | {acuracidade_valor:.2f}% (valor)")
print(f"Materiais acurados (±2%): {qtd_acurados:,} ({perc_acurados:.1f}%)")
print(f"Materiais críticos (alto valor + baixa acur.): {len(criticos):,}")
print(f"\nShrinkage (perdas): R$ {abs(shrinkage_liquido):,.2f} ({abs(shrinkage_liquido) / df['valor_estoque'].sum() * 100:.2f}%)")
print(f"Top categoria pior acuracidade: {cat_stats.iloc[0]['categoria']} ({cat_stats.iloc[0]['score_medio']:.2f}%)")

print(f"\n💰 ECONOMIA POTENCIAL ANUAL: R$ {economia_total:,.2f}")
print(f"   Reduzir shrinkage: R$ {custo_shrinkage:,.2f}")
print(f"   Otimizar ajustes: R$ {custo_ajustes:,.2f}")
print(f"   Evitar indisponibilidade: R$ {custo_indisponibilidade:,.2f}")

print("\n" + "="*70)
print("✅ DIA 12 COMPLETO!")
print("="*70 + "\n")

print("📁 Arquivos gerados:")
print("   • data/processed/acuracidade_analise.csv")
if len(criticos) > 0:
    print("   • data/processed/materiais_criticos_acuracidade.csv")
print("   • visualizations/06_acuracidade.png")

print("\n🎯 Próximo: DIA 13 - Power BI (Dashboard Interativo)\n")
