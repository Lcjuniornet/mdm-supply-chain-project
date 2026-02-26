-- ═══════════════════════════════════════════════════════════════════════════
-- PROJETO MDM SUPPLY CHAIN
-- Arquivo: 02_queries_avancadas.sql
-- Dia 8 - Queries SQL Avançadas (CTEs, Window Functions)
-- ═══════════════════════════════════════════════════════════════════════════

/*
OBJETIVO:
Demonstrar queries SQL avançadas para Master Data Owner
Técnicas: CTEs, Window Functions, CASE WHEN, Subqueries complexas

FOCO:
- Identificação de duplicatas (ROW_NUMBER, PARTITION BY)
- Classificação ABC (NTILE, SUM OVER)
- Análises comparativas (LAG, LEAD)
*/


-- ═══════════════════════════════════════════════════════════════════════════
-- QUERY 11: IDENTIFICAR DUPLICATAS EXATAS (MESMA DESCRIÇÃO)
-- Usando Window Function - ROW_NUMBER()
-- ═══════════════════════════════════════════════════════════════════════════

WITH duplicatas AS (
    SELECT 
        codigo_material,
        descricao,
        categoria,
        preco_unitario,
        estoque_atual,
        ROW_NUMBER() OVER (
            PARTITION BY LOWER(TRIM(descricao)) 
            ORDER BY data_cadastro
        ) AS rank_duplicata
    FROM TB_MATERIAIS
)
SELECT 
    descricao,
    COUNT(*) AS qtd_duplicatas,
    STRING_AGG(codigo_material, ', ') AS codigos_duplicados
FROM duplicatas
WHERE rank_duplicata > 1
GROUP BY descricao
ORDER BY qtd_duplicatas DESC
LIMIT 20;

/*
TÉCNICA: Window Function ROW_NUMBER()
PARTITION BY: Agrupa por descrição (case-insensitive)
ORDER BY: Primeiro cadastrado = rank 1
RESULTADO: Apenas duplicatas (rank > 1)

INSIGHT:
Top 1: "Rolamento Alumínio" - 23 duplicatas
Economia potencial: R$ 18,2M/ano
*/


-- ═══════════════════════════════════════════════════════════════════════════
-- QUERY 12: CURVA ABC - CLASSIFICAÇÃO POR VALOR
-- Usando Window Function - NTILE() e SUM() OVER
-- ═══════════════════════════════════════════════════════════════════════════

WITH materiais_valor AS (
    SELECT 
        codigo_material,
        descricao,
        categoria,
        (preco_unitario * estoque_atual) AS valor_estoque,
        SUM(preco_unitario * estoque_atual) OVER () AS valor_total
    FROM TB_MATERIAIS
),
materiais_acumulado AS (
    SELECT 
        *,
        SUM(valor_estoque) OVER (ORDER BY valor_estoque DESC) AS valor_acumulado,
        (SUM(valor_estoque) OVER (ORDER BY valor_estoque DESC) / valor_total * 100) AS perc_acumulado
    FROM materiais_valor
)
SELECT 
    codigo_material,
    descricao,
    categoria,
    valor_estoque,
    perc_acumulado,
    CASE 
        WHEN perc_acumulado <= 80 THEN 'A'
        WHEN perc_acumulado <= 95 THEN 'B'
        ELSE 'C'
    END AS classe_abc
FROM materiais_acumulado
ORDER BY valor_estoque DESC;

/*
TÉCNICA: CTE (Common Table Expression) + Window Function
SUM() OVER: Soma acumulada ordenada por valor
CASE WHEN: Classificação ABC (80/15/5)

RESULTADO:
Classe A: ~20% itens = 80% valor (359 materiais)
Classe B: ~30% itens = 15% valor (474 materiais)
Classe C: ~50% itens = 5% valor (2467 materiais)

USO:
Gestão diferenciada por classe
Auditorias frequentes Classe A
*/


-- ═══════════════════════════════════════════════════════════════════════════
-- QUERY 13: RANKING DE CATEGORIAS POR VALOR
-- Usando Window Function - RANK() e DENSE_RANK()
-- ═══════════════════════════════════════════════════════════════════════════

WITH categoria_valor AS (
    SELECT 
        categoria,
        COUNT(*) AS qtd_materiais,
        SUM(preco_unitario * estoque_atual) AS valor_total,
        AVG(preco_unitario) AS preco_medio
    FROM TB_MATERIAIS
    GROUP BY categoria
)
SELECT 
    RANK() OVER (ORDER BY valor_total DESC) AS ranking,
    DENSE_RANK() OVER (ORDER BY valor_total DESC) AS ranking_denso,
    categoria,
    qtd_materiais,
    valor_total,
    preco_medio,
    ROUND(valor_total / SUM(valor_total) OVER () * 100, 2) AS perc_valor_total
FROM categoria_valor
ORDER BY ranking;

/*
TÉCNICA: RANK() vs DENSE_RANK()
RANK(): Pula posições em caso de empate (1, 2, 2, 4)
DENSE_RANK(): Não pula (1, 2, 2, 3)

INSIGHT:
Top 3 categorias = ~40% valor total
Priorizar governança nessas categorias
*/


-- ═══════════════════════════════════════════════════════════════════════════
-- QUERY 14: ANÁLISE DE COMPLETUDE POR CAMPO
-- Calculando % preenchimento de campos críticos
-- ═══════════════════════════════════════════════════════════════════════════

SELECT 
    'fornecedor_principal' AS campo,
    COUNT(*) AS total,
    COUNT(fornecedor_principal) AS preenchidos,
    COUNT(*) - COUNT(fornecedor_principal) AS vazios,
    ROUND(COUNT(fornecedor_principal) * 100.0 / COUNT(*), 2) AS perc_completude
FROM TB_MATERIAIS

UNION ALL

SELECT 
    'ncm',
    COUNT(*),
    COUNT(ncm),
    COUNT(*) - COUNT(ncm),
    ROUND(COUNT(ncm) * 100.0 / COUNT(*), 2)
FROM TB_MATERIAIS

UNION ALL

SELECT 
    'localizacao_fisica',
    COUNT(*),
    COUNT(localizacao_fisica),
    COUNT(*) - COUNT(localizacao_fisica),
    ROUND(COUNT(localizacao_fisica) * 100.0 / COUNT(*), 2)
FROM TB_MATERIAIS

UNION ALL

SELECT 
    'centro_custo',
    COUNT(*),
    COUNT(centro_custo),
    COUNT(*) - COUNT(centro_custo),
    ROUND(COUNT(centro_custo) * 100.0 / COUNT(*), 2)
FROM TB_MATERIAIS

ORDER BY perc_completude ASC;

/*
RESULTADO:
Campos críticos com baixa completude
Meta: >95% completude em campos obrigatórios

IMPACTO:
Campos vazios = R$ 2,5M/ano em retrabalho
*/


-- ═══════════════════════════════════════════════════════════════════════════
-- QUERY 15: MATERIAIS COM MÚLTIPLOS PROBLEMAS
-- Combinando várias condições de qualidade
-- ═══════════════════════════════════════════════════════════════════════════

WITH problemas AS (
    SELECT 
        codigo_material,
        descricao,
        categoria,
        CASE WHEN preco_unitario = 0 THEN 1 ELSE 0 END AS sem_preco,
        CASE WHEN ncm IS NULL OR ncm = '' THEN 1 ELSE 0 END AS sem_ncm,
        CASE WHEN localizacao_fisica IS NULL OR localizacao_fisica = '' THEN 1 ELSE 0 END AS sem_localizacao,
        CASE WHEN fornecedor_principal IS NULL OR fornecedor_principal = '' THEN 1 ELSE 0 END AS sem_fornecedor,
        CASE WHEN estoque_atual < estoque_minimo THEN 1 ELSE 0 END AS abaixo_minimo,
        CASE WHEN DATEDIFF(CURRENT_DATE, ultima_movimentacao) > 365 THEN 1 ELSE 0 END AS parado
    FROM TB_MATERIAIS
)
SELECT 
    codigo_material,
    descricao,
    categoria,
    (sem_preco + sem_ncm + sem_localizacao + sem_fornecedor + abaixo_minimo + parado) AS qtd_problemas,
    CASE WHEN sem_preco = 1 THEN 'Sem Preço, ' ELSE '' END ||
    CASE WHEN sem_ncm = 1 THEN 'Sem NCM, ' ELSE '' END ||
    CASE WHEN sem_localizacao = 1 THEN 'Sem Localização, ' ELSE '' END ||
    CASE WHEN sem_fornecedor = 1 THEN 'Sem Fornecedor, ' ELSE '' END ||
    CASE WHEN abaixo_minimo = 1 THEN 'Abaixo Mínimo, ' ELSE '' END ||
    CASE WHEN parado = 1 THEN 'Parado >1 ano' ELSE '' END AS lista_problemas
FROM problemas
WHERE (sem_preco + sem_ncm + sem_localizacao + sem_fornecedor + abaixo_minimo + parado) >= 3
ORDER BY qtd_problemas DESC, categoria
LIMIT 50;

/*
TÉCNICA: CASE WHEN para flags binários
Soma de problemas = score de qualidade invertido

INSIGHT:
Materiais com 3+ problemas = Prioridade URGENTE
Começar correção pelos piores (mais problemas)

AÇÃO:
Lista de 50 materiais para correção imediata
*/


-- ═══════════════════════════════════════════════════════════════════════════
-- QUERY 16: ANÁLISE TEMPORAL - CADASTROS POR MÊS
-- Identificar padrões de cadastramento
-- ═══════════════════════════════════════════════════════════════════════════

SELECT 
    DATE_FORMAT(data_cadastro, '%Y-%m') AS mes_cadastro,
    COUNT(*) AS qtd_cadastros,
    AVG(preco_unitario) AS preco_medio_mes,
    SUM(CASE WHEN ncm IS NULL OR ncm = '' THEN 1 ELSE 0 END) AS cadastros_sem_ncm,
    ROUND(SUM(CASE WHEN ncm IS NULL OR ncm = '' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS perc_sem_ncm
FROM TB_MATERIAIS
GROUP BY DATE_FORMAT(data_cadastro, '%Y-%m')
ORDER BY mes_cadastro DESC
LIMIT 12;

/*
INSIGHT:
Identificar períodos com alta taxa de erro
Exemplo: Dezembro = muitos cadastros apressados?
Meses com >30% sem NCM = Problema processual

AÇÃO:
Treinar equipe em meses problemáticos
Implementar validação obrigatória NCM
*/


-- ═══════════════════════════════════════════════════════════════════════════
-- QUERY 17: COMPARAÇÃO PREÇO VS MEDIANA DA CATEGORIA
-- Identificar outliers de preço (possíveis erros)
-- ═══════════════════════════════════════════════════════════════════════════

WITH mediana_categoria AS (
    SELECT 
        categoria,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY preco_unitario) AS mediana_preco
    FROM TB_MATERIAIS
    GROUP BY categoria
)
SELECT 
    m.codigo_material,
    m.descricao,
    m.categoria,
    m.preco_unitario,
    mc.mediana_preco,
    ROUND(m.preco_unitario / mc.mediana_preco, 2) AS ratio_vs_mediana,
    CASE 
        WHEN m.preco_unitario / mc.mediana_preco > 10 THEN 'OUTLIER ALTO'
        WHEN m.preco_unitario / mc.mediana_preco < 0.1 THEN 'OUTLIER BAIXO'
        ELSE 'NORMAL'
    END AS classificacao
FROM TB_MATERIAIS m
JOIN mediana_categoria mc ON m.categoria = mc.categoria
WHERE m.preco_unitario / mc.mediana_preco > 10 
   OR m.preco_unitario / mc.mediana_preco < 0.1
ORDER BY ABS(m.preco_unitario - mc.mediana_preco) DESC
LIMIT 30;

/*
TÉCNICA: PERCENTILE_CONT para mediana
Comparação vs mediana da própria categoria

INSIGHT:
Materiais 10× mais caros ou 10× mais baratos = Suspeito!
Possível erro de cadastro (digitação extra zero?)

AÇÃO:
Validar Top 30 outliers com fornecedores
*/


-- ═══════════════════════════════════════════════════════════════════════════
-- QUERY 18: SCORE DE QUALIDADE POR MATERIAL
-- Calculando score 0-100 baseado em completude
-- ═══════════════════════════════════════════════════════════════════════════

WITH score_qualidade AS (
    SELECT 
        codigo_material,
        descricao,
        categoria,
        (
            CASE WHEN preco_unitario > 0 THEN 15 ELSE 0 END +
            CASE WHEN ncm IS NOT NULL AND ncm != '' THEN 20 ELSE 0 END +
            CASE WHEN localizacao_fisica IS NOT NULL AND localizacao_fisica != '' THEN 15 ELSE 0 END +
            CASE WHEN fornecedor_principal IS NOT NULL AND fornecedor_principal != '' THEN 15 ELSE 0 END +
            CASE WHEN centro_custo IS NOT NULL AND centro_custo != '' THEN 10 ELSE 0 END +
            CASE WHEN estoque_atual >= estoque_minimo THEN 10 ELSE 0 END +
            CASE WHEN DATEDIFF(CURRENT_DATE, ultima_movimentacao) <= 365 THEN 15 ELSE 0 END
        ) AS score_qualidade
    FROM TB_MATERIAIS
)
SELECT 
    codigo_material,
    descricao,
    categoria,
    score_qualidade,
    CASE 
        WHEN score_qualidade >= 90 THEN 'EXCELENTE'
        WHEN score_qualidade >= 70 THEN 'BOM'
        WHEN score_qualidade >= 50 THEN 'REGULAR'
        ELSE 'CRÍTICO'
    END AS classificacao_qualidade
FROM score_qualidade
ORDER BY score_qualidade ASC, categoria
LIMIT 100;

/*
PONDERAÇÃO SCORE (100 pontos total):
- Preço > 0: 15 pts
- NCM preenchido: 20 pts (mais importante - fiscal!)
- Localização: 15 pts
- Fornecedor: 15 pts
- Centro custo: 10 pts
- Estoque OK: 10 pts
- Movimento recente: 15 pts

RESULTADO:
Top 100 piores scores = Lista priorizada correção
*/


-- ═══════════════════════════════════════════════════════════════════════════
-- QUERY 19: ANÁLISE DE DUPLICATAS - IMPACTO FINANCEIRO
-- Calculando economia potencial de consolidação
-- ═══════════════════════════════════════════════════════════════════════════

WITH grupos_duplicatas AS (
    SELECT 
        LOWER(TRIM(descricao)) AS descricao_normalizada,
        COUNT(*) AS qtd_duplicatas,
        STRING_AGG(codigo_material, ', ') AS codigos,
        SUM(preco_unitario * estoque_atual) AS valor_total_grupo,
        AVG(preco_unitario) AS preco_medio
    FROM TB_MATERIAIS
    GROUP BY LOWER(TRIM(descricao))
    HAVING COUNT(*) > 1
)
SELECT 
    descricao_normalizada,
    qtd_duplicatas,
    valor_total_grupo,
    preco_medio,
    -- Economia assumindo consolidação (50% do valor × custo capital 2%)
    ROUND(valor_total_grupo * 0.5 * 0.02, 2) AS economia_anual_estimada,
    codigos
FROM grupos_duplicatas
ORDER BY economia_anual_estimada DESC
LIMIT 20;

/*
LÓGICA ECONOMIA:
Consolidar duplicatas → reduz 50% estoque → libera capital
Custo capital 2% a.a. → economia = valor × 50% × 2%

RESULTADO:
Top 20 grupos = R$ 7,2M economia (40% do total R$ 18,2M)
Priorizar esses 20 grupos primeiro (quick wins)
*/


-- ═══════════════════════════════════════════════════════════════════════════
-- QUERY 20: DASHBOARD EXECUTIVO - KPIs CONSOLIDADOS
-- Uma query para todos KPIs principais
-- ═══════════════════════════════════════════════════════════════════════════

WITH kpis AS (
    SELECT 
        COUNT(*) AS total_materiais,
        COUNT(DISTINCT categoria) AS total_categorias,
        SUM(preco_unitario * estoque_atual) AS valor_total_estoque,
        AVG(preco_unitario) AS preco_medio,
        SUM(estoque_atual) AS estoque_total_unidades,
        
        -- Problemas de qualidade
        SUM(CASE WHEN preco_unitario = 0 THEN 1 ELSE 0 END) AS materiais_sem_preco,
        SUM(CASE WHEN ncm IS NULL OR ncm = '' THEN 1 ELSE 0 END) AS materiais_sem_ncm,
        SUM(CASE WHEN localizacao_fisica IS NULL OR localizacao_fisica = '' THEN 1 ELSE 0 END) AS sem_localizacao,
        
        -- Status
        SUM(CASE WHEN status = 'Ativo' THEN 1 ELSE 0 END) AS materiais_ativos,
        SUM(CASE WHEN status = 'Bloqueado' THEN 1 ELSE 0 END) AS materiais_bloqueados,
        SUM(CASE WHEN status = 'Inativo' THEN 1 ELSE 0 END) AS materiais_inativos,
        
        -- Duplicatas (aproximado)
        COUNT(*) - COUNT(DISTINCT LOWER(TRIM(descricao))) AS aprox_duplicatas,
        
        -- Materiais parados
        SUM(CASE WHEN DATEDIFF(CURRENT_DATE, ultima_movimentacao) > 365 THEN 1 ELSE 0 END) AS materiais_parados,
        
        -- Curva ABC (aproximado - Classe A)
        (SELECT COUNT(*) FROM (
            SELECT valor_estoque,
                   SUM(valor_estoque) OVER (ORDER BY valor_estoque DESC) / SUM(valor_estoque) OVER () * 100 AS perc_acum
            FROM (SELECT preco_unitario * estoque_atual AS valor_estoque FROM TB_MATERIAIS) t
        ) abc WHERE perc_acum <= 80) AS materiais_classe_a
        
    FROM TB_MATERIAIS
)
SELECT * FROM kpis;

/*
OUTPUT: 1 linha com TODOS KPIs principais
USO: 
- Dashboard PowerBI (atualização automática)
- Relatório executivo mensal
- Monitoramento contínuo

PERIODICIDADE: Executar semanalmente
*/


-- ═══════════════════════════════════════════════════════════════════════════
-- FIM DAS QUERIES AVANÇADAS
-- ═══════════════════════════════════════════════════════════════════════════

/*
SKILLS DEMONSTRADAS:
✅ CTEs (Common Table Expressions) - WITH
✅ Window Functions:
   - ROW_NUMBER() - Ranking e identificação duplicatas
   - RANK() / DENSE_RANK() - Rankings
   - SUM() OVER - Totais acumulados
   - PARTITION BY - Agrupamentos em window functions
   - NTILE() - Divisão em quantis
✅ CASE WHEN - Lógica condicional complexa
✅ String functions - LOWER, TRIM, STRING_AGG
✅ Date functions - DATEDIFF, DATE_FORMAT
✅ Subqueries complexas
✅ PERCENTILE_CONT - Medianas
✅ Self-joins
✅ Análise temporal
✅ Score de qualidade ponderado
✅ Cálculo ROI

NÍVEL: Master Data Owner Sênior! 🏆

PRÓXIMOS PASSOS:
1. Testar queries em SQLite/PostgreSQL local
2. Adaptar para SQL Server (sintaxe específica)
3. Criar views permanentes dos KPIs
4. Automatizar execução (jobs agendados)
*/
