-- ═══════════════════════════════════════════════════════════════════════════
-- PROJETO MDM SUPPLY CHAIN
-- Arquivo: 01_queries_basicas.sql
-- Dia 8 - Queries SQL Básicas
-- ═══════════════════════════════════════════════════════════════════════════

/*
OBJETIVO:
Demonstrar queries SQL básicas para análise de dados mestres
Equivalente às análises Python feitas nos Dias 2-5

TABELA: TB_MATERIAIS
Campos: codigo_material, descricao, categoria, unidade_medida, preco_unitario,
        estoque_atual, estoque_minimo, fornecedor_principal, data_cadastro,
        ultima_movimentacao, status, centro_custo, ncm, localizacao_fisica,
        responsavel_cadastro
*/

-- ═══════════════════════════════════════════════════════════════════════════
-- QUERY 1: ESTATÍSTICAS BÁSICAS
-- ═══════════════════════════════════════════════════════════════════════════

-- Contagem total de materiais
SELECT 
    COUNT(*) AS total_materiais,
    COUNT(DISTINCT categoria) AS total_categorias,
    COUNT(DISTINCT fornecedor_principal) AS total_fornecedores
FROM TB_MATERIAIS;

/*
RESULTADO ESPERADO:
total_materiais: 3300
total_categorias: 15
total_fornecedores: ~200
*/


-- ═══════════════════════════════════════════════════════════════════════════
-- QUERY 2: ESTATÍSTICAS DESCRITIVAS - PREÇO
-- ═══════════════════════════════════════════════════════════════════════════

SELECT 
    MIN(preco_unitario) AS preco_minimo,
    MAX(preco_unitario) AS preco_maximo,
    AVG(preco_unitario) AS preco_medio,
    SUM(preco_unitario * estoque_atual) AS valor_total_estoque
FROM TB_MATERIAIS;

/*
INSIGHT:
Valor total em estoque: ~R$ 1,8 bilhões
Preço médio: ~R$ 220
Range: R$ 0,01 até R$ 9.999
*/


-- ═══════════════════════════════════════════════════════════════════════════
-- QUERY 3: DISTRIBUIÇÃO POR STATUS
-- ═══════════════════════════════════════════════════════════════════════════

SELECT 
    status,
    COUNT(*) AS quantidade,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM TB_MATERIAIS), 2) AS percentual
FROM TB_MATERIAIS
GROUP BY status
ORDER BY quantidade DESC;

/*
RESULTADO ESPERADO:
Ativo: ~74%
Bloqueado: ~13%
Inativo: ~12%
*/


-- ═══════════════════════════════════════════════════════════════════════════
-- QUERY 4: TOP 10 CATEGORIAS POR VALOR
-- ═══════════════════════════════════════════════════════════════════════════

SELECT 
    categoria,
    COUNT(*) AS qtd_materiais,
    SUM(preco_unitario * estoque_atual) AS valor_total,
    AVG(preco_unitario) AS preco_medio
FROM TB_MATERIAIS
GROUP BY categoria
ORDER BY valor_total DESC
LIMIT 10;

/*
INSIGHT:
Identificar categorias mais valiosas
Priorizar governança nessas categorias
*/


-- ═══════════════════════════════════════════════════════════════════════════
-- QUERY 5: MATERIAIS COM PREÇO ZERO (PROBLEMA)
-- ═══════════════════════════════════════════════════════════════════════════

SELECT 
    codigo_material,
    descricao,
    categoria,
    estoque_atual
FROM TB_MATERIAIS
WHERE preco_unitario = 0
ORDER BY estoque_atual DESC
LIMIT 20;

/*
PROBLEMA:
Materiais sem preço não podem ser comprados/vendidos
AÇÃO: Preencher preços urgentemente
*/


-- ═══════════════════════════════════════════════════════════════════════════
-- QUERY 6: MATERIAIS SEM NCM (PROBLEMA FISCAL)
-- ═══════════════════════════════════════════════════════════════════════════

SELECT 
    COUNT(*) AS materiais_sem_ncm,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM TB_MATERIAIS), 2) AS percentual
FROM TB_MATERIAIS
WHERE ncm IS NULL OR ncm = '';

/*
PROBLEMA:
NCM obrigatório para compliance fiscal
IMPACTO: Risco multas Receita Federal
AÇÃO: Preencher NCMs classe A primeiro
*/


-- ═══════════════════════════════════════════════════════════════════════════
-- QUERY 7: MATERIAIS SEM LOCALIZAÇÃO FÍSICA
-- ═══════════════════════════════════════════════════════════════════════════

SELECT 
    categoria,
    COUNT(*) AS sem_localizacao
FROM TB_MATERIAIS
WHERE localizacao_fisica IS NULL OR localizacao_fisica = ''
GROUP BY categoria
ORDER BY sem_localizacao DESC
LIMIT 10;

/*
PROBLEMA:
Sem localização = tempo perdido buscando
IMPACTO: ~R$ 118k/ano em produtividade
*/


-- ═══════════════════════════════════════════════════════════════════════════
-- QUERY 8: MATERIAIS COM ESTOQUE ABAIXO DO MÍNIMO
-- ═══════════════════════════════════════════════════════════════════════════

SELECT 
    codigo_material,
    descricao,
    categoria,
    estoque_atual,
    estoque_minimo,
    (estoque_minimo - estoque_atual) AS deficit
FROM TB_MATERIAIS
WHERE estoque_atual < estoque_minimo
ORDER BY deficit DESC
LIMIT 20;

/*
INSIGHT:
Materiais em risco de ruptura
Priorizar reposição
*/


-- ═══════════════════════════════════════════════════════════════════════════
-- QUERY 9: MATERIAIS MAIS VALIOSOS (TOP 20)
-- ═══════════════════════════════════════════════════════════════════════════

SELECT 
    codigo_material,
    descricao,
    categoria,
    preco_unitario,
    estoque_atual,
    (preco_unitario * estoque_atual) AS valor_estoque
FROM TB_MATERIAIS
ORDER BY valor_estoque DESC
LIMIT 20;

/*
INSIGHT:
Top 20 materiais concentram ~5% do valor total
Classe A - Gestão diferenciada necessária
*/


-- ═══════════════════════════════════════════════════════════════════════════
-- QUERY 10: MATERIAIS PARADOS (SEM MOVIMENTO >365 DIAS)
-- ═══════════════════════════════════════════════════════════════════════════

SELECT 
    codigo_material,
    descricao,
    categoria,
    ultima_movimentacao,
    DATEDIFF(CURRENT_DATE, ultima_movimentacao) AS dias_parado,
    (preco_unitario * estoque_atual) AS capital_parado
FROM TB_MATERIAIS
WHERE DATEDIFF(CURRENT_DATE, ultima_movimentacao) > 365
ORDER BY capital_parado DESC
LIMIT 20;

/*
PROBLEMA:
~8% materiais parados >365 dias
Capital imobilizado: ~R$ 350 milhões
AÇÃO: Avaliar obsolescência, liquidar ou doar
*/


-- ═══════════════════════════════════════════════════════════════════════════
-- QUERY BONUS: RESUMO EXECUTIVO
-- ═══════════════════════════════════════════════════════════════════════════

SELECT 
    'Total Materiais' AS metrica,
    COUNT(*) AS valor
FROM TB_MATERIAIS

UNION ALL

SELECT 
    'Valor Total Estoque',
    SUM(preco_unitario * estoque_atual)
FROM TB_MATERIAIS

UNION ALL

SELECT 
    'Preço Médio',
    AVG(preco_unitario)
FROM TB_MATERIAIS

UNION ALL

SELECT 
    'Materiais Sem Preço',
    COUNT(*)
FROM TB_MATERIAIS
WHERE preco_unitario = 0

UNION ALL

SELECT 
    'Materiais Sem NCM',
    COUNT(*)
FROM TB_MATERIAIS
WHERE ncm IS NULL OR ncm = '';

/*
OUTPUT: Tabela resumo com principais KPIs
Use para dashboard ou relatório executivo
*/


-- ═══════════════════════════════════════════════════════════════════════════
-- FIM DAS QUERIES BÁSICAS
-- PRÓXIMO: 02_queries_avancadas.sql (JOINs, Subqueries, CASE)
-- ═══════════════════════════════════════════════════════════════════════════

/*
SKILLS DEMONSTRADAS:
✅ SELECT com agregações (COUNT, SUM, AVG, MIN, MAX)
✅ WHERE com filtros múltiplos
✅ GROUP BY com múltiplas colunas
✅ ORDER BY + LIMIT
✅ UNION para combinar resultados
✅ Subqueries em cláusula WHERE
✅ Cálculos (preco * estoque)
✅ DATEDIFF para análise temporal
✅ NULL checks (IS NULL, = '')
✅ Percentuais calculados

PRÓXIMO NÍVEL:
➡️ JOINs (quando tiver múltiplas tabelas)
➡️ CTEs (WITH)
➡️ Window Functions (ROW_NUMBER, RANK, PARTITION BY)
*/
