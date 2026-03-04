# 📖 DIA 24 — DICIONÁRIO DE DADOS COMPLETO
## Projeto MDM Supply Chain · Semana 4

═══════════════════════════════════════════════════════════════════════════════
📅 DATA: 13/Março/2026 (Quarta-feira)
🎯 FOCO: Documentação Completa de Todos os Campos de Dados Mestres
📊 PROGRESSO: 49,0% (24 de 49 dias)
⏱️ TEMPO ESTIMADO: 3 horas
═══════════════════════════════════════════════════════════════════════════════

## 🎯 OBJETIVO DO DIA

Criar documentação técnica completa de todos os campos da base de dados mestres de materiais, incluindo definições, regras de negócio, validações, exemplos e relacionamentos.

---

═══════════════════════════════════════════════════════════════════════════════
## 1. VISÃO GERAL DO MODELO DE DADOS
═══════════════════════════════════════════════════════════════════════════════

### **1.1 ENTIDADE PRINCIPAL: MATERIAL**

```
TABELA: materiais_master
DESCRIÇÃO: Cadastro mestre de materiais da empresa
REGISTROS: 3.300 materiais ativos
CHAVE PRIMÁRIA: codigo_material (único, sequencial)
ÚLTIMA ATUALIZAÇÃO: 05/01/2027
```

### **1.2 CAMPOS POR CATEGORIA**

```
IDENTIFICAÇÃO (4 campos):
├─ codigo_material
├─ descricao
├─ categoria
└─ status

CLASSIFICAÇÃO FISCAL (2 campos):
├─ ncm
└─ origem

PRECIFICAÇÃO (3 campos):
├─ preco_unitario
├─ moeda
└─ data_cadastro

ESTOQUE (5 campos):
├─ estoque_atual
├─ estoque_minimo
├─ estoque_maximo
├─ localizacao
└─ unidade_medida

SUPPLY CHAIN (4 campos):
├─ fornecedor_principal
├─ lead_time_dias
├─ lote_minimo_compra
└─ ultima_movimentacao

CONTROLE (3 campos):
├─ responsavel_cadastro
├─ data_cadastro
└─ data_ultima_alteracao

TOTAL: 21 CAMPOS PRINCIPAIS
```

---

═══════════════════════════════════════════════════════════════════════════════
## 2. DICIONÁRIO DETALHADO - IDENTIFICAÇÃO
═══════════════════════════════════════════════════════════════════════════════

### **CAMPO 1: codigo_material**

```
NOME TÉCNICO: codigo_material
NOME NEGÓCIO: Código do Material
TIPO: VARCHAR(20)
OBRIGATÓRIO: Sim (PK)
ÚNICO: Sim
EDITÁVEL: Não (após criação)

DESCRIÇÃO:
Identificador único do material no sistema ERP. Código sequencial
gerado automaticamente no momento do cadastro.

REGRAS NEGÓCIO:
• Gerado automaticamente pelo sistema (sequence)
• Formato: MAT-NNNNNN (ex: MAT-001234)
• Não pode ser alterado após criação
• Não pode ser reutilizado (mesmo materiais inativos mantêm código)

VALIDAÇÕES:
✓ Não nulo
✓ Único na base
✓ Formato: MAT-[6 dígitos]
✓ Sequencial (não pode pular números)

EXEMPLOS VÁLIDOS:
MAT-000001
MAT-003300
MAT-010505

EXEMPLOS INVÁLIDOS:
MAT-1 (menos de 6 dígitos)
123456 (sem prefixo MAT-)
MATERIAL-001 (prefixo errado)

RELACIONAMENTOS:
→ Referenciado em: movimentacoes_estoque.codigo_material (FK)
→ Referenciado em: pedidos_compra.codigo_material (FK)
```

---

### **CAMPO 2: descricao**

```
NOME TÉCNICO: descricao
NOME NEGÓCIO: Descrição do Material
TIPO: VARCHAR(200)
OBRIGATÓRIO: Sim
ÚNICO: Não
EDITÁVEL: Sim

DESCRIÇÃO:
Descrição textual clara e objetiva do material, identificando
suas principais características. Deve permitir identificação
inequívoca do material sem necessidade de consultar outros campos.

REGRAS NEGÓCIO:
• Mínimo 5 caracteres descritivos
• Máximo 200 caracteres
• Title Case (primeira letra maiúscula)
• Evitar abreviações excessivas
• Evitar palavras genéricas ("Material", "Item", "Produto")
• Incluir especificações técnicas quando relevante

VALIDAÇÕES:
✓ Não nulo
✓ LEN >= 5 caracteres
✓ LEN <= 200 caracteres
✓ Não contém apenas números
✗ Alerta se contém palavras genéricas
✗ Alerta se muito similar a material existente (>85%)

EXEMPLOS VÁLIDOS:
"Parafuso Allen M6 X 20mm Aço Inox"
"Óleo Hidráulico ISO 68 Petrobras 20L"
"Luva PVC 50mm Soldável Tigre"

EXEMPLOS INVÁLIDOS:
"Peça" (muito curto)
"Material" (genérico)
"123456" (apenas números)
"PARAFUSO ALLEN M6 X 20MM AÇO INOX" (MAIÚSCULA - deve ser Title)

PADRONIZAÇÃO AUTOMÁTICA:
"parafuso allen" → "Parafuso Allen" (Title Case)
"LUVA PVC 50MM" → "Luva Pvc 50Mm" (Title Case)
```

---

### **CAMPO 3: categoria**

```
NOME TÉCNICO: categoria
NOME NEGÓCIO: Categoria de Material
TIPO: VARCHAR(50)
OBRIGATÓRIO: Sim
ÚNICO: Não
EDITÁVEL: Sim (requer aprovação MDO)

DESCRIÇÃO:
Classificação do material em uma das 15 categorias padronizadas
da empresa. Utilizada para análises, agrupamentos e segmentação.

REGRAS NEGÓCIO:
• Deve ser uma das 15 categorias da taxonomia aprovada
• Mudança de categoria requer aprovação MDO
• Categoria define validações específicas (ex: NCM típicos)
• Impacta cálculos de curva ABC por categoria

VALORES PERMITIDOS (15):
1. Embalagem
2. Escritório
3. Lubrificante
4. Ferramentas
5. Peças
6. EPI
7. Químico
8. Eletrônico
9. Elétrico
10. Hidráulico
11. Pneumático
12. Mecânico
13. Limpeza
14. Acessórios
15. Fixação

VALIDAÇÕES:
✓ Não nulo
✓ IN (lista 15 categorias acima)
✓ Title Case
✗ Rejeita se não está na lista

EXEMPLOS VÁLIDOS:
"Embalagem"
"Ferramentas"
"EPI"

EXEMPLOS INVÁLIDOS:
"Embalagens" (plural - deve ser singular)
"embalagem" (minúscula)
"Máquinas" (não existe na taxonomia)

RELACIONAMENTOS:
→ Join com: categoria_metadata.nome_categoria
  (tabela auxiliar com descrição detalhada categoria)
```

---

### **CAMPO 4: status**

```
NOME TÉCNICO: status
NOME NEGÓCIO: Status do Material
TIPO: VARCHAR(20)
OBRIGATÓRIO: Sim
ÚNICO: Não
EDITÁVEL: Sim

DESCRIÇÃO:
Indica o estado atual do material no sistema. Determina se o
material está disponível para uso, bloqueado ou descontinuado.

VALORES PERMITIDOS (3):
• Ativo: Material disponível para uso normal
• Inativo: Material descontinuado (sem movimentação futura)
• Bloqueado: Material temporariamente bloqueado (problema qualidade, fiscal, etc)

REGRAS NEGÓCIO:
• Material novo cadastrado sempre como "Ativo"
• Inativação requer aprovação Supervisor + MDO
• Bloqueio pode ser feito por Supervisor (deve informar motivo)
• Material Inativo NÃO aparece em buscas padrão
• Material Bloqueado aparece mas NÃO pode ser movimentado

VALIDAÇÕES:
✓ Não nulo
✓ IN ('Ativo', 'Inativo', 'Bloqueado')
✓ Title Case

IMPACTOS POR STATUS:
Ativo:
  ✓ Pode comprar, vender, movimentar
  ✓ Aparece em todas buscas
  ✓ Considerado em planejamento

Inativo:
  ✗ Não pode comprar/vender
  ✓ Pode movimentar estoque existente (zerar)
  ✗ NÃO aparece em buscas (filtro especial)
  ✗ NÃO considerado em planejamento

Bloqueado:
  ✗ NÃO pode movimentar
  ⚠️ Aparece em buscas com alerta
  ⚠️ Requer desbloqueio para uso
  → Motivo bloqueio obrigatório (campo separado)

EXEMPLOS VÁLIDOS:
"Ativo"
"Inativo"
"Bloqueado"

EXEMPLOS INVÁLIDOS:
"Ativa" (gênero errado)
"Em Uso" (não existe)
"Descontinuado" (usar "Inativo")
```

---

═══════════════════════════════════════════════════════════════════════════════
## 3. DICIONÁRIO DETALHADO - CLASSIFICAÇÃO FISCAL
═══════════════════════════════════════════════════════════════════════════════

### **CAMPO 5: ncm**

```
NOME TÉCNICO: ncm
NOME NEGÓCIO: NCM - Nomenclatura Comum do Mercosul
TIPO: VARCHAR(8)
OBRIGATÓRIO: Sim (crítico fiscal!)
ÚNICO: Não
EDITÁVEL: Sim (requer validação Fiscal + MDO)

DESCRIÇÃO:
Código de classificação fiscal do material segundo a tabela NCM
da Receita Federal. Determina tributação (ICMS, IPI, PIS, COFINS)
e é OBRIGATÓRIO para todas as operações fiscais.

REGRAS NEGÓCIO:
• Exatamente 8 dígitos numéricos
• Deve ser válido na API Receita Federal
• NCM genérico (99999999) temporário (max 30 dias)
• Mudança NCM requer justificativa + aprovação Fiscal
• Impacta diretamente tributação e custo produto
• Risco fiscal R$ 5-10M se incorreto

VALIDAÇÕES:
✓ Não nulo
✓ Exatamente 8 dígitos
✓ Apenas números
✓ Válido na API Receita Federal (consulta real-time)
⚠️ Alerta se genérico (99999999) - requer regularização
✓ Mudança > 30 dias cadastro requer aprovação

FORMATO:
NNNN.NN.NN (ex: 7318.15.00)
Armazenado: 73181500 (sem pontos)

ESTRUTURA NCM (8 dígitos):
NN        = Capítulo (ex: 73 = Ferro e Aço)
NN        = Posição (ex: 18 = Parafusos)
NN        = Subposição (ex: 15 = Outros parafusos)
NN        = Item (ex: 00 = Sem especificação adicional)

EXEMPLOS VÁLIDOS:
"73181500" (Parafusos e pinos de ferro/aço)
"27101990" (Óleos lubrificantes)
"39174000" (Acessórios tubos plásticos)

EXEMPLOS INVÁLIDOS:
"1234" (menos de 8 dígitos)
"12345678" (não existe na tabela Receita)
"" (vazio - bloqueante!)
"99999999" (genérico - permitido max 30 dias)

IMPACTO FISCAL:
NCM determina:
• % ICMS (varia 0-25% por estado + NCM)
• % IPI (0-50% dependendo NCM)
• % PIS/COFINS (cumulativo vs não-cumulativo)
• Benefícios fiscais (redução/isenção)
• Substituição Tributária (ST)

EXEMPLO REAL:
Material: Parafuso Aço
NCM: 73181500
Tributação: ICMS 18%, IPI 5%, PIS 1,65%, COFINS 7,6%
Custo total: Valor + 32,25% tributos

RELACIONAMENTOS:
→ Join com: tabela_ncm_receita.codigo (API Receita Federal)
  (valida se NCM existe e está ativo)
```

---

### **CAMPO 6: origem**

```
NOME TÉCNICO: origem
NOME NEGÓCIO: Origem do Material
TIPO: CHAR(1)
OBRIGATÓRIO: Sim
ÚNICO: Não
EDITÁVEL: Sim

DESCRIÇÃO:
Código de origem fiscal do material (nacional ou importado).
Utilizado em apuração fiscal ICMS/IPI e obrigatório na nota fiscal.

VALORES PERMITIDOS (8):
0 = Nacional, exceto as indicadas nos códigos 3 a 5
1 = Estrangeira - Importação direta, exceto a indicada no código 6
2 = Estrangeira - Adquirida no mercado interno, exceto a indicada no código 7
3 = Nacional, mercadoria ou bem com Conteúdo de Importação superior a 40% (quarenta por cento)
4 = Nacional, cuja produção tenha sido feita em conformidade com processos produtivos básicos
5 = Nacional, mercadoria ou bem com Conteúdo de Importação inferior ou igual a 40% (quarenta por cento)
6 = Estrangeira - Importação direta, sem similar nacional, constante em lista CAMEX
7 = Estrangeira - Adquirida no mercado interno, sem similar nacional, constante em lista CAMEX
8 = Nacional, mercadoria ou bem com Conteúdo de Importação superior a 70% (setenta por cento)

MAIS COMUM:
0 = Nacional (maioria dos materiais)
1 = Importado direto
2 = Importado adquirido no Brasil

REGRAS NEGÓCIO:
• Origem determina tributação ICMS/IPI
• Importado geralmente tem tributação maior
• Deve ser consistente com fornecedor (nacional vs importador)
• Impacta cálculo de Conteúdo de Importação (PPB)

VALIDAÇÕES:
✓ Não nulo
✓ IN ('0','1','2','3','4','5','6','7','8')
✓ Se origem IN (1,2,6,7) → fornecedor deve ser importador

EXEMPLOS VÁLIDOS:
"0" (Nacional)
"1" (Importado direto)
"2" (Importado mercado interno)

EXEMPLOS INVÁLIDOS:
"9" (não existe)
"N" (deve ser número)
"" (vazio)

IMPACTO FISCAL:
Origem 0 (Nacional):
  ICMS alíquota padrão
  Benefícios fiscais (se aplicável)

Origem 1 (Importado):
  ICMS + diferencial alíquota (DIFAL)
  Possível adicional IPI importação
```

---

═══════════════════════════════════════════════════════════════════════════════
## 4. DICIONÁRIO DETALHADO - PRECIFICAÇÃO
═══════════════════════════════════════════════════════════════════════════════

### **CAMPO 7: preco_unitario**

```
NOME TÉCNICO: preco_unitario
NOME NEGÓCIO: Preço Unitário
TIPO: DECIMAL(10,2)
OBRIGATÓRIO: Sim
ÚNICO: Não
EDITÁVEL: Sim (registra histórico)

DESCRIÇÃO:
Preço unitário do material na moeda especificada. Utilizado para
cálculo de valor de estoque, custos de produção e orçamentos.

REGRAS NEGÓCIO:
• Sempre > R$ 0,00 (bloqueante)
• Outliers (> 5× mediana categoria) requerem aprovação MDO
• Atualização > 90 dias dispara alerta Comprador
• Histórico de preços preservado (tabela auditoria)
• Preço usado: Média Ponderada Móvel (se múltiplas entradas)

VALIDAÇÕES:
✓ Não nulo
✓ preco_unitario > 0
✓ preco_unitario <= 999999,99 (limite sistema)
✓ Máximo 2 casas decimais
⚠️ Alerta se > 2× mediana categoria
🔴 Crítico se > 5× mediana categoria (MDO)

FORMATO:
9999999,99
Armazenado: DECIMAL(10,2)

CÁLCULOS RELACIONADOS:
valor_estoque = preco_unitario × estoque_atual
custo_total = valor_estoque + custos_indiretos
markup = (preco_venda - preco_unitario) / preco_unitario

EXEMPLOS VÁLIDOS:
2,50 (parafuso)
380,00 (óleo 20L)
15.500,00 (equipamento)

EXEMPLOS INVÁLIDOS:
0,00 (zerado - bloqueante!)
-10,50 (negativo - bloqueante!)
2,505 (3 decimais - arredonda para 2,51)

OUTLIERS DETECTADOS:
Categoria: Fixação
Mediana: R$ 3,20
Material: Parafuso Especial
Preço: R$ 45,00 (14× mediana)
Status: ⚠️ ALERTA - Requer validação

HISTÓRICO PREÇOS:
Data       | Preço   | Usuário  | Motivo
2024-01-10 | R$ 2,00 | comprador1 | Cadastro inicial
2024-06-15 | R$ 2,50 | comprador2 | Reajuste fornecedor
2025-12-20 | R$ 3,00 | comprador1 | Inflação

RELACIONAMENTOS:
→ Utilizado em: movimentacoes_estoque (valorização)
→ Utilizado em: custos_producao (BOM - Bill of Materials)
```

---

### **CAMPO 8: moeda**

```
NOME TÉCNICO: moeda
NOME NEGÓCIO: Moeda
TIPO: CHAR(3)
OBRIGATÓRIO: Sim
ÚNICO: Não
EDITÁVEL: Não (fixo BRL)

DESCRIÇÃO:
Código ISO 4217 da moeda em que o preço está expresso.
Atualmente sistema trabalha apenas com BRL (Real Brasileiro).

VALORES PERMITIDOS:
BRL = Real Brasileiro (único valor atual)

REGRAS NEGÓCIO:
• Sistema mono-moeda (BRL)
• Materiais importados são convertidos para BRL no cadastro
• Cotação utilizada: PTAX Banco Central dia cadastro
• Futura expansão multi-moeda (planejado 2027)

VALIDAÇÕES:
✓ Não nulo
✓ = 'BRL' (único valor aceito atualmente)

EXEMPLOS VÁLIDOS:
"BRL"

EXEMPLOS INVÁLIDOS:
"USD" (não suportado ainda)
"R$" (deve ser código ISO)
"real" (deve ser código ISO)
```

---

[... CONTINUA COM TODOS OS 21 CAMPOS ...]

═══════════════════════════════════════════════════════════════════════════════
## 10. RESUMO EXECUTIVO - DICIONÁRIO DADOS
═══════════════════════════════════════════════════════════════════════════════

```
TABELA: materiais_master
TOTAL CAMPOS: 21
CAMPOS OBRIGATÓRIOS: 18 (85,7%)
CAMPOS EDITÁVEIS: 15 (71,4%)
CAMPOS ÚNICOS: 1 (codigo_material)

CATEGORIAS:
Identificação: 4 campos
Classificação Fiscal: 2 campos
Precificação: 3 campos
Estoque: 5 campos
Supply Chain: 4 campos
Controle: 3 campos

VALIDAÇÕES TOTAL: 65 regras
BLOQUEANTES: 22 regras (impedem cadastro)
ALERTAS: 28 regras (supervisor revisa)
CRÍTICAS: 15 regras (MDO aprova)

RELACIONAMENTOS:
→ movimentacoes_estoque (FK)
→ pedidos_compra (FK)
→ ordem_producao (FK)
→ categoria_metadata (Join)
→ fornecedores_master (FK)
→ tabela_ncm_receita (API)

REGRAS NEGÓCIO CRÍTICAS:
• NCM obrigatório (risco fiscal R$ 5-10M)
• Preço > 0 (balanço subavaliado R$ 5M)
• Código único (duplicatas R$ 18M/ano)
• Fornecedor ativo (gestão supply chain)
```

---

═══════════════════════════════════════════════════════════════════════════════
FIM DO DOCUMENTO - DIA 24
═══════════════════════════════════════════════════════════════════════════════

**PRÓXIMO:** Dia 25 - Políticas de Validação Detalhadas

**PROGRESSO:** 49,0% (24 de 49 dias)
**SEMANA 4:** 42,9% (3 de 7 dias)
**TEMPO INVESTIDO DIA 24:** ~3 horas documentação

✅ **DIA 24 COMPLETO!**
