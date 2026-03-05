"""
╔══════════════════════════════════════════════════════════════════╗
║         DIA 30 — PLANO DE IMPLEMENTAÇÃO (ROADMAP 90 DIAS)       ║
║         Semana 5 · Projeto MDM Supply Chain                     ║
╚══════════════════════════════════════════════════════════════════╝

OBJETIVO:
  - Transformar os achados do projeto em ações concretas
  - Sequenciar as iniciativas por impacto e dependência
  - Definir responsáveis, prazos e critérios de sucesso
  - Gerar o Gantt chart do roadmap

📖 CONCEITO RÁPIDO — POR QUE SEQUENCIAR IMPORTA?
─────────────────────────────────────────────────────
  Você tem 6 problemas para resolver. Se tentar resolver
  todos ao mesmo tempo:
    › Equipe sobrecarregada
    › Nada termina direito
    › Resistência organizacional

  Se sequenciar por lógica de dependência:
    › Preços primeiro (alimenta ABC correto)
    › ABC correto → estoque mínimo mais preciso
    › Estoque mínimo → fornecedor com Lead time
    › Tudo junto → NCM com fiscal

  Ordem errada = retrabalho.
  Ordem certa = cada etapa sustenta a próxima.
─────────────────────────────────────────────────────
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import os, warnings
from datetime import datetime, timedelta
warnings.filterwarnings('ignore')

print("\n" + "="*68)
print("  DIA 30 — PLANO DE IMPLEMENTAÇÃO — ROADMAP 90 DIAS")
print("  Semana 5 · Projeto MDM Supply Chain")
print("="*68)

# ─────────────────────────────────────────────────────────────────
# 1. CARREGAR DADOS
# ─────────────────────────────────────────────────────────────────
CSV = 'E:/importantee/carreira/PROJETO MDM/mdm-supply-chain-project/data/raw/materiais_raw.csv'
df = None
for p in [CSV, 'data/raw/materiais_raw.csv', '../data/raw/materiais_raw.csv']:
    if os.path.exists(p):
        df = pd.read_csv(p)
        print(f"\n✅ CSV: {p} ({len(df):,} registros)")
        break
if df is None:
    raise FileNotFoundError('CSV não encontrado!')

os.makedirs('data/processed', exist_ok=True)
os.makedirs('visualizations', exist_ok=True)
ts   = datetime.now().strftime('%Y%m%d_%H%M%S')
HOJE = pd.Timestamp('2026-03-04')

df['valor']       = df['preco_unitario'] * df['estoque_atual']
df['ncm_str']     = df['ncm'].apply(lambda x: str(int(x)) if pd.notna(x) and x!=0 else '')
df['ncm_ok']      = df['ncm_str'].apply(lambda x: len(x)==8 and x.isdigit())
df['dias_parado'] = (HOJE - pd.to_datetime(df['ultima_movimentacao'])).dt.days.fillna(9999).astype(int)

N_NCM_BAD  = int((~df['ncm_ok']).sum())
N_SEM_FORN = int(df['fornecedor_principal'].isna().sum())
N_SEM_MIN  = int(df['estoque_minimo'].isna().sum())
N_PRECO_0  = int((df['preco_unitario'] == 0).sum())
N_DUP      = int(len(df) - df['codigo_material'].nunique())
N_OBSOL    = int(((df['dias_parado'] > 365) & (df['status'] == 'Ativo')).sum())
N_BLOQ     = int((df['status'] == 'Bloqueado').sum())

# ─────────────────────────────────────────────────────────────────
# 2. DEFINIÇÃO DAS INICIATIVAS — ESTRUTURA COMPLETA
# ─────────────────────────────────────────────────────────────────
# Cada iniciativa tem:
# - fase (1/2/3), semana_inicio, semana_fim
# - responsavel, esforço_horas, saving_M
# - tarefas, critério de sucesso, dependências

ROADMAP = [
    # ── FASE 1: CORREÇÕES IMEDIATAS (Semanas 1-4) ─────────────────
    {
        'id': 'I01',
        'nome': 'Corrigir preços zerados',
        'fase': 1,
        'semana_ini': 1,
        'semana_fim': 1,
        'resp': 'Analista MDM',
        'area': 'Supply',
        'esforco_h': 8,
        'saving_M': 0.44,
        'risco': 'BAIXO',
        'qtd': N_PRECO_0,
        'unidade': 'materiais',
        'tarefas': [
            'Exportar lista dos 99 materiais com preço zero',
            'Aplicar mediana da categoria (script Dia 16 já calculou)',
            'Validar com responsável_cadastro de cada item',
            'Atualizar no ERP e registrar no log de alterações',
        ],
        'criterio': f'{N_PRECO_0} materiais com preco_unitario > 0',
        'dependencia': None,
    },
    {
        'id': 'I02',
        'nome': 'Bloquear duplicatas',
        'fase': 1,
        'semana_ini': 1,
        'semana_fim': 2,
        'resp': 'Analista MDM + Almoxarife',
        'area': 'Supply + Operações',
        'esforco_h': 20,
        'saving_M': 2.8,
        'risco': 'ALTO',
        'qtd': N_DUP,
        'unidade': 'pares',
        'tarefas': [
            'Exportar relatório de duplicatas (script Dia 3)',
            'Classificar cada par: mesmo produto (bloquear) ou diferente (manter)',
            'Validar com almoxarife — ele conhece os itens físicos',
            'Bloquear código redundante no ERP',
            'Redirecionar ordens de compra abertas para código correto',
        ],
        'criterio': 'Zero duplicatas ativas no status aprovado',
        'dependencia': None,
    },
    {
        'id': 'I03',
        'nome': 'Ativar pipeline de cadastro',
        'fase': 1,
        'semana_ini': 2,
        'semana_fim': 3,
        'resp': 'Analista MDM + TI',
        'area': 'TI + Supply',
        'esforco_h': 24,
        'saving_M': 5.1,
        'risco': 'BAIXO',
        'qtd': 0,
        'unidade': 'processo',
        'tarefas': [
            'Configurar script do pipeline (Dia 26) no servidor',
            'Definir agendamento: rodar diariamente às 06h',
            'Testar com 50 cadastros novos em homologação',
            'Treinar equipe no novo fluxo (AUTO/SUPERVISOR/MDO)',
            'Documentar SLAs e responsáveis (Dia 25)',
        ],
        'criterio': 'Pipeline rodando em produção, 0 cadastros manuais sem validação',
        'dependencia': None,
    },
    {
        'id': 'I04',
        'nome': 'Corrigir NCMs — Fase 1 (curva A)',
        'fase': 1,
        'semana_ini': 2,
        'semana_fim': 4,
        'resp': 'Analista Fiscal + MDM',
        'area': 'Fiscal + Supply',
        'esforco_h': 32,
        'saving_M': 3.2,
        'risco': 'MÉDIO',
        'qtd': 240,   # só curva A
        'unidade': 'materiais (curva A)',
        'tarefas': [
            'Filtrar os 240 materiais curva A com NCM inválido',
            'Analista fiscal consulta tabela TIPI por categoria',
            'Validar NCM proposto com responsável do material',
            'Atualizar no ERP com rastreio de quem corrigiu',
            'Confirmar com sistema fiscal (NF-e) que NCM foi aceito',
        ],
        'criterio': '100% dos materiais curva A com NCM válido (8 dígitos, TIPI)',
        'dependencia': None,
    },

    # ── FASE 2: MELHORIAS ESTRUTURAIS (Semanas 5-9) ───────────────
    {
        'id': 'I05',
        'nome': 'Definir estoque mínimo',
        'fase': 2,
        'semana_ini': 5,
        'semana_fim': 8,
        'resp': 'Analista Supply + Planejamento',
        'area': 'Supply',
        'esforco_h': 40,
        'saving_M': 12.5,
        'risco': 'MÉDIO',
        'qtd': N_SEM_MIN,
        'unidade': 'materiais',
        'tarefas': [
            'Calcular consumo médio diário dos últimos 12 meses',
            'Levantar lead time real de cada fornecedor',
            'Aplicar fórmula: consumo_médio × lead_time × 1.3',
            'Validar mínimos com almoxarife e planejamento',
            'Parametrizar ponto de reposição no ERP',
        ],
        'criterio': f'≥90% dos {N_SEM_MIN} materiais com estoque_minimo definido',
        'dependencia': 'I02 (duplicatas resolvidas antes de calcular mínimos)',
    },
    {
        'id': 'I06',
        'nome': 'Cadastrar fornecedores principais',
        'fase': 2,
        'semana_ini': 5,
        'semana_fim': 9,
        'resp': 'Compras + Analista MDM',
        'area': 'Compras',
        'esforco_h': 48,
        'saving_M': 8.2,
        'risco': 'MÉDIO',
        'qtd': N_SEM_FORN,
        'unidade': 'materiais',
        'tarefas': [
            'Cruzar histórico de compras dos últimos 2 anos',
            'Identificar fornecedor mais frequente por material',
            'Validar fornecedores ativos no cadastro de terceiros',
            'Registrar fornecedor_principal e lead_time_dias no ERP',
            'Para novos fornecedores: processo de homologação',
        ],
        'criterio': f'≥80% dos {N_SEM_FORN} materiais com fornecedor_principal',
        'dependencia': None,
    },
    {
        'id': 'I07',
        'nome': 'Revisar e inativar obsoletos',
        'fase': 2,
        'semana_ini': 6,
        'semana_fim': 9,
        'resp': 'Analista MDM + Gestores de Área',
        'area': 'Supply + Operações',
        'esforco_h': 36,
        'saving_M': 0.0,
        'risco': 'MÉDIO',
        'qtd': N_OBSOL,
        'unidade': 'materiais',
        'tarefas': [
            'Exportar lista de 809 materiais parados > 365 dias',
            'Enviar para cada gestor de área validar: usar ou inativar?',
            'Prazo de resposta: 10 dias úteis (SLA definido)',
            'Sem resposta = inativação automática após 15 dias',
            'Para os que ficam ativos: justificativa obrigatória',
        ],
        'criterio': 'Taxa de obsoletos ativos < 5% (meta KPI Dia 25)',
        'dependencia': None,
    },
    {
        'id': 'I08',
        'nome': 'Corrigir NCMs — Fase 2 (curva B+C)',
        'fase': 2,
        'semana_ini': 7,
        'semana_fim': 10,
        'resp': 'Analista Fiscal',
        'area': 'Fiscal',
        'esforco_h': 40,
        'saving_M': 2.1,
        'risco': 'MÉDIO',
        'qtd': N_NCM_BAD - 240,
        'unidade': 'materiais (B+C)',
        'tarefas': [
            'Processar os 548 materiais curva B e C restantes',
            'Priorizar por categoria (Elétrico, Hidráulico primeiro)',
            'Usar tabela TIPI com mapeamento categoria → NCM',
            'Processar em lotes de 50 por semana',
        ],
        'criterio': f'100% dos {N_NCM_BAD} NCMs válidos no total',
        'dependencia': 'I04 (curva A concluída)',
    },

    # ── FASE 3: GOVERNANÇA CONTÍNUA (Semanas 10-13) ───────────────
    {
        'id': 'I09',
        'nome': 'Implantar KPIs e dashboard',
        'fase': 3,
        'semana_ini': 10,
        'semana_fim': 11,
        'resp': 'Analista MDM',
        'area': 'Supply + TI',
        'esforco_h': 16,
        'saving_M': 1.4,
        'risco': 'BAIXO',
        'qtd': 12,
        'unidade': 'KPIs monitorados',
        'tarefas': [
            'Publicar dashboard HTML (Dia 28) em servidor interno',
            'Agendar atualização automática semanal',
            'Distribuir relatório de KPIs para gestores (toda segunda)',
            'Definir dono de cada KPI e meta para 6 meses',
        ],
        'criterio': 'Dashboard atualizado semanalmente, KPIs enviados aos donos',
        'dependencia': 'I03 (pipeline ativo)',
    },
    {
        'id': 'I10',
        'nome': 'Treinar equipe no novo processo',
        'fase': 3,
        'semana_ini': 11,
        'semana_fim': 12,
        'resp': 'MDO + RH',
        'area': 'Todos',
        'esforco_h': 20,
        'saving_M': 3.5,
        'risco': 'BAIXO',
        'qtd': 0,
        'unidade': 'processo',
        'tarefas': [
            'Treinamento presencial: pipeline e novo fluxo de cadastro',
            'Material de apoio: Dicionário de Dados (Dia 24) impresso',
            'Simulação prática: cadastrar 10 materiais reais pelo pipeline',
            'Teste de conhecimento (>70% = aprovado)',
        ],
        'criterio': '100% da equipe de almoxarifado e compras treinada',
        'dependencia': 'I03 (pipeline em produção)',
    },
    {
        'id': 'I11',
        'nome': 'Revisão de contas contábeis e CST',
        'fase': 3,
        'semana_ini': 11,
        'semana_fim': 13,
        'resp': 'Fiscal + Contabilidade',
        'area': 'Fiscal',
        'esforco_h': 32,
        'saving_M': 1.2,
        'risco': 'ALTO',
        'qtd': N_BLOQ,
        'unidade': 'materiais bloqueados',
        'tarefas': [
            'Revisar os 438 materiais bloqueados — identificar motivo',
            'Corrigir conta_contabil nos que têm erro fiscal',
            'Validar CST ICMS com regulamento vigente',
            'Desbloquear após correção ou manter bloqueado c/ justificativa',
        ],
        'criterio': 'Bloqueados < 5% do total (meta: ≤165 materiais)',
        'dependencia': 'I08 (NCMs corrigidos)',
    },
    {
        'id': 'I12',
        'nome': 'Auditoria e entrega final',
        'fase': 3,
        'semana_ini': 12,
        'semana_fim': 13,
        'resp': 'MDO',
        'area': 'Supply + Gestão',
        'esforco_h': 24,
        'saving_M': 0.0,
        'risco': 'BAIXO',
        'qtd': 0,
        'unidade': 'processo',
        'tarefas': [
            'Rodar suite QA completa (Dia 20) — meta score ≥ 97%',
            'Validar KPIs: completude ≥ 95%, NCM = 100%, dup = 0%',
            'Apresentar resultados para diretoria (Dia 31)',
            'Documentar lições aprendidas e próximos ciclos',
        ],
        'criterio': 'QA Score ≥ 97% | Todos os KPIs críticos atingidos',
        'dependencia': 'Todas as iniciativas anteriores',
    },
]

# ─────────────────────────────────────────────────────────────────
# 3. EXIBIR ROADMAP NO TERMINAL
# ─────────────────────────────────────────────────────────────────
fases = {
    1: ('FASE 1 — CORREÇÕES IMEDIATAS', 'Semanas 1–4 | Impacto rápido'),
    2: ('FASE 2 — MELHORIAS ESTRUTURAIS', 'Semanas 5–10 | Maior saving'),
    3: ('FASE 3 — GOVERNANÇA CONTÍNUA', 'Semanas 11–13 | Sustentação'),
}

for fase_n, (titulo, sub) in fases.items():
    print(f"\n  ══ {titulo} — {sub} ══")
    fase_items = [r for r in ROADMAP if r['fase'] == fase_n]
    fase_saving = sum(r['saving_M'] for r in fase_items)
    for r in fase_items:
        print(f"\n  [{r['id']}] {r['nome']}")
        print(f"       Semanas: {r['semana_ini']}–{r['semana_fim']}  |  "
              f"Resp: {r['resp']}  |  "
              f"Esforço: {r['esforco_h']}h  |  "
              f"Saving: R${r['saving_M']:.1f}M  |  Risco: {r['risco']}")
        if r['qtd'] > 0:
            print(f"       Volume: {r['qtd']:,} {r['unidade']}")
        print(f"       Meta: {r['criterio']}")
        if r['dependencia']:
            print(f"       Depende de: {r['dependencia']}")
    print(f"\n  Saving total Fase {fase_n}: R$ {fase_saving:.1f}M/ano")

total_esforco = sum(r['esforco_h'] for r in ROADMAP)
total_saving  = sum(r['saving_M'] for r in ROADMAP)
print(f"\n  {'─'*60}")
print(f"  TOTAL DO ROADMAP:")
print(f"  ├─ Iniciativas:  {len(ROADMAP)}")
print(f"  ├─ Esforço total: {total_esforco}h (~{total_esforco/8:.0f} dias úteis)")
print(f"  ├─ Saving total: R$ {total_saving:.1f}M/ano")
print(f"  └─ Prazo:        13 semanas (~90 dias úteis)")

# ─────────────────────────────────────────────────────────────────
# 4. GRÁFICO GANTT
# ─────────────────────────────────────────────────────────────────
print("\n" + "-"*68)
print("  GERANDO GANTT CHART + DASHBOARD...")

BG, PANEL = '#0B1220', '#111927'
BORDER, TEXT, MUTED = '#1E2D40', '#E2E8F0', '#64748B'
C = {
    'teal':  '#00C9B1', 'blue':  '#4A9EDB', 'green': '#34D399',
    'red':   '#F87171', 'amber': '#FBB124', 'purple':'#A78BFA',
}
FASE_COR = {1: C['teal'], 2: C['blue'], 3: C['purple']}

fig = plt.figure(figsize=(24, 18), facecolor=BG)
fig.suptitle('DIA 30 — ROADMAP 90 DIAS  |  MDM Supply Chain',
             fontsize=18, color=TEXT, fontweight='bold', y=0.98)
gs = GridSpec(2, 3, figure=fig, hspace=0.42, wspace=0.35,
              left=0.04, right=0.97, top=0.93, bottom=0.04,
              height_ratios=[2.2, 1])

def stl(ax):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=MUTED, labelsize=9)
    for sp in ax.spines.values(): sp.set_color(BORDER)
    ax.title.set_color(TEXT)
    ax.xaxis.label.set_color(MUTED); ax.yaxis.label.set_color(MUTED)
    return ax

# ── G1: Gantt (ocupa 2 colunas) ──────────────────────────────────
ax1 = stl(fig.add_subplot(gs[0, :2]))
ax1.set_facecolor(PANEL)
ax1.grid(axis='x', color=BORDER, lw=0.5, alpha=0.6)

n = len(ROADMAP)
y_positions = list(range(n))
labels = [f"{r['id']} {r['nome']}" for r in ROADMAP]

for i, r in enumerate(ROADMAP):
    y   = n - 1 - i
    dur = r['semana_fim'] - r['semana_ini'] + 1
    cor = FASE_COR[r['fase']]

    # Barra principal
    ax1.barh(y, dur, left=r['semana_ini']-1, height=0.62,
             color=cor, alpha=0.85, zorder=3)
    # Label dentro da barra
    cx = r['semana_ini'] - 1 + dur / 2
    ax1.text(cx, y, f"R${r['saving_M']:.1f}M | {r['esforco_h']}h",
             ha='center', va='center', fontsize=8,
             color=BG, fontweight='bold')
    # Risco badge
    risco_cor = C['red'] if r['risco'] == 'ALTO' else \
                C['amber'] if r['risco'] == 'MÉDIO' else C['green']
    ax1.scatter(r['semana_fim'] - 0.5 + dur*0.5, y + 0.42,
                s=28, color=risco_cor, zorder=5)

# Faixas de fase
for fx, fy, fw, flbl in [
    (0, -0.5, 4,  'FASE 1\nImediata'),
    (4, -0.5, 6,  'FASE 2\nEstrutural'),
    (9, -0.5, 4,  'FASE 3\nGovernança'),
]:
    ax1.axvspan(fx, fx+fw, alpha=0.04,
                color=list(FASE_COR.values())[0 if fx==0 else 1 if fx==4 else 2])

ax1.set_yticks(list(range(n)))
ax1.set_yticklabels([f"{r['id']} — {r['nome']}" for r in reversed(ROADMAP)],
                    fontsize=9)
ax1.set_xticks(range(14))
ax1.set_xticklabels([f'S{i}' if i > 0 else 'Início' for i in range(14)], fontsize=9)
ax1.set_xlim(0, 13)
ax1.set_title('Gantt Chart — Roadmap 90 Dias (Semanas 1–13)', fontsize=13, pad=10)

patches = [mpatches.Patch(color=FASE_COR[f], label=fases[f][0].split(' — ')[1])
           for f in [1, 2, 3]]
patches += [mpatches.Patch(color=C['red'],   label='Risco Alto'),
            mpatches.Patch(color=C['amber'], label='Risco Médio'),
            mpatches.Patch(color=C['green'], label='Risco Baixo')]
ax1.legend(handles=patches, fontsize=8, facecolor=PANEL, labelcolor=TEXT,
           loc='lower right', ncol=3)

# ── G2: Saving acumulado ao longo das semanas ────────────────────
ax2 = stl(fig.add_subplot(gs[0, 2]))
ax2.grid(color=BORDER, lw=0.5, alpha=0.6)
semanas = list(range(1, 14))
saving_por_semana = []
for s in semanas:
    finalizados = [r for r in ROADMAP if r['semana_fim'] <= s]
    saving_por_semana.append(sum(r['saving_M'] for r in finalizados))

ax2.fill_between(semanas, saving_por_semana, color=C['teal'], alpha=0.20)
ax2.plot(semanas, saving_por_semana, color=C['teal'], lw=2.5, marker='o', ms=6)
for s, v in zip(semanas, saving_por_semana):
    if v > 0 and (v != saving_por_semana[s-2] if s > 1 else True):
        ax2.annotate(f'R${v:.1f}M', xy=(s, v), xytext=(s+0.1, v+0.4),
                     fontsize=8, color=C['teal'])
ax2.axhline(y=total_saving, color=MUTED, lw=1, ls='--', alpha=0.5,
            label=f'Total R${total_saving:.1f}M')
ax2.set_xticks(semanas)
ax2.set_xticklabels([f'S{s}' for s in semanas], fontsize=9)
ax2.set_title('Saving Acumulado por Semana (R$M/ano)', fontsize=12, pad=8)
ax2.set_ylabel('R$ Milhões')
ax2.legend(fontsize=9, facecolor=PANEL, labelcolor=TEXT)

# ── G3: Esforço por área ─────────────────────────────────────────
ax3 = stl(fig.add_subplot(gs[1, 0]))
ax3.grid(color=BORDER, lw=0.5, alpha=0.6)
areas = {}
for r in ROADMAP:
    a = r['area'].split(' + ')[0].strip()
    areas[a] = areas.get(a, 0) + r['esforco_h']
areas = dict(sorted(areas.items(), key=lambda x: x[1]))
cores_a = [C['teal'] if v == max(areas.values()) else C['blue'] for v in areas.values()]
bars = ax3.barh(list(areas.keys()), list(areas.values()),
                color=cores_a, alpha=0.85, height=0.6)
for b, v in zip(bars, areas.values()):
    ax3.text(v+0.5, b.get_y()+b.get_height()/2, f'{v}h',
             va='center', color=TEXT, fontsize=9, fontweight='bold')
ax3.set_title('Esforço por Área (horas)', fontsize=12, pad=8)

# ── G4: Saving por fase (pizza) ──────────────────────────────────
ax4 = stl(fig.add_subplot(gs[1, 1]))
fase_sav = {f: sum(r['saving_M'] for r in ROADMAP if r['fase'] == f) for f in [1,2,3]}
labels4  = [f'Fase {f}\n({fases[f][0].split("—")[1].strip()[:14]})\nR${v:.1f}M'
            for f, v in fase_sav.items()]
vals4    = list(fase_sav.values())
cores4   = [FASE_COR[f] for f in [1,2,3]]
ax4.pie(vals4, labels=labels4, colors=cores4, autopct='%1.0f%%',
        startangle=90, wedgeprops={'edgecolor': BG, 'lw': 2},
        textprops={'color': TEXT, 'fontsize': 9})
ax4.set_title('Saving por Fase (R$M/ano)', fontsize=12, pad=8)
ax4.set_facecolor(PANEL)

# ── G5: Resumo executivo ─────────────────────────────────────────
ax5 = fig.add_subplot(gs[1, 2])
ax5.set_facecolor(PANEL); ax5.axis('off')
for sp in ax5.spines.values(): sp.set_color(BORDER)
ax5.set_title('Resumo do Roadmap', fontsize=12, pad=8, color=TEXT)
cards = [
    ('Iniciativas',     f'{len(ROADMAP)}',                     C['teal']),
    ('Prazo Total',     '13 semanas (~90 dias)',               C['blue']),
    ('Saving Total',    f'R$ {total_saving:.1f}M/ano',         C['green']),
    ('Esforço',         f'{total_esforco}h',                   C['amber']),
    ('1º Saving',       'Semana 1 (preços + dup.)',            C['teal']),
    ('Risco Crítico',   'Duplicatas (validar c/ área)',        C['red']),
]
for i, (lbl, val, cor) in enumerate(cards):
    col = i % 2; row = i // 2
    xp  = 0.04 + col * 0.50
    yp  = 0.88 - row * 0.32
    ax5.text(xp, yp,      val, ha='left', fontsize=13, fontweight='bold',
             color=cor, transform=ax5.transAxes, family='monospace', wrap=True)
    ax5.text(xp, yp-0.10, lbl, ha='left', fontsize=9,
             color=MUTED, transform=ax5.transAxes)

plt.savefig('visualizations/18_roadmap_implementacao.png',
            dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print("\n  ✅ visualizations/18_roadmap_implementacao.png")

# ─────────────────────────────────────────────────────────────────
# 5. SALVAR CSVs DO ROADMAP
# ─────────────────────────────────────────────────────────────────
rows = []
for r in ROADMAP:
    rows.append({
        'id': r['id'],
        'nome': r['nome'],
        'fase': r['fase'],
        'semana_inicio': r['semana_ini'],
        'semana_fim': r['semana_fim'],
        'responsavel': r['resp'],
        'area': r['area'],
        'esforco_horas': r['esforco_h'],
        'saving_M': r['saving_M'],
        'risco': r['risco'],
        'volume': r['qtd'],
        'unidade': r['unidade'],
        'criterio_sucesso': r['criterio'],
        'dependencia': r['dependencia'] or '',
        'tarefas': ' | '.join(r['tarefas']),
    })
df_road = pd.DataFrame(rows)
df_road.to_csv(f'data/processed/roadmap_iniciativas_{ts}.csv',
               index=False, encoding='utf-8-sig')
print(f"  ✅ data/processed/roadmap_iniciativas_{ts}.csv")

# ─────────────────────────────────────────────────────────────────
# 6. RESUMO FINAL
# ─────────────────────────────────────────────────────────────────
print("\n" + "="*68)
print("  ✅ DIA 30 CONCLUÍDO — ROADMAP 90 DIAS!")
print("="*68)
print(f"""
  ROADMAP COMPLETO — 12 INICIATIVAS EM 13 SEMANAS:

  FASE 1 (S1–S4)  Correções imediatas
  ├─ I01 Preços zerados     → 1 semana   R$ 0,4M  Risco BAIXO
  ├─ I02 Duplicatas         → 2 semanas  R$ 2,8M  Risco ALTO
  ├─ I03 Pipeline ativo     → 2 semanas  R$ 5,1M  Risco BAIXO
  └─ I04 NCM curva A        → 3 semanas  R$ 3,2M  Risco MÉDIO

  FASE 2 (S5–S10)  Melhorias estruturais
  ├─ I05 Estoque mínimo     → 4 semanas  R$12,5M  Risco MÉDIO
  ├─ I06 Fornecedores       → 5 semanas  R$ 8,2M  Risco MÉDIO
  ├─ I07 Inativar obsoletos → 4 semanas  —        Risco MÉDIO
  └─ I08 NCM B+C            → 4 semanas  R$ 2,1M  Risco MÉDIO

  FASE 3 (S11–S13)  Governança contínua
  ├─ I09 KPIs + dashboard   → 2 semanas  R$ 1,4M  Risco BAIXO
  ├─ I10 Treinamento        → 2 semanas  R$ 3,5M  Risco BAIXO
  ├─ I11 Fiscal/CST         → 3 semanas  R$ 1,2M  Risco ALTO
  └─ I12 Auditoria final    → 2 semanas  —        Risco BAIXO

  TOTAL:  {total_esforco}h de esforço  |  R$ {total_saving:.1f}M/ano  |  13 semanas

  QUICK WIN (Semana 1):
  ├─ Corrigir 99 preços zerados (1 dia)
  └─ Iniciar validação de 299 duplicatas

  PRÓXIMO: DIA 31 — Apresentação Final para Gestão
""")
print("="*68 + "\n")
