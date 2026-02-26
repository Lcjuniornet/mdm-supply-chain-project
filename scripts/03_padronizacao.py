"""
╔══════════════════════════════════════════════════════════════╗
║         DIA 9 — ANÁLISE DE PADRONIZAÇÃO                     ║
║         Consistência de Textos · Master Data Quality        ║
╚══════════════════════════════════════════════════════════════╝

O que fazemos hoje:
  - Detectar inconsistências de caixa (MAIÚSCULA / minúscula / Mista)
  - Identificar abreviações inconsistentes
  - Encontrar espaços extras e caracteres indesejados
  - Detectar padrões de descrição fora do padrão
  - Gerar lista de correções prioritárias
  - Calcular impacto financeiro da falta de padronização
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import re
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────
# 1. CARREGAR DADOS
# ─────────────────────────────────────────────────────────────
print("\n" + "═"*62)
print("  DIA 9 — ANÁLISE DE PADRONIZAÇÃO")
print("═"*62)

import os
caminhos = ['../data/raw/materiais_raw.csv', 'materiais_raw.csv', 'materiais.csv']
df = None
for c in caminhos:
    if os.path.exists(c):
        df = pd.read_csv(c)
        print(f"\n✅ Arquivo carregado: {c} ({len(df):,} registros)")
        break

if df is None:
    print("\n⚠️  Gerando dados com problemas de padronização intencionais...")
    np.random.seed(42)
    n = 3300
    # Gerado com problemas reais de caixa/abreviação
    categorias = ['Mecânico','mecânico','MECANICO','Elétrico','ELETRICO',
                  'Hidráulico','hidraulico','Embalagem','EMBALAGEM','Escritório']
    uoms = ['UN','un','Un','UND','Und','und','PC','Pc','pc','PÇ',
            'KG','kg','Kg','LT','lt','Lt','L','l','CX','cx']
    df = pd.DataFrame({
        'codigo_material': [f'MAT-{str(i).zfill(5)}' for i in range(1, n+1)],
        'descricao':       [f'Item {i} teste' for i in range(1, n+1)],
        'categoria':       np.random.choice(categorias, n),
        'unidade_medida':  np.random.choice(uoms, n),
        'preco_unitario':  np.random.lognormal(4, 2, n).round(2),
        'estoque_atual':   np.random.randint(0, 500, n),
        'status':          np.random.choice(['Ativo','ativo','ATIVO','Inativo','INATIVO'], n),
        'fornecedor_principal': np.random.choice(['Fornecedor ABC','fornecedor abc','FORNECEDOR ABC','Metalúrgica XYZ'], n),
    })
    print(f"   Dados simulados: {len(df):,} registros")

# Garantir coluna valor
if 'valor_estoque' not in df.columns:
    df['valor_estoque'] = df['preco_unitario'].fillna(0) * df['estoque_atual'].fillna(0)

total = len(df)
print()

# ─────────────────────────────────────────────────────────────
# 2. MÉTODO 1 — CONSISTÊNCIA DE CAIXA (CASE)
# ─────────────────────────────────────────────────────────────
print("─"*62)
print("  MÉTODO 1: CONSISTÊNCIA DE CAIXA (MAIÚSCULAS/MINÚSCULAS)")
print("─"*62)

excluir = ['codigo_material','data_cadastro','ultima_movimentacao','localizacao_fisica','centro_custo','ncm']
colunas_texto = [c for c in df.columns if str(df[c].dtype) in ('object','string','str') and c not in excluir]
if not colunas_texto:
    colunas_texto = [c for c in df.columns if df[c].apply(lambda x: isinstance(x, str)).any() and c not in excluir]
# REMOVIDO
def tipo_caixa(valor):
    if pd.isna(valor):     return 'NULO'
    v = str(valor).strip()
    if v == v.upper():     return 'MAIÚSCULA'
    if v == v.lower():     return 'minúscula'
    if v == v.title():     return 'Title Case'
    return 'Mista Irregular'

resultado_caixa = []
for col in colunas_texto:
    dist = df[col].dropna().apply(tipo_caixa).value_counts()
    dominante = dist.index[0] if len(dist) > 0 else 'N/A'
    inconsistentes = dist[dist.index != dominante].sum() if len(dist) > 1 else 0
    pct_inconsist = inconsistentes / total * 100

    resultado_caixa.append({
        'campo':         col,
        'dominante':     dominante,
        'maiuscula':     dist.get('MAIÚSCULA', 0),
        'minuscula':     dist.get('minúscula', 0),
        'title':         dist.get('Title Case', 0),
        'mista':         dist.get('Mista Irregular', 0),
        'inconsistentes':inconsistentes,
        'pct_inconsist': round(pct_inconsist, 1),
    })

df_caixa = pd.DataFrame(resultado_caixa).sort_values('inconsistentes', ascending=False)

print(f"\n  {'CAMPO':<24} {'PADRÃO DOM.':<18} {'INCONSIST.':>10} {'%':>7}  STATUS")
print("  " + "─"*65)
for _, r in df_caixa.iterrows():
    st = "✅ OK" if r['pct_inconsist'] == 0 else ("⚠️  ATENÇÃO" if r['pct_inconsist'] < 5 else "🔴 CRÍTICO")
    print(f"  {r['campo']:<24} {r['dominante']:<18} {r['inconsistentes']:>10,} {r['pct_inconsist']:>6.1f}%  {st}")

total_inconsist_caixa = df_caixa['inconsistentes'].sum()
print(f"\n  Total de inconsistências de caixa: {total_inconsist_caixa:,}")

# ─────────────────────────────────────────────────────────────
# 3. MÉTODO 2 — ESPAÇOS EXTRAS E CARACTERES INDESEJADOS
# ─────────────────────────────────────────────────────────────
print("\n" + "─"*62)
print("  MÉTODO 2: ESPAÇOS EXTRAS E CARACTERES INDESEJADOS")
print("─"*62)

resultado_espacos = []
for col in colunas_texto:
    serie = df[col].dropna().astype(str)

    espaco_inicio   = serie.apply(lambda x: x != x.lstrip()).sum()
    espaco_fim      = serie.apply(lambda x: x != x.rstrip()).sum()
    espaco_duplo    = serie.apply(lambda x: '  ' in x).sum()
    char_especial   = serie.apply(lambda x: bool(re.search(r'[!@#$%^&*(){}\[\]|\\<>]', x))).sum()
    numero_inicio   = serie.apply(lambda x: bool(re.match(r'^\d', x))).sum()

    total_prob = espaco_inicio + espaco_fim + espaco_duplo + char_especial

    resultado_espacos.append({
        'campo':         col,
        'esp_inicio':    espaco_inicio,
        'esp_fim':       espaco_fim,
        'esp_duplo':     espaco_duplo,
        'char_especial': char_especial,
        'num_inicio':    numero_inicio,
        'total_prob':    total_prob,
    })

df_esp = pd.DataFrame(resultado_espacos).sort_values('total_prob', ascending=False)

print(f"\n  {'CAMPO':<24} {'ESP.INÍCIO':>10} {'ESP.FIM':>8} {'ESP.DUPLO':>10} {'CHAR ESP':>9} {'TOTAL':>7}")
print("  " + "─"*72)
for _, r in df_esp.iterrows():
    print(f"  {r['campo']:<24} {r['esp_inicio']:>10,} {r['esp_fim']:>8,} {r['esp_duplo']:>10,} {r['char_especial']:>9,} {r['total_prob']:>7,}")

# ─────────────────────────────────────────────────────────────
# 4. MÉTODO 3 — INCONSISTÊNCIA DE VALORES CATEGÓRICOS
# ─────────────────────────────────────────────────────────────
print("\n" + "─"*62)
print("  MÉTODO 3: INCONSISTÊNCIA DE VALORES CATEGÓRICOS")
print("─"*62)

colunas_cat = ['categoria', 'unidade_medida', 'status',
               'fornecedor_principal', 'responsavel_cadastro']
colunas_cat = [c for c in colunas_cat if c in df.columns]

resultado_cat = []
for col in colunas_cat:
    serie_orig = df[col].dropna().astype(str)
    serie_norm = serie_orig.str.strip().str.upper()

    n_orig = serie_orig.nunique()
    n_norm = serie_norm.nunique()
    reduziu = n_orig - n_norm
    pct_red = reduziu / n_orig * 100 if n_orig > 0 else 0

    # Grupos que seriam unificados
    grupos = {}
    for val_orig, val_norm in zip(serie_orig, serie_norm):
        if val_norm not in grupos:
            grupos[val_norm] = set()
        grupos[val_norm].add(val_orig)

    grupos_problematicos = {k: v for k, v in grupos.items() if len(v) > 1}

    resultado_cat.append({
        'campo':          col,
        'valores_antes':  n_orig,
        'valores_depois': n_norm,
        'reduziu':        reduziu,
        'pct_reducao':    round(pct_red, 1),
        'grupos_prob':    len(grupos_problematicos),
        'exemplos':       grupos_problematicos,
    })

df_cat_pad = pd.DataFrame(resultado_cat).sort_values('reduziu', ascending=False)

print(f"\n  {'CAMPO':<24} {'ANTES':>8} {'DEPOIS':>8} {'REDUZIU':>8} {'%':>7}  GRUPOS AFETADOS")
print("  " + "─"*68)
for _, r in df_cat_pad.iterrows():
    st = "✅" if r['reduziu'] == 0 else "🔴"
    print(f"  {st} {r['campo']:<22} {r['valores_antes']:>8,} {r['valores_depois']:>8,} {r['reduziu']:>8,} {r['pct_reducao']:>6.1f}%  {r['grupos_prob']} grupos")
    # Mostrar exemplos dos grupos problemáticos
    for chave, variantes in list(r['exemplos'].items())[:3]:
        variantes_str = ' | '.join(sorted(variantes))
        print(f"       → '{chave}': {variantes_str}")

# ─────────────────────────────────────────────────────────────
# 5. MÉTODO 4 — PADRÃO DAS DESCRIÇÕES
# ─────────────────────────────────────────────────────────────
print("\n" + "─"*62)
print("  MÉTODO 4: ANÁLISE DO PADRÃO DAS DESCRIÇÕES")
print("─"*62)

if 'descricao' in df.columns:
    desc = df['descricao'].dropna().astype(str)

    # Classificar padrão
    def classifica_descricao(d):
        d = d.strip()
        if len(d) < 5:                        return 'MUITO CURTA (<5 chars)'
        if len(d) > 80:                       return 'MUITO LONGA (>80 chars)'
        if d == d.upper():                    return 'TUDO MAIÚSCULO'
        if d == d.lower():                    return 'tudo minúsculo'
        if re.match(r'^[A-Z][a-z]', d):      return 'Title Case (OK)'
        if re.match(r'^[a-z]', d):           return 'início minúsculo'
        return 'Padrão irregular'

    df['_padrao_desc'] = desc.apply(classifica_descricao)
    dist_padrao = df['_padrao_desc'].value_counts()

    print(f"\n  {'PADRÃO':<28} {'QTD':>8} {'%':>8}")
    print("  " + "─"*48)
    for padrao, qtd in dist_padrao.items():
        pct = qtd/total*100
        st  = "✅" if 'OK' in padrao else ("⚠️ " if 'MUITO' in padrao else "🔴")
        print(f"  {st} {padrao:<26} {qtd:>8,} {pct:>7.1f}%")

    # Detectar abreviações inconsistentes nas descrições
    abreviacoes_comuns = {
        'em ': ['em ','Em ','EM '],
        'de ': ['de ','De ','DE '],
        'para ': ['para ','Para ','PARA '],
        'm10': ['m10','M10','M-10'],
        'inox': ['inox','INOX','Inox'],
        'pvc': ['pvc','PVC','Pvc'],
        'aço': ['aço','AÇO','Aço'],
    }

    print(f"\n  PREPOSIÇÕES/MATERIAIS COM CAIXA INCONSISTENTE:")
    print("  " + "─"*55)
    for termo, variantes in abreviacoes_comuns.items():
        contagens = {}
        for var in variantes:
            cnt = desc.str.contains(var, regex=False).sum()
            if cnt > 0:
                contagens[var] = cnt
        if len(contagens) > 1:
            total_termo = sum(contagens.values())
            print(f"\n  '{termo.strip()}' ({total_termo} ocorrências totais):")
            for var, cnt in sorted(contagens.items(), key=lambda x: -x[1]):
                pct = cnt/total_termo*100
                print(f"    {repr(var):<15} → {cnt:>5,} ({pct:.0f}%)")

# ─────────────────────────────────────────────────────────────
# 6. SIMULAÇÃO DE CORREÇÕES AUTOMÁTICAS
# ─────────────────────────────────────────────────────────────
print("\n" + "─"*62)
print("  SIMULAÇÃO: APLICAR CORREÇÕES AUTOMÁTICAS")
print("─"*62)

df_corrigido = df.copy()
correcoes_aplicadas = []

# Correção 1: Remover espaços extras em todas colunas texto
for col in colunas_texto:
    if col in df_corrigido.columns:
        antes = df_corrigido[col].dropna().apply(lambda x: str(x) != str(x).strip()).sum()
        df_corrigido[col] = df_corrigido[col].astype(str).str.strip()
        if antes > 0:
            correcoes_aplicadas.append(f"✅ {col}: {antes:,} espaços extras removidos")

# Correção 2: Padronizar status para Title Case
if 'status' in df_corrigido.columns:
    antes = df_corrigido['status'].nunique()
    df_corrigido['status_padrao'] = df_corrigido['status'].str.strip().str.title()
    depois = df_corrigido['status_padrao'].nunique()
    correcoes_aplicadas.append(f"✅ status: {antes} variações → {depois} (redução de {antes-depois})")

# Correção 3: Padronizar categoria para Title Case
if 'categoria' in df_corrigido.columns:
    antes = df_corrigido['categoria'].nunique()
    df_corrigido['categoria_padrao'] = df_corrigido['categoria'].str.strip().str.title()
    depois = df_corrigido['categoria_padrao'].nunique()
    correcoes_aplicadas.append(f"✅ categoria: {antes} variações → {depois} (redução de {antes-depois})")

# Correção 4: Padronizar unidade de medida para MAIÚSCULA
if 'unidade_medida' in df_corrigido.columns:
    antes = df_corrigido['unidade_medida'].dropna().nunique()
    df_corrigido['uom_padrao'] = df_corrigido['unidade_medida'].str.strip().str.upper()
    depois = df_corrigido['uom_padrao'].dropna().nunique()
    correcoes_aplicadas.append(f"✅ unidade_medida: {antes} variações → {depois} (redução de {antes-depois})")

# Correção 5: Padronizar descrição para Title Case
if 'descricao' in df_corrigido.columns:
    antes_min = df_corrigido['descricao'].dropna().apply(
        lambda x: str(x)[0].islower() if str(x) else False).sum()
    df_corrigido['descricao_padrao'] = df_corrigido['descricao'].apply(
        lambda x: str(x).strip().title() if pd.notna(x) else x)
    correcoes_aplicadas.append(f"✅ descricao: {antes_min:,} começando com minúscula corrigidas")

print()
for c in correcoes_aplicadas:
    print(f"  {c}")

# ─────────────────────────────────────────────────────────────
# 7. IMPACTO FINANCEIRO
# ─────────────────────────────────────────────────────────────
print("\n" + "─"*62)
print("  IMPACTO FINANCEIRO DA FALTA DE PADRONIZAÇÃO")
print("─"*62)

# Calcular registros com problemas de padronização
total_prob_cat = df_cat_pad['grupos_prob'].sum() if len(df_cat_pad) > 0 else 0
registros_afetados = min(int(total_inconsist_caixa + df_esp['total_prob'].sum()), total)
pct_afetados = registros_afetados / total * 100

custo_hora       = 60    # R$/hora
tempo_busca      = 5/60  # 5 min por busca mal sucedida
buscas_por_dia   = 20    # buscas que falham por falta de padronização
dias_uteis       = 250   # dias úteis por ano
custo_busca_ano  = custo_hora * tempo_busca * buscas_por_dia * dias_uteis

tempo_correcao_h = registros_afetados * 0.05 / 60  # 3 seg por registro
custo_correcao   = tempo_correcao_h * custo_hora

custo_pedido_erro = total_prob_cat * 200  # pedidos com código errado
custo_total_ano   = custo_busca_ano + custo_pedido_erro

print(f"""
  Registros com problemas de padronização: {registros_afetados:,} ({pct_afetados:.1f}%)
  Grupos categóricos problemáticos:         {total_prob_cat}

  ┌──────────────────────────────────────────────────────┐
  │         CUSTO ANUAL DA FALTA DE PADRONIZAÇÃO        │
  │                                                      │
  │  Tempo perdido em buscas sem resultado:              │
  │    R$ {custo_busca_ano:>10,.2f}/ano                          │
  │                                                      │
  │  Pedidos com código/categoria errados:               │
  │    R$ {custo_pedido_erro:>10,.2f}/ano                          │
  │                                                      │
  │  ─────────────────────────────────────────           │
  │  TOTAL ANUAL:  R$ {custo_total_ano:>10,.2f}                  │
  │  Custo p/ corrigir agora: R$ {custo_correcao:>8,.2f} (1x)   │
  └──────────────────────────────────────────────────────┘
""")

# ─────────────────────────────────────────────────────────────
# 8. GRÁFICOS
# ─────────────────────────────────────────────────────────────
print("─"*62)
print("  GERANDO GRÁFICOS...")
print("─"*62)

C = {'verde':'#2ecc71','amarelo':'#f39c12','vermelho':'#e74c3c','azul':'#3498db',
     'roxo':'#9b59b6','ciano':'#1abc9c','laranja':'#e67e22',
     'bg':'#1a1a2e','panel':'#16213e','texto':'#ecf0f1'}

fig = plt.figure(figsize=(20, 16), facecolor=C['bg'])
fig.suptitle('📊 DIA 9 — ANÁLISE DE PADRONIZAÇÃO | Master Data Quality',
             fontsize=20, color=C['texto'], fontweight='bold', y=0.98)

gs = GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.38,
              left=0.06, right=0.97, top=0.93, bottom=0.05)

# ── GRÁFICO 1: Inconsistências de caixa por campo ────────────
ax1 = fig.add_subplot(gs[0, :2])
ax1.set_facecolor(C['panel'])

df_c = df_caixa[df_caixa['inconsistentes'] > 0].sort_values('inconsistentes', ascending=True)
if len(df_c) > 0:
    cores_b = [C['vermelho'] if p > 10 else C['amarelo'] if p > 2 else C['ciano']
               for p in df_c['pct_inconsist']]
    bars = ax1.barh(df_c['campo'], df_c['inconsistentes'], color=cores_b, alpha=0.85)
    for bar, pct in zip(bars, df_c['pct_inconsist']):
        ax1.text(bar.get_width()*1.01, bar.get_y()+bar.get_height()/2,
                 f"{bar.get_width():.0f} ({pct:.1f}%)",
                 va='center', color=C['texto'], fontsize=9)
else:
    ax1.text(0.5, 0.5, 'Nenhuma inconsistência\nde caixa detectada! ✅',
             ha='center', va='center', color=C['verde'], fontsize=14,
             transform=ax1.transAxes)
ax1.set_title('Inconsistências de Caixa por Campo', color=C['texto'], fontsize=13, pad=10)
ax1.set_xlabel('Quantidade de Registros', color=C['texto'])
ax1.tick_params(colors=C['texto'])
for spine in ax1.spines.values(): spine.set_color('#444')

# ── GRÁFICO 2: Pizza — Padrão das Descrições ─────────────────
ax2 = fig.add_subplot(gs[0, 2])
ax2.set_facecolor(C['panel'])
if '_padrao_desc' in df.columns:
    dist_pd = df['_padrao_desc'].value_counts()
    cores_pd = [C['verde'] if 'OK' in l else (C['vermelho'] if 'MUITO' in l or 'irreg' in l else C['amarelo'])
                for l in dist_pd.index]
    wedges, texts, autotexts = ax2.pie(
        dist_pd.values, labels=[l[:18] for l in dist_pd.index],
        colors=cores_pd, autopct='%1.1f%%', startangle=140,
        textprops={'color': C['texto'], 'fontsize': 8})
    for at in autotexts: at.set_fontsize(8)
ax2.set_title('Padrão das Descrições', color=C['texto'], fontsize=12, pad=10)
for spine in ax2.spines.values(): spine.set_color('#444')

# ── GRÁFICO 3: Categorias — valores únicos antes vs depois ───
ax3 = fig.add_subplot(gs[1, :2])
ax3.set_facecolor(C['panel'])
if len(df_cat_pad) > 0:
    x    = range(len(df_cat_pad))
    w    = 0.35
    b1 = ax3.bar([i-w/2 for i in x], df_cat_pad['valores_antes'],  width=w, color=C['vermelho'], alpha=0.8, label='Antes (com inconsistências)')
    b2 = ax3.bar([i+w/2 for i in x], df_cat_pad['valores_depois'], width=w, color=C['verde'],    alpha=0.8, label='Depois (padronizado)')
    ax3.set_xticks(list(x))
    ax3.set_xticklabels(df_cat_pad['campo'], rotation=20, ha='right', color=C['texto'], fontsize=10)
    for bar in b1:
        ax3.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.1,
                 str(int(bar.get_height())), ha='center', color=C['texto'], fontsize=9)
    for bar in b2:
        ax3.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.1,
                 str(int(bar.get_height())), ha='center', color=C['texto'], fontsize=9)
    ax3.legend(facecolor=C['panel'], labelcolor=C['texto'])
ax3.set_title('Valores Únicos por Campo — Antes vs Depois da Padronização', color=C['texto'], fontsize=13)
ax3.set_ylabel('Quantidade de Valores Únicos', color=C['texto'])
ax3.tick_params(colors=C['texto'])
for spine in ax3.spines.values(): spine.set_color('#444')

# ── GRÁFICO 4: KPIs de padronização ──────────────────────────
ax4 = fig.add_subplot(gs[1, 2])
ax4.set_facecolor(C['panel'])
ax4.axis('off')

ax4.set_title('KPIs de Padronização', color=C['texto'], fontsize=12, pad=15)
kpis_pad = [
    ('📋 Total Registros',        f'{total:,}',                      C['azul']),
    ('⚠️  Inconsist. de Caixa',  f'{total_inconsist_caixa:,}',      C['vermelho']),
    ('🔤 Grupos Problemáticos',   f'{total_prob_cat}',               C['amarelo']),
    ('✅ Após Padronização',       f'{total_inconsist_caixa} → 0',   C['verde']),
    ('💰 Custo Anual',            f'R$ {custo_total_ano:,.0f}',      C['amarelo']),
    ('⚡ Custo Corrigir',          f'R$ {custo_correcao:,.0f} (1x)', C['verde']),
]
for i, (lbl, val, cor) in enumerate(kpis_pad):
    y = 0.88 - i*0.155
    ax4.text(0.05, y, lbl, transform=ax4.transAxes, fontsize=10, color=C['texto'], va='center')
    ax4.text(0.95, y-0.04, val, transform=ax4.transAxes, fontsize=11, color=cor,
             va='center', ha='right', fontweight='bold')
    ax4.plot([0.02, 0.98], [y-0.085, y-0.085], color='#333', lw=0.8, transform=ax4.transAxes)

# ── GRÁFICO 5: Impacto financeiro — barras ────────────────────
ax5 = fig.add_subplot(gs[2, :2])
ax5.set_facecolor(C['panel'])

problemas_fin = {
    'Buscas sem resultado\n(padronização)': custo_busca_ano,
    'Pedidos com código\nerrado': custo_pedido_erro,
}
labels_f = list(problemas_fin.keys())
values_f = list(problemas_fin.values())
cores_f  = [C['vermelho'], C['amarelo']]
bars_f = ax5.bar(labels_f, values_f, color=cores_f, alpha=0.85, width=0.5)
for bar, val in zip(bars_f, values_f):
    ax5.text(bar.get_x()+bar.get_width()/2, bar.get_height()*1.02,
             f'R$ {val:,.0f}', ha='center', color=C['texto'], fontsize=11, fontweight='bold')
ax5.axhline(custo_total_ano, color='white', ls='--', alpha=0.5, lw=1.5, label=f'Total: R$ {custo_total_ano:,.0f}/ano')
ax5.set_title('Custo Anual da Falta de Padronização por Tipo', color=C['texto'], fontsize=13)
ax5.set_ylabel('Custo Anual (R$)', color=C['texto'])
ax5.tick_params(colors=C['texto'])
ax5.legend(facecolor=C['panel'], labelcolor=C['texto'])
for spine in ax5.spines.values(): spine.set_color('#444')

# ── GRÁFICO 6: Progresso do projeto ──────────────────────────
ax6 = fig.add_subplot(gs[2, 2])
ax6.set_facecolor(C['panel'])
ax6.axis('off')

ax6.set_title('Progresso Acumulado', color=C['texto'], fontsize=12, pad=15)
dias_concluidos = 9
total_dias = 49
pct_proj = dias_concluidos / total_dias * 100

# Barra de progresso manual
ax6.add_patch(plt.Rectangle((0.05, 0.65), 0.9, 0.12,
              facecolor='#1a2a3a', edgecolor='#444', transform=ax6.transAxes))
ax6.add_patch(plt.Rectangle((0.05, 0.65), 0.9*(pct_proj/100), 0.12,
              facecolor=C['verde'], edgecolor=C['verde'], transform=ax6.transAxes))
ax6.text(0.5, 0.82, f'{pct_proj:.1f}% CONCLUÍDO', transform=ax6.transAxes,
         ha='center', fontsize=13, fontweight='bold', color=C['verde'])
ax6.text(0.5, 0.52, f'{dias_concluidos} de {total_dias} dias', transform=ax6.transAxes,
         ha='center', fontsize=11, color=C['texto'])

semanas = {
    'Sem. 1\n(1–7)':    (1, True),
    'Sem. 2\n(8–14)':   (8, False),
    'Sem. 3+':          (15, False),
}
ax6.text(0.5, 0.38, '✅ Dias 1–9 concluídos', transform=ax6.transAxes,
         ha='center', fontsize=10, color=C['verde'])
ax6.text(0.5, 0.28, '⏳ Dias 10–49 restantes', transform=ax6.transAxes,
         ha='center', fontsize=10, color=C['amarelo'])
ax6.text(0.5, 0.12, f'Economia mapeada até agora:\nR$ 20,7M/ano', transform=ax6.transAxes,
         ha='center', fontsize=10, color=C['ciano'], fontweight='bold')

plt.savefig('03_padronizacao.png', dpi=150, bbox_inches='tight',
            facecolor=C['bg'], edgecolor='none')
plt.close()
print("  ✅ 03_padronizacao.png gerado!")

# ─────────────────────────────────────────────────────────────
# 9. EXPORTAR CSV DE CORREÇÕES
# ─────────────────────────────────────────────────────────────
# Arquivo com todos os registros + flags de problemas
df_export = df[['codigo_material','descricao','categoria','unidade_medida','status']].copy()

if 'descricao' in df.columns:
    df_export['desc_inicio_minusculo'] = df['descricao'].dropna().reindex(df.index).apply(
        lambda x: 'SIM' if pd.notna(x) and str(x) and str(x)[0].islower() else 'NAO')
if 'categoria' in df.columns:
    df_export['categoria_inconsistente'] = df['categoria'].apply(
        lambda x: 'SIM' if pd.notna(x) and str(x) != str(x).strip() else 'NAO')
if 'unidade_medida' in df.columns:
    df_export['uom_nao_maiusculo'] = df['unidade_medida'].apply(
        lambda x: 'SIM' if pd.notna(x) and str(x) != str(x).upper().strip() else 'NAO')

df_export['total_problemas'] = (
    (df_export.get('desc_inicio_minusculo','NAO') == 'SIM').astype(int) +
    (df_export.get('categoria_inconsistente','NAO') == 'SIM').astype(int) +
    (df_export.get('uom_nao_maiusculo','NAO') == 'SIM').astype(int)
)

df_export = df_export.sort_values('total_problemas', ascending=False)
df_export.to_csv('padronizacao.csv', index=False, encoding='utf-8-sig')
print("  ✅ padronizacao.csv gerado!")

# ─────────────────────────────────────────────────────────────
# 10. RESUMO FINAL
# ─────────────────────────────────────────────────────────────
print("\n" + "═"*62)
print("  ✅ DIA 9 CONCLUÍDO COM SUCESSO!")
print("═"*62)

probs_totais = total_inconsist_caixa + df_esp['total_prob'].sum()
print(f"""
  RESULTADOS DO DIA 9:

  🔤 INCONSISTÊNCIAS DE CAIXA:
     · {total_inconsist_caixa:,} registros com caixa não padronizada
     · {df_caixa[df_caixa['inconsistentes']>0]['campo'].count()} campos afetados

  📋 ESPAÇOS E CARACTERES:
     · {int(df_esp['total_prob'].sum()):,} problemas encontrados
     · Solução: strip() automático em todos os campos

  🏷️  CATEGORIAS INCONSISTENTES:
     · {total_prob_cat} grupos com variações de escrita
     · Ex: "Mecânico" / "mecânico" / "MECANICO" = mesmo item

  💰 IMPACTO FINANCEIRO:
     · Custo anual da falta de padronização: R$ {custo_total_ano:,.2f}
     · Custo para corrigir agora (1x): R$ {custo_correcao:,.2f}
     · ROI: corrigir em 1 semana, economizar o ano todo!

  📁 ARQUIVOS GERADOS:
     · 03_padronizacao.png  (6 gráficos)
     · padronizacao.csv     ({len(df_export):,} registros com flags)

  PROGRESSO DO PROJETO:
     ✅ Dia 1: Setup
     ✅ Dia 2: Geração de dados
     ✅ Dia 3: Duplicatas       (R$ 18,2M)
     ✅ Dia 4: Completude
     ✅ Dia 5: Análise Exploratória
     ✅ Dia 6: Dashboard Excel
     ✅ Dia 7: Checkpoint Semana 1
     ✅ Dia 8: SQL (análises avançadas)
     ✅ Dia 9: Padronização    ← VOCÊ ESTÁ AQUI
     ⏳ Dia 10: Fornecedores   (amanhã)
""")
print("═"*62)
print("  AMANHÃ — DIA 10: Análise de Fornecedores 🚀")
print("═"*62 + "\n")
