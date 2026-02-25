"""
═══════════════════════════════════════════════════════════════════════════════
PROJETO MDM SUPPLY CHAIN
Script: Cálculo de Completude
Dia 4 - Análise de campos vazios e completude cadastral
═══════════════════════════════════════════════════════════════════════════════

DESCRIÇÃO:
Calcula percentual de completude de cada campo do cadastro de materiais.
Identifica campos críticos com baixa completude e prioriza correções.

IMPACTO FINANCEIRO:
- Redução retrabalho: R$ 6.000/ano
- Compliance fiscal (NCM): R$ 4.000/ano
- Produtividade equipe: R$ 2.000/ano
TOTAL: R$ 12.000/ano

═══════════════════════════════════════════════════════════════════════════════
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

print("\n" + "="*80)
print("📊 ANÁLISE DE COMPLETUDE - PROJETO MDM")
print("="*80 + "\n")

# ═══════════════════════════════════════════════════════════════════════════
# 1. CARREGAR DADOS
# ═══════════════════════════════════════════════════════════════════════════

print("📂 Carregando dados...")
df = pd.read_csv('data/raw/materiais_raw.csv')
print(f"✅ Dados carregados: {len(df):,} registros")
print(f"   Total de campos: {len(df.columns)}\n")

# ═══════════════════════════════════════════════════════════════════════════
# 2. CÁLCULO DE COMPLETUDE GERAL
# ═══════════════════════════════════════════════════════════════════════════

print("="*80)
print("📋 CÁLCULO DE COMPLETUDE POR CAMPO")
print("="*80 + "\n")

# Calcular completude (% não-nulo)
completude = (1 - df.isnull().sum() / len(df)) * 100
completude = completude.sort_values()

# Calcular quantidade de vazios
vazios = df.isnull().sum()
vazios = vazios[completude.index]  # Mesma ordem

# Criar DataFrame resumo
df_completude = pd.DataFrame({
    'Campo': completude.index,
    'Completude %': completude.values.round(2),
    'Registros Vazios': vazios.values,
    'Registros Preenchidos': (len(df) - vazios.values)
})

print("Completude por campo (ordenado do PIOR para MELHOR):\n")
print(df_completude.to_string(index=False))

# Score médio de completude
completude_media = completude.mean()
print(f"\n{'─'*80}")
print(f"📊 SCORE MÉDIO DE COMPLETUDE: {completude_media:.2f}%")
print(f"{'─'*80}\n")

# ═══════════════════════════════════════════════════════════════════════════
# 3. CLASSIFICAÇÃO DE CAMPOS POR CRITICIDADE
# ═══════════════════════════════════════════════════════════════════════════

print("="*80)
print("🎯 CLASSIFICAÇÃO DE CAMPOS POR CRITICIDADE")
print("="*80 + "\n")

# Definir campos críticos (obrigatórios)
campos_criticos = [
    'codigo_material',
    'descricao', 
    'categoria',
    'unidade_medida',
    'preco_unitario',
    'ncm',
    'fornecedor_principal',
    'localizacao_fisica',
    'centro_custo'
]

# Campos importantes (desejáveis)
campos_importantes = [
    'estoque_minimo',
    'estoque_atual',
    'data_cadastro',
    'responsavel_cadastro'
]

# Campos complementares (opcionais)
campos_complementares = [
    'status',
    'ultima_movimentacao'
]

# Calcular completude por criticidade
print("CAMPOS CRÍTICOS (obrigatórios):")
completude_criticos = completude[campos_criticos].sort_values()
for campo, comp in completude_criticos.items():
    status = "✅" if comp == 100 else "⚠️" if comp >= 80 else "❌"
    print(f"   {status} {campo:25s}: {comp:6.2f}% ({int(len(df) * (100-comp)/100)} vazios)")

print(f"\n   Completude média críticos: {completude_criticos.mean():.2f}%")

print("\nCAMPOS IMPORTANTES (desejáveis):")
completude_importantes = completude[campos_importantes].sort_values()
for campo, comp in completude_importantes.items():
    status = "✅" if comp == 100 else "⚠️" if comp >= 80 else "❌"
    print(f"   {status} {campo:25s}: {comp:6.2f}%")

print(f"\n   Completude média importantes: {completude_importantes.mean():.2f}%")

# ═══════════════════════════════════════════════════════════════════════════
# 4. ANÁLISE DE COMPLETUDE POR CATEGORIA
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*80)
print("📊 COMPLETUDE POR CATEGORIA DE MATERIAL")
print("="*80 + "\n")

# Para cada categoria, calcular completude média
categorias = df['categoria'].unique()
completude_por_categoria = []

for cat in categorias:
    df_cat = df[df['categoria'] == cat]
    comp_media = (1 - df_cat.isnull().sum().sum() / (len(df_cat) * len(df.columns))) * 100
    n_materiais = len(df_cat)
    
    completude_por_categoria.append({
        'Categoria': cat,
        'Completude %': comp_media,
        'Qtd Materiais': n_materiais
    })

df_cat_comp = pd.DataFrame(completude_por_categoria)
df_cat_comp = df_cat_comp.sort_values('Completude %')

print("Completude média por categoria:\n")
for _, row in df_cat_comp.iterrows():
    cat = row['Categoria']
    comp = row['Completude %']
    qtd = row['Qtd Materiais']
    status = "✅" if comp >= 90 else "⚠️" if comp >= 80 else "❌"
    print(f"   {status} {cat:15s}: {comp:5.2f}% ({qtd:3d} materiais)")

print(f"\nCategoria com MELHOR completude: {df_cat_comp.iloc[-1]['Categoria']} ({df_cat_comp.iloc[-1]['Completude %']:.2f}%)")
print(f"Categoria com PIOR completude:   {df_cat_comp.iloc[0]['Categoria']} ({df_cat_comp.iloc[0]['Completude %']:.2f}%)")

# ═══════════════════════════════════════════════════════════════════════════
# 5. IMPACTO FINANCEIRO
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*80)
print("💰 CÁLCULO DE IMPACTO FINANCEIRO")
print("="*80 + "\n")

# Calcular impacto por campo vazio
impactos = {
    'fornecedor_principal': {
        'vazios': vazios['fornecedor_principal'],
        'custo_unitario': 10,  # R$ 10 por campo vazio (retrabalho compra)
        'descricao': 'Retrabalho em compras'
    },
    'localizacao_fisica': {
        'vazios': vazios['localizacao_fisica'],
        'custo_unitario': 15,  # R$ 15 por campo vazio (tempo busca)
        'descricao': 'Tempo perdido localizando'
    },
    'ncm': {
        'vazios': vazios['ncm'],
        'custo_unitario': 8,  # R$ 8 por campo vazio (risco fiscal)
        'descricao': 'Risco compliance fiscal'
    },
    'centro_custo': {
        'vazios': vazios['centro_custo'],
        'custo_unitario': 5,  # R$ 5 por campo vazio (contabilidade)
        'descricao': 'Retrabalho contábil'
    },
    'estoque_minimo': {
        'vazios': vazios['estoque_minimo'],
        'custo_unitario': 3,  # R$ 3 por campo vazio (gestão estoque)
        'descricao': 'Ineficiência gestão estoque'
    }
}

impacto_total_anual = 0

print("Impacto por campo vazio:\n")
for campo, info in impactos.items():
    impacto_anual = info['vazios'] * info['custo_unitario'] * 12  # × 12 meses
    impacto_total_anual += impacto_anual
    print(f"   {campo:20s}:")
    print(f"      Registros vazios: {info['vazios']:,}")
    print(f"      Custo unitário/mês: R$ {info['custo_unitario']}")
    print(f"      Impacto anual: R$ {impacto_anual:,.2f}")
    print(f"      ({info['descricao']})")
    print()

print(f"{'─'*80}")
print(f"💰 ECONOMIA TOTAL ANUAL (preenchendo campos): R$ {impacto_total_anual:,.2f}")
print(f"{'─'*80}\n")

# ═══════════════════════════════════════════════════════════════════════════
# 6. MATERIAIS COM MAIOR DÉFICIT DE COMPLETUDE
# ═══════════════════════════════════════════════════════════════════════════

print("="*80)
print("🔍 MATERIAIS COM PIOR COMPLETUDE (TOP 20)")
print("="*80 + "\n")

# Calcular completude por material (linha)
completude_por_material = (1 - df[campos_criticos].isnull().sum(axis=1) / len(campos_criticos)) * 100
df['completude_score'] = completude_por_material

# Top 20 piores - calcular vazios por material
df['vazios_count'] = df[campos_criticos].isnull().sum(axis=1)
piores = df.nlargest(20, 'vazios_count')[
    ['codigo_material', 'descricao', 'categoria', 'completude_score', 'vazios_count']
]

print("Materiais prioritários para correção:\n")
print(piores.to_string(index=False))

# ═══════════════════════════════════════════════════════════════════════════
# 7. PLANO DE AÇÃO PRIORIZADO
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*80)
print("📋 PLANO DE AÇÃO - PREENCHIMENTO PRIORITÁRIO")
print("="*80 + "\n")

# Priorizar campos críticos com pior completude
campos_priorizar = completude_criticos[completude_criticos < 100].sort_values()

if len(campos_priorizar) > 0:
    print("PRIORIDADE 1 (7 dias) - Campos críticos com maior déficit:\n")
    for i, (campo, comp) in enumerate(campos_priorizar.head(3).items(), 1):
        vazios_campo = vazios[campo]
        economia = impactos.get(campo, {}).get('custo_unitario', 5) * vazios_campo * 12
        print(f"   {i}. {campo}")
        print(f"      Completude: {comp:.2f}%")
        print(f"      Vazios: {vazios_campo:,} registros")
        print(f"      Economia anual: R$ {economia:,.2f}")
        print(f"      Tempo estimado: {int(vazios_campo * 2 / 60)} horas")
        print()
    
    print("PRIORIDADE 2 (30 dias) - Demais campos críticos:")
    for campo, comp in campos_priorizar.tail(-3).items():
        print(f"   • {campo}: {comp:.2f}% completo ({vazios[campo]:,} vazios)")
    
    print(f"\nPRIORIDADE 3 (90 dias) - Campos importantes:")
    for campo in campos_importantes:
        if completude[campo] < 100:
            print(f"   • {campo}: {completude[campo]:.2f}% completo ({vazios[campo]:,} vazios)")
else:
    print("✅ Todos os campos críticos estão 100% completos!")

# ═══════════════════════════════════════════════════════════════════════════
# 8. SALVAR RELATÓRIO
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*80)
print("💾 SALVANDO RELATÓRIO DE COMPLETUDE")
print("="*80 + "\n")

# Adicionar classificação de criticidade
def classificar_criticidade(campo):
    if campo in campos_criticos:
        return 'CRÍTICO'
    elif campo in campos_importantes:
        return 'IMPORTANTE'
    else:
        return 'COMPLEMENTAR'

df_completude['Criticidade'] = df_completude['Campo'].apply(classificar_criticidade)

# Adicionar impacto financeiro anual
def calcular_impacto(row):
    campo = row['Campo']
    vazios_campo = row['Registros Vazios']
    custo = impactos.get(campo, {}).get('custo_unitario', 2)
    return vazios_campo * custo * 12

df_completude['Impacto Anual R$'] = df_completude.apply(calcular_impacto, axis=1)

# Reordenar colunas
df_completude = df_completude[[
    'Campo', 'Criticidade', 'Completude %', 
    'Registros Vazios', 'Registros Preenchidos', 'Impacto Anual R$'
]]

# Ordenar por criticidade e depois por completude
ordem_criticidade = {'CRÍTICO': 1, 'IMPORTANTE': 2, 'COMPLEMENTAR': 3}
df_completude['_ordem'] = df_completude['Criticidade'].map(ordem_criticidade)
df_completude = df_completude.sort_values(['_ordem', 'Completude %'])
df_completude = df_completude.drop('_ordem', axis=1)

# Salvar CSV
os.makedirs('data/processed', exist_ok=True)
output_file = 'data/processed/completude.csv'
df_completude.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"✅ Relatório salvo: {output_file}")
print(f"   {len(df_completude)} campos analisados\n")

# ═══════════════════════════════════════════════════════════════════════════
# 9. VISUALIZAÇÕES
# ═══════════════════════════════════════════════════════════════════════════

print("="*80)
print("📊 GERANDO VISUALIZAÇÕES...")
print("="*80 + "\n")

os.makedirs('visualizations', exist_ok=True)

# FIGURA 1: Dashboard Completude (4 gráficos)
fig = plt.figure(figsize=(16, 10))
gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

fig.suptitle('Análise de Completude - Cadastro de Materiais', 
             fontsize=18, fontweight='bold', y=0.98)

# 1. Completude por campo (horizontal bar)
ax1 = fig.add_subplot(gs[0, :])
cores_criticidade = df_completude['Criticidade'].map({
    'CRÍTICO': '#e74c3c',
    'IMPORTANTE': '#f39c12', 
    'COMPLEMENTAR': '#95a5a6'
})
bars = ax1.barh(df_completude['Campo'], df_completude['Completude %'], 
                color=cores_criticidade, alpha=0.8, edgecolor='black')
ax1.axvline(x=80, color='orange', linestyle='--', linewidth=2, alpha=0.7, label='Meta Mínima (80%)')
ax1.axvline(x=95, color='green', linestyle='--', linewidth=2, alpha=0.7, label='Meta Ideal (95%)')
ax1.set_xlabel('Completude (%)', fontweight='bold', fontsize=11)
ax1.set_title('Completude por Campo (Vermelho=Crítico, Laranja=Importante, Cinza=Complementar)', 
              fontweight='bold', fontsize=12, pad=10)
ax1.set_xlim(0, 105)
ax1.grid(axis='x', alpha=0.3)
ax1.legend(loc='lower right')

# Adicionar valores
for i, (bar, val) in enumerate(zip(bars, df_completude['Completude %'])):
    ax1.text(val + 1, bar.get_y() + bar.get_height()/2, 
             f'{val:.1f}%', va='center', fontsize=8, fontweight='bold')

# 2. Score por criticidade
ax2 = fig.add_subplot(gs[1, 0])
criticos_score = df_completude[df_completude['Criticidade'] == 'CRÍTICO']['Completude %'].mean()
importantes_score = df_completude[df_completude['Criticidade'] == 'IMPORTANTE']['Completude %'].mean()
compl_score = df_completude[df_completude['Criticidade'] == 'COMPLEMENTAR']['Completude %'].mean()

categorias_crit = ['CRÍTICOS', 'IMPORTANTES', 'COMPLEMENTARES']
scores = [criticos_score, importantes_score, compl_score]
cores_bar = ['#e74c3c', '#f39c12', '#95a5a6']

bars = ax2.bar(categorias_crit, scores, color=cores_bar, alpha=0.8, edgecolor='black')
ax2.set_ylabel('Completude Média (%)', fontweight='bold')
ax2.set_title('Score de Completude por Criticidade', fontweight='bold', fontsize=12)
ax2.set_ylim(0, 105)
ax2.axhline(y=95, color='green', linestyle='--', alpha=0.5)
ax2.axhline(y=80, color='orange', linestyle='--', alpha=0.5)
ax2.grid(axis='y', alpha=0.3)

for bar in bars:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
             f'{height:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=11)

# 3. Impacto financeiro por campo
ax3 = fig.add_subplot(gs[1, 1])
top_impacto = df_completude.nlargest(8, 'Impacto Anual R$')
bars = ax3.barh(top_impacto['Campo'], top_impacto['Impacto Anual R$']/1000, 
                color='steelblue', alpha=0.8, edgecolor='black')
ax3.set_xlabel('Impacto Anual (R$ mil)', fontweight='bold')
ax3.set_title('Top 8 Campos por Impacto Financeiro', fontweight='bold', fontsize=12)
ax3.grid(axis='x', alpha=0.3)
ax3.invert_yaxis()

for bar in bars:
    width = bar.get_width()
    ax3.text(width + 0.5, bar.get_y() + bar.get_height()/2,
             f'R$ {width:.1f}k', va='center', fontsize=9, fontweight='bold')

# 4. Completude por categoria
ax4 = fig.add_subplot(gs[2, :])
df_cat_comp_sorted = df_cat_comp.sort_values('Completude %', ascending=True)
cores_cat = ['#e74c3c' if x < 80 else '#f39c12' if x < 90 else '#27ae60' 
             for x in df_cat_comp_sorted['Completude %']]
bars = ax4.barh(df_cat_comp_sorted['Categoria'], df_cat_comp_sorted['Completude %'],
                color=cores_cat, alpha=0.8, edgecolor='black')
ax4.axvline(x=80, color='orange', linestyle='--', linewidth=2, alpha=0.7)
ax4.axvline(x=90, color='green', linestyle='--', linewidth=2, alpha=0.7)
ax4.set_xlabel('Completude Média (%)', fontweight='bold', fontsize=11)
ax4.set_title('Completude Média por Categoria de Material', fontweight='bold', fontsize=12)
ax4.set_xlim(0, 105)
ax4.grid(axis='x', alpha=0.3)

for bar in bars:
    width = bar.get_width()
    ax4.text(width + 0.5, bar.get_y() + bar.get_height()/2,
             f'{width:.1f}%', va='center', fontsize=9, fontweight='bold')

plt.savefig('visualizations/02_completude_detalhado.png', dpi=150, bbox_inches='tight')
print("✅ Gráfico salvo: visualizations/02_completude_detalhado.png")
plt.close()

# FIGURA 2: Heatmap Completude (amostra)
fig, ax = plt.subplots(figsize=(14, 10))

# Pegar amostra estratificada (20 materiais de cada faixa de completude)
df_sorted = df.sort_values('completude_score')
n_por_faixa = 20
amostra_idx = []
amostra_idx.extend(df_sorted.head(n_por_faixa).index.tolist())  # Piores
amostra_idx.extend(df_sorted.iloc[len(df)//2-n_por_faixa//2:len(df)//2+n_por_faixa//2].index.tolist())  # Médios
amostra_idx.extend(df_sorted.tail(n_por_faixa).index.tolist())  # Melhores

df_amostra = df.loc[amostra_idx, campos_criticos].isnull()

# Criar heatmap
sns.heatmap(df_amostra.T, cmap='RdYlGn_r', cbar_kws={'label': 'Campo Vazio'}, 
            ax=ax, linewidths=0.5, linecolor='gray')
ax.set_title('Heatmap de Completude - Amostra Estratificada (60 materiais)\nVermelho = Vazio | Verde = Preenchido', 
             fontweight='bold', fontsize=14, pad=15)
ax.set_xlabel('Material (índice)', fontweight='bold', fontsize=11)
ax.set_ylabel('Campo', fontweight='bold', fontsize=11)
ax.set_yticklabels(ax.get_yticklabels(), rotation=0)

# Adicionar legendas das faixas
ax.text(10, -1.5, 'PIORES (0-33%)', ha='center', fontweight='bold', color='red')
ax.text(30, -1.5, 'MÉDIOS (33-66%)', ha='center', fontweight='bold', color='orange')
ax.text(50, -1.5, 'MELHORES (66-100%)', ha='center', fontweight='bold', color='green')

plt.tight_layout()
plt.savefig('visualizations/02_heatmap_completude_full.png', dpi=150, bbox_inches='tight')
print("✅ Gráfico salvo: visualizations/02_heatmap_completude_full.png")
plt.close()

# ═══════════════════════════════════════════════════════════════════════════
# 10. RESUMO EXECUTIVO
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*80)
print("📊 RESUMO EXECUTIVO - ANÁLISE DE COMPLETUDE")
print("="*80 + "\n")

print(f"Total de materiais analisados: {len(df):,}")
print(f"Total de campos analisados: {len(df.columns)}")
print(f"\n📊 SCORE MÉDIO GERAL: {completude_media:.2f}%")

# Campos 100% completos
campos_100 = df_completude[df_completude['Completude %'] == 100]['Campo'].tolist()
print(f"\nCampos 100% completos: {len(campos_100)}")
if len(campos_100) > 0:
    print(f"   {', '.join(campos_100)}")

# Campos com problemas
campos_problema = df_completude[df_completude['Completude %'] < 100].sort_values('Completude %')
print(f"\nCampos com déficit: {len(campos_problema)}")
for _, row in campos_problema.head(5).iterrows():
    print(f"   ⚠️ {row['Campo']:20s}: {row['Completude %']:5.1f}% ({int(row['Registros Vazios']):,} vazios)")

print(f"\nCategoria com MELHOR completude: {df_cat_comp.iloc[-1]['Categoria']} ({df_cat_comp.iloc[-1]['Completude %']:.1f}%)")
print(f"Categoria com PIOR completude:   {df_cat_comp.iloc[0]['Categoria']} ({df_cat_comp.iloc[0]['Completude %']:.1f}%)")

print(f"\n💰 ECONOMIA ANUAL (preenchendo vazios): R$ {impacto_total_anual:,.2f}")

print(f"\n{'─'*80}")
print(f"AÇÕES RECOMENDADAS:")
print(f"{'─'*80}")
print(f"1. IMEDIATO (7 dias): Preencher Top 3 campos críticos vazios")
print(f"   Economia: ~40% do total")
print(f"\n2. CURTO PRAZO (30 dias): Completar todos campos críticos")
print(f"   Economia: ~70% do total")
print(f"\n3. MÉDIO PRAZO (90 dias): Atingir 95%+ completude em todos campos")
print(f"   Economia: R$ {impacto_total_anual:,.2f} (100%)")
print(f"\n4. META: Completude geral > 95% (atual: {completude_media:.1f}%)")

print(f"\n{'─'*80}")
print(f"ARQUIVOS GERADOS:")
print(f"{'─'*80}")
print(f"📄 data/processed/completude.csv")
print(f"   → Relatório completo com {len(df_completude)} campos")
print(f"   → Priorizado por criticidade e completude")
print(f"\n📊 visualizations/02_completude_detalhado.png")
print(f"   → 4 gráficos: campos, criticidade, impacto, categorias")
print(f"\n📊 visualizations/02_heatmap_completude_full.png")
print(f"   → Heatmap visual (vermelho = vazio, verde = completo)")

print("\n" + "="*80)
print("✅ ANÁLISE DE COMPLETUDE COMPLETA!")
print("="*80 + "\n")

print("🎯 PRÓXIMOS PASSOS:")
print("   1. Revisar arquivo: data/processed/completude.csv")
print("   2. Analisar gráficos: visualizations/02_completude*.png")
print("   3. Priorizar preenchimento Top 3 campos")
print("   4. Amanhã: DIA 5 - Análise Python Avançada!\n")

print("="*80)
print("🚀 BOM TRABALHO! DIA 4 COMPLETO!")
print("="*80 + "\n")
