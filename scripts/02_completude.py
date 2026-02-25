"""
╔══════════════════════════════════════════════════════════════╗
║         DIA 4 - ANÁLISE DE COMPLETUDE DE MATERIAIS          ║
║              Data Quality | Master Data Owner                ║
╚══════════════════════════════════════════════════════════════╝
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import os
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────
# 1. CARREGAR DADOS
# ─────────────────────────────────────────────────────────────
print("\n" + "═"*60)
print("  DIA 4 - ANÁLISE DE COMPLETUDE")
print("═"*60)

# Tenta carregar o arquivo gerado no Dia 2
possiveis_arquivos = [
    'materiais.csv',
    'dados_materiais.csv',
    'materiais_gerados.csv',
]

df = None
for arquivo in possiveis_arquivos:
    if os.path.exists(arquivo):
        df = pd.read_csv(arquivo)
        print(f"\n✅ Arquivo carregado: {arquivo}")
        print(f"   Registros: {len(df):,}")
        print(f"   Colunas:   {list(df.columns)}")
        break

# Se não encontrar, gera dados simulados (igual ao Dia 2)
if df is None:
    print("\n⚠️  Arquivo não encontrado. Gerando dados simulados...")
    np.random.seed(42)
    n = 3300

    categorias = ['Mecânico', 'Elétrico', 'Hidráulico', 'Embalagem',
                  'Escritório', 'Lubrificante', 'Peças', 'Ferramentas',
                  'EPI', 'Químico']
    tipos = ['Parafuso', 'Rolamento', 'Válvula', 'Mangueira', 'Cabo',
             'Filtro', 'Bomba', 'Motor', 'Correia', 'Porca',
             'Pasta', 'Óleo', 'Graxa', 'Papel', 'Caixa']
    materiais = ['Alumínio', 'Aço', 'PVC', 'Borracha', 'Latão',
                 'Plástico', 'Inox', 'Cobre', 'Nylon', 'Ferro']
    uoms = ['UN', 'KG', 'LT', 'MT', 'CX', 'PC', 'GL', None]
    fabricantes = ['ABB', 'SKF', 'Bosch', 'Siemens', 'WEG',
                   'Parker', 'Atlas', 'Emerson', None, None, None]
    locais = ['Almox-A', 'Almox-B', 'Almox-C', 'Deposito-1', 'Deposito-2', None, None]
    ncm_vals = ['8482.10.10', '8483.30.00', '8484.10.00', '3917.21.00', None, None]

    # Gera descrições (com muitas duplicatas como no Dia 2)
    descricoes_base = [f"{t} {m}" for t in tipos for m in materiais][:100]

    df = pd.DataFrame({
        'codigo':      [f"MAT-{str(i).zfill(5)}" for i in range(1, n+1)],
        'descricao':   np.random.choice(descricoes_base, n),
        'categoria':   np.random.choice(categorias, n),
        'unidade_med': np.random.choice(uoms, n, p=[0.15,0.15,0.10,0.10,0.10,0.10,0.05,0.25]),
        'preco_unit':  np.where(np.random.rand(n) < 0.1, np.nan,
                                np.random.lognormal(4, 2, n).round(2)),
        'fabricante':  np.random.choice(fabricantes, n),
        'local_estoque': np.random.choice(locais, n),
        'ncm':         np.random.choice(ncm_vals, n),
        'estoque_min': np.where(np.random.rand(n) < 0.35, np.nan,
                                np.random.randint(1, 50, n).astype(float)),
        'estoque_max': np.where(np.random.rand(n) < 0.40, np.nan,
                                np.random.randint(50, 500, n).astype(float)),
        'data_cadastro': pd.date_range('2020-01-01', periods=n, freq='8h').strftime('%Y-%m-%d'),
        'usuario_cad': np.random.choice(['joao.silva', 'maria.souza', 'pedro.lima',
                                          'ana.costa', 'carlos.melo', None], n,
                                         p=[0.2, 0.2, 0.2, 0.2, 0.15, 0.05]),
    })

    # Adiciona valores nulos estrategicamente para análise realista
    idx_sem_desc = np.random.choice(df.index, 80, replace=False)
    df.loc[idx_sem_desc, 'descricao'] = np.nan

    print(f"   ✅ Dados simulados: {len(df):,} registros | {len(df.columns)} colunas")

print()

# ─────────────────────────────────────────────────────────────
# 2. ANÁLISE DE COMPLETUDE POR CAMPO
# ─────────────────────────────────────────────────────────────
print("─"*60)
print("  MÉTODO 1: COMPLETUDE POR CAMPO (coluna a coluna)")
print("─"*60)

total = len(df)
resultado_campos = []

# Definir campos obrigatórios vs opcionais
campos_obrigatorios = ['codigo', 'descricao', 'categoria', 'unidade_med', 'preco_unit']
campos_importantes  = ['fabricante', 'local_estoque', 'ncm', 'estoque_min', 'estoque_max']
campos_informativos = [c for c in df.columns
                       if c not in campos_obrigatorios + campos_importantes]

classificacao_campo = {}
for c in df.columns:
    if c in campos_obrigatorios:
        classificacao_campo[c] = 'OBRIGATÓRIO'
    elif c in campos_importantes:
        classificacao_campo[c] = 'IMPORTANTE'
    else:
        classificacao_campo[c] = 'INFORMATIVO'

for col in df.columns:
    nulos     = df[col].isna().sum()
    vazios    = (df[col].astype(str).str.strip() == '').sum() if df[col].dtype == object else 0
    total_inv = nulos + vazios
    pct_ok    = round((total - total_inv) / total * 100, 1)
    pct_nulo  = round(total_inv / total * 100, 1)

    resultado_campos.append({
        'campo':       col,
        'tipo':        classificacao_campo[col],
        'total':       total,
        'preenchidos': total - total_inv,
        'nulos':       nulos,
        'vazios':      vazios,
        'invalidos':   total_inv,
        'pct_ok':      pct_ok,
        'pct_nulo':    pct_nulo,
    })

df_campos = pd.DataFrame(resultado_campos).sort_values('pct_ok')

print(f"\n{'CAMPO':<18} {'TIPO':<14} {'PREENCH.':>10} {'NULOS':>8} {'% OK':>8}  STATUS")
print("─"*70)
for _, row in df_campos.iterrows():
    if row['pct_ok'] >= 95:
        status = "✅ ÓTIMO"
    elif row['pct_ok'] >= 80:
        status = "⚠️  ATENÇÃO"
    elif row['pct_ok'] >= 60:
        status = "🔴 CRÍTICO"
    else:
        status = "💀 GRAVE"
    print(f"{row['campo']:<18} {row['tipo']:<14} {row['preenchidos']:>10,} {row['nulos']:>8,} {row['pct_ok']:>7.1f}%  {status}")

# ─────────────────────────────────────────────────────────────
# 3. SCORE DE COMPLETUDE POR REGISTRO
# ─────────────────────────────────────────────────────────────
print("\n" + "─"*60)
print("  MÉTODO 2: SCORE DE COMPLETUDE POR REGISTRO")
print("─"*60)

# Pesos: campos obrigatórios valem mais
pesos = {}
for c in df.columns:
    if c in campos_obrigatorios:
        pesos[c] = 3
    elif c in campos_importantes:
        pesos[c] = 2
    else:
        pesos[c] = 1

peso_total = sum(pesos.values())

def calcular_score(row):
    pts = 0
    for col, peso in pesos.items():
        val = row[col]
        if pd.notna(val) and str(val).strip() != '':
            pts += peso
    return round(pts / peso_total * 100, 1)

df['score_completude'] = df.apply(calcular_score, axis=1)

# Classificar registros
def classificar_score(s):
    if s >= 90:   return 'A - Completo'
    elif s >= 70: return 'B - Bom'
    elif s >= 50: return 'C - Regular'
    else:         return 'D - Incompleto'

df['classe_completude'] = df['score_completude'].apply(classificar_score)

dist = df['classe_completude'].value_counts().sort_index()
score_medio = df['score_completude'].mean()

print(f"\n  Score Médio Geral: {score_medio:.1f}%\n")
print(f"  {'CLASSE':<20} {'QTD':>8} {'%':>8}")
print("  " + "─"*40)
for cls, qtd in dist.items():
    pct = qtd / total * 100
    barra = "█" * int(pct / 2)
    print(f"  {cls:<20} {qtd:>8,} {pct:>7.1f}%  {barra}")

# Piores registros
piores = df[df['score_completude'] < 50][['codigo', 'descricao', 'categoria', 'score_completude']].head(10)
print(f"\n  TOP 10 REGISTROS MAIS INCOMPLETOS:")
print(f"  {'CÓDIGO':<12} {'DESCRIÇÃO':<25} {'CATEGORIA':<14} {'SCORE':>6}")
print("  " + "─"*62)
for _, r in piores.iterrows():
    desc = str(r['descricao'])[:24] if pd.notna(r['descricao']) else '[VAZIO]'
    cat  = str(r['categoria'])[:13] if pd.notna(r['categoria']) else '[VAZIO]'
    print(f"  {r['codigo']:<12} {desc:<25} {cat:<14} {r['score_completude']:>5.1f}%")

# ─────────────────────────────────────────────────────────────
# 4. ANÁLISE DE CAMPOS OBRIGATÓRIOS VAZIOS
# ─────────────────────────────────────────────────────────────
print("\n" + "─"*60)
print("  MÉTODO 3: VIOLAÇÕES DE CAMPOS OBRIGATÓRIOS")
print("─"*60)

violacoes = {}
for campo in campos_obrigatorios:
    mask = df[campo].isna() | (df[campo].astype(str).str.strip() == '')
    violacoes[campo] = df[mask]['codigo'].tolist()

total_violacoes = sum(len(v) for v in violacoes.values())
materiais_com_violacao = df[
    df[campos_obrigatorios].isnull().any(axis=1)
]['codigo'].nunique()

print(f"\n  Materiais com campo obrigatório vazio: {materiais_com_violacao:,} ({materiais_com_violacao/total*100:.1f}%)")
print(f"  Total de violações:                    {total_violacoes:,}")
print()
for campo, lista in violacoes.items():
    if lista:
        print(f"  ❌ {campo:<18} → {len(lista):>5,} registros sem preenchimento")
    else:
        print(f"  ✅ {campo:<18} → Todos preenchidos!")

# ─────────────────────────────────────────────────────────────
# 5. ANÁLISE POR CATEGORIA
# ─────────────────────────────────────────────────────────────
print("\n" + "─"*60)
print("  ANÁLISE POR CATEGORIA")
print("─"*60)

df_cat = (df.groupby('categoria')['score_completude']
            .agg(['mean', 'count', 'min'])
            .rename(columns={'mean': 'score_medio', 'count': 'qtd', 'min': 'pior_score'})
            .sort_values('score_medio'))

print(f"\n  {'CATEGORIA':<16} {'QTD':>6} {'SCORE MÉDIO':>12} {'PIOR SCORE':>12}")
print("  " + "─"*50)
for cat, row in df_cat.iterrows():
    emoji = "✅" if row['score_medio'] >= 80 else ("⚠️ " if row['score_medio'] >= 60 else "🔴")
    print(f"  {emoji} {cat:<14} {int(row['qtd']):>6,} {row['score_medio']:>11.1f}% {row['pior_score']:>11.1f}%")

# ─────────────────────────────────────────────────────────────
# 6. IMPACTO FINANCEIRO DA INCOMPLETUDE
# ─────────────────────────────────────────────────────────────
print("\n" + "─"*60)
print("  IMPACTO FINANCEIRO DA INCOMPLETUDE")
print("─"*60)

# Materiais sem preço
sem_preco = df['preco_unit'].isna().sum()
# Materiais sem UOM (não se pode fazer requisição)
sem_uom   = df['unidade_med'].isna().sum()
# Materiais sem local de estoque
sem_local = df['local_estoque'].isna().sum() if 'local_estoque' in df.columns else 0

custo_hora      = 60      # R$ por hora (analista)
tempo_correcao  = 0.5     # hora por campo corrigido

custo_retrabalho  = total_violacoes * custo_hora * tempo_correcao
custo_busca       = sem_local * 10  # R$10 por material sem local (tempo de busca/mês)
custo_pedido_errado = sem_uom * 200  # R$200 por pedido errado por falta de UOM

total_custo_mensal = custo_retrabalho + custo_busca + custo_pedido_errado
total_custo_anual  = total_custo_mensal * 12

print(f"""
  Materiais sem preço unitário: {sem_preco:,} registros
  Materiais sem unidade de med: {sem_uom:,} registros
  Materiais sem local de estoque: {sem_local:,} registros

  ┌─────────────────────────────────────────────────┐
  │           CUSTO DA INCOMPLETUDE                 │
  │                                                 │
  │  Retrabalho de correção:  R$ {custo_retrabalho:>12,.2f}/mês  │
  │  Tempo buscando material: R$ {custo_busca:>12,.2f}/mês  │
  │  Pedidos com erro UOM:    R$ {custo_pedido_errado:>12,.2f}/mês  │
  │                           ────────────────────  │
  │  TOTAL MENSAL:            R$ {total_custo_mensal:>12,.2f}       │
  │  TOTAL ANUAL:             R$ {total_custo_anual:>12,.2f}       │
  └─────────────────────────────────────────────────┘
""")

# ─────────────────────────────────────────────────────────────
# 7. GRÁFICOS
# ─────────────────────────────────────────────────────────────
print("─"*60)
print("  GERANDO GRÁFICOS...")
print("─"*60)

cores = {
    'verde':    '#2ecc71',
    'amarelo':  '#f39c12',
    'vermelho': '#e74c3c',
    'azul':     '#3498db',
    'cinza':    '#95a5a6',
    'roxo':     '#9b59b6',
    'bg':       '#1a1a2e',
    'panel':    '#16213e',
    'texto':    '#ecf0f1',
}

fig = plt.figure(figsize=(20, 16), facecolor=cores['bg'])
fig.suptitle('📊 DIA 4 - ANÁLISE DE COMPLETUDE | Master Data Quality',
             fontsize=22, color=cores['texto'], fontweight='bold', y=0.98)

gs = GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.35,
              left=0.06, right=0.97, top=0.93, bottom=0.05)

# ── GRÁFICO 1: Completude por campo (barras horizontais) ──
ax1 = fig.add_subplot(gs[0, :2])
ax1.set_facecolor(cores['panel'])

df_plot = df_campos.sort_values('pct_ok', ascending=True)
y_pos   = range(len(df_plot))
cores_barra = []
for _, row in df_plot.iterrows():
    if row['tipo'] == 'OBRIGATÓRIO':
        c = cores['vermelho'] if row['pct_ok'] < 95 else cores['verde']
    elif row['tipo'] == 'IMPORTANTE':
        c = cores['amarelo'] if row['pct_ok'] < 90 else cores['azul']
    else:
        c = cores['cinza']
    cores_barra.append(c)

bars = ax1.barh(list(y_pos), df_plot['pct_ok'].values,
                color=cores_barra, alpha=0.85, height=0.7)

for i, (bar, (_, row)) in enumerate(zip(bars, df_plot.iterrows())):
    ax1.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
             f"{row['pct_ok']:.1f}%  ({row['nulos']:,} nulos)",
             va='center', color=cores['texto'], fontsize=9)

ax1.axvline(95, color=cores['verde'],  ls='--', alpha=0.6, lw=1.5, label='Meta: 95%')
ax1.axvline(80, color=cores['amarelo'],ls='--', alpha=0.6, lw=1.5, label='Atenção: 80%')
ax1.set_yticks(list(y_pos))
ax1.set_yticklabels([f"{r['campo']} [{r['tipo'][:3]}]"
                     for _, r in df_plot.iterrows()], color=cores['texto'], fontsize=10)
ax1.set_xlim(0, 115)
ax1.set_xlabel('% Preenchimento', color=cores['texto'])
ax1.set_title('Completude por Campo', color=cores['texto'], fontsize=13, pad=10)
ax1.tick_params(colors=cores['texto'])
ax1.spines[:].set_color('#444')
ax1.legend(facecolor=cores['panel'], labelcolor=cores['texto'], fontsize=9)
for spine in ax1.spines.values(): spine.set_color('#444')

# ── GRÁFICO 2: Distribuição do Score (pizza) ──
ax2 = fig.add_subplot(gs[0, 2])
ax2.set_facecolor(cores['panel'])

dist_vals = df['classe_completude'].value_counts().sort_index()
cores_pizza = [cores['verde'], cores['azul'], cores['amarelo'], cores['vermelho']][:len(dist_vals)]
wedges, texts, autotexts = ax2.pie(
    dist_vals.values,
    labels=dist_vals.index,
    colors=cores_pizza,
    autopct='%1.1f%%',
    startangle=140,
    textprops={'color': cores['texto'], 'fontsize': 9},
)
for at in autotexts:
    at.set_fontsize(9)
    at.set_color('white')
ax2.set_title('Score de Completude\npor Registro', color=cores['texto'], fontsize=12, pad=10)
ax2.text(0, -1.4, f'Score Médio: {score_medio:.1f}%',
         ha='center', color=cores['texto'], fontsize=11, fontweight='bold')

# ── GRÁFICO 3: Score por categoria (barras) ──
ax3 = fig.add_subplot(gs[1, :2])
ax3.set_facecolor(cores['panel'])

df_cat_plot = df_cat.sort_values('score_medio')
cores_cat = [cores['vermelho'] if s < 60 else (cores['amarelo'] if s < 80 else cores['verde'])
             for s in df_cat_plot['score_medio']]
bars3 = ax3.bar(range(len(df_cat_plot)), df_cat_plot['score_medio'].values,
                color=cores_cat, alpha=0.85, width=0.65)

for bar, val in zip(bars3, df_cat_plot['score_medio'].values):
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
             f'{val:.0f}%', ha='center', color=cores['texto'], fontsize=9)

ax3.axhline(80, color=cores['amarelo'], ls='--', alpha=0.7, lw=1.5, label='Meta 80%')
ax3.axhline(95, color=cores['verde'],   ls='--', alpha=0.7, lw=1.5, label='Meta 95%')
ax3.set_xticks(range(len(df_cat_plot)))
ax3.set_xticklabels(df_cat_plot.index, rotation=30, ha='right', color=cores['texto'], fontsize=10)
ax3.set_ylim(0, 115)
ax3.set_ylabel('Score Médio (%)', color=cores['texto'])
ax3.set_title('Score de Completude por Categoria', color=cores['texto'], fontsize=13)
ax3.tick_params(colors=cores['texto'])
ax3.legend(facecolor=cores['panel'], labelcolor=cores['texto'])
for spine in ax3.spines.values(): spine.set_color('#444')

# ── GRÁFICO 4: Campos obrigatórios - violações ──
ax4 = fig.add_subplot(gs[1, 2])
ax4.set_facecolor(cores['panel'])

campos_viol   = list(violacoes.keys())
qtd_viol      = [len(v) for v in violacoes.values()]
cores_viol    = [cores['verde'] if q == 0 else (cores['amarelo'] if q < 100 else cores['vermelho'])
                 for q in qtd_viol]
bars4 = ax4.barh(campos_viol, qtd_viol, color=cores_viol, alpha=0.85, height=0.6)

for bar, val in zip(bars4, qtd_viol):
    ax4.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
             f'{val:,}', va='center', color=cores['texto'], fontsize=9)

ax4.set_title('Violações em Campos\nObrigatórios', color=cores['texto'], fontsize=12)
ax4.tick_params(colors=cores['texto'])
ax4.set_xlabel('Quantidade de Registros', color=cores['texto'])
for spine in ax4.spines.values(): spine.set_color('#444')

# ── GRÁFICO 5: Histograma score individual ──
ax5 = fig.add_subplot(gs[2, :2])
ax5.set_facecolor(cores['panel'])

n_bins = 20
counts, bins, patches = ax5.hist(df['score_completude'], bins=n_bins,
                                  color=cores['azul'], alpha=0.7, edgecolor='#222')
for patch, left in zip(patches, bins[:-1]):
    if left < 50:   patch.set_facecolor(cores['vermelho'])
    elif left < 70: patch.set_facecolor(cores['amarelo'])
    elif left < 90: patch.set_facecolor(cores['azul'])
    else:           patch.set_facecolor(cores['verde'])

ax5.axvline(score_medio, color='white', ls='--', lw=2, label=f'Média: {score_medio:.1f}%')
ax5.axvline(80,           color=cores['amarelo'], ls=':', lw=1.5, label='Meta mínima: 80%')
ax5.set_xlabel('Score de Completude (%)', color=cores['texto'])
ax5.set_ylabel('Quantidade de Materiais', color=cores['texto'])
ax5.set_title('Distribuição do Score de Completude por Material', color=cores['texto'], fontsize=13)
ax5.tick_params(colors=cores['texto'])
ax5.legend(facecolor=cores['panel'], labelcolor=cores['texto'])
for spine in ax5.spines.values(): spine.set_color('#444')

legend_patches = [
    mpatches.Patch(color=cores['vermelho'], label='D - Incompleto (<50%)'),
    mpatches.Patch(color=cores['amarelo'],  label='C - Regular (50-70%)'),
    mpatches.Patch(color=cores['azul'],     label='B - Bom (70-90%)'),
    mpatches.Patch(color=cores['verde'],    label='A - Completo (>90%)'),
]
ax5.legend(handles=legend_patches, facecolor=cores['panel'], labelcolor=cores['texto'], fontsize=9)

# ── GRÁFICO 6: KPIs financeiros ──
ax6 = fig.add_subplot(gs[2, 2])
ax6.set_facecolor(cores['panel'])
ax6.axis('off')

kpis = [
    ("📋 Total Materiais",   f"{total:,}",                   cores['azul']),
    ("✅ Score Médio",        f"{score_medio:.1f}%",          cores['verde'] if score_medio>=80 else cores['amarelo']),
    ("❌ Campos Obrig. Nulos",f"{total_violacoes:,} violações", cores['vermelho']),
    ("💰 Custo/Mês",          f"R$ {total_custo_mensal:,.0f}", cores['amarelo']),
    ("💸 Custo/Ano",          f"R$ {total_custo_anual:,.0f}",  cores['vermelho']),
    ("🎯 Meta",              "Score ≥ 95%",                   cores['cinza']),
]

ax6.set_title('KPIs de Completude', color=cores['texto'], fontsize=12, pad=15)
for i, (label, valor, cor) in enumerate(kpis):
    y = 0.88 - i * 0.155
    ax6.text(0.05, y,       label, transform=ax6.transAxes,
             fontsize=10, color=cores['texto'], va='center')
    ax6.text(0.95, y - 0.04, valor, transform=ax6.transAxes,
             fontsize=12, color=cor, va='center', ha='right', fontweight='bold')
    ax6.plot([0.02, 0.98], [y - 0.085, y - 0.085], color='#333', lw=0.8,
             transform=ax6.transAxes)

# Salvar
plt.savefig('02_completude.png', dpi=150, bbox_inches='tight',
            facecolor=cores['bg'], edgecolor='none')
plt.close()
print("\n  ✅ 02_completude.png salvo com sucesso!")

# ─────────────────────────────────────────────────────────────
# 8. EXPORTAR RELATÓRIO CSV
# ─────────────────────────────────────────────────────────────
df_export = df[['codigo', 'descricao', 'categoria',
                'score_completude', 'classe_completude']].copy()

for campo in campos_obrigatorios:
    df_export[f'vazio_{campo}'] = df[campo].isna().map({True: 'SIM', False: 'NAO'})

df_export = df_export.sort_values('score_completude', ascending=True)
df_export.to_csv('completude.csv', index=False, encoding='utf-8-sig')
print("  ✅ completude.csv salvo com sucesso!")
print(f"     → {len(df_export):,} registros | Score do pior: {df_export['score_completude'].min():.1f}%\n")

# ─────────────────────────────────────────────────────────────
# 9. RESUMO FINAL
# ─────────────────────────────────────────────────────────────
print("═"*60)
print("  ✅ DIA 4 CONCLUÍDO COM SUCESSO!")
print("═"*60)

abaixo_meta = (df['score_completude'] < 80).sum()
classe_A    = (df['classe_completude'] == 'A - Completo').sum()

print(f"""
  RESULTADOS DO DIA 4:

  📊 COMPLETUDE POR CAMPO:
     • {len(df_campos[df_campos['pct_ok'] >= 95])} campos com 95%+ preenchimento ✅
     • {len(df_campos[df_campos['pct_ok'] < 80])} campos abaixo da meta de 80% ❌

  🎯 SCORE POR REGISTRO:
     • Score médio: {score_medio:.1f}%
     • Registros Classe A (≥90%): {classe_A:,} ({classe_A/total*100:.1f}%)
     • Registros abaixo da meta: {abaixo_meta:,} ({abaixo_meta/total*100:.1f}%)

  ❌ CAMPOS OBRIGATÓRIOS:
     • {total_violacoes:,} violações encontradas
     • {materiais_com_violacao:,} materiais com ao menos 1 campo obrigatório vazio

  💰 IMPACTO FINANCEIRO:
     • Custo mensal da incompletude: R$ {total_custo_mensal:,.2f}
     • Custo anual estimado:         R$ {total_custo_anual:,.2f}

  📁 ARQUIVOS GERADOS:
     • completude.csv     (registros ordenados por score)
     • 02_completude.png  (4 gráficos profissionais)

  PROGRESSO DO PROJETO:
     ✅ Dia 1: Setup
     ✅ Dia 2: Geração de dados
     ✅ Dia 3: Análise de Duplicatas  (R$ 18,2M identificados)
     ✅ Dia 4: Análise de Completude  (R$ {total_custo_anual:,.0f}/ano) ← HOJE
     ⏳ Dia 5: Análise de Padronização (amanhã)
""")
print("═"*60)
print("  AMANHÃ: DIA 5 - Padronização e Consistência 🚀")
print("═"*60 + "\n")
