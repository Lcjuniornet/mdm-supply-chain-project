"""
═══════════════════════════════════════════════════════════════════════════════
PROJETO MDM SUPPLY CHAIN
Script: Exploração Inicial dos Dados
Dia 2 - Primeira análise do dataset gerado
═══════════════════════════════════════════════════════════════════════════════
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

print("\n" + "="*80)
print("📊 EXPLORAÇÃO INICIAL - DADOS MDM SUPPLY CHAIN")
print("="*80 + "\n")

# ═══════════════════════════════════════════════════════════════════════════
# 1. CARREGAR DADOS
# ═══════════════════════════════════════════════════════════════════════════

print("📂 Carregando dados...")
df = pd.read_csv('data/raw/materiais_raw.csv')
print(f"✅ Dados carregados: {len(df)} registros\n")

# ═══════════════════════════════════════════════════════════════════════════
# 2. VISÃO GERAL
# ═══════════════════════════════════════════════════════════════════════════

print("="*80)
print("📋 VISÃO GERAL DO DATASET")
print("="*80 + "\n")

print(f"Total de registros: {len(df):,}")
print(f"Total de colunas: {len(df.columns)}")
print(f"Tamanho em memória: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB\n")

print("Colunas disponíveis:")
for i, col in enumerate(df.columns, 1):
    print(f"  {i:2d}. {col}")

# ═══════════════════════════════════════════════════════════════════════════
# 3. PRIMEIRAS LINHAS
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*80)
print("👀 PRIMEIRAS 5 LINHAS")
print("="*80 + "\n")
print(df.head())

# ═══════════════════════════════════════════════════════════════════════════
# 4. INFORMAÇÕES DAS COLUNAS
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*80)
print("ℹ️  INFORMAÇÕES DAS COLUNAS")
print("="*80 + "\n")
print(df.info())

# ═══════════════════════════════════════════════════════════════════════════
# 5. ESTATÍSTICAS DESCRITIVAS
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*80)
print("📈 ESTATÍSTICAS DESCRITIVAS (Colunas Numéricas)")
print("="*80 + "\n")
print(df.describe())

# ═══════════════════════════════════════════════════════════════════════════
# 6. DISTRIBUIÇÃO CATEGORIAS
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*80)
print("📊 DISTRIBUIÇÃO POR CATEGORIA")
print("="*80 + "\n")
categorias = df['categoria'].value_counts()
print(categorias)

print(f"\nTotal de categorias: {df['categoria'].nunique()}")
print(f"Categoria mais comum: {categorias.index[0]} ({categorias.iloc[0]} materiais)")

# ═══════════════════════════════════════════════════════════════════════════
# 7. VALORES NULOS (COMPLETUDE)
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*80)
print("❓ VALORES NULOS (Completude dos Dados)")
print("="*80 + "\n")

nulos = df.isnull().sum()
nulos_pct = (nulos / len(df) * 100).round(2)

completude_df = pd.DataFrame({
    'Campo': nulos.index,
    'Nulos': nulos.values,
    'Percentual': nulos_pct.values,
    'Completude %': (100 - nulos_pct.values).round(2)
})

completude_df = completude_df.sort_values('Nulos', ascending=False)
print(completude_df.to_string(index=False))

# ═══════════════════════════════════════════════════════════════════════════
# 8. ANÁLISE PREÇOS
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*80)
print("💰 ANÁLISE DE PREÇOS")
print("="*80 + "\n")

print(f"Preço médio: R$ {df['preco_unitario'].mean():.2f}")
print(f"Preço mediano: R$ {df['preco_unitario'].median():.2f}")
print(f"Preço mínimo: R$ {df['preco_unitario'].min():.2f}")
print(f"Preço máximo: R$ {df['preco_unitario'].max():.2f}")
print(f"Desvio padrão: R$ {df['preco_unitario'].std():.2f}")

# Distribuição por faixas
faixas = pd.cut(df['preco_unitario'], bins=[0, 10, 100, 1000, df['preco_unitario'].max()],
                labels=['< R$ 10', 'R$ 10-100', 'R$ 100-1000', '> R$ 1000'])
print(f"\nDistribuição por faixa de preço:")
print(faixas.value_counts().sort_index())

# ═══════════════════════════════════════════════════════════════════════════
# 9. VALOR TOTAL ESTOQUE
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*80)
print("🏭 ANÁLISE DE ESTOQUE")
print("="*80 + "\n")

valor_estoque = (df['estoque_atual'] * df['preco_unitario']).sum()
print(f"Valor total em estoque: R$ {valor_estoque:,.2f}")

print(f"\nEstoque médio: {df['estoque_atual'].mean():.0f} unidades")
print(f"Estoque total: {df['estoque_atual'].sum():,} unidades")

# Top 10 materiais por valor estoque
print("\nTop 10 materiais por valor em estoque:")
df['valor_estoque'] = df['estoque_atual'] * df['preco_unitario']
top10_valor = df.nlargest(10, 'valor_estoque')[['codigo_material', 'descricao', 'valor_estoque']]
print(top10_valor.to_string(index=False))

# ═══════════════════════════════════════════════════════════════════════════
# 10. PROBLEMAS IDENTIFICADOS (PREVIEW)
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*80)
print("🔍 PREVIEW DE PROBLEMAS DE QUALIDADE")
print("="*80 + "\n")

# Duplicatas (preview simples)
duplicatas_codigo = df[df.duplicated('codigo_material', keep=False)]
print(f"Possíveis duplicatas por código: {len(duplicatas_codigo)}")

# Preços zerados
precos_zero = df[df['preco_unitario'] == 0]
print(f"Materiais com preço R$ 0,00: {len(precos_zero)}")

# NCM inválidos (00000000)
ncm_invalido = df[df['ncm'] == '00000000']
print(f"NCMs inválidos (00000000): {len(ncm_invalido)}")

# Campos vazios críticos
campos_criticos = ['fornecedor_principal', 'localizacao_fisica', 'ncm']
for campo in campos_criticos:
    vazios = df[campo].isnull().sum()
    print(f"{campo} vazios: {vazios} ({vazios/len(df)*100:.1f}%)")

# ═══════════════════════════════════════════════════════════════════════════
# 11. VISUALIZAÇÕES INICIAIS
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*80)
print("📊 GERANDO VISUALIZAÇÕES...")
print("="*80 + "\n")

# Criar pasta visualizations se não existir
import os
os.makedirs('visualizations', exist_ok=True)

# 1. Distribuição de categorias
plt.figure(figsize=(12, 6))
categorias[:10].plot(kind='bar', color='steelblue')
plt.title('Top 10 Categorias - Quantidade de Materiais', fontsize=14, fontweight='bold')
plt.xlabel('Categoria')
plt.ylabel('Quantidade de Materiais')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('visualizations/00_distribuicao_categorias.png', dpi=150, bbox_inches='tight')
print("✅ Gráfico salvo: visualizations/00_distribuicao_categorias.png")
plt.close()

# 2. Distribuição de preços (histograma)
plt.figure(figsize=(12, 6))
plt.hist(df['preco_unitario'], bins=50, color='green', alpha=0.7, edgecolor='black')
plt.title('Distribuição de Preços Unitários', fontsize=14, fontweight='bold')
plt.xlabel('Preço (R$)')
plt.ylabel('Frequência')
plt.axvline(df['preco_unitario'].median(), color='red', linestyle='--', label=f'Mediana: R$ {df["preco_unitario"].median():.2f}')
plt.legend()
plt.tight_layout()
plt.savefig('visualizations/00_distribuicao_precos.png', dpi=150, bbox_inches='tight')
print("✅ Gráfico salvo: visualizations/00_distribuicao_precos.png")
plt.close()

# 3. Heatmap completude (preview)
plt.figure(figsize=(10, 8))
completude_sample = df.head(100).isnull().T  # Primeiras 100 linhas
sns.heatmap(completude_sample, cmap='RdYlGn_r', cbar_kws={'label': 'Valor Ausente'})
plt.title('Heatmap Completude - Amostra (100 primeiros registros)', fontsize=14, fontweight='bold')
plt.xlabel('Registro')
plt.ylabel('Campo')
plt.tight_layout()
plt.savefig('visualizations/00_heatmap_completude_preview.png', dpi=150, bbox_inches='tight')
print("✅ Gráfico salvo: visualizations/00_heatmap_completude_preview.png")
plt.close()

# ═══════════════════════════════════════════════════════════════════════════
# 12. RESUMO FINAL
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*80)
print("✅ EXPLORAÇÃO INICIAL COMPLETA!")
print("="*80 + "\n")

print("📌 PRÓXIMOS PASSOS:")
print("   1. Revisar gráficos em: visualizations/")
print("   2. Analisar problemas identificados")
print("   3. Executar: scripts/01_identificar_duplicatas.py")
print("   4. Executar: scripts/02_calcular_completude.py\n")

print("🎯 Dataset está pronto para análise!")
print(f"📁 Arquivo: data/raw/materiais_raw.csv ({len(df):,} registros)")
print(f"📊 Gráficos: visualizations/ (3 arquivos PNG)\n")

print("="*80)
print("🚀 BOM TRABALHO! DIA 2 COMPLETO!")
print("="*80 + "\n")
