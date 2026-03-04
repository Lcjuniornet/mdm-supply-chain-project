"""
╔══════════════════════════════════════════════════════════════════╗
║         DIA 26 — PIPELINE DE INTEGRAÇÃO DE DADOS                ║
║         Semana 4 · Projeto MDM Supply Chain                     ║
╚══════════════════════════════════════════════════════════════════╝

OBJETIVO:
  - Construir pipeline completo: Ingestão → Validação →
    Enriquecimento → Aprovação → Saída
  - Conectar todos os scripts anteriores num fluxo único
  - Registrar métricas de cada etapa (quantos passaram, falharam)
  - Gerar relatório de rastreabilidade do pipeline

📖 CONCEITO RÁPIDO — O QUE É UM PIPELINE DE DADOS?
─────────────────────────────────────────────────────
  Pense numa linha de produção de fábrica:

  [Matéria-prima] → [Corte] → [Solda] → [Pintura] → [Produto final]

  Um pipeline de dados funciona igual:

  [CSV bruto] → [Ingestão] → [Validação] → [Enriquecimento]
             → [Aprovação] → [Saída limpa]

  Em cada etapa, alguns materiais passam, outros são
  retidos para correção. No final, você sabe exatamente
  quantos entraram e quantos saíram em cada fase.
─────────────────────────────────────────────────────
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import os, json, warnings
from datetime import datetime
warnings.filterwarnings('ignore')

print("\n" + "="*68)
print("  DIA 26 — PIPELINE DE INTEGRAÇÃO DE DADOS")
print("  Semana 4 · Projeto MDM Supply Chain")
print("="*68)

# ─────────────────────────────────────────────────────────────────
# CONFIGURAÇÃO
# ─────────────────────────────────────────────────────────────────
CSV = 'E:/importantee/carreira/PROJETO MDM/mdm-supply-chain-project/data/raw/materiais_raw.csv'
df_raw = None
for p in [CSV, 'data/raw/materiais_raw.csv', '../data/raw/materiais_raw.csv']:
    if os.path.exists(p):
        df_raw = pd.read_csv(p)
        print(f"\n✅ CSV carregado: {p} ({len(df_raw):,} registros)")
        break
if df_raw is None:
    raise FileNotFoundError('CSV não encontrado!')

os.makedirs('data/processed', exist_ok=True)
os.makedirs('visualizations', exist_ok=True)
ts  = datetime.now().strftime('%Y%m%d_%H%M%S')
t0  = datetime.now()
HOJE = pd.Timestamp('2026-03-04')

CATS_VALIDAS = {
    'Acessórios','EPI','Eletrônico','Elétrico','Embalagem','Escritório',
    'Ferramentas','Fixação','Hidráulico','Limpeza','Lubrificante',
    'Mecânico','Peças','Pneumático','Químico'
}
UOM_VALIDAS = {'UN','KG','L','M','CX','PCT','GL','RL','M²','MT','PC','GR'}

# ─────────────────────────────────────────────────────────────────
# CLASSE PIPELINE — registra cada etapa
# ─────────────────────────────────────────────────────────────────
class Pipeline:
    def __init__(self, nome, df_total):
        self.nome     = nome
        self.total    = len(df_total)
        self.etapas   = []
        self.log      = []

    def registrar(self, etapa, passou, retido, motivo=''):
        self.etapas.append({
            'etapa':   etapa,
            'passou':  passou,
            'retido':  retido,
            'taxa':    round(passou / self.total * 100, 1),
            'motivo':  motivo,
        })
        print(f"  {'✅' if retido == 0 else '⚠️ '} {etapa:<40} "
              f"Passou: {passou:>5,}  Retido: {retido:>4,}  ({passou/self.total*100:.1f}%)")

    def resumo(self):
        return pd.DataFrame(self.etapas)

pipe = Pipeline('MDM-PIPELINE', df_raw)

# ─────────────────────────────────────────────────────────────────
# STAGE 1 — INGESTÃO
# ─────────────────────────────────────────────────────────────────
print("\n" + "-"*68)
print("  STAGE 1 — INGESTÃO E LIMPEZA INICIAL")
print("-"*68 + "\n")

df = df_raw.copy()

# 1a: Remover linhas completamente vazias
antes = len(df)
df = df.dropna(how='all')
pipe.registrar('1a. Remover linhas totalmente vazias',
               len(df), antes - len(df))

# 1b: Converter e limpar tipos
df['preco_unitario']   = pd.to_numeric(df['preco_unitario'], errors='coerce').fillna(0)
df['estoque_atual']    = pd.to_numeric(df['estoque_atual'],  errors='coerce').fillna(0).astype(int)
df['ultima_mov_dt']    = pd.to_datetime(df['ultima_movimentacao'], errors='coerce')
df['data_cad_dt']      = pd.to_datetime(df['data_cadastro'],       errors='coerce')
df['dias_parado']      = (HOJE - df['ultima_mov_dt']).dt.days.fillna(9999).astype(int)
df['valor_estoque']    = df['preco_unitario'] * df['estoque_atual']

# NCM: float → string 8 dígitos
df['ncm_str'] = df['ncm'].apply(
    lambda x: str(int(x)) if pd.notna(x) and x != 0 else ''
)

# Padronizar textos: strip espaços extras
for col in ['descricao','categoria','fornecedor_principal','status','unidade_medida']:
    df[col] = df[col].astype(str).str.strip()
    df[col] = df[col].replace('nan', '')

pipe.registrar('1b. Normalizar tipos e limpar espaços',
               len(df), 0, 'Conversão de tipos automática')

# 1c: Validar campos mínimos para continuar no pipeline
mask_basico = (
    df['codigo_material'].notna() &
    df['descricao'].str.len().gt(0) &
    (df['preco_unitario'] >= 0)
)
df_ok  = df[mask_basico].copy()
df_rej = df[~mask_basico].copy()
df_rej['motivo_retencao'] = 'STAGE1: Campos mínimos ausentes'
pipe.registrar('1c. Filtrar campos mínimos obrigatórios',
               len(df_ok), len(df_rej), 'Sem código, descrição ou preço')

s1_out = len(df_ok)

# ─────────────────────────────────────────────────────────────────
# STAGE 2 — VALIDAÇÃO
# ─────────────────────────────────────────────────────────────────
print("\n" + "-"*68)
print("  STAGE 2 — VALIDAÇÃO DE REGRAS DE NEGÓCIO")
print("-"*68 + "\n")

df = df_ok.copy()
df['alertas']  = [[] for _ in range(len(df))]
df['erros']    = [[] for _ in range(len(df))]

# 2a: Validar NCM
def valida_ncm(x):
    s = str(x).strip()
    return len(s) == 8 and s.isdigit()

ncm_invalido = ~df['ncm_str'].apply(valida_ncm)
for idx in df[ncm_invalido].index:
    df.at[idx, 'erros'].append('NCM inválido ou vazio')
pipe.registrar('2a. Validar NCM (8 dígitos obrigatório)',
               (~ncm_invalido).sum(), ncm_invalido.sum(), 'NCM != 8 dígitos')

# 2b: Validar preço
preco_zero = df['preco_unitario'] == 0
for idx in df[preco_zero].index:
    df.at[idx, 'erros'].append('Preço zerado')
pipe.registrar('2b. Validar preço > 0',
               (~preco_zero).sum(), preco_zero.sum())

# 2c: Validar categoria
cat_invalida = ~df['categoria'].isin(CATS_VALIDAS)
for idx in df[cat_invalida].index:
    df.at[idx, 'erros'].append(f'Categoria inválida: {df.at[idx,"categoria"]}')
pipe.registrar('2c. Validar categoria (15 valores)',
               (~cat_invalida).sum(), cat_invalida.sum())

# 2d: Alertas (não bloqueantes)
sem_forn = (df['fornecedor_principal'] == '') | df['fornecedor_principal'].isna()
for idx in df[sem_forn].index:
    df.at[idx, 'alertas'].append('Sem fornecedor')

sem_min = df['estoque_minimo'].isna()
for idx in df[sem_min].index:
    df.at[idx, 'alertas'].append('Sem estoque mínimo')

parado = df['dias_parado'] > 365
for idx in df[parado].index:
    df.at[idx, 'alertas'].append(f'Parado {df.at[idx,"dias_parado"]} dias')

pipe.registrar('2d. Alertas não-bloqueantes registrados',
               len(df), 0,
               f'Sem forn: {sem_forn.sum()} | Sem min: {sem_min.sum()} | Parado: {parado.sum()}')

# Separar: com erros → retidos; sem erros → avançam
df['n_erros']   = df['erros'].apply(len)
df['n_alertas'] = df['alertas'].apply(len)
df_com_erros    = df[df['n_erros'] > 0].copy()
df_sem_erros    = df[df['n_erros'] == 0].copy()

pipe.registrar('2e. Separar aprovados vs. com erros críticos',
               len(df_sem_erros), len(df_com_erros))

s2_out = len(df_sem_erros)

# ─────────────────────────────────────────────────────────────────
# STAGE 3 — ENRIQUECIMENTO
# ─────────────────────────────────────────────────────────────────
print("\n" + "-"*68)
print("  STAGE 3 — ENRIQUECIMENTO DE DADOS")
print("-"*68 + "\n")

df = df_sem_erros.copy()

# 3a: Calcular curva ABC por valor de estoque
df_abc = df[df['valor_estoque'] > 0].copy()
df_abc = df_abc.drop_duplicates(subset='codigo_material').sort_values('valor_estoque', ascending=False)
df_abc['pct_acumulado'] = df_abc['valor_estoque'].cumsum() / df_abc['valor_estoque'].sum() * 100
df_abc['curva_abc'] = df_abc['pct_acumulado'].apply(
    lambda x: 'A' if x <= 80 else ('B' if x <= 95 else 'C')
)
df = df.merge(df_abc[['codigo_material','curva_abc']], on='codigo_material', how='left')
df['curva_abc'] = df['curva_abc'].fillna('C')
abc_counts = df['curva_abc'].value_counts()
pipe.registrar('3a. Calcular curva ABC por valor de estoque',
               len(df), 0,
               f'A:{abc_counts.get("A",0)} B:{abc_counts.get("B",0)} C:{abc_counts.get("C",0)}')

# 3b: Calcular score de qualidade por material
def calcular_score(row):
    score = 0
    # Campos obrigatórios (70 pts total)
    if row['codigo_material']:         score += 15
    if row['descricao']:               score += 15
    if row['categoria'] in CATS_VALIDAS: score += 10
    if valida_ncm(row['ncm_str']):     score += 20
    if row['preco_unitario'] > 0:      score += 10
    # Campos complementares (30 pts)
    if row['fornecedor_principal'] and row['fornecedor_principal'] != '': score += 10
    if pd.notna(row['estoque_minimo']): score += 10
    if row['localizacao_fisica'] and row['localizacao_fisica'] != 'nan': score += 5
    if row['centro_custo'] and row['centro_custo'] != 'nan': score += 5
    return score

df['score_qualidade'] = df.apply(calcular_score, axis=1)
score_med = df['score_qualidade'].mean()
pipe.registrar('3b. Calcular score de qualidade individual',
               len(df), 0, f'Score médio: {score_med:.1f}/100')

# 3c: Classificar criticidade de estoque
def classifica_estoque(row):
    if pd.isna(row['estoque_minimo']):
        return 'SEM_MINIMO'
    if row['estoque_atual'] == 0:
        return 'ZERADO'
    if row['estoque_atual'] < row['estoque_minimo']:
        return 'ABAIXO_MINIMO'
    if row['estoque_atual'] < row['estoque_minimo'] * 1.2:
        return 'ALERTA'
    return 'NORMAL'

df['status_estoque'] = df.apply(classifica_estoque, axis=1)
est_counts = df['status_estoque'].value_counts()
pipe.registrar('3c. Classificar situação de estoque',
               len(df), 0,
               f'Normal:{est_counts.get("NORMAL",0)} '
               f'Alerta:{est_counts.get("ALERTA",0)} '
               f'Abaixo:{est_counts.get("ABAIXO_MINIMO",0)}')

# 3d: Identificar materiais candidatos a inativação
df['candidato_inativacao'] = (
    (df['dias_parado'] > 365) &
    (df['status'] == 'Ativo') &
    (df['estoque_atual'] > 0)
)
n_candidatos = df['candidato_inativacao'].sum()
pipe.registrar('3d. Identificar candidatos a inativação',
               len(df), 0, f'{n_candidatos} materiais parados > 365 dias')

s3_out = len(df)

# ─────────────────────────────────────────────────────────────────
# STAGE 4 — APROVAÇÃO (WORKFLOW)
# ─────────────────────────────────────────────────────────────────
print("\n" + "-"*68)
print("  STAGE 4 — APROVAÇÃO VIA WORKFLOW")
print("-"*68 + "\n")

def determinar_caminho(row):
    if row['n_erros'] > 0:
        return 'REJEITADO'
    elif row['n_alertas'] == 0 and row['score_qualidade'] >= 80:
        return 'AUTO'
    elif row['n_alertas'] <= 1:
        return 'SUPERVISOR'
    else:
        return 'MDO'

df['caminho_aprovacao'] = df.apply(determinar_caminho, axis=1)
caminhos = df['caminho_aprovacao'].value_counts()

c_auto = caminhos.get('AUTO', 0)
c_sup  = caminhos.get('SUPERVISOR', 0)
c_mdo  = caminhos.get('MDO', 0)
c_rej  = caminhos.get('REJEITADO', 0)

pipe.registrar(f'4a. Caminho AUTO-APROVAÇÃO',
               c_auto, 0, f'{c_auto/len(df)*100:.1f}% dos materiais')
pipe.registrar(f'4b. Caminho SUPERVISOR (revisão 4h)',
               c_sup, 0, f'{c_sup} materiais com 1 alerta')
pipe.registrar(f'4c. Caminho MDO (revisão 24h)',
               c_mdo, 0, f'{c_mdo} materiais com 2+ alertas')

# Calcular SLA estimado
sla_horas = c_auto * (3/3600) + c_sup * 4 + c_mdo * 24
sla_medio = sla_horas / max(len(df), 1)

s4_auto = c_auto
s4_revisao = c_sup + c_mdo

# ─────────────────────────────────────────────────────────────────
# STAGE 5 — SAÍDA
# ─────────────────────────────────────────────────────────────────
print("\n" + "-"*68)
print("  STAGE 5 — GERAÇÃO DE SAÍDAS")
print("-"*68 + "\n")

# 5a: CSV master limpo (apenas aprovados automáticos)
cols_saida = [
    'codigo_material','descricao','categoria','unidade_medida',
    'preco_unitario','estoque_atual','estoque_minimo','fornecedor_principal',
    'data_cadastro','ultima_movimentacao','status','centro_custo','ncm_str',
    'localizacao_fisica','responsavel_cadastro',
    'curva_abc','score_qualidade','status_estoque','caminho_aprovacao',
    'n_erros','n_alertas'
]
df_master = df[cols_saida].copy()
df_master = df_master.rename(columns={'ncm_str': 'ncm_formatado'})
df_master.to_csv(f'data/processed/master_integrado_{ts}.csv',
                 index=False, encoding='utf-8-sig')
pipe.registrar('5a. Gerar CSV master integrado',
               len(df_master), 0, f'{len(df_master):,} materiais processados')

# 5b: CSV de retidos para correção
df_com_erros['erros_str'] = df_com_erros['erros'].apply('; '.join)
cols_rej = ['codigo_material','descricao','categoria','preco_unitario','erros_str']
df_com_erros[cols_rej].to_csv(
    f'data/processed/pipeline_retidos_{ts}.csv', index=False, encoding='utf-8-sig')
pipe.registrar('5b. Gerar CSV de retidos para correção',
               len(df_com_erros), 0, f'{len(df_com_erros):,} materiais retidos')

# 5c: Resumo JSON do pipeline
duracao = (datetime.now() - t0).total_seconds()
resumo_json = {
    'pipeline': 'MDM-PIPELINE',
    'executado_em': ts,
    'duracao_segundos': round(duracao, 2),
    'total_entrada': len(df_raw),
    'total_saida': len(df_master),
    'total_retidos': len(df_com_erros),
    'taxa_aprovacao': round(len(df_master) / len(df_raw) * 100, 1),
    'caminhos': {
        'auto': int(c_auto),
        'supervisor': int(c_sup),
        'mdo': int(c_mdo),
    },
    'score_medio': round(float(score_med), 1),
    'curva_abc': {k: int(v) for k, v in abc_counts.items()},
    'status_estoque': {k: int(v) for k, v in est_counts.items()},
}
with open(f'data/processed/pipeline_resumo_{ts}.json', 'w', encoding='utf-8') as f:
    json.dump(resumo_json, f, ensure_ascii=False, indent=2)
pipe.registrar('5c. Gerar resumo JSON do pipeline',
               1, 0, f'Duração: {duracao:.1f}s')

# ─────────────────────────────────────────────────────────────────
# MÉTRICAS CONSOLIDADAS
# ─────────────────────────────────────────────────────────────────
print("\n" + "-"*68)
print("  MÉTRICAS DO PIPELINE")
print("-"*68)
print(f"""
  FUNIL DE DADOS:
  ┌─────────────────────────────────────────────────────┐
  │  Entrada (CSV bruto):          {len(df_raw):>6,} materiais    │
  │  Stage 1 (Ingestão OK):        {s1_out:>6,} materiais    │
  │  Stage 2 (Validação OK):       {s2_out:>6,} materiais    │
  │  Stage 3 (Enriquecidos):       {s3_out:>6,} materiais    │
  │                                                     │
  │  ├─ Auto-aprovados:            {c_auto:>6,} ({c_auto/len(df_raw)*100:.1f}%)      │
  │  ├─ Para Supervisor:           {c_sup:>6,} ({c_sup/len(df_raw)*100:.1f}%)      │
  │  ├─ Para MDO:                  {c_mdo:>6,} ({c_mdo/len(df_raw)*100:.1f}%)      │
  │  └─ Retidos (erros críticos):  {len(df_com_erros):>6,} ({len(df_com_erros)/len(df_raw)*100:.1f}%)      │
  └─────────────────────────────────────────────────────┘

  QUALIDADE:
  ├─ Score médio ponderado: {score_med:.1f}/100
  ├─ Curva A: {abc_counts.get("A",0):,} | B: {abc_counts.get("B",0):,} | C: {abc_counts.get("C",0):,}
  └─ Duração total: {duracao:.2f} segundos

  ESTOQUE:
  ├─ Normal:        {est_counts.get("NORMAL",0):,}
  ├─ Alerta:        {est_counts.get("ALERTA",0):,}
  ├─ Abaixo mínimo: {est_counts.get("ABAIXO_MINIMO",0):,}
  ├─ Zerado:        {est_counts.get("ZERADO",0):,}
  └─ Sem mínimo:    {est_counts.get("SEM_MINIMO",0):,}
""")

# ─────────────────────────────────────────────────────────────────
# DASHBOARD VISUAL
# ─────────────────────────────────────────────────────────────────
print("-"*68)
print("  GERANDO DASHBOARD...")
print("-"*68)

BG, PANEL = '#0b1220', '#111927'
BORDER, TEXT, MUTED = '#1e2d40', '#e2e8f0', '#64748b'
C = {
    'green':  '#34d399', 'red':    '#f87171',
    'orange': '#fb923c', 'blue':   '#38bdf8',
    'yellow': '#fbbf24', 'purple': '#a78bfa',
    'teal':   '#2dd4bf',
}

fig = plt.figure(figsize=(22, 16), facecolor=BG)
fig.suptitle('DIA 26 — PIPELINE DE INTEGRAÇÃO MDM | Supply Chain',
             fontsize=18, color=TEXT, fontweight='bold', y=0.98)
gs = GridSpec(3, 3, figure=fig, hspace=0.48, wspace=0.35,
              left=0.04, right=0.97, top=0.93, bottom=0.05)

def styled(ax):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=MUTED, labelsize=9)
    for sp in ax.spines.values(): sp.set_color(BORDER)
    ax.grid(color=BORDER, linewidth=0.5, alpha=0.6)
    ax.xaxis.label.set_color(MUTED); ax.yaxis.label.set_color(MUTED)
    ax.title.set_color(TEXT)
    return ax

# G1: Funil do pipeline
ax1 = styled(fig.add_subplot(gs[0, :2]))
etapas_funil = [
    ('Entrada CSV', len(df_raw)),
    ('Stage 1\nIngestão', s1_out),
    ('Stage 2\nValidação', s2_out),
    ('Stage 3\nEnriquec.', s3_out),
    ('Auto\nAprov.', c_auto),
    ('Supervisor\n+MDO', c_sup + c_mdo),
]
xs = range(len(etapas_funil))
vals_f = [v for _, v in etapas_funil]
labels_f = [l for l, _ in etapas_funil]
cores_f = [C['blue'], C['teal'], C['green'], C['green'],
           C['yellow'], C['orange']]
bars = ax1.bar(xs, vals_f, color=cores_f, alpha=0.85, width=0.65)
for b, v in zip(bars, vals_f):
    ax1.text(b.get_x()+b.get_width()/2, v+20, f'{v:,}',
             ha='center', color=TEXT, fontsize=9, fontweight='bold')
# Setas de fluxo
for i in range(len(etapas_funil)-1):
    ax1.annotate('', xy=(i+1-0.3, vals_f[i+1]*0.5),
                 xytext=(i+0.3, vals_f[i]*0.5),
                 arrowprops=dict(arrowstyle='->', color=MUTED, lw=1.2))
ax1.set_xticks(list(xs))
ax1.set_xticklabels(labels_f, fontsize=9)
ax1.set_title('Funil do Pipeline — Materiais por Etapa', fontsize=12, pad=8)
ax1.set_ylabel('Quantidade')

# G2: Pizza caminhos de aprovação
ax2 = styled(fig.add_subplot(gs[0, 2]))
pie_vals  = [c_auto, c_sup, c_mdo, len(df_com_erros)]
pie_labs  = [f'Auto\n{c_auto}', f'Supervisor\n{c_sup}',
             f'MDO\n{c_mdo}', f'Retidos\n{len(df_com_erros)}']
pie_cores = [C['green'], C['yellow'], C['orange'], C['red']]
pie_data  = [(v, l, c) for v, l, c in zip(pie_vals, pie_labs, pie_cores) if v > 0]
if pie_data:
    pv, pl, pc = zip(*pie_data)
    ax2.pie(pv, labels=pl, colors=pc, autopct='%1.0f%%', startangle=90,
            wedgeprops={'edgecolor': BG, 'linewidth': 2},
            textprops={'color': TEXT, 'fontsize': 9})
ax2.set_title('Caminhos de Aprovação', fontsize=12, pad=8)

# G3: Score de qualidade por categoria
ax3 = styled(fig.add_subplot(gs[1, :2]))
score_cat = df.groupby('categoria')['score_qualidade'].mean().sort_values()
cores_sc = [C['green'] if v >= 80 else (C['orange'] if v >= 60 else C['red'])
            for v in score_cat.values]
bars3 = ax3.barh(range(len(score_cat)), score_cat.values,
                 color=cores_sc, alpha=0.85, height=0.6)
ax3.set_yticks(range(len(score_cat)))
ax3.set_yticklabels(score_cat.index, fontsize=9)
ax3.axvline(x=80, color=C['yellow'], ls='--', lw=1.5, label='Meta 80')
ax3.axvline(x=score_med, color=C['blue'], ls='--', lw=1.5, label=f'Média {score_med:.0f}')
for b, v in zip(bars3, score_cat.values):
    ax3.text(v+0.3, b.get_y()+b.get_height()/2, f'{v:.0f}',
             va='center', color=TEXT, fontsize=9)
ax3.set_title('Score Médio de Qualidade por Categoria', fontsize=12, pad=8)
ax3.set_xlabel('Score (0–100)')
ax3.legend(fontsize=9, facecolor=PANEL, labelcolor=TEXT)

# G4: Status estoque
ax4 = styled(fig.add_subplot(gs[1, 2]))
est_labels = list(est_counts.index)
est_vals   = list(est_counts.values)
est_cores  = {
    'NORMAL': C['green'], 'ALERTA': C['yellow'],
    'ABAIXO_MINIMO': C['orange'], 'ZERADO': C['red'],
    'SEM_MINIMO': MUTED,
}
cores_est = [est_cores.get(l, MUTED) for l in est_labels]
ax4.bar(range(len(est_labels)), est_vals, color=cores_est, alpha=0.85, width=0.6)
ax4.set_xticks(range(len(est_labels)))
ax4.set_xticklabels([l.replace('_','\n') for l in est_labels], fontsize=8)
for i, v in enumerate(est_vals):
    ax4.text(i, v+5, str(v), ha='center', color=TEXT, fontsize=9, fontweight='bold')
ax4.set_title('Status de Estoque', fontsize=12, pad=8)

# G5: Curva ABC
ax5 = styled(fig.add_subplot(gs[2, 0]))
abc_labels = ['A', 'B', 'C']
abc_vals   = [int(abc_counts.get(l, 0)) for l in abc_labels]
abc_cores  = [C['red'], C['orange'], C['green']]
ax5.bar(abc_labels, abc_vals, color=abc_cores, alpha=0.85, width=0.5)
for i, v in enumerate(abc_vals):
    ax5.text(i, v+5, str(v), ha='center', color=TEXT, fontsize=11, fontweight='bold')
ax5.set_title('Curva ABC', fontsize=12, pad=8)
ax5.set_ylabel('Materiais')

# G6: Top 10 erros nos retidos
ax6 = styled(fig.add_subplot(gs[2, 1]))
from collections import Counter
todos_erros = []
for e_list in df_com_erros['erros']:
    for e in e_list:
        todos_erros.append(e.split(':')[0].strip())
erros_cnt = Counter(todos_erros).most_common(5)
if erros_cnt:
    e_labels = [e[:20] for e, _ in erros_cnt]
    e_vals   = [v for _, v in erros_cnt]
    ax6.barh(range(len(e_labels)), e_vals, color=C['red'], alpha=0.8, height=0.5)
    ax6.set_yticks(range(len(e_labels)))
    ax6.set_yticklabels(e_labels, fontsize=9)
    ax6.invert_yaxis()
ax6.set_title('Principais Erros (Retidos)', fontsize=12, pad=8)

# G7: KPI panel
ax7 = fig.add_subplot(gs[2, 2])
ax7.set_facecolor(PANEL)
ax7.axis('off')
for sp in ax7.spines.values(): sp.set_color(BORDER)
ax7.set_title('Resumo Executivo', fontsize=12, pad=8, color=TEXT)

cards = [
    ('Aprovados',      f'{len(df_master):,}',        C['green']),
    ('Retidos',        f'{len(df_com_erros):,}',      C['red']),
    ('Score Médio',    f'{score_med:.0f}/100',         C['blue']),
    ('Curva A',        f'{abc_counts.get("A",0):,}',  C['yellow']),
    ('Auto-aprovados', f'{c_auto:,} ({c_auto/len(df_raw)*100:.0f}%)', C['teal']),
    ('Duração',        f'{duracao:.1f}s',              MUTED),
]
for i, (lbl, val, cor) in enumerate(cards):
    col = i % 2; row = i // 2
    xp  = 0.06 + col * 0.50
    yp  = 0.85 - row * 0.30
    ax7.text(xp, yp,      val, ha='left', fontsize=18, fontweight='bold',
             color=cor, transform=ax7.transAxes, family='monospace')
    ax7.text(xp, yp-0.10, lbl, ha='left', fontsize=9,
             color=MUTED, transform=ax7.transAxes)

plt.savefig('visualizations/15_pipeline_integracao.png', dpi=150,
            bbox_inches='tight', facecolor=BG)
plt.close()
print("\n  ✅ visualizations/15_pipeline_integracao.png gerado!")

# ─────────────────────────────────────────────────────────────────
# RELATÓRIO DO PIPELINE (CSV das etapas)
# ─────────────────────────────────────────────────────────────────
pipe.resumo().to_csv(
    f'data/processed/pipeline_etapas_{ts}.csv', index=False, encoding='utf-8-sig')
print(f"  ✅ data/processed/master_integrado_{ts}.csv")
print(f"  ✅ data/processed/pipeline_retidos_{ts}.csv")
print(f"  ✅ data/processed/pipeline_etapas_{ts}.csv")
print(f"  ✅ data/processed/pipeline_resumo_{ts}.json")

# ─────────────────────────────────────────────────────────────────
# RESUMO FINAL
# ─────────────────────────────────────────────────────────────────
print("\n" + "="*68)
print("  ✅ DIA 26 CONCLUÍDO — PIPELINE DE INTEGRAÇÃO!")
print("="*68)
print(f"""
  🔄 PIPELINE EXECUTADO EM {duracao:.1f} SEGUNDOS

  FUNIL COMPLETO:
  ├─ Entrada:          {len(df_raw):,} materiais
  ├─ Saída aprovada:   {len(df_master):,} materiais ({len(df_master)/len(df_raw)*100:.1f}%)
  └─ Retidos:          {len(df_com_erros):,} materiais ({len(df_com_erros)/len(df_raw)*100:.1f}%)

  ROTEAMENTO:
  ├─ Auto-aprovados:   {c_auto:,} ({c_auto/len(df_raw)*100:.1f}%) — prontos agora
  ├─ Para supervisor:  {c_sup:,} ({c_sup/len(df_raw)*100:.1f}%) — até 4h
  └─ Para MDO:         {c_mdo:,} ({c_mdo/len(df_raw)*100:.1f}%) — até 24h

  ENRIQUECIMENTO:
  ├─ Score médio:      {score_med:.1f}/100
  ├─ Curva ABC:        A={abc_counts.get("A",0)} · B={abc_counts.get("B",0)} · C={abc_counts.get("C",0)}
  └─ Candidatos inativ: {n_candidatos:,} materiais

  ARQUIVOS GERADOS: 4 arquivos (CSV + JSON)

  PRÓXIMO: DIA 27 — Relatório Executivo Final (Semana 4)
""")
print("="*68 + "\n")
