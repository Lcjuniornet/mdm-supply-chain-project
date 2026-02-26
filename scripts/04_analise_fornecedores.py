"""
═══════════════════════════════════════════════════════════════════════════════
PROJETO MDM SUPPLY CHAIN
Script: Análise de Fornecedores
Dia 10 - Gestão de Base de Fornecedores
═══════════════════════════════════════════════════════════════════════════════

OBJETIVO:
Analisar base de fornecedores para identificar:
- Concentração e risco de dependência
- Materiais sem fornecedor definido
- Oportunidades de consolidação
- Impacto financeiro da má gestão de fornecedores

IMPACTO ESPERADO: R$ 15.000/ano
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

print("\n" + "="*70)
print("📦 DIA 10 — ANÁLISE DE FORNECEDORES")
print("="*70 + "\n")

# ═══════════════════════════════════════════════════════════════════════════
# 1. CARREGAR DADOS
# ═══════════════════════════════════════════════════════════════════════════

print("📂 Carregando dados...")
import os
# Tenta caminhos relativos ao script ou ao diretório atual
for _path in ['data/raw/materiais_raw.csv', '../data/raw/materiais_raw.csv', 'materiais_raw.csv']:
    if os.path.exists(_path):
        _csv_path = _path
        break
else:
    _csv_path = 'data/raw/materiais_raw.csv'
df = pd.read_csv(_csv_path)
print(f"✅ Dados carregados: {len(df):,} materiais\n")

# ═══════════════════════════════════════════════════════════════════════════
# 2. ESTATÍSTICAS BÁSICAS FORNECEDORES
# ═══════════════════════════════════════════════════════════════════════════

print("="*70)
print("📊 ESTATÍSTICAS BÁSICAS DE FORNECEDORES")
print("="*70 + "\n")

# Fornecedores únicos
fornecedores_unicos = df['fornecedor_principal'].dropna().nunique()
total_materiais = len(df)
materiais_sem_fornecedor = df['fornecedor_principal'].isna().sum()
materiais_com_fornecedor = total_materiais - materiais_sem_fornecedor

print(f"Total de fornecedores únicos: {fornecedores_unicos:,}")
print(f"Total de materiais: {total_materiais:,}")
print(f"Materiais COM fornecedor: {materiais_com_fornecedor:,} ({materiais_com_fornecedor/total_materiais*100:.1f}%)")
print(f"Materiais SEM fornecedor: {materiais_sem_fornecedor:,} ({materiais_sem_fornecedor/total_materiais*100:.1f}%)")
print(f"\nMédia materiais por fornecedor: {materiais_com_fornecedor/fornecedores_unicos:.1f}\n")

# ═══════════════════════════════════════════════════════════════════════════
# 3. CONCENTRAÇÃO DE FORNECEDORES (CURVA ABC)
# ═══════════════════════════════════════════════════════════════════════════

print("="*70)
print("📈 CURVA ABC DE FORNECEDORES")
print("="*70 + "\n")

# Agrupar por fornecedor
df_fornecedores = df[df['fornecedor_principal'].notna()].groupby('fornecedor_principal').agg({
    'codigo_material': 'count',
    'preco_unitario': lambda x: (x * df.loc[x.index, 'estoque_atual']).sum()
}).reset_index()

df_fornecedores.columns = ['fornecedor', 'qtd_materiais', 'valor_total']

# Ordenar por valor
df_fornecedores = df_fornecedores.sort_values('valor_total', ascending=False)

# Calcular percentual acumulado
df_fornecedores['valor_acumulado'] = df_fornecedores['valor_total'].cumsum()
valor_total_fornecedores = df_fornecedores['valor_total'].sum()
df_fornecedores['perc_acumulado'] = (df_fornecedores['valor_acumulado'] / valor_total_fornecedores) * 100

# Classificação ABC
df_fornecedores['classe_abc'] = df_fornecedores['perc_acumulado'].apply(
    lambda x: 'A' if x <= 80 else ('B' if x <= 95 else 'C')
)

# Adicionar perc_valor a df_fornecedores (necessário para fornecedores_criticos)
df_fornecedores['perc_valor'] = (df_fornecedores['valor_total'] / valor_total_fornecedores * 100).round(1)

# Estatísticas ABC
abc_stats = df_fornecedores.groupby('classe_abc').agg({
    'fornecedor': 'count',
    'qtd_materiais': 'sum',
    'valor_total': 'sum'
}).reset_index()

abc_stats['perc_fornecedores'] = (abc_stats['fornecedor'] / len(df_fornecedores) * 100).round(1)
abc_stats['perc_valor'] = (abc_stats['valor_total'] / valor_total_fornecedores * 100).round(1)

print("Classificação ABC de Fornecedores:\n")
print(abc_stats.to_string(index=False))

# Top 10 fornecedores
print(f"\n🏆 TOP 10 FORNECEDORES POR VALOR:\n")
top10 = df_fornecedores.head(10)[['fornecedor', 'qtd_materiais', 'valor_total', 'perc_acumulado']]
for idx, row in top10.iterrows():
    print(f"{row['fornecedor']:30s} | {row['qtd_materiais']:3d} materiais | R$ {row['valor_total']:,.2f} | {row['perc_acumulado']:.1f}%")

# ═══════════════════════════════════════════════════════════════════════════
# 4. RISCO DE DEPENDÊNCIA
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("⚠️ ANÁLISE DE RISCO - DEPENDÊNCIA DE FORNECEDORES")
print("="*70 + "\n")

# Fornecedores Classe A (críticos)
fornecedores_criticos = df_fornecedores[df_fornecedores['classe_abc'] == 'A']
print(f"Fornecedores Classe A (críticos): {len(fornecedores_criticos)}")
print(f"Representam {fornecedores_criticos['perc_valor'].sum():.1f}% do valor total")
print(f"Responsáveis por {fornecedores_criticos['qtd_materiais'].sum():,} materiais\n")

# Fornecedor mais crítico (maior concentração)
fornecedor_maior = df_fornecedores.iloc[0]
print(f"🚨 FORNECEDOR MAIS CRÍTICO:")
print(f"   Nome: {fornecedor_maior['fornecedor']}")
print(f"   Materiais: {fornecedor_maior['qtd_materiais']}")
print(f"   Valor: R$ {fornecedor_maior['valor_total']:,.2f}")
print(f"   % do total: {fornecedor_maior['valor_total']/valor_total_fornecedores*100:.1f}%")
print(f"   Risco: ALTO (muita dependência!)\n")

# ═══════════════════════════════════════════════════════════════════════════
# 5. MATERIAIS SEM FORNECEDOR (PROBLEMA)
# ═══════════════════════════════════════════════════════════════════════════

print("="*70)
print("🔴 MATERIAIS SEM FORNECEDOR DEFINIDO")
print("="*70 + "\n")

if materiais_sem_fornecedor > 0:
    df_sem_fornecedor = df[df['fornecedor_principal'].isna()]
    
    # Valor bloqueado
    valor_bloqueado = (df_sem_fornecedor['preco_unitario'] * df_sem_fornecedor['estoque_atual']).sum()
    
    print(f"Total materiais sem fornecedor: {materiais_sem_fornecedor:,} ({materiais_sem_fornecedor/total_materiais*100:.1f}%)")
    print(f"Valor em estoque bloqueado: R$ {valor_bloqueado:,.2f}")
    
    # Por categoria
    print(f"\nDistribuição por categoria:")
    sem_forn_cat = df_sem_fornecedor['categoria'].value_counts().head(5)
    for cat, qtd in sem_forn_cat.items():
        print(f"   {cat:20s}: {qtd:4d} materiais")
    
    # Top 20 materiais sem fornecedor (por valor)
    print(f"\n🔴 TOP 20 MATERIAIS SEM FORNECEDOR (maior valor):\n")
    df_sem_fornecedor['valor_estoque'] = df_sem_fornecedor['preco_unitario'] * df_sem_fornecedor['estoque_atual']
    top20_sem = df_sem_fornecedor.nlargest(20, 'valor_estoque')[
        ['codigo_material', 'descricao', 'categoria', 'valor_estoque']
    ]
    print(top20_sem.to_string(index=False))
else:
    print("✅ Todos materiais têm fornecedor definido!")

# ═══════════════════════════════════════════════════════════════════════════
# 6. FORNECEDORES COM POUCOS MATERIAIS (CONSOLIDAÇÃO)
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("📉 OPORTUNIDADE DE CONSOLIDAÇÃO")
print("="*70 + "\n")

# Fornecedores com 1-5 materiais
fornecedores_pequenos = df_fornecedores[df_fornecedores['qtd_materiais'] <= 5]
print(f"Fornecedores com ≤5 materiais: {len(fornecedores_pequenos)} ({len(fornecedores_pequenos)/len(df_fornecedores)*100:.1f}%)")
print(f"Total de materiais: {fornecedores_pequenos['qtd_materiais'].sum()}")
print(f"Valor envolvido: R$ {fornecedores_pequenos['valor_total'].sum():,.2f}\n")

print("💡 OPORTUNIDADE:")
print(f"   Consolidar {len(fornecedores_pequenos)} fornecedores pequenos")
print(f"   em 5-10 fornecedores maiores")
print(f"   Redução de {len(fornecedores_pequenos)} → 10 fornecedores")
print(f"   Economia gestão: ~R$ 8.000/ano\n")

# ═══════════════════════════════════════════════════════════════════════════
# 7. QUALIDADE CADASTRAL FORNECEDORES
# ═══════════════════════════════════════════════════════════════════════════

print("="*70)
print("📋 QUALIDADE CADASTRAL - FORNECEDORES")
print("="*70 + "\n")

# Inconsistências de caixa (upper/lower)
df_com_fornecedor = df[df['fornecedor_principal'].notna()].copy()

def tipo_caixa(texto):
    if pd.isna(texto):
        return 'NULO'
    s = str(texto).strip()
    if s == s.upper():
        return 'MAIÚSCULA'
    if s == s.lower():
        return 'minúscula'
    if s == s.title():
        return 'Title Case'
    return 'Mista'

# Análise de caixa
caixa_dist = df_com_fornecedor['fornecedor_principal'].apply(tipo_caixa).value_counts()
print("Padrão de caixa (upper/lower):")
for padrao, qtd in caixa_dist.items():
    print(f"   {padrao:15s}: {qtd:,} ({qtd/len(df_com_fornecedor)*100:.1f}%)")

# Variações do mesmo fornecedor
print(f"\n🔍 Detectando variações do mesmo fornecedor:")
fornecedor_normalizado = df_com_fornecedor['fornecedor_principal'].str.lower().str.strip()
variações = fornecedor_normalizado.value_counts()
fornecedores_originais = df_com_fornecedor['fornecedor_principal'].value_counts()

duplicados_potenciais = 0
for forn_norm, count_norm in variações.items():
    # Ver quantas formas diferentes existem desse fornecedor
    formas_diferentes = df_com_fornecedor[
        df_com_fornecedor['fornecedor_principal'].str.lower().str.strip() == forn_norm
    ]['fornecedor_principal'].unique()
    
    if len(formas_diferentes) > 1:
        duplicados_potenciais += len(formas_diferentes) - 1
        print(f"\n   {forn_norm.upper()}:")
        for forma in formas_diferentes:
            qtd = (df_com_fornecedor['fornecedor_principal'] == forma).sum()
            print(f"      • '{forma}' ({qtd} materiais)")

if duplicados_potenciais > 0:
    print(f"\n⚠️ Identificadas {duplicados_potenciais} variações que podem ser consolidadas")
else:
    print("\n✅ Nenhuma variação detectada")

# ═══════════════════════════════════════════════════════════════════════════
# 8. IMPACTO FINANCEIRO
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("💰 IMPACTO FINANCEIRO - GESTÃO DE FORNECEDORES")
print("="*70 + "\n")

# Custos atuais
custo_gestao_fornecedor = 50  # R$/fornecedor/mês
custo_anual_atual = fornecedores_unicos * custo_gestao_fornecedor * 12

# Cenário otimizado
fornecedores_otimizados = fornecedores_unicos - len(fornecedores_pequenos) + 10  # Consolidar pequenos em 10
custo_anual_otimizado = fornecedores_otimizados * custo_gestao_fornecedor * 12

economia_consolidacao = custo_anual_atual - custo_anual_otimizado

# Custo materiais sem fornecedor
custo_sem_fornecedor = materiais_sem_fornecedor * 10 * 12  # R$ 10/material/mês em retrabalho

# Custo variações (duplicados)
custo_variações = duplicados_potenciais * 5 * 12  # R$ 5/variação/mês em confusão

# Total
economia_total = economia_consolidacao + custo_sem_fornecedor + custo_variações

print("CUSTOS ATUAIS:")
print(f"   Gestão {fornecedores_unicos} fornecedores: R$ {custo_anual_atual:,.2f}/ano")
print(f"   Materiais sem fornecedor: R$ {custo_sem_fornecedor:,.2f}/ano")
print(f"   Variações cadastrais: R$ {custo_variações:,.2f}/ano")
print(f"   TOTAL: R$ {custo_anual_atual + custo_sem_fornecedor + custo_variações:,.2f}/ano\n")

print("CENÁRIO OTIMIZADO:")
print(f"   Gestão {fornecedores_otimizados} fornecedores: R$ {custo_anual_otimizado:,.2f}/ano")
print(f"   Materiais sem fornecedor: R$ 0 (corrigidos)")
print(f"   Variações cadastrais: R$ 0 (padronizados)")
print(f"   TOTAL: R$ {custo_anual_otimizado:,.2f}/ano\n")

print("─"*70)
print(f"💰 ECONOMIA ANUAL TOTAL: R$ {economia_total:,.2f}")
print("─"*70 + "\n")

# ═══════════════════════════════════════════════════════════════════════════
# 9. SALVAR ANÁLISE
# ═══════════════════════════════════════════════════════════════════════════

print("="*70)
print("💾 SALVANDO ANÁLISE DE FORNECEDORES")
print("="*70 + "\n")

# CSV com análise completa
os.makedirs('data/processed', exist_ok=True)
df_fornecedores.to_csv('data/processed/fornecedores_analise.csv', index=False, encoding='utf-8-sig')
print("✅ Arquivo salvo: data/processed/fornecedores_analise.csv")

# CSV materiais sem fornecedor (se existir)
if materiais_sem_fornecedor > 0:
    top20_sem.to_csv('data/processed/materiais_sem_fornecedor.csv', index=False, encoding='utf-8-sig')
    print("✅ Arquivo salvo: data/processed/materiais_sem_fornecedor.csv")

# ═══════════════════════════════════════════════════════════════════════════
# 10. VISUALIZAÇÕES
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("📊 GERANDO VISUALIZAÇÕES...")
print("="*70 + "\n")

fig = plt.figure(figsize=(16, 10))
gs = GridSpec(3, 2, figure=fig, hspace=0.3, wspace=0.3)

fig.suptitle('DIA 10 — ANÁLISE DE FORNECEDORES | Master Data Management', 
             fontsize=16, fontweight='bold', y=0.98)

# 1. Curva ABC Fornecedores
ax1 = fig.add_subplot(gs[0, :])
x = range(len(df_fornecedores))
ax1.bar(x, df_fornecedores['valor_total']/1e6, color='steelblue', alpha=0.7, edgecolor='black')
ax2 = ax1.twinx()
ax2.plot(x, df_fornecedores['perc_acumulado'], color='red', linewidth=3, label='% Acumulado')
ax2.axhline(y=80, color='green', linestyle='--', linewidth=2, alpha=0.7, label='80% (Classe A)')
ax2.axhline(y=95, color='orange', linestyle='--', linewidth=2, alpha=0.7, label='95% (Classe B)')
ax1.set_xlabel('Fornecedores (ordenados por valor)', fontweight='bold')
ax1.set_ylabel('Valor em Estoque (R$ Milhões)', fontweight='bold')
ax2.set_ylabel('Percentual Acumulado (%)', fontweight='bold')
ax1.set_title('Curva ABC de Fornecedores - Concentração', fontweight='bold', fontsize=12)
ax2.legend(loc='lower right')
ax1.grid(alpha=0.3)

# 2. Top 10 Fornecedores
ax3 = fig.add_subplot(gs[1, 0])
top10_plot = df_fornecedores.head(10)
y_pos = np.arange(len(top10_plot))
ax3.barh(y_pos, top10_plot['valor_total']/1e6, color='steelblue', alpha=0.7, edgecolor='black')
ax3.set_yticks(y_pos)
ax3.set_yticklabels([f[:25] + '...' if len(f) > 25 else f for f in top10_plot['fornecedor']])
ax3.set_xlabel('Valor em Estoque (R$ Milhões)', fontweight='bold')
ax3.set_title('Top 10 Fornecedores por Valor', fontweight='bold', fontsize=12)
ax3.invert_yaxis()
ax3.grid(axis='x', alpha=0.3)

# 3. Distribuição Classe ABC
ax4 = fig.add_subplot(gs[1, 1])
abc_plot = abc_stats.set_index('classe_abc')
colors = ['#27ae60', '#f39c12', '#e74c3c']
ax4.bar(abc_plot.index, abc_plot['fornecedor'], color=colors, alpha=0.7, edgecolor='black')
ax4.set_ylabel('Quantidade de Fornecedores', fontweight='bold')
ax4.set_title('Distribuição Classe ABC', fontweight='bold', fontsize=12)
ax4.grid(axis='y', alpha=0.3)
for i, (idx, val) in enumerate(abc_plot['fornecedor'].items()):
    perc = abc_plot.loc[idx, 'perc_fornecedores']
    ax4.text(i, val + 2, f'{int(val)}\n({perc:.1f}%)', ha='center', fontweight='bold')

# 4. Materiais por Fornecedor
ax5 = fig.add_subplot(gs[2, 0])
bins = [0, 5, 10, 20, 50, 100, df_fornecedores['qtd_materiais'].max()+1]
labels = ['1-5', '6-10', '11-20', '21-50', '51-100', '100+']
df_fornecedores['faixa_materiais'] = pd.cut(df_fornecedores['qtd_materiais'], bins=bins, labels=labels, right=False)
faixa_counts = df_fornecedores['faixa_materiais'].value_counts().sort_index()
ax5.bar(range(len(faixa_counts)), faixa_counts.values, color='coral', alpha=0.7, edgecolor='black')
ax5.set_xticks(range(len(faixa_counts)))
ax5.set_xticklabels(faixa_counts.index, rotation=45)
ax5.set_ylabel('Quantidade de Fornecedores', fontweight='bold')
ax5.set_xlabel('Faixa de Materiais por Fornecedor', fontweight='bold')
ax5.set_title('Distribuição: Materiais por Fornecedor', fontweight='bold', fontsize=12)
ax5.grid(axis='y', alpha=0.3)

# 5. KPIs Box
ax6 = fig.add_subplot(gs[2, 1])
ax6.axis('off')

kpis_text = f"""
KPIS FORNECEDORES

Total Fornecedores: {fornecedores_unicos:,}

Materiais SEM Fornecedor:
{materiais_sem_fornecedor:,} ({materiais_sem_fornecedor/total_materiais*100:.1f}%)

Classe A (Críticos):
{len(fornecedores_criticos)} fornecedores
{fornecedores_criticos['perc_valor'].sum():.1f}% do valor

Oportunidade Consolidação:
{len(fornecedores_pequenos)} pequenos → 10
Redução: {len(fornecedores_pequenos) - 10} fornecedores

ECONOMIA ANUAL:
R$ {economia_total:,.2f}
"""

ax6.text(0.1, 0.5, kpis_text, fontsize=11, verticalalignment='center',
         bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))

os.makedirs('visualizations', exist_ok=True)
plt.savefig('visualizations/04_fornecedores.png', dpi=150, bbox_inches='tight')
print("✅ Dashboard salvo: visualizations/04_fornecedores.png")
plt.close()

# ═══════════════════════════════════════════════════════════════════════════
# 11. RESUMO EXECUTIVO
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("📊 RESUMO EXECUTIVO - ANÁLISE DE FORNECEDORES")
print("="*70 + "\n")

print(f"Total de fornecedores: {fornecedores_unicos:,}")
print(f"Fornecedores Classe A (críticos): {len(fornecedores_criticos)} ({len(fornecedores_criticos)/len(df_fornecedores)*100:.1f}%)")
print(f"Materiais sem fornecedor: {materiais_sem_fornecedor:,} ({materiais_sem_fornecedor/total_materiais*100:.1f}%)")
print(f"Fornecedores pequenos (≤5 materiais): {len(fornecedores_pequenos)} ({len(fornecedores_pequenos)/len(df_fornecedores)*100:.1f}%)")
print(f"Variações cadastrais detectadas: {duplicados_potenciais}")

print(f"\n💰 ECONOMIA ANUAL TOTAL: R$ {economia_total:,.2f}")
print(f"   Consolidação base: R$ {economia_consolidacao:,.2f}")
print(f"   Corrigir sem fornecedor: R$ {custo_sem_fornecedor:,.2f}")
print(f"   Padronização: R$ {custo_variações:,.2f}")

print(f"\n🎯 AÇÕES RECOMENDADAS:")
print(f"   1. Definir fornecedor para {materiais_sem_fornecedor} materiais")
print(f"   2. Consolidar {len(fornecedores_pequenos)} fornecedores pequenos")
print(f"   3. Padronizar {duplicados_potenciais} variações cadastrais")
print(f"   4. Negociar melhores condições com Classe A")

print("\n" + "="*70)
print("✅ DIA 10 COMPLETO!")
print("="*70 + "\n")

print("📁 Arquivos gerados:")
print("   • data/processed/fornecedores_analise.csv")
if materiais_sem_fornecedor > 0:
    print("   • data/processed/materiais_sem_fornecedor.csv")
print("   • visualizations/04_fornecedores.png")

print("\n🎯 Próximo: DIA 11 - Análise de Movimentações\n")