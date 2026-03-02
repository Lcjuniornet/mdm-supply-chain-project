"""
╔══════════════════════════════════════════════════════════════════╗
║         DIAS 18-19 — IMPLEMENTAÇÃO DE CORREÇÕES                 ║
║         Semana 3 · Projeto MDM Supply Chain                     ║
╚══════════════════════════════════════════════════════════════════╝

OBJETIVO:
  - Criar scripts automatizados para corrigir problemas identificados
  - Batch processing de correções em massa
  - Workflow de governança (validação → correção → auditoria)
  - Logging completo de todas as operações
  - Backup antes de qualquer alteração
  - Relatório consolidado de correções aplicadas
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import json
import shutil
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────────
# CONFIGURAÇÕES GLOBAIS
# ─────────────────────────────────────────────────────────────────
MODO_SIMULACAO = True  # True = simula correções, False = aplica realmente

CONFIG = {
    'paths': {
        'input': 'data/raw/materiais_raw.csv',
        'backup': 'data/backup/',
        'output': 'data/processed/',
        'logs': 'logs/'
    },
    'limites': {
        'max_correcoes_batch': 1000,  # Máximo de correções por vez
        'timeout_segundos': 300,       # 5 minutos timeout
    },
    'validacao': {
        'preco_min': 0.01,
        'preco_max': 10000,
        'estoque_min': 0,
        'estoque_max': 100000,
    }
}

# ─────────────────────────────────────────────────────────────────
# CLASSE LOGGER
# ─────────────────────────────────────────────────────────────────
class CorrecaoLogger:
    def __init__(self, log_dir='logs'):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = f"{log_dir}/correcoes_{self.timestamp}.log"
        self.correcoes = []
        
    def log(self, tipo, codigo, campo, valor_antes, valor_depois, motivo):
        registro = {
            'timestamp': datetime.now().isoformat(),
            'tipo': tipo,
            'codigo_material': codigo,
            'campo': campo,
            'valor_antes': valor_antes,
            'valor_depois': valor_depois,
            'motivo': motivo
        }
        self.correcoes.append(registro)
        
        # Escrever no arquivo
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(registro, ensure_ascii=False) + '\n')
    
    def resumo(self):
        df_log = pd.DataFrame(self.correcoes)
        return df_log

# ─────────────────────────────────────────────────────────────────
# 1. INICIALIZAÇÃO
# ─────────────────────────────────────────────────────────────────
print("\n" + "="*68)
print("  DIAS 18-19 — IMPLEMENTAÇÃO DE CORREÇÕES AUTOMATIZADAS")
print("  Semana 3 · Projeto MDM Supply Chain")
print("="*68)

if MODO_SIMULACAO:
    print("\n⚠️  MODO SIMULAÇÃO ATIVADO")
    print("   Nenhuma alteração será feita nos dados originais")
    print("   Para aplicar correções reais, altere MODO_SIMULACAO = False")
else:
    print("\n🔴 MODO PRODUÇÃO ATIVADO")
    print("   As correções serão aplicadas nos dados!")

# Carregar dados
CSV = 'E:/importantee/carreira/PROJETO MDM/mdm-supply-chain-project/data/raw/materiais_raw.csv'
df = None
for p in [CSV, 'data/raw/materiais_raw.csv', '../data/raw/materiais_raw.csv', 'materiais_raw.csv']:
    if os.path.exists(p):
        df = pd.read_csv(p)
        print(f"\n✅ CSV carregado: {p} ({len(df):,} registros)")
        CSV_PATH = p
        break

if df is None:
    raise FileNotFoundError('CSV não encontrado!')

# Criar cópias para segurança
df_original = df.copy()
df_corrigido = df.copy()

# Inicializar logger
logger = CorrecaoLogger()

# Criar diretórios (pula o input que é arquivo, não pasta)
dirs_para_criar = ['backup', 'output', 'logs']
for key in dirs_para_criar:
    os.makedirs(CONFIG['paths'][key], exist_ok=True)

# Backup do arquivo original
if not MODO_SIMULACAO:
    backup_file = f"{CONFIG['paths']['backup']}materiais_raw_backup_{logger.timestamp}.csv"
    shutil.copy2(CSV_PATH, backup_file)
    print(f"✅ Backup criado: {backup_file}")

total_materiais = len(df)

# ─────────────────────────────────────────────────────────────────
# 2. CORREÇÃO 1 — PREÇOS ZERADOS
# ─────────────────────────────────────────────────────────────────
print("\n" + "-"*68)
print("  CORREÇÃO 1: PREÇOS ZERADOS")
print("-"*68)
print("  Problema: Materiais com preço R$ 0,00 mas com estoque físico")
print("  Solução:  Atribuir mediana da categoria")

df_zero = df_corrigido[df_corrigido['preco_unitario'] == 0].copy()
n_zero = len(df_zero)

if n_zero > 0:
    print(f"\n  📊 {n_zero} materiais com preço zerado encontrados")
    
    # Calcular mediana por categoria (excluindo zeros)
    medianas_cat = df_corrigido[df_corrigido['preco_unitario'] > 0].groupby('categoria')['preco_unitario'].median()
    
    print(f"\n  Medianas por categoria:")
    for cat, med in medianas_cat.items():
        n_zero_cat = len(df_zero[df_zero['categoria'] == cat])
        if n_zero_cat > 0:
            print(f"    {cat:<16} R$ {med:>8.2f}  ({n_zero_cat} materiais)")
    
    # Aplicar correção
    correcoes_preco = 0
    for idx, row in df_zero.iterrows():
        cat = row['categoria']
        if cat in medianas_cat:
            preco_novo = medianas_cat[cat]
            
            # Log da correção
            logger.log(
                tipo='PRECO_ZERADO',
                codigo=row['codigo_material'],
                campo='preco_unitario',
                valor_antes=0.0,
                valor_depois=preco_novo,
                motivo=f"Aplicada mediana categoria {cat}"
            )
            
            # Aplicar no DataFrame
            df_corrigido.at[idx, 'preco_unitario'] = preco_novo
            correcoes_preco += 1
    
    print(f"\n  ✅ {correcoes_preco} preços corrigidos")
    valor_recuperado = (df_corrigido['preco_unitario'] * df_corrigido['estoque_atual']).sum() - \
                       (df_original['preco_unitario'] * df_original['estoque_atual']).sum()
    print(f"  💰 Valor recuperado no balanço: R$ {valor_recuperado:,.2f}")
else:
    print(f"\n  ✅ Nenhum preço zerado encontrado")

# ─────────────────────────────────────────────────────────────────
# 3. CORREÇÃO 2 — COMPLETUDE (CAMPOS VAZIOS)
# ─────────────────────────────────────────────────────────────────
print("\n" + "-"*68)
print("  CORREÇÃO 2: COMPLETUDE — CAMPOS VAZIOS")
print("-"*68)
print("  Problema: Campos críticos vazios/nulos")
print("  Solução:  Preencher com valores padrão ou inferidos")

# NCM vazio
ncm_vazios = df_corrigido['ncm'].isna() | (df_corrigido['ncm'] == '')
n_ncm_vazios = ncm_vazios.sum()

if n_ncm_vazios > 0:
    print(f"\n  📊 {n_ncm_vazios} materiais sem NCM")
    print(f"  Solução: Atribuir NCM genérico '99999999' (requer validação manual)")
    
    df_corrigido['ncm'] = df_corrigido['ncm'].astype(str).replace('nan', '')
    for idx in df_corrigido[ncm_vazios].index:
        logger.log(
            tipo='NCM_VAZIO',
            codigo=df_corrigido.at[idx, 'codigo_material'],
            campo='ncm',
            valor_antes='',
            valor_depois='99999999',
            motivo='NCM genérico - REQUER VALIDAÇÃO MANUAL'
        )
        df_corrigido.at[idx, 'ncm'] = '99999999'
    
    print(f"  ✅ {n_ncm_vazios} NCMs preenchidos com código genérico")
    print(f"  ⚠️  ATENÇÃO: Estes {n_ncm_vazios} materiais REQUEREM revisão manual!")
else:
    print(f"\n  ✅ Todos materiais possuem NCM")

# Fornecedor vazio
forn_vazios = df_corrigido['fornecedor_principal'].isna() | (df_corrigido['fornecedor_principal'] == '')
n_forn_vazios = forn_vazios.sum()

if n_forn_vazios > 0:
    print(f"\n  📊 {n_forn_vazios} materiais sem fornecedor")
    print(f"  Solução: Atribuir 'SEM_FORNECEDOR' (requer cadastro)")
    
    for idx in df_corrigido[forn_vazios].index:
        logger.log(
            tipo='FORNECEDOR_VAZIO',
            codigo=df_corrigido.at[idx, 'codigo_material'],
            campo='fornecedor_principal',
            valor_antes='',
            valor_depois='SEM_FORNECEDOR',
            motivo='Requer cadastro de fornecedor'
        )
        df_corrigido.at[idx, 'fornecedor_principal'] = 'SEM_FORNECEDOR'
    
    print(f"  ✅ {n_forn_vazios} fornecedores marcados para cadastro")
else:
    print(f"\n  ✅ Todos materiais possuem fornecedor")

# Estoque mínimo vazio
estmin_vazios = df_corrigido['estoque_minimo'].isna()
n_estmin_vazios = estmin_vazios.sum()

if n_estmin_vazios > 0:
    print(f"\n  📊 {n_estmin_vazios} materiais sem estoque mínimo")
    print(f"  Solução: Calcular como 20% do estoque atual")
    
    for idx in df_corrigido[estmin_vazios].index:
        est_atual = df_corrigido.at[idx, 'estoque_atual']
        est_min_calc = max(1, int(est_atual * 0.2))  # Mínimo 1 unidade
        
        logger.log(
            tipo='ESTOQUE_MINIMO_VAZIO',
            codigo=df_corrigido.at[idx, 'codigo_material'],
            campo='estoque_minimo',
            valor_antes=None,
            valor_depois=est_min_calc,
            motivo='Calculado como 20% estoque atual'
        )
        df_corrigido.at[idx, 'estoque_minimo'] = est_min_calc
    
    print(f"  ✅ {n_estmin_vazios} estoques mínimos calculados")
else:
    print(f"\n  ✅ Todos materiais possuem estoque mínimo")

# ─────────────────────────────────────────────────────────────────
# 4. CORREÇÃO 3 — PADRONIZAÇÃO
# ─────────────────────────────────────────────────────────────────
print("\n" + "-"*68)
print("  CORREÇÃO 3: PADRONIZAÇÃO DE TEXTOS")
print("-"*68)
print("  Problema: Inconsistências de caixa (MAIÚSCULA, minúscula, MiStO)")
print("  Solução:  Aplicar padrão Title Case")

campos_texto = ['descricao', 'categoria', 'fornecedor_principal']
total_padronizacoes = 0

for campo in campos_texto:
    if campo in df_corrigido.columns:
        inconsistentes = df_corrigido[campo] != df_corrigido[campo].str.title()
        n_inconsistentes = inconsistentes.sum()
        
        if n_inconsistentes > 0:
            print(f"\n  📊 {campo}: {n_inconsistentes} inconsistências")
            
            for idx in df_corrigido[inconsistentes].index:
                valor_antes = df_corrigido.at[idx, campo]
                valor_depois = str(valor_antes).title() if pd.notna(valor_antes) else valor_antes
                
                logger.log(
                    tipo='PADRONIZACAO_TEXTO',
                    codigo=df_corrigido.at[idx, 'codigo_material'],
                    campo=campo,
                    valor_antes=valor_antes,
                    valor_depois=valor_depois,
                    motivo='Aplicado Title Case'
                )
                df_corrigido.at[idx, campo] = valor_depois
                total_padronizacoes += 1
            
            print(f"  ✅ {n_inconsistentes} valores padronizados")

print(f"\n  ✅ Total: {total_padronizacoes} padronizações aplicadas")

# ─────────────────────────────────────────────────────────────────
# 5. CORREÇÃO 4 — OUTLIERS DE PREÇO
# ─────────────────────────────────────────────────────────────────
print("\n" + "-"*68)
print("  CORREÇÃO 4: OUTLIERS DE PREÇO (SUSPEITOS)")
print("-"*68)
print("  Problema: Preços muito discrepantes da categoria")
print("  Solução:  Marcar para revisão manual (não alterar automaticamente)")

# Detectar outliers IQR por categoria
outliers_marcados = 0

for cat in df_corrigido['categoria'].unique():
    df_cat = df_corrigido[df_corrigido['categoria'] == cat].copy()
    precos = df_cat['preco_unitario']
    
    if len(precos) > 3:  # Precisa pelo menos 4 valores
        Q1 = precos.quantile(0.25)
        Q3 = precos.quantile(0.75)
        IQR = Q3 - Q1
        lim_sup = Q3 + 1.5 * IQR
        lim_inf = max(0, Q1 - 1.5 * IQR)
        
        outliers = (precos > lim_sup) | (precos < lim_inf)
        
        if outliers.any():
            for idx in df_cat[outliers].index:
                preco = df_corrigido.at[idx, 'preco_unitario']
                
                logger.log(
                    tipo='OUTLIER_PRECO',
                    codigo=df_corrigido.at[idx, 'codigo_material'],
                    campo='preco_unitario',
                    valor_antes=preco,
                    valor_depois=preco,  # Não altera
                    motivo=f'Outlier IQR categoria {cat} (lim: {lim_inf:.2f}-{lim_sup:.2f}) - REQUER REVISÃO MANUAL'
                )
                outliers_marcados += 1

if outliers_marcados > 0:
    print(f"\n  ⚠️  {outliers_marcados} outliers de preço identificados")
    print(f"  ✅ Marcados no log para revisão manual")
    print(f"  ℹ️  Preços NÃO foram alterados automaticamente (decisão de negócio)")
else:
    print(f"\n  ✅ Nenhum outlier significativo detectado")

# ─────────────────────────────────────────────────────────────────
# 6. VALIDAÇÃO PÓS-CORREÇÃO
# ─────────────────────────────────────────────────────────────────
print("\n" + "-"*68)
print("  VALIDAÇÃO PÓS-CORREÇÃO")
print("-"*68)

validacoes = {
    'precos_zerados': (df_corrigido['preco_unitario'] == 0).sum(),
    'precos_negativos': (df_corrigido['preco_unitario'] < 0).sum(),
    'ncm_vazios': (df_corrigido['ncm'].isna() | (df_corrigido['ncm'] == '')).sum(),
    'fornecedor_vazios': (df_corrigido['fornecedor_principal'].isna() | 
                         (df_corrigido['fornecedor_principal'] == '')).sum(),
    'estoque_minimo_vazios': df_corrigido['estoque_minimo'].isna().sum(),
}

print(f"\n  Verificações de integridade:")
print(f"  {'Verificação':<25} {'Antes':>8} {'Depois':>8} {'Status':>10}")
print("  " + "-"*56)

checks_passed = 0
checks_total = len(validacoes)

# Valores "Antes" (do original)
valores_antes = {
    'precos_zerados': (df_original['preco_unitario'] == 0).sum(),
    'precos_negativos': (df_original['preco_unitario'] < 0).sum(),
    'ncm_vazios': (df_original['ncm'].isna() | (df_original['ncm'] == '')).sum(),
    'fornecedor_vazios': (df_original['fornecedor_principal'].isna() | 
                         (df_original['fornecedor_principal'] == '')).sum(),
    'estoque_minimo_vazios': df_original['estoque_minimo'].isna().sum(),
}

for check, depois in validacoes.items():
    antes = valores_antes[check]
    status = "✅ OK" if depois == 0 else "⚠️ REVISAR"
    if depois == 0:
        checks_passed += 1
    print(f"  {check:<25} {antes:>8,} {depois:>8,} {status:>10}")

print(f"\n  📊 Validações: {checks_passed}/{checks_total} passaram")

# ─────────────────────────────────────────────────────────────────
# 7. RELATÓRIO DE CORREÇÕES
# ─────────────────────────────────────────────────────────────────
print("\n" + "-"*68)
print("  RELATÓRIO DE CORREÇÕES")
print("-"*68)

df_log = logger.resumo()

if len(df_log) > 0:
    print(f"\n  Total de correções registradas: {len(df_log):,}")
    
    # Resumo por tipo
    print(f"\n  Correções por tipo:")
    print(f"  {'TIPO':<30} {'QTD':>8}")
    print("  " + "-"*40)
    for tipo, qtd in df_log['tipo'].value_counts().items():
        print(f"  {tipo:<30} {qtd:>8,}")
    
    # Correções por campo
    print(f"\n  Correções por campo:")
    print(f"  {'CAMPO':<30} {'QTD':>8}")
    print("  " + "-"*40)
    for campo, qtd in df_log['campo'].value_counts().items():
        print(f"  {campo:<30} {qtd:>8,}")
    
    # Salvar log detalhado
    log_csv = f"{CONFIG['paths']['logs']}correcoes_detalhadas_{logger.timestamp}.csv"
    df_log.to_csv(log_csv, index=False, encoding='utf-8-sig')
    print(f"\n  ✅ Log detalhado salvo: {log_csv}")
else:
    print(f"\n  ℹ️  Nenhuma correção foi necessária")

# ─────────────────────────────────────────────────────────────────
# 8. COMPARAÇÃO ANTES vs DEPOIS
# ─────────────────────────────────────────────────────────────────
print("\n" + "-"*68)
print("  COMPARAÇÃO: ANTES vs DEPOIS")
print("-"*68)

metricas_antes = {
    'valor_total_estoque': (df_original['preco_unitario'] * df_original['estoque_atual']).sum(),
    'preco_medio': df_original['preco_unitario'].mean(),
    'materiais_sem_ncm': (df_original['ncm'].isna() | (df_original['ncm'] == '')).sum(),
    'materiais_sem_fornecedor': (df_original['fornecedor_principal'].isna() | 
                                 (df_original['fornecedor_principal'] == '')).sum(),
    'score_completude': (1 - df_original[['ncm', 'fornecedor_principal', 'estoque_minimo']].isna().sum().sum() / 
                        (len(df_original) * 3)) * 100
}

metricas_depois = {
    'valor_total_estoque': (df_corrigido['preco_unitario'] * df_corrigido['estoque_atual']).sum(),
    'preco_medio': df_corrigido['preco_unitario'].mean(),
    'materiais_sem_ncm': (df_corrigido['ncm'].isna() | (df_corrigido['ncm'] == '')).sum(),
    'materiais_sem_fornecedor': (df_corrigido['fornecedor_principal'].isna() | 
                                 (df_corrigido['fornecedor_principal'] == '')).sum(),
    'score_completude': (1 - df_corrigido[['ncm', 'fornecedor_principal', 'estoque_minimo']].isna().sum().sum() / 
                        (len(df_corrigido) * 3)) * 100
}

print(f"\n  {'MÉTRICA':<30} {'ANTES':>15} {'DEPOIS':>15} {'DELTA':>12}")
print("  " + "-"*76)

print(f"  {'Valor Total Estoque':<30} R$ {metricas_antes['valor_total_estoque']:>12,.2f}"
      f" R$ {metricas_depois['valor_total_estoque']:>12,.2f}"
      f" {'+' if metricas_depois['valor_total_estoque'] > metricas_antes['valor_total_estoque'] else ''}"
      f"R$ {metricas_depois['valor_total_estoque'] - metricas_antes['valor_total_estoque']:>9,.2f}")

print(f"  {'Preço Médio':<30} R$ {metricas_antes['preco_medio']:>12,.2f}"
      f" R$ {metricas_depois['preco_medio']:>12,.2f}"
      f" {'+' if metricas_depois['preco_medio'] > metricas_antes['preco_medio'] else ''}"
      f"R$ {metricas_depois['preco_medio'] - metricas_antes['preco_medio']:>9,.2f}")

print(f"  {'Materiais sem NCM':<30} {metricas_antes['materiais_sem_ncm']:>15,}"
      f" {metricas_depois['materiais_sem_ncm']:>15,}"
      f" {metricas_depois['materiais_sem_ncm'] - metricas_antes['materiais_sem_ncm']:>12,}")

print(f"  {'Materiais sem Fornecedor':<30} {metricas_antes['materiais_sem_fornecedor']:>15,}"
      f" {metricas_depois['materiais_sem_fornecedor']:>15,}"
      f" {metricas_depois['materiais_sem_fornecedor'] - metricas_antes['materiais_sem_fornecedor']:>12,}")

print(f"  {'Score Completude':<30} {metricas_antes['score_completude']:>14.2f}%"
      f" {metricas_depois['score_completude']:>14.2f}%"
      f" {'+' if metricas_depois['score_completude'] > metricas_antes['score_completude'] else ''}"
      f"{metricas_depois['score_completude'] - metricas_antes['score_completude']:>10.2f}%")

# ─────────────────────────────────────────────────────────────────
# 9. SALVAR DADOS CORRIGIDOS
# ─────────────────────────────────────────────────────────────────
print("\n" + "-"*68)
print("  SALVANDO DADOS CORRIGIDOS")
print("-"*68)

if MODO_SIMULACAO:
    output_file = f"{CONFIG['paths']['output']}materiais_corrigidos_SIMULACAO_{logger.timestamp}.csv"
    print(f"\n  ℹ️  MODO SIMULAÇÃO: Salvando em arquivo separado")
else:
    output_file = f"{CONFIG['paths']['output']}materiais_corrigidos_{logger.timestamp}.csv"
    print(f"\n  🔴 MODO PRODUÇÃO: Salvando dados corrigidos")

df_corrigido.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"  ✅ Arquivo salvo: {output_file}")

# Relatório resumo
relatorio_file = f"{CONFIG['paths']['output']}relatorio_correcoes_{logger.timestamp}.txt"
with open(relatorio_file, 'w', encoding='utf-8') as f:
    f.write("="*68 + "\n")
    f.write("RELATÓRIO DE CORREÇÕES AUTOMATIZADAS\n")
    f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
    f.write(f"Modo: {'SIMULAÇÃO' if MODO_SIMULACAO else 'PRODUÇÃO'}\n")
    f.write("="*68 + "\n\n")
    
    f.write(f"Total de materiais processados: {total_materiais:,}\n")
    f.write(f"Total de correções aplicadas: {len(df_log):,}\n\n")
    
    if len(df_log) > 0:
        f.write("CORREÇÕES POR TIPO:\n")
        for tipo, qtd in df_log['tipo'].value_counts().items():
            f.write(f"  {tipo}: {qtd:,}\n")
        f.write("\n")
    
    f.write("COMPARAÇÃO ANTES vs DEPOIS:\n")
    for metrica, valor_antes in metricas_antes.items():
        valor_depois = metricas_depois[metrica]
        delta = valor_depois - valor_antes
        f.write(f"  {metrica}:\n")
        f.write(f"    Antes:  {valor_antes:,.2f}\n")
        f.write(f"    Depois: {valor_depois:,.2f}\n")
        f.write(f"    Delta:  {delta:+,.2f}\n\n")

print(f"  ✅ Relatório salvo: {relatorio_file}")

# ─────────────────────────────────────────────────────────────────
# 10. RESUMO EXECUTIVO
# ─────────────────────────────────────────────────────────────────
print("\n" + "="*68)
print("  RESUMO EXECUTIVO — DIAS 18-19")
print("="*68)

print(f"""
✅ IMPLEMENTAÇÃO COMPLETA:
   • {total_materiais:,} materiais processados
   • {len(df_log):,} correções aplicadas
   • {checks_passed}/{checks_total} validações passaram

📊 CORREÇÕES POR CATEGORIA:
""")

if len(df_log) > 0:
    for tipo, qtd in df_log['tipo'].value_counts().items():
        print(f"   • {tipo}: {qtd:,}")

print(f"""
💰 IMPACTO NOS DADOS:
   • Valor estoque recuperado: R$ {metricas_depois['valor_total_estoque'] - metricas_antes['valor_total_estoque']:,.2f}
   • Score completude: {metricas_antes['score_completude']:.2f}% → {metricas_depois['score_completude']:.2f}%
   • Materiais sem NCM: {metricas_antes['materiais_sem_ncm']:,} → {metricas_depois['materiais_sem_ncm']:,}

📁 ARQUIVOS GERADOS:
   • {output_file}
   • {log_csv}
   • {relatorio_file}
""")

if not MODO_SIMULACAO:
    print(f"   • Backup original: {backup_file}")

print(f"""
⚠️  AÇÕES MANUAIS NECESSÁRIAS:
   • Revisar {metricas_depois['materiais_sem_ncm']:,} materiais com NCM genérico '99999999'
   • Cadastrar fornecedores para {metricas_depois['materiais_sem_fornecedor']:,} materiais
   • Validar {outliers_marcados:,} outliers de preço identificados no log

🎯 PRÓXIMO: DIA 20 — Testes e Validação Completa
""")

print("="*68)
print("✅ DIAS 18-19 COMPLETOS!")
print("="*68)
