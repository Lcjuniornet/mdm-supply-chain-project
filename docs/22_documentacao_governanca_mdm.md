# 📋 DIA 22 — DOCUMENTAÇÃO GOVERNANÇA MDM
## Projeto MDM Supply Chain · Semana 4

═══════════════════════════════════════════════════════════════════════════════
📅 DATA: 11/Março/2026 (Segunda-feira)
🎯 FOCO: Formalizar Políticas e Processos de Governança
📊 PROGRESSO: 44,9% (22 de 49 dias)
⏱️ TEMPO ESTIMADO: 2 horas
═══════════════════════════════════════════════════════════════════════════════

## 🎯 OBJETIVO DO DIA

```
CRIAR DOCUMENTAÇÃO FORMAL DE GOVERNANÇA MDM:
═══════════════════════════════════════════════════════════

1. Políticas de Qualidade de Dados
2. Workflow de Aprovação (3 Níveis)
3. Matriz RACI Detalhada
4. Regras de Validação Formalizadas
5. Processos de Exceção
6. SLAs por Caminho de Aprovação
```

---

═══════════════════════════════════════════════════════════════════════════════
## 1. POLÍTICAS DE QUALIDADE DE DADOS
═══════════════════════════════════════════════════════════════════════════════

### **1.1 PRINCÍPIOS FUNDAMENTAIS**

```
PRINCÍPIO 1: DADOS COMO ATIVO ESTRATÉGICO
─────────────────────────────────────────────────────────────
Dados mestres são tratados como ativos corporativos críticos
que requerem governança, proteção e gestão ativa.

Implicações:
• Qualidade de dados é responsabilidade de todos
• Investimento em dados é aprovado como CAPEX
• Métricas de qualidade são KPIs corporativos


PRINCÍPIO 2: QUALIDADE NA ORIGEM
─────────────────────────────────────────────────────────────
Dados devem ser criados corretos desde o cadastro inicial,
não corrigidos posteriormente.

Implicações:
• Validações automáticas no ponto de entrada
• Cadastro bloqueado se regras não atendidas
• Responsável pelo cadastro = responsável pela qualidade


PRINCÍPIO 3: CONFIANÇA E RASTREABILIDADE
─────────────────────────────────────────────────────────────
Todos os dados devem ter origem conhecida e mudanças auditáveis.

Implicações:
• Logs completos de todas alterações
• Identificação de quem criou/alterou/aprovou
• Histórico de mudanças preservado


PRINCÍPIO 4: GOVERNANÇA POR EXCEÇÃO
─────────────────────────────────────────────────────────────
A maioria dos casos segue regras automáticas; apenas exceções
requerem intervenção humana.

Implicações:
• 70-80% auto-aprovados (meta)
• 15-20% supervisor (alertas)
• 5-10% MDO (casos críticos)
```

---

### **1.2 DIMENSÕES DE QUALIDADE (DAMA DMBOK)**

```
DIMENSÃO 1: ACURACIDADE (Accuracy)
═══════════════════════════════════════════════════════════

Definição: Dados refletem a realidade corretamente

Métricas:
• % materiais com preço = físico (±2%)
• % estoque sistema = físico (shrinkage < 1%)
• % NCMs validados vs Receita Federal

Meta: > 98% acuracidade
Responsável: Equipe Almoxarifado
Frequência: Inventário mensal


DIMENSÃO 2: COMPLETUDE (Completeness)
═══════════════════════════════════════════════════════════

Definição: Campos obrigatórios estão preenchidos

Métricas:
• Score completude ponderado por criticidade
• % materiais com todos campos obrigatórios
• % campos vazios em campos críticos

Meta: > 95% completude
Responsável: Cadastrador + Supervisor
Frequência: Validação real-time


DIMENSÃO 3: CONSISTÊNCIA (Consistency)
═══════════════════════════════════════════════════════════

Definição: Dados são uniformes e padronizados

Métricas:
• % textos padronizados (Title Case)
• % unidades medida no padrão
• % categorias dentro da taxonomia

Meta: > 90% consistência
Responsável: Sistema (automatizado)
Frequência: Batch noturno


DIMENSÃO 4: VALIDADE (Validity)
═══════════════════════════════════════════════════════════

Definição: Dados atendem regras de negócio

Métricas:
• % NCMs válidos (8 dígitos + API Receita)
• % preços dentro range esperado
• % fornecedores ativos no cadastro

Meta: 100% validade (bloqueante)
Responsável: Sistema (pré-cadastro)
Frequência: Real-time


DIMENSÃO 5: UNICIDADE (Uniqueness)
═══════════════════════════════════════════════════════════

Definição: Sem duplicatas no cadastro

Métricas:
• % materiais sem duplicata (fuzzy match)
• % códigos únicos no sistema
• % fornecedores consolidados

Meta: 0% duplicatas
Responsável: MDO (validação manual)
Frequência: Semanal


DIMENSÃO 6: ATUALIDADE (Timeliness)
═══════════════════════════════════════════════════════════

Definição: Dados refletem estado atual

Métricas:
• % materiais com movimentação < 365 dias
• % preços atualizados < 90 dias
• % fornecedores revisados < 180 dias

Meta: > 85% atualidade
Responsável: Comprador + Almoxarife
Frequência: Trimestral
```

---

═══════════════════════════════════════════════════════════════════════════════
## 2. WORKFLOW DE APROVAÇÃO (3 NÍVEIS)
═══════════════════════════════════════════════════════════════════════════════

### **2.1 VISÃO GERAL DO WORKFLOW**

```
┌─────────────────────────────────────────────────────────┐
│                  CADASTRO MATERIAL                       │
│                  (Sistema ERP)                           │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  VALIDAÇÃO AUTOMÁTICA  │
         │  (Regras Bloqueantes)  │
         └───────┬───────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
    APROVADO         REJEITADO
        │                 │
        │                 └──► Retorna para correção
        │
        ▼
┌───────────────────┐
│  CLASSIFICAÇÃO    │
│  AUTOMÁTICA       │
│  (Score/Regras)   │
└────┬──────────────┘
     │
     ├──► 70-80% ──► CAMINHO 1: AUTO-APROVAÇÃO
     │                SLA: ~3 segundos
     │                Ação: Cadastro imediato
     │
     ├──► 15-20% ──► CAMINHO 2: SUPERVISOR
     │                SLA: 4 horas
     │                Ação: Análise alertas
     │
     └──► 5-10%  ──► CAMINHO 3: MDO
                      SLA: 24 horas
                      Ação: Análise caso crítico
```

---

### **2.2 CAMINHO 1: AUTO-APROVAÇÃO (70-80%)**

```
CRITÉRIOS PARA AUTO-APROVAÇÃO:
═══════════════════════════════════════════════════════════

✅ TODAS as validações bloqueantes passaram
✅ NENHUM alerta crítico identificado
✅ Material NÃO é Classe A (valor < R$ 50k)
✅ NCM válido e comum (não genérico)
✅ Fornecedor cadastrado ativo
✅ Preço dentro de 2× mediana categoria
✅ Campos obrigatórios 100% preenchidos
✅ Sem similaridade alta com existentes (> 90%)

PROCESSO:
─────────────────────────────────────────────────────────────
1. Sistema valida automaticamente
2. Score > 80 pontos (de 100)
3. Cadastro aprovado instantaneamente
4. Log de aprovação automática gerado
5. Disponível para uso imediato

SLA: ~3 segundos
RESPONSÁVEL: Sistema automatizado
AUDITORIA: Log completo preservado

EXEMPLO:
─────────────────────────────────────────────────────────────
Material: "Parafuso Allen M6 X 20mm"
Categoria: Fixação
Preço: R$ 2,50/un
NCM: 73181500 (válido API Receita)
Fornecedor: Parafusos Brasil Ltda (ativo)
Estoque: 500 unidades
Score: 95 pontos

RESULTADO: ✅ AUTO-APROVADO (Caminho 1)
```

---

### **2.3 CAMINHO 2: SUPERVISOR (15-20%)**

```
CRITÉRIOS PARA CAMINHO 2:
═══════════════════════════════════════════════════════════

⚠️ Validações bloqueantes: PASS
⚠️ MAS há 1+ alertas não-críticos:

ALERTAS TÍPICOS:
• Preço outlier (> 2× mas < 5× mediana)
• Fornecedor sem histórico recente
• Estoque mínimo não definido
• Descrição genérica (mas > 5 caracteres)
• Categoria secundária não preenchida
• Última atualização preço > 180 dias

PROCESSO:
─────────────────────────────────────────────────────────────
1. Sistema identifica alertas
2. Ticket criado automaticamente
3. Email supervisor (em até 1h)
4. Supervisor analisa em até 4h
5. Decide: Aprovar / Rejeitar / Solicitar correção
6. Log decisão + justificativa

SLA: 4 horas (turno)
RESPONSÁVEL: Supervisor Almoxarifado
AUDITORIA: Decisão + justificativa obrigatória

EXEMPLO:
─────────────────────────────────────────────────────────────
Material: "Óleo Hidráulico ISO 68 Petrobras 20L"
Categoria: Lubrificante
Preço: R$ 380,00/un (mediana: R$ 150,00)
⚠️ ALERTA: Preço 2,5× acima mediana categoria
NCM: 27101990 (válido)
Fornecedor: Distribuidora Óleos SP (ativo)

Supervisor analisa:
"Preço justificado - produto Petrobras premium.
Mediana inclui marcas econômicas. APROVADO."

RESULTADO: ✅ APROVADO VIA SUPERVISOR (Caminho 2)
TEMPO REAL: 2h 15min
```

---

### **2.4 CAMINHO 3: MDO - MASTER DATA OWNER (5-10%)**

```
CRITÉRIOS PARA CAMINHO 3 (CRÍTICO):
═══════════════════════════════════════════════════════════

🔴 Material Classe A (valor > R$ 50.000)
🔴 NCM genérico ou suspeito (99999999, etc)
🔴 Duplicata potencial (similaridade > 85%)
🔴 Preço outlier extremo (> 5× mediana)
🔴 Fornecedor novo sem due diligence
🔴 Categoria nova (fora taxonomia)
🔴 Importado (requer documentação específica)
🔴 Controlado (ANVISA, Exército, etc)

PROCESSO:
─────────────────────────────────────────────────────────────
1. Sistema identifica caso crítico
2. Ticket prioritário criado
3. Email + SMS MDO (imediato)
4. MDO analisa profundamente
5. Pode requerer:
   • Documentação adicional
   • Validação fornecedor
   • Análise mercado (3 cotações)
   • Aprovação Gerência
6. Decisão documentada
7. Log completo + anexos

SLA: 24 horas (1 dia útil)
RESPONSÁVEL: Master Data Owner
AUDITORIA: Documentação completa obrigatória

EXEMPLO:
─────────────────────────────────────────────────────────────
Material: "Torno CNC Haas ST-20Y"
Categoria: Máquinas (NOVA! - não existe)
Preço: R$ 485.000,00
🔴 CRÍTICO: Valor > R$ 50k (Classe A)
🔴 CRÍTICO: Categoria inexistente
NCM: 84581100
Fornecedor: Haas do Brasil (novo cadastro)

MDO analisa:
1. Cria categoria "Máquinas-Ferramentas"
2. Valida 3 cotações fornecedor
3. Confirma NCM com despachante
4. Solicita aprovação CFO (CAPEX)
5. Documenta business case
6. APROVADO com ressalvas

RESULTADO: ✅ APROVADO VIA MDO (Caminho 3)
TEMPO REAL: 18h (incluindo aprovação CFO)
DOCUMENTOS: 5 anexos (cotações, NCM, business case)
```

---

### **2.5 CAMINHO 0: REJEITADO**

```
CRITÉRIOS PARA REJEIÇÃO:
═══════════════════════════════════════════════════════════

❌ Validação bloqueante FALHOU:
• NCM inválido (≠ 8 dígitos ou API Receita rejeita)
• Preço = 0 ou negativo
• Descrição < 5 caracteres
• Unidade medida não padronizada
• Categoria não existe
• Campos obrigatórios vazios
• Fornecedor bloqueado/inativo

PROCESSO:
─────────────────────────────────────────────────────────────
1. Sistema rejeita automaticamente
2. Mensagem clara do motivo
3. Retorna para cadastrador
4. Log de rejeição gerado
5. Não entra no sistema

SLA: Imediato (0 segundos)
RESPONSÁVEL: Sistema + Cadastrador (correção)
AUDITORIA: Tentativa rejeitada registrada

EXEMPLO:
─────────────────────────────────────────────────────────────
Material: "Peça"
Categoria: Metal
Preço: R$ 0,00
NCM: 1234 (inválido - precisa 8 dígitos)

❌ REJEITADO:
• Descrição muito curta (< 5 caracteres)
• Preço = R$ 0,00 (bloqueante)
• NCM inválido (4 dígitos, requer 8)

Ação: Retorna para cadastrador corrigir
Tentativa: Registrada mas NÃO cadastrada
```

---

═══════════════════════════════════════════════════════════════════════════════
## 3. MATRIZ RACI DETALHADA
═══════════════════════════════════════════════════════════════════════════════

### **3.1 LEGENDA RACI**

```
R = RESPONSIBLE (Responsável pela execução)
A = ACCOUNTABLE (Autoridade final, quem aprova)
C = CONSULTED (Consultado antes da decisão)
I = INFORMED (Informado após a decisão)
```

---

### **3.2 MATRIZ RACI - PROCESSOS MDM**

```
════════════════════════════════════════════════════════════════════════════════
PROCESSO                    │ Cadastr│ Superv│  MDO  │Compra│Almox│ TI  │ CFO
                            │  ador  │  isor │       │ dor  │  ife│     │
════════════════════════════════════════════════════════════════════════════════
CADASTRO MATERIAL NOVO      │   R    │   C   │   A   │  C   │  I  │  I  │  -
Caminho 1 (Auto-Aprovação)  │   R    │   I   │   I   │  I   │  I  │  -  │  -
Caminho 2 (Supervisor)      │   R    │   A   │   C   │  C   │  I  │  -  │  -
Caminho 3 (MDO Crítico)     │   R    │   C   │   A   │  C   │  I  │  C  │  C
────────────────────────────┼────────┼───────┼───────┼──────┼─────┼─────┼────
ATUALIZAÇÃO PREÇO           │   -    │   R   │   A   │  C   │  I  │  -  │  -
ATUALIZAÇÃO NCM             │   -    │   C   │   A   │  -   │  I  │  C  │  -
MUDANÇA FORNECEDOR PRINCIPAL│   -    │   R   │   C   │  A   │  I  │  -  │  -
────────────────────────────┼────────┼───────┼───────┼──────┼─────┼─────┼────
CORREÇÃO DUPLICATA          │   -    │   C   │   A   │  I   │  R  │  C  │  -
VALIDAÇÃO INVENTÁRIO        │   -    │   C   │   A   │  -   │  R  │  -  │  -
EXCLUSÃO MATERIAL (INATIVO) │   -    │   C   │   A   │  C   │  R  │  C  │  -
────────────────────────────┼────────┼───────┼───────┼──────┼─────┼─────┼────
DEFINIÇÃO POLÍTICAS         │   I    │   C   │   A   │  C   │  C  │  C  │  C
AUDITORIA QUALIDADE DADOS   │   I    │   C   │   R   │  I   │  C  │  C  │  -
REPORTE EXECUTIVO (KPIs)    │   -    │   I   │   R   │  I   │  I  │  I  │  A
════════════════════════════════════════════════════════════════════════════════

NOTAS:
─────────────────────────────────────────────────────────────
• Cadastrador: Almoxarife, Comprador, ou quem cadastra
• Supervisor: Supervisor Almoxarifado/Compras
• MDO: Master Data Owner (responsável governança)
• TI: Envolvido em mudanças sistema
• CFO: Envolvido em materiais alto valor (CAPEX)
```

---

═══════════════════════════════════════════════════════════════════════════════
## 4. REGRAS DE VALIDAÇÃO FORMALIZADAS
═══════════════════════════════════════════════════════════════════════════════

### **4.1 VALIDAÇÕES BLOQUEANTES (CRÍTICAS)**

```
REGRA B01: NCM OBRIGATÓRIO E VÁLIDO
═══════════════════════════════════════════════════════════
Descrição: Todo material deve ter NCM válido
Validação: 
  • NCM != vazio
  • NCM = 8 dígitos numéricos
  • NCM válido na API Receita Federal
Ação se falhar: REJEITAR cadastro
Mensagem: "NCM inválido. Consulte tabela NCM Receita Federal"
Responsável: Cadastrador


REGRA B02: PREÇO UNITÁRIO POSITIVO
═══════════════════════════════════════════════════════════
Descrição: Preço deve ser maior que zero
Validação:
  • preco_unitario > 0
  • preco_unitario é numérico
Ação se falhar: REJEITAR cadastro
Mensagem: "Preço deve ser maior que R$ 0,00"
Responsável: Cadastrador


REGRA B03: DESCRIÇÃO MÍNIMA
═══════════════════════════════════════════════════════════
Descrição: Descrição clara com mínimo 5 caracteres
Validação:
  • descricao != vazio
  • LEN(descricao) >= 5
  • Não contém apenas números
Ação se falhar: REJEITAR cadastro
Mensagem: "Descrição muito curta. Mínimo 5 caracteres descritivos"
Responsável: Cadastrador


REGRA B04: CATEGORIA VÁLIDA
═══════════════════════════════════════════════════════════
Descrição: Categoria deve existir na taxonomia
Validação:
  • categoria IN (lista aprovada)
  • Taxonomia com 3 níveis máximo
Ação se falhar: REJEITAR cadastro
Mensagem: "Categoria inválida. Selecione da lista aprovada"
Responsável: Cadastrador + MDO (taxonomia)


REGRA B05: UNIDADE MEDIDA PADRONIZADA
═══════════════════════════════════════════════════════════
Descrição: Unidade de medida no padrão corporativo
Validação:
  • unidade_medida IN (UN, KG, LT, M, M2, M3, PC, CX, etc)
  • Lista de 20 unidades aprovadas
Ação se falhar: REJEITAR cadastro
Mensagem: "Unidade inválida. Use: UN, KG, LT, M, PC, CX"
Responsável: Cadastrador


REGRA B06: FORNECEDOR ATIVO (se informado)
═══════════════════════════════════════════════════════════
Descrição: Se fornecedor informado, deve estar ativo
Validação:
  • SE fornecedor != vazio
  • ENTÃO fornecedor.status = "Ativo"
Ação se falhar: REJEITAR cadastro
Mensagem: "Fornecedor bloqueado ou inativo. Selecione outro"
Responsável: Cadastrador + Comprador
```

---

### **4.2 VALIDAÇÕES DE ALERTA (NÃO-BLOQUEANTES)**

```
REGRA A01: PREÇO OUTLIER MODERADO
═══════════════════════════════════════════════════════════
Descrição: Preço 2-5× acima/abaixo mediana categoria
Validação:
  • preco > (mediana_categoria × 2) AND
  • preco < (mediana_categoria × 5)
Ação: CAMINHO 2 (Supervisor)
Mensagem: "Preço 2-5× acima/abaixo mediana. Requer aprovação"
Responsável: Supervisor


REGRA A02: ESTOQUE MÍNIMO NÃO DEFINIDO
═══════════════════════════════════════════════════════════
Descrição: Estoque mínimo deveria estar preenchido
Validação:
  • estoque_minimo = vazio OR
  • estoque_minimo = 0
Ação: CAMINHO 2 (Supervisor)
Mensagem: "Estoque mínimo não definido. Recomenda-se preencher"
Responsável: Supervisor + Almoxarife


REGRA A03: FORNECEDOR SEM HISTÓRICO RECENTE
═══════════════════════════════════════════════════════════
Descrição: Fornecedor sem compras nos últimos 180 dias
Validação:
  • fornecedor.ultima_compra > 180 dias
Ação: CAMINHO 2 (Supervisor)
Mensagem: "Fornecedor sem histórico recente. Verificar situação"
Responsável: Supervisor + Comprador


REGRA A04: DESCRIÇÃO GENÉRICA
═══════════════════════════════════════════════════════════
Descrição: Descrição contém palavras genéricas
Validação:
  • descricao CONTAINS ("Material", "Produto", "Item", "Diversos")
Ação: CAMINHO 2 (Supervisor)
Mensagem: "Descrição genérica. Recomenda-se mais detalhes"
Responsável: Supervisor
```

---

### **4.3 VALIDAÇÕES CRÍTICAS (MDO)**

```
REGRA C01: MATERIAL CLASSE A (ALTO VALOR)
═══════════════════════════════════════════════════════════
Descrição: Material com valor estoque > R$ 50.000
Validação:
  • (preco_unitario × estoque_atual) > 50000
Ação: CAMINHO 3 (MDO)
Mensagem: "Material Classe A. Requer análise MDO"
Responsável: MDO + CFO (se CAPEX)


REGRA C02: NCM GENÉRICO OU SUSPEITO
═══════════════════════════════════════════════════════════
Descrição: NCM genérico ou placeholder
Validação:
  • NCM = "99999999" OR
  • NCM = "00000000" OR
  • NCM em lista_ncms_genericos
Ação: CAMINHO 3 (MDO)
Mensagem: "NCM genérico. Requer validação fiscal específica"
Responsável: MDO + Fiscal


REGRA C03: DUPLICATA POTENCIAL
═══════════════════════════════════════════════════════════
Descrição: Material similar já existe (fuzzy match > 85%)
Validação:
  • Levenshtein(descricao, descricoes_existentes) > 85%
Ação: CAMINHO 3 (MDO)
Mensagem: "Material similar detectado. Verificar duplicata"
Responsável: MDO


REGRA C04: PREÇO OUTLIER EXTREMO
═══════════════════════════════════════════════════════════
Descrição: Preço > 5× mediana categoria
Validação:
  • preco > (mediana_categoria × 5)
Ação: CAMINHO 3 (MDO)
Mensagem: "Preço extremamente alto. Requer validação mercado"
Responsável: MDO + Comprador


REGRA C05: FORNECEDOR NOVO (SEM CADASTRO)
═══════════════════════════════════════════════════════════
Descrição: Fornecedor não existe no cadastro
Validação:
  • fornecedor NOT IN cadastro_fornecedores
Ação: CAMINHO 3 (MDO)
Mensagem: "Fornecedor novo. Requer due diligence"
Responsável: MDO + Comprador + Jurídico
```

---

═══════════════════════════════════════════════════════════════════════════════
## 5. SLAs POR CAMINHO DE APROVAÇÃO
═══════════════════════════════════════════════════════════════════════════════

```
╔══════════════════════════════════════════════════════════════════════╗
║                    ACORDO DE NÍVEL DE SERVIÇO (SLA)                  ║
╚══════════════════════════════════════════════════════════════════════╝

CAMINHO 1: AUTO-APROVAÇÃO (70-80% dos casos)
────────────────────────────────────────────────────────────────────
SLA: 3 segundos (real-time)
Horário: 24×7 (sistema automatizado)
Meta: > 95% processados em < 5 segundos
Responsável: Sistema
Penalidade: N/A (automatizado)


CAMINHO 2: SUPERVISOR (15-20% dos casos)
────────────────────────────────────────────────────────────────────
SLA: 4 horas (turno de trabalho)
Horário: 08:00-17:00 (dias úteis)
Meta: > 90% aprovados em < 4 horas
Responsável: Supervisor Almoxarifado/Compras
Penalidade: Escalonamento para MDO se > 4h
Urgente: < 2 horas (se material parado linha)


CAMINHO 3: MDO (5-10% dos casos)
────────────────────────────────────────────────────────────────────
SLA: 24 horas (1 dia útil)
Horário: 08:00-17:00 (dias úteis)
Meta: > 85% aprovados em < 24 horas
Responsável: Master Data Owner
Penalidade: Aprovação automática após 48h (casos não-críticos)
Urgente: < 8 horas (se impacto produção)


CAMINHO 0: REJEIÇÃO
────────────────────────────────────────────────────────────────────
SLA: Imediato (< 1 segundo)
Horário: 24×7
Meta: 100% feedback instantâneo
Responsável: Sistema
Ação: Retorna para correção com mensagem clara


MEDIÇÃO SLA:
────────────────────────────────────────────────────────────────────
• Timestamp cadastro inicial
• Timestamp cada etapa workflow
• Timestamp decisão final
• Cálculo: decisão_final - cadastro_inicial
• Report mensal: % dentro do SLA por caminho
• Meta global: 92% materiais aprovados em < 8h
```

---

═══════════════════════════════════════════════════════════════════════════════
## 6. PROCESSOS DE EXCEÇÃO
═══════════════════════════════════════════════════════════════════════════════

### **6.1 URGÊNCIA (PRODUÇÃO PARADA)**

```
CENÁRIO: Material urgente, produção parada aguardando
────────────────────────────────────────────────────────────

PROCESSO EXCEÇÃO:
1. Cadastrador marca material como "URGENTE - PRODUÇÃO PARADA"
2. Sistema notifica IMEDIATAMENTE:
   • Supervisor (SMS + Email)
   • MDO (se Caminho 3)
   • Gerente Operações
3. SLA reduzido:
   • Caminho 2: 2 horas (vs 4h normal)
   • Caminho 3: 8 horas (vs 24h normal)
4. Se não aprovado no SLA urgente:
   • Aprovação provisória automática (48h validade)
   • Revisão obrigatória posterior
   • Log de aprovação provisória

RESPONSÁVEL: Gerente Operações + MDO
AUTORIZAÇÃO: Gerente Operações (email/SMS)
AUDITORIA: Justificativa "produção parada" obrigatória
```

---

### **6.2 FORA DO HORÁRIO (EMERGÊNCIA)**

```
CENÁRIO: Cadastro necessário fora horário comercial
────────────────────────────────────────────────────────────

PROCESSO EXCEÇÃO:
1. Sistema permite cadastro 24×7
2. Validações bloqueantes sempre ativas
3. Fora do horário (17:00-08:00):
   • Caminho 1: Funciona normal (automático)
   • Caminho 2: Aguarda próximo turno (8h)
   • Caminho 3: Notifica MDO de plantão (se existe)
4. Plantão MDO (opcional):
   • Escala semanal alternada
   • Apenas casos críticos URGENTES
   • Adicional por plantão

RESPONSÁVEL: Plantão rotativo (opcional)
FREQUÊNCIA: Avaliar necessidade (histórico urgências)
```

---

### **6.3 OVERRIDE (SOBREPOSIÇÃO)**

```
CENÁRIO: Necessidade de sobrepor validação em caso excepcional
────────────────────────────────────────────────────────────

REGRAS OVERRIDE:
• Apenas MDO ou superior pode fazer override
• Apenas validações NÃO-bloqueantes
• NUNCA override de validações bloqueantes (B01-B06)
• Justificativa OBRIGATÓRIA (texto livre + anexo)
• Aprovação dupla (MDO + Gerente)
• Auditoria completa registrada
• Review trimestral de todos overrides

PROCESSO:
1. MDO solicita override com justificativa
2. Gerente aprova (email formal)
3. Sistema permite cadastro com flag "OVERRIDE"
4. Material marcado permanentemente
5. Auditoria trimestral revisa todos overrides
6. Métricas: % materiais com override (meta: < 0,5%)

EXEMPLO VÁLIDO:
Material importado urgente, NCM temporariamente genérico
aguardando classificação despachante. Override aprovado
com prazo 30 dias para regularização.

RESPONSÁVEL: MDO + Gerente
AUDITORIA: Compliance + Auditoria Interna
```

---

═══════════════════════════════════════════════════════════════════════════════
## 7. RESUMO EXECUTIVO GOVERNANÇA
═══════════════════════════════════════════════════════════════════════════════

```
╔══════════════════════════════════════════════════════════════════════╗
║           MODELO DE GOVERNANÇA MDM - RESUMO EXECUTIVO               ║
╚══════════════════════════════════════════════════════════════════════╝

PRINCÍPIOS:
──────────────────────────────────────────────────────────────────
✅ Dados como ativo estratégico
✅ Qualidade na origem (não correção posterior)
✅ Governança por exceção (maioria automática)
✅ Rastreabilidade 100%

WORKFLOW 3 NÍVEIS:
──────────────────────────────────────────────────────────────────
Caminho 1: Auto-Aprovação     70-80%  (SLA: 3 seg)
Caminho 2: Supervisor          15-20%  (SLA: 4 horas)
Caminho 3: MDO                 5-10%   (SLA: 24 horas)
Rejeitados: Bloqueantes        1-2%    (SLA: imediato)

VALIDAÇÕES:
──────────────────────────────────────────────────────────────────
Bloqueantes:    6 regras (B01-B06)
Alertas:        4 regras (A01-A04)
Críticas MDO:   5 regras (C01-C05)
Total:          15 regras formalizadas

MATRIZ RACI:
──────────────────────────────────────────────────────────────────
Definida para 10 processos principais
7 papéis mapeados (Cadastrador → CFO)
Clareza total de responsabilidades

EXCEÇÕES:
──────────────────────────────────────────────────────────────────
Urgência:       SLA reduzido 50%
Fora horário:   Caminho 1 funciona 24×7
Override:       Apenas MDO+Gerente, auditado

DIMENSÕES QUALIDADE (DAMA):
──────────────────────────────────────────────────────────────────
Acuracidade:    > 98%  (inventário mensal)
Completude:     > 95%  (real-time)
Consistência:   > 90%  (batch noturno)
Validade:       100%   (bloqueante)
Unicidade:      0% dup (detecção semanal)
Atualidade:     > 85%  (revisão trimestral)

EFICIÊNCIA:
──────────────────────────────────────────────────────────────────
SLA Médio:      ~5 horas (vs 48h manual)
Throughput:     200 materiais/dia (vs 20 manual)
Auto-aprovação: 73%+ (meta: 75%)
Rejeição:       < 2% (qualidade origem)

ROI GOVERNANÇA:
──────────────────────────────────────────────────────────────────
Custo anual:    R$ 180.000 (FTE MDO + sistema)
Economia:       R$ 43.340.869 (dados qualidade)
ROI:            24.000%
Payback:        < 3 dias

╔══════════════════════════════════════════════════════════════════════╗
║  MODELO IMPLEMENTADO: APROVADO PARA PRODUÇÃO                        ║
║  BASE: Projeto MDM (Dias 18-19) + Formalização (Dia 22)            ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

═══════════════════════════════════════════════════════════════════════════════
FIM DO DOCUMENTO - DIA 22
═══════════════════════════════════════════════════════════════════════════════

**PRÓXIMO:** Dia 23 - SLAs e Métricas de Processo (KPIs Detalhados)

**PROGRESSO:** 44,9% (22 de 49 dias)
**SEMANA 4:** 14,3% (1 de 7 dias)
**ECONOMIA SEMANA 4:** R$ 0 (governança = prevenção)
**TEMPO INVESTIDO DIA 22:** ~2 horas documentação

✅ **DIA 22 COMPLETO!**
