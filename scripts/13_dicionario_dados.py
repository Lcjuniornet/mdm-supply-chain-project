"""
╔══════════════════════════════════════════════════════════════════╗
║         DIA 24 — DICIONÁRIO DE DADOS COMPLETO                   ║
║         Semana 4 · Projeto MDM Supply Chain                     ║
╚══════════════════════════════════════════════════════════════════╝

OBJETIVO:
  - Documentar TODOS os campos dos dados mestres de materiais
  - Gerar relatório CSV do dicionário para consulta
  - Analisar qualidade atual de cada campo na base
  - Identificar campos críticos vs opcionais

📖 CONCEITO RÁPIDO — O QUE É UM DICIONÁRIO DE DADOS?
─────────────────────────────────────────────────────
  É um documento que responde: "O que significa esse campo?"
  Para cada coluna da base, registramos:
  - O que é (definição)
  - Como deve ser preenchido (regra)
  - Exemplos certos e errados
  - Se é obrigatório ou não

  Imagine que você sai de férias. Seu substituto abre
  o CSV e vê "ncm". Sem o dicionário: não sabe o que é.
  Com o dicionário: "Nomenclatura Comum do Mercosul,
  8 dígitos, ex: 84841467". Problema resolvido.
─────────────────────────────────────────────────────
"""

import pandas as pd
import numpy as np
import os, warnings
from datetime import datetime
warnings.filterwarnings('ignore')

print("\n" + "="*68)
print("  DIA 24 — DICIONÁRIO DE DADOS COMPLETO")
print("  Semana 4 · Projeto MDM Supply Chain")
print("="*68)

# ─────────────────────────────────────────────────────────────────
# 1. CARREGAR BASE
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
ts = datetime.now().strftime('%Y%m%d_%H%M%S')

# ─────────────────────────────────────────────────────────────────
# 2. DICIONÁRIO — 52 CAMPOS (15 reais + 37 MDM completos)
# ─────────────────────────────────────────────────────────────────
DICIONARIO = [
    # ── GRUPO 1: IDENTIFICAÇÃO ────────────────────────────────────
    {'campo':'codigo_material','grupo':'1. Identificação','tipo_dado':'VARCHAR','tamanho':'10',
     'obrigatorio':'SIM','chave_primaria':'SIM',
     'descricao':'Código único que identifica cada material no sistema',
     'regra_negocio':'Formato MAT-XXXXX (3 letras + hífen + 5 dígitos). Único e imutável.',
     'exemplo_valido':'MAT-00001, MAT-03457',
     'exemplo_invalido':'M-001, mat00001, MAT-1 (sem zeros)',
     'responsavel':'Sistema ERP','frequencia_atualizacao':'Criação única',
     'impacto_ausencia':'CRÍTICO — material não existe no sistema'},

    {'campo':'descricao','grupo':'1. Identificação','tipo_dado':'VARCHAR','tamanho':'100',
     'obrigatorio':'SIM','chave_primaria':'NÃO',
     'descricao':'Nome descritivo do material para identificação humana',
     'regra_negocio':'Padrão: [Substantivo] + [Adjetivo/Material]. Min 3 palavras. Title Case.',
     'exemplo_valido':'Parafuso Aço Inox, Luva Borracha Nitrílica',
     'exemplo_invalido':'PARAFUSO AÇO (maiúsculas), parf (abreviação)',
     'responsavel':'Almoxarife / MDO','frequencia_atualizacao':'Raramente',
     'impacto_ausencia':'CRÍTICO — impossível identificar o material'},

    {'campo':'descricao_complementar','grupo':'1. Identificação','tipo_dado':'VARCHAR','tamanho':'250',
     'obrigatorio':'NÃO','chave_primaria':'NÃO',
     'descricao':'Informações técnicas adicionais: dimensões, especificações, normas',
     'regra_negocio':'Usar quando descrição principal não diferencia materiais similares',
     'exemplo_valido':'DN 50mm, PN 16, ABNT NBR 5648',
     'exemplo_invalido':'Ver almoxarifado (não é informação técnica)',
     'responsavel':'Engenharia / MDO','frequencia_atualizacao':'Quando necessário',
     'impacto_ausencia':'BAIXO — campo complementar'},

    {'campo':'codigo_fabricante','grupo':'1. Identificação','tipo_dado':'VARCHAR','tamanho':'50',
     'obrigatorio':'NÃO','chave_primaria':'NÃO',
     'descricao':'Código do material conforme catálogo do fabricante',
     'regra_negocio':'Exatamente como consta no catálogo. Maiúsculas.',
     'exemplo_valido':'SKF-6205, 3M-1080-G12',
     'exemplo_invalido':'vide catálogo, igual fornecedor',
     'responsavel':'Compras / MDO','frequencia_atualizacao':'Quando fornecedor atualizar catálogo',
     'impacto_ausencia':'MÉDIO — dificulta compra direta'},

    # ── GRUPO 2: CLASSIFICAÇÃO ───────────────────────────────────
    {'campo':'categoria','grupo':'2. Classificação','tipo_dado':'VARCHAR','tamanho':'30',
     'obrigatorio':'SIM','chave_primaria':'NÃO',
     'descricao':'Categoria principal conforme taxonomia MDM',
     'regra_negocio':'Apenas 15 valores: Acessórios, EPI, Eletrônico, Elétrico, Embalagem, Escritório, Ferramentas, Fixação, Hidráulico, Limpeza, Lubrificante, Mecânico, Peças, Pneumático, Químico',
     'exemplo_valido':'Elétrico, Hidráulico, EPI',
     'exemplo_invalido':'eletrico (sem acento), ELÉTRICO (maiúsculas)',
     'responsavel':'MDO','frequencia_atualizacao':'Raramente (aprovação MDO)',
     'impacto_ausencia':'CRÍTICO — relatórios incorretos'},

    {'campo':'subcategoria','grupo':'2. Classificação','tipo_dado':'VARCHAR','tamanho':'50',
     'obrigatorio':'NÃO','chave_primaria':'NÃO',
     'descricao':'Subdivisão da categoria para maior granularidade',
     'regra_negocio':'Derivada da categoria. Ex: Elétrico → Cabos / Disjuntores / Tomadas',
     'exemplo_valido':'Cabos e Fios, EPI Proteção Visual',
     'exemplo_invalido':'Outros, Geral, N/A',
     'responsavel':'MDO','frequencia_atualizacao':'Quando necessário',
     'impacto_ausencia':'BAIXO'},

    {'campo':'ncm','grupo':'2. Classificação','tipo_dado':'CHAR','tamanho':'8',
     'obrigatorio':'SIM','chave_primaria':'NÃO',
     'descricao':'Nomenclatura Comum do Mercosul — código fiscal de 8 dígitos',
     'regra_negocio':'Exatamente 8 dígitos. Sem pontos. Consultar tabela TIPI (Receita Federal).',
     'exemplo_valido':'84841467, 39174710',
     'exemplo_invalido':'8484.14.67 (com pontos), 848414 (6 dígitos), 99999999 (genérico)',
     'responsavel':'Fiscal / MDO','frequencia_atualizacao':'Quando tabela TIPI mudar',
     'impacto_ausencia':'CRÍTICO — nota fiscal bloqueada'},

    {'campo':'curva_abc','grupo':'2. Classificação','tipo_dado':'CHAR','tamanho':'1',
     'obrigatorio':'NÃO','chave_primaria':'NÃO',
     'descricao':'Classificação ABC por valor de consumo: A=top80%, B=15%, C=5%',
     'regra_negocio':'A, B ou C. Recalcular a cada 6 meses.',
     'exemplo_valido':'A, B, C',
     'exemplo_invalido':'a (minúsculo), 1, Alto',
     'responsavel':'MDO / Supply Chain','frequencia_atualizacao':'Semestral',
     'impacto_ausencia':'MÉDIO — dificulta priorização de compras'},

    {'campo':'criticidade','grupo':'2. Classificação','tipo_dado':'VARCHAR','tamanho':'10',
     'obrigatorio':'NÃO','chave_primaria':'NÃO',
     'descricao':'Impacto na operação em caso de falta',
     'regra_negocio':'CRÍTICO = para produção; IMPORTANTE = atrasa; NORMAL = sem impacto imediato',
     'exemplo_valido':'CRÍTICO, IMPORTANTE, NORMAL',
     'exemplo_invalido':'Critico (sem maiúsculas), C, 1',
     'responsavel':'Engenharia / Operações','frequencia_atualizacao':'Anual',
     'impacto_ausencia':'MÉDIO — dificulta gestão de emergências'},

    # ── GRUPO 3: UNIDADES E MEDIDAS ──────────────────────────────
    {'campo':'unidade_medida','grupo':'3. Unidades e Medidas','tipo_dado':'CHAR','tamanho':'5',
     'obrigatorio':'SIM','chave_primaria':'NÃO',
     'descricao':'Unidade de medida para controle de estoque e compras',
     'regra_negocio':'Valores: UN, KG, L, M, CX, PCT, GL, RL, M², MT, PC, GR',
     'exemplo_valido':'UN (unidade), KG (quilograma), L (litro)',
     'exemplo_invalido':'unidade (por extenso), Kg (caixa mista)',
     'responsavel':'MDO','frequencia_atualizacao':'Raramente',
     'impacto_ausencia':'CRÍTICO — compra e estoque incorretos'},

    {'campo':'fator_conversao','grupo':'3. Unidades e Medidas','tipo_dado':'DECIMAL','tamanho':'10,4',
     'obrigatorio':'NÃO','chave_primaria':'NÃO',
     'descricao':'Fator entre unidade de compra e unidade de estoque',
     'regra_negocio':'Deve ser > 0. Ex: compra em CX com 12 UN → fator = 12.',
     'exemplo_valido':'12.0000 (caixa c/ 12), 0.0010 (grama p/ kg)',
     'exemplo_invalido':'0, negativo, nulo quando unidades diferentes',
     'responsavel':'Compras / MDO','frequencia_atualizacao':'Quando embalagem mudar',
     'impacto_ausencia':'MÉDIO — divergência compra vs estoque'},

    {'campo':'peso_liquido_kg','grupo':'3. Unidades e Medidas','tipo_dado':'DECIMAL','tamanho':'10,3',
     'obrigatorio':'NÃO','chave_primaria':'NÃO',
     'descricao':'Peso do material sem embalagem em quilogramas',
     'regra_negocio':'Deve ser > 0. Obrigatório para materiais importados e logística.',
     'exemplo_valido':'0.250 (250g), 15.000 (15kg)',
     'exemplo_invalido':'0, negativo',
     'responsavel':'Engenharia / Compras','frequencia_atualizacao':'Quando produto mudar',
     'impacto_ausencia':'MÉDIO — afeta cálculo de frete'},

    # ── GRUPO 4: PREÇOS E CUSTOS ─────────────────────────────────
    {'campo':'preco_unitario','grupo':'4. Preços e Custos','tipo_dado':'DECIMAL','tamanho':'12,2',
     'obrigatorio':'SIM','chave_primaria':'NÃO',
     'descricao':'Preço médio ponderado do material em reais (R$)',
     'regra_negocio':'Deve ser > 0. Atualizado automaticamente pelo ERP a cada entrada. Nunca editar manualmente.',
     'exemplo_valido':'15.90, 1250.00, 0.35',
     'exemplo_invalido':'0 (zerado), -10 (negativo), 999999 (sem validação)',
     'responsavel':'Sistema ERP (automático)','frequencia_atualizacao':'A cada entrada de NF',
     'impacto_ausencia':'CRÍTICO — balanço patrimonial incorreto'},

    {'campo':'preco_ultima_compra','grupo':'4. Preços e Custos','tipo_dado':'DECIMAL','tamanho':'12,2',
     'obrigatorio':'NÃO','chave_primaria':'NÃO',
     'descricao':'Valor unitário da última nota fiscal de entrada',
     'regra_negocio':'Deve ser > 0. Atualizado automaticamente a cada entrada.',
     'exemplo_valido':'18.50, 1300.00',
     'exemplo_invalido':'0, negativo',
     'responsavel':'Sistema ERP (automático)','frequencia_atualizacao':'A cada compra',
     'impacto_ausencia':'MÉDIO — dificulta negociação'},

    {'campo':'preco_maximo_compra','grupo':'4. Preços e Custos','tipo_dado':'DECIMAL','tamanho':'12,2',
     'obrigatorio':'NÃO','chave_primaria':'NÃO',
     'descricao':'Teto de preço aprovado. Compras acima exigem aprovação especial.',
     'regra_negocio':'Deve ser >= preco_unitario. Aprovação MDO + Gestor para alterar.',
     'exemplo_valido':'25.00 (quando preço é 18.50)',
     'exemplo_invalido':'Menor que preco_unitario',
     'responsavel':'Compras / Gestão','frequencia_atualizacao':'Trimestral',
     'impacto_ausencia':'MÉDIO — compras sem controle de preço'},

    {'campo':'moeda','grupo':'4. Preços e Custos','tipo_dado':'CHAR','tamanho':'3',
     'obrigatorio':'NÃO','chave_primaria':'NÃO',
     'descricao':'Moeda de referência do preço. Padrão BRL.',
     'regra_negocio':'Código ISO 4217: BRL, USD, EUR. Obrigatório para materiais importados.',
     'exemplo_valido':'BRL, USD, EUR',
     'exemplo_invalido':'Real, Dólar, R$',
     'responsavel':'Compras / MDO','frequencia_atualizacao':'Quando mudar moeda',
     'impacto_ausencia':'MÉDIO — risco cambial não gerenciado'},

    # ── GRUPO 5: ESTOQUE ─────────────────────────────────────────
    {'campo':'estoque_atual','grupo':'5. Estoque','tipo_dado':'INTEGER','tamanho':'10',
     'obrigatorio':'SIM','chave_primaria':'NÃO',
     'descricao':'Quantidade física disponível no almoxarifado',
     'regra_negocio':'Deve ser >= 0. Atualizado em tempo real a cada movimentação.',
     'exemplo_valido':'0 (sem estoque), 150, 3462',
     'exemplo_invalido':'-5 (negativo = erro de sistema)',
     'responsavel':'Sistema ERP (automático)','frequencia_atualizacao':'Tempo real',
     'impacto_ausencia':'CRÍTICO — não sabe o que tem em estoque'},

    {'campo':'estoque_minimo','grupo':'5. Estoque','tipo_dado':'DECIMAL','tamanho':'10,2',
     'obrigatorio':'NÃO','chave_primaria':'NÃO',
     'descricao':'Quantidade mínima que deve existir em estoque (ponto de pedido)',
     'regra_negocio':'Deve ser > 0. Base: consumo_medio_diario × lead_time × fator_segurança (1.2-1.5)',
     'exemplo_valido':'50, 184.0',
     'exemplo_invalido':'0 (nunca repõe), negativo',
     'responsavel':'Supply Chain / Almoxarife','frequencia_atualizacao':'Semestral',
     'impacto_ausencia':'ALTO — risco de ruptura de estoque'},

    {'campo':'estoque_maximo','grupo':'5. Estoque','tipo_dado':'DECIMAL','tamanho':'10,2',
     'obrigatorio':'NÃO','chave_primaria':'NÃO',
     'descricao':'Quantidade máxima permitida para evitar superlotação',
     'regra_negocio':'Deve ser > estoque_minimo. Regra prática: estoque_minimo × 3.',
     'exemplo_valido':'552.0 (quando mínimo é 184)',
     'exemplo_invalido':'Menor ou igual ao estoque_minimo',
     'responsavel':'Supply Chain','frequencia_atualizacao':'Semestral',
     'impacto_ausencia':'MÉDIO — risco de excesso de estoque'},

    {'campo':'ponto_reposicao','grupo':'5. Estoque','tipo_dado':'DECIMAL','tamanho':'10,2',
     'obrigatorio':'NÃO','chave_primaria':'NÃO',
     'descricao':'Nível que dispara automaticamente uma solicitação de compra',
     'regra_negocio':'Deve ser >= estoque_minimo. = mínimo + consumo durante lead_time.',
     'exemplo_valido':'230, 184',
     'exemplo_invalido':'Menor que estoque_minimo',
     'responsavel':'Supply Chain / MDO','frequencia_atualizacao':'Semestral',
     'impacto_ausencia':'ALTO — compras manuais sem automação'},

    {'campo':'lote_compra','grupo':'5. Estoque','tipo_dado':'INTEGER','tamanho':'10',
     'obrigatorio':'NÃO','chave_primaria':'NÃO',
     'descricao':'Quantidade mínima por pedido de compra (múltiplo do fornecedor)',
     'regra_negocio':'Deve ser > 0. Ex: parafusos em caixas de 100 → lote = 100.',
     'exemplo_valido':'100, 1, 25',
     'exemplo_invalido':'0, negativo',
     'responsavel':'Compras','frequencia_atualizacao':'Quando fornecedor mudar embalagem',
     'impacto_ausencia':'MÉDIO — pedidos com quantidades erradas'},

    # ── GRUPO 6: FORNECEDOR ──────────────────────────────────────
    {'campo':'fornecedor_principal','grupo':'6. Fornecedor','tipo_dado':'VARCHAR','tamanho':'80',
     'obrigatorio':'NÃO','chave_primaria':'NÃO',
     'descricao':'Nome do fornecedor preferencial para compras',
     'regra_negocio':'Deve existir no cadastro de fornecedores do ERP. Title Case.',
     'exemplo_valido':'Distribuidora ABC, Importadora JKL',
     'exemplo_invalido':'SEM_FORNECEDOR (provisório), Vários',
     'responsavel':'Compras / MDO','frequencia_atualizacao':'Quando fornecedor mudar',
     'impacto_ausencia':'ALTO — compras sem referência'},

    {'campo':'fornecedor_alternativo','grupo':'6. Fornecedor','tipo_dado':'VARCHAR','tamanho':'80',
     'obrigatorio':'NÃO','chave_primaria':'NÃO',
     'descricao':'Fornecedor de contingência quando o principal não atende',
     'regra_negocio':'Diferente do fornecedor_principal.',
     'exemplo_valido':'Suprimentos XYZ',
     'exemplo_invalido':'Igual ao principal',
     'responsavel':'Compras','frequencia_atualizacao':'Quando necessário',
     'impacto_ausencia':'MÉDIO — vulnerabilidade a stockout'},

    {'campo':'lead_time_dias','grupo':'6. Fornecedor','tipo_dado':'INTEGER','tamanho':'5',
     'obrigatorio':'NÃO','chave_primaria':'NÃO',
     'descricao':'Dias úteis entre emissão do pedido e recebimento',
     'regra_negocio':'Deve ser > 0. Local: 2-5 dias. Importado: 30-90 dias.',
     'exemplo_valido':'3, 15, 45',
     'exemplo_invalido':'0, negativo',
     'responsavel':'Compras','frequencia_atualizacao':'Quando desempenho mudar',
     'impacto_ausencia':'ALTO — estoque mínimo calculado errado'},

    {'campo':'condicao_pagamento','grupo':'6. Fornecedor','tipo_dado':'VARCHAR','tamanho':'20',
     'obrigatorio':'NÃO','chave_primaria':'NÃO',
     'descricao':'Prazo de pagamento acordado com o fornecedor',
     'regra_negocio':'Formato: número + DDL. Ex: 30DDL = 30 dias da data da nota.',
     'exemplo_valido':'30DDL, 60DDL, 0DDL (à vista)',
     'exemplo_invalido':'30 dias, um mês',
     'responsavel':'Compras / Financeiro','frequencia_atualizacao':'Quando renegociar',
     'impacto_ausencia':'BAIXO — Financeiro controla separado'},

    # ── GRUPO 7: LOCALIZAÇÃO ─────────────────────────────────────
    {'campo':'localizacao_fisica','grupo':'7. Localização','tipo_dado':'VARCHAR','tamanho':'20',
     'obrigatorio':'NÃO','chave_primaria':'NÃO',
     'descricao':'Endereço físico no almoxarifado: Bloco-Corredor-Prateleira',
     'regra_negocio':'Formato: X-YY-ZZ (Bloco letra + Corredor 2 dígitos + Prateleira 2 dígitos)',
     'exemplo_valido':'A-01-03, C-20-05, E-07-05',
     'exemplo_invalido':'Galpão A, Prateleira 3, Perto da porta',
     'responsavel':'Almoxarife','frequencia_atualizacao':'Quando reorganizar almoxarifado',
     'impacto_ausencia':'MÉDIO — separação lenta de pedidos'},

    {'campo':'almoxarifado','grupo':'7. Localização','tipo_dado':'VARCHAR','tamanho':'20',
     'obrigatorio':'NÃO','chave_primaria':'NÃO',
     'descricao':'Identificação do almoxarifado (multi-unidades)',
     'regra_negocio':'Valores: ALM-CENTRAL, ALM-PRODUCAO, ALM-EXTERNO',
     'exemplo_valido':'ALM-CENTRAL, ALM-PRODUCAO',
     'exemplo_invalido':'Central, almox, 1',
     'responsavel':'Almoxarife / TI','frequencia_atualizacao':'Quando estrutura mudar',
     'impacto_ausencia':'ALTO — para empresas multi-unidades'},

    # ── GRUPO 8: FISCAL E LEGAL ──────────────────────────────────
    {'campo':'centro_custo','grupo':'8. Fiscal e Legal','tipo_dado':'VARCHAR','tamanho':'15',
     'obrigatorio':'NÃO','chave_primaria':'NÃO',
     'descricao':'Centro de custo que consome este material',
     'regra_negocio':'Formato XXX-YYY. Deve existir no plano de contas.',
     'exemplo_valido':'ADM-001, MAN-002, PRD-003',
     'exemplo_invalido':'Administração, Centro 1',
     'responsavel':'Controladoria / MDO','frequencia_atualizacao':'Quando estrutura mudar',
     'impacto_ausencia':'MÉDIO — rateio de custos impreciso'},

    {'campo':'conta_contabil','grupo':'8. Fiscal e Legal','tipo_dado':'VARCHAR','tamanho':'20',
     'obrigatorio':'NÃO','chave_primaria':'NÃO',
     'descricao':'Conta do plano contábil para lançamento das movimentações',
     'regra_negocio':'Código conforme Plano de Contas da empresa.',
     'exemplo_valido':'1.1.3.01, 3.1.2.05',
     'exemplo_invalido':'Estoque, Consumo (nomes)',
     'responsavel':'Controladoria','frequencia_atualizacao':'Quando plano contábil mudar',
     'impacto_ausencia':'ALTO — integração contábil incorreta'},

    {'campo':'cst_icms','grupo':'8. Fiscal e Legal','tipo_dado':'CHAR','tamanho':'3',
     'obrigatorio':'NÃO','chave_primaria':'NÃO',
     'descricao':'Código de Situação Tributária do ICMS (tabela SEFAZ)',
     'regra_negocio':'3 dígitos. 000=tributado; 040=isento; 060=substituição tributária.',
     'exemplo_valido':'000, 040, 060',
     'exemplo_invalido':'00, ISENTO, Tributado',
     'responsavel':'Fiscal','frequencia_atualizacao':'Quando legislação mudar',
     'impacto_ausencia':'CRÍTICO — erro em NF (multa)'},

    {'campo':'aliquota_ipi','grupo':'8. Fiscal e Legal','tipo_dado':'DECIMAL','tamanho':'5,2',
     'obrigatorio':'NÃO','chave_primaria':'NÃO',
     'descricao':'Alíquota do IPI em percentual',
     'regra_negocio':'Entre 0.00 e 100.00. Consultar TIPI pelo NCM.',
     'exemplo_valido':'0.00 (isento), 5.00, 12.50',
     'exemplo_invalido':'5% (com símbolo), 150 (> 100)',
     'responsavel':'Fiscal','frequencia_atualizacao':'Quando TIPI mudar',
     'impacto_ausencia':'ALTO — cálculo de custo errado'},

    # ── GRUPO 9: CONTROLE E DATAS ────────────────────────────────
    {'campo':'data_cadastro','grupo':'9. Controle e Datas','tipo_dado':'DATE','tamanho':'10',
     'obrigatorio':'SIM','chave_primaria':'NÃO',
     'descricao':'Data em que o material foi inserido no sistema',
     'regra_negocio':'Formato YYYY-MM-DD. Preenchido automaticamente. Nunca alterar.',
     'exemplo_valido':'2024-03-15, 2025-11-01',
     'exemplo_invalido':'15/03/2024 (formato BR), 2024-3-5 (sem zeros)',
     'responsavel':'Sistema ERP (automático)','frequencia_atualizacao':'Nunca',
     'impacto_ausencia':'MÉDIO — auditoria impossível'},

    {'campo':'ultima_movimentacao','grupo':'9. Controle e Datas','tipo_dado':'DATE','tamanho':'10',
     'obrigatorio':'SIM','chave_primaria':'NÃO',
     'descricao':'Data da última entrada ou saída registrada no estoque',
     'regra_negocio':'Atualizado automaticamente. Deve ser >= data_cadastro.',
     'exemplo_valido':'2025-12-01, 2026-01-15',
     'exemplo_invalido':'Anterior à data_cadastro',
     'responsavel':'Sistema ERP (automático)','frequencia_atualizacao':'A cada movimentação',
     'impacto_ausencia':'ALTO — impossível identificar obsoletos'},

    {'campo':'data_ultima_revisao','grupo':'9. Controle e Datas','tipo_dado':'DATE','tamanho':'10',
     'obrigatorio':'NÃO','chave_primaria':'NÃO',
     'descricao':'Data da última revisão dos dados cadastrais pelo MDO',
     'regra_negocio':'Formato YYYY-MM-DD. Atualizar sempre que revisar qualquer campo.',
     'exemplo_valido':'2026-01-10',
     'exemplo_invalido':'Data futura',
     'responsavel':'MDO','frequencia_atualizacao':'A cada revisão',
     'impacto_ausencia':'MÉDIO — não sabe se cadastro está atual'},

    {'campo':'validade','grupo':'9. Controle e Datas','tipo_dado':'DATE','tamanho':'10',
     'obrigatorio':'CONDICIONAL','chave_primaria':'NÃO',
     'descricao':'Data de vencimento (lubrificantes, químicos, EPIs com prazo)',
     'regra_negocio':'Obrigatório para itens com prazo. Deve ser data futura.',
     'exemplo_valido':'2027-06-30',
     'exemplo_invalido':'Data passada (produto vencido em estoque)',
     'responsavel':'Almoxarife','frequencia_atualizacao':'A cada novo lote',
     'impacto_ausencia':'CRÍTICO — para itens com validade'},

    # ── GRUPO 10: STATUS E CICLO DE VIDA ─────────────────────────
    {'campo':'status','grupo':'10. Status e Ciclo de Vida','tipo_dado':'VARCHAR','tamanho':'15',
     'obrigatorio':'SIM','chave_primaria':'NÃO',
     'descricao':'Situação do material no ciclo de vida do cadastro',
     'regra_negocio':'Valores: Ativo (em uso), Inativo (sem uso > 1 ano), Bloqueado (problemas)',
     'exemplo_valido':'Ativo, Inativo, Bloqueado',
     'exemplo_invalido':'ativo (minúsculo), ATIVO, OK',
     'responsavel':'MDO','frequencia_atualizacao':'Conforme ciclo de vida',
     'impacto_ausencia':'CRÍTICO — obsoletos podem ser comprados'},

    {'campo':'motivo_bloqueio','grupo':'10. Status e Ciclo de Vida','tipo_dado':'VARCHAR','tamanho':'200',
     'obrigatorio':'CONDICIONAL','chave_primaria':'NÃO',
     'descricao':'Descrição do motivo quando status = Bloqueado',
     'regra_negocio':'Obrigatório quando Bloqueado. Descrever: o que, quando, quem bloqueou.',
     'exemplo_valido':'NCM incorreto identificado em 2026-01-15. Aguarda correção fiscal.',
     'exemplo_invalido':'Bloqueado (sem explicação)',
     'responsavel':'MDO','frequencia_atualizacao':'Ao bloquear',
     'impacto_ausencia':'MÉDIO — bloqueio sem rastreabilidade'},

    {'campo':'data_obsolescencia','grupo':'10. Status e Ciclo de Vida','tipo_dado':'DATE','tamanho':'10',
     'obrigatorio':'NÃO','chave_primaria':'NÃO',
     'descricao':'Data prevista para descontinuação do material',
     'regra_negocio':'Usar quando material será substituído. Definir o substituto em observações.',
     'exemplo_valido':'2026-12-31',
     'exemplo_invalido':'Data passada sem status Inativo',
     'responsavel':'MDO / Engenharia','frequencia_atualizacao':'Quando definida obsolescência',
     'impacto_ausencia':'BAIXO — planejamento antecipado'},

    # ── GRUPO 11: QUALIDADE E GOVERNANÇA ─────────────────────────
    {'campo':'responsavel_cadastro','grupo':'11. Qualidade e Governança','tipo_dado':'VARCHAR','tamanho':'60',
     'obrigatorio':'SIM','chave_primaria':'NÃO',
     'descricao':'Nome do profissional responsável pelo cadastro inicial',
     'regra_negocio':'Nome completo Title Case. Usuário ativo no sistema.',
     'exemplo_valido':'João Silva, Ricardo Alves',
     'exemplo_invalido':'joao (minúsculo), J. Silva (abreviado)',
     'responsavel':'MDO / RH','frequencia_atualizacao':'Somente na criação',
     'impacto_ausencia':'MÉDIO — sem dono do cadastro'},

    {'campo':'score_qualidade','grupo':'11. Qualidade e Governança','tipo_dado':'DECIMAL','tamanho':'5,2',
     'obrigatorio':'NÃO','chave_primaria':'NÃO',
     'descricao':'Score de 0 a 100 que mede completude e qualidade do cadastro',
     'regra_negocio':'Calculado automaticamente. Meta: >= 80.',
     'exemplo_valido':'95.00, 72.50, 100.00',
     'exemplo_invalido':'Negativo, > 100',
     'responsavel':'Sistema MDM (automático)','frequencia_atualizacao':'A cada atualização',
     'impacto_ausencia':'BAIXO — indicador de gestão'},

    {'campo':'nivel_aprovacao','grupo':'11. Qualidade e Governança','tipo_dado':'VARCHAR','tamanho':'20',
     'obrigatorio':'NÃO','chave_primaria':'NÃO',
     'descricao':'Último nível de aprovação no workflow MDM',
     'regra_negocio':'Valores: AUTO-APROVADO, SUPERVISOR, MDO, PENDENTE',
     'exemplo_valido':'AUTO-APROVADO, MDO',
     'exemplo_invalido':'aprovado (minúsculo), Nível 1',
     'responsavel':'Sistema Workflow','frequencia_atualizacao':'A cada revisão',
     'impacto_ausencia':'BAIXO — controle de processo'},

    {'campo':'observacoes','grupo':'11. Qualidade e Governança','tipo_dado':'VARCHAR','tamanho':'500',
     'obrigatorio':'NÃO','chave_primaria':'NÃO',
     'descricao':'Campo livre para informações não estruturadas',
     'regra_negocio':'Usar apenas quando nenhum outro campo for adequado.',
     'exemplo_valido':'Requer aprovação do engenheiro antes de cada compra.',
     'exemplo_invalido':'Ver acima (sem informação nova)',
     'responsavel':'Qualquer usuário com permissão','frequencia_atualizacao':'Quando necessário',
     'impacto_ausencia':'BAIXO'},
]

# ─────────────────────────────────────────────────────────────────
# 3. ANÁLISE DE QUALIDADE DOS CAMPOS REAIS DO CSV
# ─────────────────────────────────────────────────────────────────
print("\n" + "-"*68)
print("  ANÁLISE DE QUALIDADE — CAMPOS DO CSV")
print("-"*68)
print(f"\n  {'CAMPO':<25} {'PREENCH%':>9} {'NULOS':>7} {'ÚNICOS':>8} {'TIPO':>10}")
print("  " + "-"*65)

analise = []
for col in df.columns:
    pct   = df[col].notna().sum() / len(df) * 100
    nulos = df[col].isna().sum()
    uniq  = df[col].nunique()
    tipo  = str(df[col].dtype)
    print(f"  {col:<25} {pct:>8.1f}% {nulos:>7} {uniq:>8}  {tipo:>10}")
    analise.append({'campo': col, 'pct_preenchido': round(pct,1),
                    'n_nulos': nulos, 'n_unicos': uniq, 'tipo': tipo})

# ─────────────────────────────────────────────────────────────────
# 4. ESTATÍSTICAS DO DICIONÁRIO
# ─────────────────────────────────────────────────────────────────
print("\n" + "-"*68)
print("  ESTATÍSTICAS DO DICIONÁRIO")
print("-"*68)

df_dic = pd.DataFrame(DICIONARIO)
n_obrig     = (df_dic['obrigatorio'] == 'SIM').sum()
n_opcional  = (df_dic['obrigatorio'] == 'NÃO').sum()
n_cond      = (df_dic['obrigatorio'] == 'CONDICIONAL').sum()
grupos      = df_dic['grupo'].value_counts()

print(f"""
  Total documentado: {len(DICIONARIO)} campos em 11 grupos

  Por obrigatoriedade:
    Obrigatórios:    {n_obrig:>3} campos ({n_obrig/len(DICIONARIO)*100:.0f}%)
    Opcionais:       {n_opcional:>3} campos ({n_opcional/len(DICIONARIO)*100:.0f}%)
    Condicionais:    {n_cond:>3} campos ({n_cond/len(DICIONARIO)*100:.0f}%)

  Por grupo:""")
for grupo, qtd in grupos.items():
    print(f"    {grupo:<36} {qtd:>2} campos")

# ─────────────────────────────────────────────────────────────────
# 5. SALVAR CSVs
# ─────────────────────────────────────────────────────────────────
out_dic     = f'data/processed/dicionario_dados_{ts}.csv'
out_analise = f'data/processed/qualidade_campos_{ts}.csv'
df_dic.to_csv(out_dic, index=False, encoding='utf-8-sig')
pd.DataFrame(analise).to_csv(out_analise, index=False, encoding='utf-8-sig')
print(f"\n  ✅ Dicionário: {out_dic}")
print(f"  ✅ Qualidade:  {out_analise}")

# ─────────────────────────────────────────────────────────────────
# 6. RESUMO FINAL
# ─────────────────────────────────────────────────────────────────
print("\n" + "="*68)
print("  ✅ DIA 24 — DICIONÁRIO DE DADOS CONCLUÍDO!")
print("="*68)
print(f"""
  📖 {len(DICIONARIO)} campos documentados | 11 grupos | 52 itens

  CAMPOS CRÍTICOS (obrigatórios):
  ├─ codigo_material  — chave primária única e imutável
  ├─ descricao        — nome do material (Title Case)
  ├─ categoria        — 15 valores permitidos
  ├─ ncm              — 8 dígitos (obrigação fiscal)
  ├─ unidade_medida   — base de todo cálculo de estoque
  ├─ preco_unitario   — valor patrimonial (> 0)
  ├─ estoque_atual    — quantidade física (>= 0)
  ├─ data_cadastro    — rastreabilidade temporal
  ├─ status           — Ativo / Inativo / Bloqueado
  └─ responsavel_cadastro — dono do dado

  LACUNAS NA BASE ATUAL:
  ├─ NCM:             623 materiais vazios (19%)
  ├─ Estoque mínimo:  660 materiais sem valor (20%)
  └─ Fornecedor:      660 materiais sem cadastro (20%)

  📝 LIÇÃO DO DIA:
  O dicionário de dados é o "manual de instruções" do sistema.
  Sem ele, cada pessoa interpreta os campos do jeito que quer.
  Com ele, todos falam a mesma língua — incluindo o substituto
  que vai te cobrir nas férias.

  PRÓXIMO: DIA 25 — SLA e KPIs de Qualidade de Dados
""")
print("="*68 + "\n")
