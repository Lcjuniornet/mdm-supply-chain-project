"""
╔══════════════════════════════════════════════════════════════════╗
║         DIA 25 — SLA E KPIs DE QUALIDADE DE DADOS               ║
║         Semana 4 · Projeto MDM Supply Chain                     ║
╚══════════════════════════════════════════════════════════════════╝

OBJETIVO:
  - Definir e calcular KPIs de qualidade de dados mestres
  - Estabelecer SLAs por tipo de operação
  - Criar painel de métricas para acompanhamento contínuo
  - Gerar relatório de situação atual vs metas

📖 CONCEITO RÁPIDO — KPI vs SLA
─────────────────────────────────────────────────────
  KPI (Key Performance Indicator):
    Mede QUALIDADE. "Quantos materiais estão com
    cadastro completo?" → resposta: 80,4%

  SLA (Service Level Agreement):
    Mede TEMPO. "Em quanto tempo um cadastro novo
    deve ser aprovado?" → resposta: até 4 horas

  Juntos, respondem: estamos indo bem? (KPI)
  e estamos indo rápido o suficiente? (SLA)
─────────────────────────────────────────────────────
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import os, warnings
from datetime import datetime
warnings.filterwarnings('ignore')

print("\n" + "="*68)
print("  DIA 25 — SLA E KPIs DE QUALIDADE DE DADOS")
print("  Semana 4 · Projeto MDM Supply Chain")
print("="*68)

# ─────────────────────────────────────────────────────────────────
# 1. CARREGAR DADOS
# ─────────────────────────────────────────────────────────────────
CSV = 'E:/importantee/carreira/PROJETO MDM/mdm-supply-chain-project/data/raw/materiais_raw.csv'
df = None
for p in [CSV, 'data/raw/materiais_raw.csv', '../data/raw/materiais_raw.csv']:
    if os.path.exists(p):
        df = pd.read_csv(p)
        print(f"\n✅ CSV carregado: {p} ({len(df):,} registros)")
        break
if df is None:
    raise FileNotFoundError('CSV não encontrado!')

os.makedirs('data/processed', exist_ok=True)
os.makedirs('visualizations', exist_ok=True)
ts = datetime.now().strftime('%Y%m%d_%H%M%S')
HOJE = pd.Timestamp('2026-03-04')

df['valor_estoque']   = df['preco_unitario'] * df['estoque_atual']
df['ultima_mov_dt']   = pd.to_datetime(df['ultima_movimentacao'])
df['data_cad_dt']     = pd.to_datetime(df['data_cadastro'])
df['dias_parado']     = (HOJE - df['ultima_mov_dt']).dt.days
df['ncm_str']         = df['ncm'].apply(lambda x: str(int(x)) if pd.notna(x) and x != 0 else '')
df['ncm_valido']      = df['ncm_str'].apply(lambda x: len(x) == 8 and x.isdigit())

TOTAL = len(df)

# ─────────────────────────────────────────────────────────────────
# 2. DEFINIÇÃO DOS KPIs — 12 INDICADORES
# ─────────────────────────────────────────────────────────────────
# KPI = (valor_atual, meta, unidade, descrição, peso)

print("\n" + "-"*68)
print("  CALCULANDO KPIs DE QUALIDADE...")
print("-"*68)

kpis = {}

# ── KPI 1: COMPLETUDE GERAL ───────────────────────────────────────
campos_obrig = ['codigo_material','descricao','categoria','unidade_medida',
                'preco_unitario','estoque_atual','data_cadastro','status',
                'responsavel_cadastro']
completos = df[campos_obrig].notna().all(axis=1).sum()
kpis['completude_geral'] = {
    'valor': round(completos / TOTAL * 100, 1),
    'meta': 95.0,
    'unidade': '%',
    'descricao': 'Materiais com todos campos obrigatórios preenchidos',
    'peso': 30,
    'categoria': 'Completude',
}

# ── KPI 2: COMPLETUDE NCM ─────────────────────────────────────────
ncm_ok = df['ncm_valido'].sum()
kpis['completude_ncm'] = {
    'valor': round(ncm_ok / TOTAL * 100, 1),
    'meta': 100.0,
    'unidade': '%',
    'descricao': 'Materiais com NCM de 8 dígitos válido',
    'peso': 20,
    'categoria': 'Completude',
}

# ── KPI 3: COMPLETUDE FORNECEDOR ─────────────────────────────────
forn_ok = df['fornecedor_principal'].notna().sum()
kpis['completude_fornecedor'] = {
    'valor': round(forn_ok / TOTAL * 100, 1),
    'meta': 90.0,
    'unidade': '%',
    'descricao': 'Materiais com fornecedor principal cadastrado',
    'peso': 15,
    'categoria': 'Completude',
}

# ── KPI 4: ACURACIDADE DE PREÇOS ─────────────────────────────────
# Preços sem zero, sem negativo e dentro de IQR razoável
preco_ok = df[(df['preco_unitario'] > 0) &
              (df['preco_unitario'] < 2000)].shape[0]
kpis['acuracidade_precos'] = {
    'valor': round(preco_ok / TOTAL * 100, 1),
    'meta': 95.0,
    'unidade': '%',
    'descricao': 'Materiais com preço > 0 e dentro do limite razoável',
    'peso': 15,
    'categoria': 'Acuracidade',
}

# ── KPI 5: PADRONIZAÇÃO DESCRIÇÕES ───────────────────────────────
# Title Case = primeira letra de cada palavra maiúscula
desc_padrao = df['descricao'].apply(
    lambda x: str(x) == str(x).title() if pd.notna(x) else False
).sum()
kpis['padronizacao_descricoes'] = {
    'valor': round(desc_padrao / TOTAL * 100, 1),
    'meta': 95.0,
    'unidade': '%',
    'descricao': 'Descrições no padrão Title Case',
    'peso': 10,
    'categoria': 'Padronização',
}

# ── KPI 6: PADRONIZAÇÃO CATEGORIAS ───────────────────────────────
cats_validas = {'Acessórios','EPI','Eletrônico','Elétrico','Embalagem',
                'Escritório','Ferramentas','Fixação','Hidráulico','Limpeza',
                'Lubrificante','Mecânico','Peças','Pneumático','Químico'}
cat_ok = df['categoria'].isin(cats_validas).sum()
kpis['padronizacao_categorias'] = {
    'valor': round(cat_ok / TOTAL * 100, 1),
    'meta': 100.0,
    'unidade': '%',
    'descricao': 'Materiais com categoria dentro das 15 válidas',
    'peso': 10,
    'categoria': 'Padronização',
}

# ── KPI 7: MATERIAIS ATIVOS ───────────────────────────────────────
ativos = (df['status'] == 'Ativo').sum()
kpis['taxa_ativos'] = {
    'valor': round(ativos / TOTAL * 100, 1),
    'meta': 70.0,
    'unidade': '%',
    'descricao': 'Proporção de materiais com status Ativo',
    'peso': 5,
    'categoria': 'Ciclo de Vida',
}

# ── KPI 8: MATERIAIS OBSOLETOS ────────────────────────────────────
# Parados > 365 dias e ainda marcados como Ativo
obsoletos = df[(df['dias_parado'] > 365) & (df['status'] == 'Ativo')].shape[0]
kpis['taxa_obsoletos'] = {
    'valor': round(obsoletos / TOTAL * 100, 1),
    'meta': 5.0,
    'unidade': '%',
    'descricao': 'Materiais Ativos sem movimentação há > 365 dias',
    'peso': 10,
    'categoria': 'Ciclo de Vida',
    'inverso': True,  # meta é MENOR que este valor
}

# ── KPI 9: ESTOQUE MÍNIMO DEFINIDO ───────────────────────────────
est_min_ok = df['estoque_minimo'].notna().sum()
kpis['cobertura_estoque_minimo'] = {
    'valor': round(est_min_ok / TOTAL * 100, 1),
    'meta': 90.0,
    'unidade': '%',
    'descricao': 'Materiais com estoque mínimo definido',
    'peso': 5,
    'categoria': 'Completude',
}

# ── KPI 10: UNICIDADE DOS CÓDIGOS ─────────────────────────────────
unicos = df['codigo_material'].nunique()
kpis['unicidade_codigos'] = {
    'valor': round(unicos / TOTAL * 100, 1),
    'meta': 100.0,
    'unidade': '%',
    'descricao': 'Códigos de material únicos (sem duplicatas)',
    'peso': 20,
    'categoria': 'Unicidade',
}

# ── KPI 11: SCORE COMPLETUDE PONDERADO ───────────────────────────
# Score ponderado por criticidade dos campos
pesos_campos = {
    'codigo_material': 15, 'descricao': 15, 'categoria': 10,
    'ncm_str': 20, 'unidade_medida': 10, 'preco_unitario': 15,
    'estoque_atual': 5, 'fornecedor_principal': 10
}
score_total = 0
for campo, peso in pesos_campos.items():
    if campo == 'ncm_str':
        preench = df['ncm_valido'].mean()
    elif campo == 'preco_unitario':
        preench = (df[campo] > 0).mean()
    else:
        preench = df[campo].notna().mean()
    score_total += preench * peso

kpis['score_ponderado'] = {
    'valor': round(score_total, 1),
    'meta': 85.0,
    'unidade': 'pts',
    'descricao': 'Score ponderado por criticidade dos campos',
    'peso': 0,
    'categoria': 'Consolidado',
}

# ── KPI 12: DUPLICATAS ────────────────────────────────────────────
n_dup = TOTAL - df['codigo_material'].nunique()
kpis['taxa_duplicatas'] = {
    'valor': round(n_dup / TOTAL * 100, 1),
    'meta': 0.0,
    'unidade': '%',
    'descricao': 'Percentual de códigos duplicados na base',
    'peso': 0,
    'categoria': 'Unicidade',
    'inverso': True,
}

# ─────────────────────────────────────────────────────────────────
# 3. EXIBIR KPIs
# ─────────────────────────────────────────────────────────────────
print(f"\n  {'KPI':<35} {'ATUAL':>8} {'META':>7} {'STATUS':>8}")
print("  " + "-"*65)

for nome, k in kpis.items():
    val, meta = k['valor'], k['meta']
    inverso   = k.get('inverso', False)
    atingiu   = val <= meta if inverso else val >= meta
    icone     = '✅' if atingiu else ('⚠️ ' if abs(val-meta) < 10 else '❌')
    print(f"  {k['descricao'][:35]:<35} {val:>7.1f}{k['unidade']} {meta:>6.1f}{k['unidade']} {icone}")

# ─────────────────────────────────────────────────────────────────
# 4. DEFINIÇÃO DE SLAs
# ─────────────────────────────────────────────────────────────────
print("\n" + "-"*68)
print("  SLAs DEFINIDOS — TEMPOS MÁXIMOS POR OPERAÇÃO")
print("-"*68)

SLAS = [
    # operação, sla_horas, tipo, descricao
    ('Novo cadastro simples (automático)',    0.05,  'AUTOMÁTICO',
     'Score > 80 e campos OK → aprovação em segundos'),
    ('Novo cadastro — revisão supervisor',   4.0,   'SUPERVISOR',
     '1-2 alertas → supervisor valida em até 4h'),
    ('Novo cadastro — revisão MDO',          24.0,  'MDO',
     'Problemas moderados → MDO resolve em 1 dia útil'),
    ('Correção de preço zerado',             8.0,   'SUPERVISOR',
     'Requer pesquisa de preço de mercado'),
    ('Correção de NCM inválido',             24.0,  'FISCAL',
     'Requer consulta tabela TIPI com fiscal'),
    ('Bloqueio de material duplicado',       2.0,   'MDO',
     'Ação crítica — bloquear antes de compras'),
    ('Inativação de material obsoleto',      48.0,  'GESTOR',
     'Requer aprovação do gestor da área'),
    ('Revisão de categoria incorreta',       24.0,  'MDO',
     'Impacta relatórios — tratar com prioridade'),
    ('Cadastro de fornecedor novo',          72.0,  'COMPRAS',
     'Requer documentação e aprovação de compras'),
    ('Resposta a auditoria de dados',        4.0,   'MDO',
     'SLA de resposta para auditores internos/externos'),
]

tipos_cor = {
    'AUTOMÁTICO': '⚡', 'SUPERVISOR': '👤', 'MDO': '🎯',
    'FISCAL': '🔒', 'GESTOR': '📋', 'COMPRAS': '🛒',
}

print(f"\n  {'OPERAÇÃO':<42} {'SLA':>6} {'TIPO':<12} DESCRIÇÃO")
print("  " + "-"*78)
for op, horas, tipo, desc in SLAS:
    icone = tipos_cor.get(tipo, '•')
    sla_fmt = f'{horas:.0f}h' if horas >= 1 else f'{int(horas*60)}min'
    print(f"  {op:<42} {sla_fmt:>6} {icone} {tipo:<10} {desc[:30]}")

# ─────────────────────────────────────────────────────────────────
# 5. SITUAÇÃO ATUAL VS META — POR CATEGORIA DE KPI
# ─────────────────────────────────────────────────────────────────
print("\n" + "-"*68)
print("  SITUAÇÃO ATUAL VS METAS")
print("-"*68)

categorias_kpi = {}
for nome, k in kpis.items():
    cat = k['categoria']
    if cat not in categorias_kpi:
        categorias_kpi[cat] = {'atingidos': 0, 'total': 0}
    categorias_kpi[cat]['total'] += 1
    inverso = k.get('inverso', False)
    if (k['valor'] <= k['meta']) if inverso else (k['valor'] >= k['meta']):
        categorias_kpi[cat]['atingidos'] += 1

print(f"\n  {'DIMENSÃO':<20} {'KPIS OK':>8} {'TOTAL':>7} {'STATUS'}")
print("  " + "-"*50)
for cat, v in categorias_kpi.items():
    pct = v['atingidos'] / v['total'] * 100
    barra = '█' * v['atingidos'] + '░' * (v['total'] - v['atingidos'])
    print(f"  {cat:<20} {v['atingidos']:>8}/{v['total']}   {barra}  {pct:.0f}%")

total_ok  = sum(v['atingidos'] for v in categorias_kpi.values())
total_kpi = sum(v['total'] for v in categorias_kpi.values())
score_geral = total_ok / total_kpi * 100

# ─────────────────────────────────────────────────────────────────
# 6. PLANO DE AÇÃO — PRIORIZADO
# ─────────────────────────────────────────────────────────────────
print("\n" + "-"*68)
print("  PLANO DE AÇÃO — TOP 5 PRIORIDADES")
print("-"*68)

acoes = [
    (1, 'ALTA',   'Corrigir 623 NCMs vazios',
     'Consultar tabela TIPI por categoria', '623 materiais', '2 semanas'),
    (2, 'ALTA',   'Cadastrar 660 fornecedores',
     'Levantar fornecedores no ERP + Compras', '660 materiais', '3 semanas'),
    (3, 'ALTA',   'Definir estoque mínimo',
     'Calcular: consumo médio × lead time × 1.3', '660 materiais', '2 semanas'),
    (4, 'MÉDIA',  'Revisar 1.070 materiais obsoletos',
     'Inativar ou justificar status Ativo', '1.070 materiais', '4 semanas'),
    (5, 'MÉDIA',  'Corrigir 99 preços zerados',
     'Atribuir mediana da categoria (já calculado)', '99 materiais', '1 semana'),
]

for pri, nivel, acao, como, qtd, prazo in acoes:
    print(f"\n  #{pri} [{nivel}] {acao}")
    print(f"       Como:  {como}")
    print(f"       Qtd:   {qtd}  |  Prazo: {prazo}")

# ─────────────────────────────────────────────────────────────────
# 7. DASHBOARD VISUAL
# ─────────────────────────────────────────────────────────────────
print("\n" + "-"*68)
print("  GERANDO DASHBOARD...")
print("-"*68)

BG, PANEL = '#0b1220', '#111927'
BORDER, TEXT, MUTED = '#1e2d40', '#e2e8f0', '#64748b'
C = {
    'green':  '#34d399', 'red':    '#f87171',
    'orange': '#fb923c', 'blue':   '#38bdf8',
    'yellow': '#fbbf24', 'purple': '#a78bfa',
}

fig = plt.figure(figsize=(22, 16), facecolor=BG)
fig.suptitle('DIA 25 — KPIs E SLA DE QUALIDADE | MDM Supply Chain',
             fontsize=18, color=TEXT, fontweight='bold', y=0.98)
gs = GridSpec(3, 4, figure=fig, hspace=0.50, wspace=0.38,
              left=0.04, right=0.98, top=0.93, bottom=0.05)

def styled(ax):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=MUTED, labelsize=9)
    for sp in ax.spines.values(): sp.set_color(BORDER)
    ax.grid(color=BORDER, linewidth=0.5, alpha=0.6)
    ax.xaxis.label.set_color(MUTED); ax.yaxis.label.set_color(MUTED)
    ax.title.set_color(TEXT)
    return ax

def cor_kpi(val, meta, inverso=False):
    ok = val <= meta if inverso else val >= meta
    if ok: return C['green']
    gap = abs(val - meta)
    return C['orange'] if gap < 10 else C['red']

# G1–G4: Gauge KPIs principais (linha 1)
kpis_destaque = [
    ('completude_geral',     'Completude\nGeral'),
    ('completude_ncm',       'NCM\nVálido'),
    ('acuracidade_precos',   'Acuracidade\nPreços'),
    ('score_ponderado',      'Score\nPonderado'),
]

for i, (nome, label) in enumerate(kpis_destaque):
    ax = fig.add_subplot(gs[0, i])
    ax.set_facecolor(PANEL)
    ax.set_xlim(-1.2, 1.2); ax.set_ylim(-0.3, 1.2)
    ax.axis('off')

    k = kpis[nome]
    val, meta = k['valor'], k['meta']
    inv = k.get('inverso', False)
    cor = cor_kpi(val, meta, inv)
    pct = min(val / (meta * 1.1), 1.0) if not inv else min((meta * 2 - val) / meta, 1.0)
    pct = max(pct, 0.0)

    theta = np.linspace(np.pi, 0, 100)
    ax.plot(np.cos(theta), np.sin(theta), color=BORDER, lw=12, solid_capstyle='round')
    theta_val = np.linspace(np.pi, np.pi - pct * np.pi, 100)
    ax.plot(np.cos(theta_val), np.sin(theta_val), color=cor, lw=12, solid_capstyle='round')

    ax.text(0, 0.15, f'{val:.1f}{k["unidade"]}', ha='center', va='center',
            fontsize=20, fontweight='bold', color=cor, family='monospace')
    ax.text(0, -0.05, f'meta {meta:.0f}{k["unidade"]}', ha='center',
            fontsize=9, color=MUTED)
    ax.set_title(label, fontsize=11, pad=8, color=TEXT)
    for sp in ax.spines.values(): sp.set_color(cor); sp.set_linewidth(1.5)

# G5: Radar / bar de todas KPIs
ax5 = styled(fig.add_subplot(gs[1, :2]))
nomes_curtos = {
    'completude_geral': 'Completude\nGeral',
    'completude_ncm': 'NCM\nVálido',
    'completude_fornecedor': 'Fornecedor',
    'acuracidade_precos': 'Preços\nVálidos',
    'padronizacao_descricoes': 'Padron.\nDesc.',
    'padronizacao_categorias': 'Padron.\nCat.',
    'taxa_ativos': 'Taxa\nAtivos',
    'cobertura_estoque_minimo': 'Est.\nMínimo',
    'unicidade_codigos': 'Unicidade',
}
nomes_sel = [k for k in kpis if k in nomes_curtos]
vals  = [kpis[k]['valor'] for k in nomes_sel]
metas = [kpis[k]['meta'] for k in nomes_sel]
cores = [cor_kpi(kpis[k]['valor'], kpis[k]['meta'], kpis[k].get('inverso',False))
         for k in nomes_sel]
x = range(len(nomes_sel))
bars = ax5.bar(x, vals, color=cores, alpha=0.85, width=0.55, zorder=3)
ax5.scatter(x, metas, color=C['yellow'], s=80, zorder=5, marker='D', label='Meta')
for i, (bar, v) in enumerate(zip(bars, vals)):
    ax5.text(bar.get_x()+bar.get_width()/2, v+0.5, f'{v:.0f}%',
             ha='center', color=TEXT, fontsize=8, fontweight='bold')
ax5.set_xticks(list(x))
ax5.set_xticklabels([nomes_curtos[k] for k in nomes_sel], fontsize=8)
ax5.set_ylim(0, 115)
ax5.set_title('KPIs de Qualidade — Atual vs Meta', fontsize=12, pad=8)
ax5.set_ylabel('Score (%)')
ax5.legend(fontsize=9, facecolor=PANEL, labelcolor=TEXT)

# G6: SLA por tipo
ax6 = styled(fig.add_subplot(gs[1, 2:]))
sla_tipos = {}
for op, horas, tipo, desc in SLAS:
    if tipo not in sla_tipos:
        sla_tipos[tipo] = []
    sla_tipos[tipo].append(horas)
sla_med = {t: np.mean(h) for t, h in sla_tipos.items()}
cores_sla = [C['green'], C['blue'], C['orange'], C['red'], C['purple'], C['yellow']]
bars6 = ax6.barh(list(sla_med.keys()), list(sla_med.values()),
                 color=cores_sla[:len(sla_med)], alpha=0.85, height=0.5)
for bar, val in zip(bars6, sla_med.values()):
    ax6.text(val+0.2, bar.get_y()+bar.get_height()/2,
             f'{val:.0f}h', va='center', color=TEXT, fontsize=9, fontweight='bold')
ax6.set_title('SLA Médio por Responsável (horas)', fontsize=12, pad=8)
ax6.set_xlabel('Horas')
ax6.invert_yaxis()

# G7: KPIs por dimensão
ax7 = styled(fig.add_subplot(gs[2, :2]))
dims = list(categorias_kpi.keys())
ok_v   = [categorias_kpi[d]['atingidos'] for d in dims]
fail_v = [categorias_kpi[d]['total'] - categorias_kpi[d]['atingidos'] for d in dims]
x7 = range(len(dims))
ax7.bar(x7, ok_v,   color=C['green'],  alpha=0.85, label='Atingido', width=0.5)
ax7.bar(x7, fail_v, bottom=ok_v, color=C['red'], alpha=0.85, label='Abaixo', width=0.5)
ax7.set_xticks(list(x7))
ax7.set_xticklabels(dims, fontsize=9)
ax7.set_title('KPIs Atingidos por Dimensão', fontsize=12, pad=8)
ax7.legend(fontsize=9, facecolor=PANEL, labelcolor=TEXT)

# G8: KPI panel resumo
ax8 = fig.add_subplot(gs[2, 2:])
ax8.set_facecolor(PANEL)
ax8.axis('off')
for sp in ax8.spines.values(): sp.set_color(BORDER)
ax8.set_title('Resumo Executivo', fontsize=12, pad=8, color=TEXT)

kpi_cards = [
    ('KPIs Atingidos',     f'{total_ok}/{total_kpi}',    C['green']),
    ('Score Ponderado',    f'{kpis["score_ponderado"]["valor"]:.1f}/100', C['blue']),
    ('NCMs Pendentes',     '623',                        C['red']),
    ('Obsoletos Ativos',   '1.070',                      C['orange']),
    ('Preços Zerados',     '99',                         C['orange']),
    ('Sem Fornecedor',     '660',                        C['red']),
]
for i, (label, val, cor) in enumerate(kpi_cards):
    col = i % 2
    row = i // 2
    x_pos = 0.08 + col * 0.50
    y_pos = 0.80 - row * 0.30
    ax8.text(x_pos, y_pos, val, ha='left', va='center',
             fontsize=22, fontweight='bold', color=cor, transform=ax8.transAxes,
             family='monospace')
    ax8.text(x_pos, y_pos - 0.09, label, ha='left', va='center',
             fontsize=9, color=MUTED, transform=ax8.transAxes)

plt.savefig('visualizations/14_kpis_sla.png', dpi=150,
            bbox_inches='tight', facecolor=BG)
plt.close()
print("\n  ✅ visualizations/14_kpis_sla.png gerado!")

# ─────────────────────────────────────────────────────────────────
# 8. SALVAR RELATÓRIO CSV
# ─────────────────────────────────────────────────────────────────
rows_kpi = []
for nome, k in kpis.items():
    inv = k.get('inverso', False)
    atingiu = k['valor'] <= k['meta'] if inv else k['valor'] >= k['meta']
    rows_kpi.append({
        'kpi': nome,
        'descricao': k['descricao'],
        'categoria': k['categoria'],
        'valor_atual': k['valor'],
        'meta': k['meta'],
        'unidade': k['unidade'],
        'status': 'ATINGIDO' if atingiu else 'ABAIXO',
        'gap': round(abs(k['valor'] - k['meta']), 1),
    })
df_kpi = pd.DataFrame(rows_kpi)
df_sla = pd.DataFrame([
    {'operacao': op, 'sla_horas': h, 'responsavel': t, 'descricao': d}
    for op, h, t, d in SLAS
])
df_kpi.to_csv(f'data/processed/kpis_qualidade_{ts}.csv', index=False, encoding='utf-8-sig')
df_sla.to_csv(f'data/processed/slas_definidos_{ts}.csv', index=False, encoding='utf-8-sig')
print(f"  ✅ data/processed/kpis_qualidade_{ts}.csv")
print(f"  ✅ data/processed/slas_definidos_{ts}.csv")

# ─────────────────────────────────────────────────────────────────
# 9. RESUMO FINAL
# ─────────────────────────────────────────────────────────────────
print("\n" + "="*68)
print("  ✅ DIA 25 CONCLUÍDO — KPIs E SLA DEFINIDOS!")
print("="*68)
print(f"""
  📊 12 KPIs CALCULADOS:
  ├─ {total_ok} de {total_kpi} metas atingidas ({score_geral:.0f}%)
  ├─ Score ponderado: {kpis['score_ponderado']['valor']:.1f}/100 (meta: 85)
  └─ Maior gap: NCM válido {kpis['completude_ncm']['valor']:.1f}% (meta 100%)

  ⏱️  10 SLAs DEFINIDOS:
  ├─ Mais rápido: Auto-aprovação em 3 segundos
  ├─ Mais lento: Inativação de obsoleto (48h)
  └─ SLA padrão MDO: 24 horas

  🎯 TOP 3 AÇÕES PRIORITÁRIAS:
  ├─ 1. Corrigir 623 NCMs (impacto fiscal direto)
  ├─ 2. Cadastrar 660 fornecedores
  └─ 3. Definir estoque mínimo para 660 materiais

  PRÓXIMO: DIA 26 — Pipeline de Integração de Dados
""")
print("="*68 + "\n")
