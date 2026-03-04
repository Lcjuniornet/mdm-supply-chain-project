# 📊 DIA 23 — SLAs E MÉTRICAS DE PROCESSO
## Projeto MDM Supply Chain · Semana 4

═══════════════════════════════════════════════════════════════════════════════
📅 DATA: 12/Março/2026 (Terça-feira)
🎯 FOCO: KPIs Detalhados e Dashboard Monitoramento Governança
📊 PROGRESSO: 46,9% (23 de 49 dias)
⏱️ TEMPO ESTIMADO: 2 horas
═══════════════════════════════════════════════════════════════════════════════

## 🎯 OBJETIVO DO DIA

```
TRANSFORMAR POLÍTICAS (DIA 22) EM MÉTRICAS ACIONÁVEIS:
═══════════════════════════════════════════════════════════

1. KPIs por Dimensão de Qualidade (6 dimensões DAMA)
2. Métricas de Performance Workflow (3 caminhos)
3. Thresholds de Alertas Automáticos
4. Dashboard de Monitoramento (visualização)
5. Relatórios Automáticos (frequência e destinatários)
6. Scorecard Executivo MDM
```

---

═══════════════════════════════════════════════════════════════════════════════
## 1. KPIs POR DIMENSÃO DE QUALIDADE
═══════════════════════════════════════════════════════════════════════════════

### **1.1 ACURACIDADE (ACCURACY)**

```
DEFINIÇÃO: Dados refletem a realidade física corretamente

╔══════════════════════════════════════════════════════════════════════╗
║ KPI 1.1: ACURACIDADE DE PREÇOS                                      ║
╚══════════════════════════════════════════════════════════════════════╝

Fórmula:
────────────────────────────────────────────────────────────────────
  (Materiais com preço_sistema ≈ preço_físico ±2%) 
  ───────────────────────────────────────────────── × 100
              Total de materiais auditados

Meta: > 98%
Threshold Alerta: < 95% (amarelo) | < 90% (vermelho)
Frequência: Inventário mensal
Responsável: Supervisor Almoxarifado
Fonte Dados: Inventário físico vs sistema ERP

Exemplo Cálculo:
────────────────────────────────────────────────────────────────────
Auditados: 500 materiais inventário março
Acurados: 492 (diferença < 2%)
KPI = 492/500 × 100 = 98,4% ✅ (acima meta 98%)


╔══════════════════════════════════════════════════════════════════════╗
║ KPI 1.2: SHRINKAGE (PERDA DE ESTOQUE)                               ║
╚══════════════════════════════════════════════════════════════════════╝

Fórmula:
────────────────────────────────────────────────────────────────────
  (Estoque_sistema - Estoque_físico)
  ─────────────────────────────────── × 100
          Estoque_sistema

Meta: < 1% (perda aceitável)
Threshold Alerta: > 1,5% (amarelo) | > 2% (vermelho)
Frequência: Inventário mensal
Responsável: Gerente Almoxarifado
Fonte Dados: Inventário completo

Exemplo Cálculo:
────────────────────────────────────────────────────────────────────
Estoque sistema: R$ 1.833.000.000
Estoque físico:  R$ 1.816.700.000
Diferença:       R$    16.300.000
Shrinkage = 16.300.000 / 1.833.000.000 × 100 = 0,89% ✅


╔══════════════════════════════════════════════════════════════════════╗
║ KPI 1.3: NCMs VALIDADOS                                             ║
╚══════════════════════════════════════════════════════════════════════╝

Fórmula:
────────────────────────────────────────────────────────────────────
  Materiais com NCM validado API Receita Federal
  ────────────────────────────────────────────── × 100
            Total de materiais cadastrados

Meta: 100% (crítico fiscal)
Threshold Alerta: < 100% (vermelho sempre - risco fiscal!)
Frequência: Real-time (validação cadastro) + auditoria mensal
Responsável: MDO + Fiscal
Fonte Dados: API Receita Federal + ERP

Exemplo Cálculo:
────────────────────────────────────────────────────────────────────
Total materiais: 3.300
NCM válido: 2.677 (81,1%)
NCM genérico: 623 (18,9%) ⚠️ CRÍTICO!
KPI = 2.677/3.300 × 100 = 81,1% ❌ (meta: 100%)

AÇÃO: Validar 623 materiais urgente (risco R$ 5-10M)
```

---

### **1.2 COMPLETUDE (COMPLETENESS)**

```
DEFINIÇÃO: Campos obrigatórios estão preenchidos

╔══════════════════════════════════════════════════════════════════════╗
║ KPI 2.1: SCORE COMPLETUDE PONDERADO                                 ║
╚══════════════════════════════════════════════════════════════════════╝

Fórmula:
────────────────────────────────────────────────────────────────────
Score = Σ (campo_preenchido × peso_campo) / Σ (pesos_totais)

Pesos por Criticidade:
  NCM:                 30 pontos (crítico fiscal)
  Fornecedor:          20 pontos (gestão supply chain)
  Estoque Mínimo:      15 pontos (planejamento)
  Lead Time:           10 pontos (operacional)
  Categoria_2:          5 pontos (opcional)

Meta: > 95%
Threshold Alerta: < 90% (amarelo) | < 85% (vermelho)
Frequência: Real-time (dashboard)
Responsável: Supervisor + Cadastrador
Fonte Dados: ERP queries

Exemplo Cálculo Material:
────────────────────────────────────────────────────────────────────
Material: MAT-1234
NCM: ✅ preenchido (30 pts)
Fornecedor: ✅ preenchido (20 pts)
Estoque Mínimo: ❌ vazio (0 pts)
Lead Time: ✅ preenchido (10 pts)
Categoria_2: ❌ vazio (0 pts)

Score = (30+20+10) / (30+20+15+10+5) = 60/80 = 75% ⚠️


╔══════════════════════════════════════════════════════════════════════╗
║ KPI 2.2: CAMPOS CRÍTICOS COMPLETOS                                  ║
╚══════════════════════════════════════════════════════════════════════╝

Fórmula:
────────────────────────────────────────────────────────────────────
  Materiais com TODOS campos críticos preenchidos
  ─────────────────────────────────────────────── × 100
              Total de materiais

Campos Críticos: NCM, Fornecedor, Estoque_Mínimo (3 campos)

Meta: > 90%
Threshold Alerta: < 85% (amarelo) | < 80% (vermelho)
Frequência: Semanal
Responsável: Supervisor
Fonte Dados: ERP query COUNT()

Exemplo:
────────────────────────────────────────────────────────────────────
Total: 3.300 materiais
Completos: 2.970 (90%)
KPI = 90% ✅ (na meta)
```

---

### **1.3 CONSISTÊNCIA (CONSISTENCY)**

```
DEFINIÇÃO: Dados uniformes e padronizados

╔══════════════════════════════════════════════════════════════════════╗
║ KPI 3.1: PADRONIZAÇÃO TEXTOS                                        ║
╚══════════════════════════════════════════════════════════════════════╝

Fórmula:
────────────────────────────────────────────────────────────────────
  Materiais com textos em Title Case (padrão)
  ──────────────────────────────────────────── × 100
          Total de materiais

Meta: > 90%
Threshold Alerta: < 85% (amarelo) | < 80% (vermelho)
Frequência: Batch noturno (correção automática)
Responsável: Sistema automatizado
Fonte Dados: Script padronização

Exemplo:
────────────────────────────────────────────────────────────────────
Total: 3.300
Padronizados: 3.019 (91,5%)
Inconsistentes: 281 (8,5%)
KPI = 91,5% ✅


╔══════════════════════════════════════════════════════════════════════╗
║ KPI 3.2: UNIDADES MEDIDA PADRONIZADAS                               ║
╚══════════════════════════════════════════════════════════════════════╝

Fórmula:
────────────────────────────────────────────────────────────────────
  Materiais com unidade no padrão (lista aprovada)
  ───────────────────────────────────────────────── × 100
              Total de materiais

Lista Aprovada: UN, KG, LT, M, M2, M3, PC, CX (20 unidades)

Meta: 100% (bloqueante cadastro)
Threshold Alerta: < 100% (vermelho - investigar)
Frequência: Real-time + auditoria semanal
Responsável: Sistema + MDO
Fonte Dados: Validação cadastro

KPI = 100% sempre (validação bloqueante) ✅
```

---

### **1.4 VALIDADE (VALIDITY)**

```
DEFINIÇÃO: Dados atendem regras de negócio

╔══════════════════════════════════════════════════════════════════════╗
║ KPI 4.1: VALIDAÇÕES BLOQUEANTES ATENDIDAS                           ║
╚══════════════════════════════════════════════════════════════════════╝

Fórmula:
────────────────────────────────────────────────────────────────────
  Tentativas cadastro aprovadas (passaram validações)
  ─────────────────────────────────────────────────────── × 100
            Total tentativas cadastro

Meta: > 95% (qualidade origem)
Threshold Alerta: < 90% (amarelo - treinamento)
Frequência: Diária (relatório)
Responsável: Supervisor + Treinamento
Fonte Dados: Logs sistema

Exemplo:
────────────────────────────────────────────────────────────────────
Tentativas: 120 materiais (semana)
Aprovados: 115 (95,8%)
Rejeitados: 5 (4,2% - erros cadastrador)
KPI = 95,8% ✅


╔══════════════════════════════════════════════════════════════════════╗
║ KPI 4.2: FORNECEDORES ATIVOS                                        ║
╚══════════════════════════════════════════════════════════════════════╝

Fórmula:
────────────────────────────────────────────────────────────────────
  Materiais com fornecedor status "Ativo"
  ─────────────────────────────────────────── × 100
    Materiais com fornecedor informado

Meta: 100% (validação bloqueante)
Threshold Alerta: < 100% (vermelho - dados corrompidos)
Frequência: Semanal (auditoria)
Responsável: Comprador
Fonte Dados: ERP query com JOIN

KPI = 100% sempre (validação bloqueante) ✅
```

---

### **1.5 UNICIDADE (UNIQUENESS)**

```
DEFINIÇÃO: Sem duplicatas no cadastro

╔══════════════════════════════════════════════════════════════════════╗
║ KPI 5.1: TAXA DUPLICATAS                                            ║
╚══════════════════════════════════════════════════════════════════════╝

Fórmula:
────────────────────────────────────────────────────────────────────
  Materiais com similaridade > 85% (potencial duplicata)
  ────────────────────────────────────────────────────────── × 100
                  Total de materiais

Método: Fuzzy matching (Levenshtein distance)

Meta: 0% duplicatas
Threshold Alerta: > 0,5% (amarelo) | > 1% (vermelho)
Frequência: Semanal (detecção automática)
Responsável: MDO
Fonte Dados: Script análise duplicatas

Exemplo:
────────────────────────────────────────────────────────────────────
Total: 3.300
Duplicatas detectadas: 12 (0,36%)
KPI = 0,36% ✅ (abaixo threshold 0,5%)

AÇÃO: MDO analisa 12 casos (aprovar consolidação ou não)


╔══════════════════════════════════════════════════════════════════════╗
║ KPI 5.2: CÓDIGOS ÚNICOS                                             ║
╚══════════════════════════════════════════════════════════════════════╝

Fórmula:
────────────────────────────────────────────────────────────────────
  COUNT(DISTINCT codigo_material) = COUNT(codigo_material)

Meta: 100% únicos (constraint database)
Threshold Alerta: < 100% (vermelho crítico - falha sistema)
Frequência: Real-time (constraint) + auditoria mensal
Responsável: TI
Fonte Dados: Database constraint

KPI = 100% sempre (constraint database) ✅
```

---

### **1.6 ATUALIDADE (TIMELINESS)**

```
DEFINIÇÃO: Dados refletem estado atual

╔══════════════════════════════════════════════════════════════════════╗
║ KPI 6.1: MOVIMENTAÇÃO RECENTE                                       ║
╚══════════════════════════════════════════════════════════════════════╝

Fórmula:
────────────────────────────────────────────────────────────────────
  Materiais com movimentação < 365 dias
  ──────────────────────────────────────── × 100
          Total de materiais ativos

Meta: > 85%
Threshold Alerta: < 80% (amarelo) | < 75% (vermelho)
Frequência: Mensal
Responsável: Almoxarife + Comprador
Fonte Dados: Última movimentação ERP

Exemplo:
────────────────────────────────────────────────────────────────────
Ativos: 3.150 materiais (status "Ativo")
Movimentados < 365d: 2.740 (87%)
Parados > 365d: 410 (13%)
KPI = 87% ✅

AÇÃO: Revisar 410 materiais (inativar ou manter)


╔══════════════════════════════════════════════════════════════════════╗
║ KPI 6.2: PREÇOS ATUALIZADOS                                         ║
╚══════════════════════════════════════════════════════════════════════╝

Fórmula:
────────────────────────────────────────────────────────────────────
  Materiais com preço atualizado < 90 dias
  ────────────────────────────────────────── × 100
          Total de materiais

Meta: > 80%
Threshold Alerta: < 70% (amarelo) | < 60% (vermelho)
Frequência: Mensal
Responsável: Comprador
Fonte Dados: Campo data_ultima_alteracao_preco

Exemplo:
────────────────────────────────────────────────────────────────────
Total: 3.300
Atualizados < 90d: 2.640 (80%)
Desatualizados: 660 (20%)
KPI = 80% ✅ (na meta)
```

---

═══════════════════════════════════════════════════════════════════════════════
## 2. MÉTRICAS DE PERFORMANCE WORKFLOW
═══════════════════════════════════════════════════════════════════════════════

### **2.1 DISTRIBUIÇÃO POR CAMINHO**

```
╔══════════════════════════════════════════════════════════════════════╗
║ KPI W1: TAXA AUTO-APROVAÇÃO (CAMINHO 1)                             ║
╚══════════════════════════════════════════════════════════════════════╝

Fórmula:
────────────────────────────────────────────────────────────────────
  Materiais aprovados via Caminho 1 (auto)
  ──────────────────────────────────────── × 100
      Total materiais cadastrados (aprovados)

Meta: 70-80% (eficiência)
Threshold Alerta: < 65% (amarelo - revisar validações)
Frequência: Semanal
Responsável: MDO
Fonte Dados: Logs workflow

Exemplo:
────────────────────────────────────────────────────────────────────
Total aprovados semana: 100 materiais
Caminho 1: 73 (73%)
Caminho 2: 22 (22%)
Caminho 3: 5 (5%)

KPI = 73% ✅ (dentro meta 70-80%)

INTERPRETAÇÃO:
✅ 73% eficiência excelente (maioria automática)
✅ Apenas 27% requer intervenção humana


╔══════════════════════════════════════════════════════════════════════╗
║ KPI W2: TAXA REJEIÇÃO                                               ║
╚══════════════════════════════════════════════════════════════════════╝

Fórmula:
────────────────────────────────────────────────────────────────────
  Tentativas rejeitadas (validações bloqueantes)
  ────────────────────────────────────────────── × 100
          Total tentativas cadastro

Meta: < 5% (qualidade origem)
Threshold Alerta: > 10% (amarelo - treinamento urgente)
Frequência: Diária
Responsável: Supervisor + Treinamento
Fonte Dados: Logs rejeição

Exemplo:
────────────────────────────────────────────────────────────────────
Tentativas: 105 materiais
Rejeitados: 5 (4,8%)
Aprovados: 100 (95,2%)

KPI = 4,8% ✅ (abaixo meta 5%)

Motivos rejeição (analisar para treinamento):
• NCM inválido: 2 casos
• Preço zerado: 2 casos
• Descrição curta: 1 caso
```

---

### **2.2 PERFORMANCE SLA**

```
╔══════════════════════════════════════════════════════════════════════╗
║ KPI W3: ADERÊNCIA SLA CAMINHO 1                                     ║
╚══════════════════════════════════════════════════════════════════════╝

Fórmula:
────────────────────────────────────────────────────────────────────
  Materiais Caminho 1 processados em < 5 segundos
  ──────────────────────────────────────────────── × 100
        Total materiais Caminho 1

SLA: 3 segundos (meta: 95% em < 5s)
Threshold Alerta: < 90% (amarelo - performance sistema)
Frequência: Diária (automático)
Responsável: TI
Fonte Dados: Logs timestamp

Exemplo:
────────────────────────────────────────────────────────────────────
Caminho 1 semana: 73 materiais
Processados < 5s: 72 (98,6%)
Processados > 5s: 1 (1,4% - spike performance)

KPI = 98,6% ✅ (acima meta 95%)


╔══════════════════════════════════════════════════════════════════════╗
║ KPI W4: ADERÊNCIA SLA CAMINHO 2                                     ║
╚══════════════════════════════════════════════════════════════════════╝

Fórmula:
────────────────────────────────────────────────────────────────────
  Materiais Caminho 2 decididos em < 4 horas
  ──────────────────────────────────────────── × 100
        Total materiais Caminho 2

SLA: 4 horas (meta: 90% em < 4h)
Threshold Alerta: < 80% (amarelo) | < 70% (vermelho)
Frequência: Semanal
Responsável: Supervisor
Fonte Dados: Logs workflow

Exemplo:
────────────────────────────────────────────────────────────────────
Caminho 2 semana: 22 materiais
Decididos < 4h: 20 (90,9%)
Decididos > 4h: 2 (9,1%)

KPI = 90,9% ✅ (acima meta 90%)

AÇÃO: Revisar 2 casos > 4h (motivo atraso)


╔══════════════════════════════════════════════════════════════════════╗
║ KPI W5: ADERÊNCIA SLA CAMINHO 3                                     ║
╚══════════════════════════════════════════════════════════════════════╝

Fórmula:
────────────────────────────────────────────────────────────────────
  Materiais Caminho 3 decididos em < 24 horas
  ───────────────────────────────────────────── × 100
        Total materiais Caminho 3

SLA: 24 horas (meta: 85% em < 24h)
Threshold Alerta: < 75% (amarelo) | < 65% (vermelho)
Frequência: Semanal
Responsável: MDO
Fonte Dados: Logs workflow

Exemplo:
────────────────────────────────────────────────────────────────────
Caminho 3 semana: 5 materiais
Decididos < 24h: 4 (80%)
Decididos > 24h: 1 (20% - CAPEX CFO atrasou)

KPI = 80% ⚠️ (abaixo meta 85%)

AÇÃO: 1 caso atrasou por aprovação CFO (documentar)


╔══════════════════════════════════════════════════════════════════════╗
║ KPI W6: SLA MÉDIO PONDERADO                                         ║
╚══════════════════════════════════════════════════════════════════════╝

Fórmula:
────────────────────────────────────────────────────────────────────
  Σ (tempo_decisão × quantidade_materiais) / Total_materiais

Meta: < 8 horas (global)
Threshold Alerta: > 12h (amarelo) | > 16h (vermelho)
Frequência: Semanal
Responsável: MDO
Fonte Dados: Logs completos

Exemplo:
────────────────────────────────────────────────────────────────────
Caminho 1: 73 mat × 0,001h = 0,073h
Caminho 2: 22 mat × 3,5h = 77h
Caminho 3: 5 mat × 18h = 90h
Total: 100 materiais, 167,073h

SLA Médio = 167,073 / 100 = 1,67 horas ✅

EXCELENTE! Muito abaixo meta 8h
(maioria auto-aprovada puxa média para baixo)
```

---

═══════════════════════════════════════════════════════════════════════════════
## 3. THRESHOLDS DE ALERTAS AUTOMÁTICOS
═══════════════════════════════════════════════════════════════════════════════

```
SISTEMA DE ALERTAS EM 3 NÍVEIS:
═══════════════════════════════════════════════════════════

🟢 VERDE (Normal): KPI dentro da meta
   Ação: Nenhuma (monitorar)

🟡 AMARELO (Atenção): KPI abaixo meta mas acima crítico
   Ação: Alerta Supervisor/MDO (email diário)
   
🔴 VERMELHO (Crítico): KPI abaixo limite crítico
   Ação: Alerta URGENTE Gerência (email + SMS imediato)


╔══════════════════════════════════════════════════════════════════════╗
║ TABELA DE THRESHOLDS POR KPI                                        ║
╚══════════════════════════════════════════════════════════════════════╝

KPI                        │ VERDE  │ AMARELO │ VERMELHO │ Responsável
─────────────────────────────┼────────┼─────────┼──────────┼─────────────
ACURACIDADE:                │        │         │          │
Preços (1.1)               │ ≥ 98%  │ 95-98%  │ < 95%    │ Supervisor
Shrinkage (1.2)            │ ≤ 1%   │ 1-1,5%  │ > 1,5%   │ Gerente
NCMs Validados (1.3)       │ 100%   │ -       │ < 100%   │ MDO+Fiscal
                           │        │         │          │
COMPLETUDE:                │        │         │          │
Score Ponderado (2.1)      │ ≥ 95%  │ 90-95%  │ < 90%    │ Supervisor
Campos Críticos (2.2)      │ ≥ 90%  │ 85-90%  │ < 85%    │ Supervisor
                           │        │         │          │
CONSISTÊNCIA:              │        │         │          │
Padronização Textos (3.1)  │ ≥ 90%  │ 85-90%  │ < 85%    │ Sistema
Unidades Medida (3.2)      │ 100%   │ -       │ < 100%   │ MDO
                           │        │         │          │
VALIDADE:                  │        │         │          │
Validações Bloq (4.1)      │ ≥ 95%  │ 90-95%  │ < 90%    │ Treinamento
Fornecedores Ativos (4.2)  │ 100%   │ -       │ < 100%   │ Comprador
                           │        │         │          │
UNICIDADE:                 │        │         │          │
Taxa Duplicatas (5.1)      │ ≤ 0,5% │ 0,5-1%  │ > 1%     │ MDO
Códigos Únicos (5.2)       │ 100%   │ -       │ < 100%   │ TI
                           │        │         │          │
ATUALIDADE:                │        │         │          │
Movimentação Recente (6.1) │ ≥ 85%  │ 80-85%  │ < 80%    │ Almoxarife
Preços Atualizados (6.2)   │ ≥ 80%  │ 70-80%  │ < 70%    │ Comprador
                           │        │         │          │
WORKFLOW:                  │        │         │          │
Auto-Aprovação (W1)        │ 70-80% │ 65-70%  │ < 65%    │ MDO
Taxa Rejeição (W2)         │ ≤ 5%   │ 5-10%   │ > 10%    │ Treinamento
SLA Caminho 1 (W3)         │ ≥ 95%  │ 90-95%  │ < 90%    │ TI
SLA Caminho 2 (W4)         │ ≥ 90%  │ 80-90%  │ < 80%    │ Supervisor
SLA Caminho 3 (W5)         │ ≥ 85%  │ 75-85%  │ < 75%    │ MDO
SLA Médio Ponderado (W6)   │ ≤ 8h   │ 8-12h   │ > 12h    │ MDO
─────────────────────────────┴────────┴─────────┴──────────┴─────────────


EXEMPLOS ALERTAS AUTOMÁTICOS:
═══════════════════════════════════════════════════════════

🟡 AMARELO - Email Supervisor (diário 8h):
────────────────────────────────────────────────────────────────────
Assunto: [ATENÇÃO] Score Completude em 92% (meta: > 95%)

Olá Supervisor,

O Score de Completude está em 92%, abaixo da meta de 95%.

Campos mais vazios:
• Estoque Mínimo: 280 materiais sem preenchimento
• Lead Time: 150 materiais sem preenchimento

Ação recomendada: Priorizar preenchimento campos críticos.

Dashboard: http://bi.empresa.com/mdm/completude


🔴 VERMELHO - Email + SMS Gerência (imediato):
────────────────────────────────────────────────────────────────────
Assunto: [CRÍTICO] Shrinkage em 1,8% (meta: < 1%)

ALERTA CRÍTICO!

Shrinkage subiu para 1,8%, acima do limite 1,5%.

Perda estimada: R$ 32M (inventário março)

Categorias mais afetadas:
• Eletrônico: 2,5% shrinkage
• Ferramentas: 2,1% shrinkage

AÇÃO URGENTE: Auditoria inventário + revisão controles.

Dashboard: http://bi.empresa.com/mdm/shrinkage
```

---

═══════════════════════════════════════════════════════════════════════════════
## 4. DASHBOARD DE MONITORAMENTO
═══════════════════════════════════════════════════════════════════════════════

### **4.1 DASHBOARD EXECUTIVO MDM**

```
╔══════════════════════════════════════════════════════════════════════╗
║                 DASHBOARD MDM - VISÃO EXECUTIVA                      ║
╚══════════════════════════════════════════════════════════════════════╝

LAYOUT (4 SEÇÕES):
─────────────────────────────────────────────────────────────────────

┌─────────────────────────────────────────────────────────────────┐
│ SEÇÃO 1: SCORECARD GERAL (TOPO)                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  QUALIDADE GERAL        WORKFLOW EFICIÊNCIA     SLA MÉDIO      │
│  ┌────────────┐         ┌────────────┐          ┌───────────┐ │
│  │    94%     │         │    73%     │          │   5,2h    │ │
│  │   🟢 OK    │         │   🟢 OK    │          │  🟢 OK    │ │
│  └────────────┘         └────────────┘          └───────────┘ │
│                                                                 │
│  Meta: > 90%            Meta: 70-80%             Meta: < 8h    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ SEÇÃO 2: 6 DIMENSÕES QUALIDADE (CENTRO ESQUERDA)               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Acuracidade      [████████████████████] 98,4% 🟢              │
│  Completude       [████████████████▒▒▒▒] 92,0% 🟡              │
│  Consistência     [████████████████████] 91,5% 🟢              │
│  Validade         [████████████████████] 100%  🟢              │
│  Unicidade        [████████████████████] 99,6% 🟢              │
│  Atualidade       [████████████████████] 87,0% 🟢              │
│                                                                 │
│  SCORE GERAL: 94,75% 🟢                                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ SEÇÃO 3: WORKFLOW PERFORMANCE (CENTRO DIREITA)                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  DISTRIBUIÇÃO CAMINHOS (Semana):                               │
│  ┌─────────────────────────────────────┐                       │
│  │ Caminho 1: ████████████████ 73%    │ (73 materiais)        │
│  │ Caminho 2: █████░░ 22%             │ (22 materiais)        │
│  │ Caminho 3: ██░ 5%                  │ (5 materiais)         │
│  └─────────────────────────────────────┘                       │
│                                                                 │
│  SLA ADERÊNCIA:                                                 │
│  Caminho 1 (< 5s):   98,6% 🟢 (72/73)                          │
│  Caminho 2 (< 4h):   90,9% 🟢 (20/22)                          │
│  Caminho 3 (< 24h):  80,0% 🟡 (4/5)                            │
│                                                                 │
│  REJEIÇÕES: 4,8% 🟢 (5/105 tentativas)                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ SEÇÃO 4: ALERTAS E AÇÕES (FUNDO)                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🟡 ALERTAS ATIVOS:                                            │
│  • Completude 92% (meta: 95%) - 280 mat. sem estoque_mínimo  │
│  • SLA Caminho 3: 80% (meta: 85%) - 1 caso atrasou (CAPEX)   │
│                                                                 │
│  ✅ AÇÕES RECOMENDADAS:                                        │
│  1. Priorizar preenchimento estoque_mínimo (280 materiais)    │
│  2. Revisar caso Caminho 3 atrasado (aprovação CFO)           │
│                                                                 │
│  📊 TENDÊNCIAS (vs semana anterior):                           │
│  • Qualidade Geral: 94,75% (+1,2%) ⬆️                         │
│  • SLA Médio: 5,2h (-0,8h) ⬆️                                 │
│  • Taxa Rejeição: 4,8% (-2,1%) ⬆️                             │
└─────────────────────────────────────────────────────────────────┘

ATUALIZAÇÃO: Real-time (métricas) + Diário 8h (cálculos batch)
ACESSO: Gerência, MDO, Supervisores
URL: http://bi.empresa.com/mdm/dashboard
```

---

### **4.2 DASHBOARD OPERACIONAL (DETALHADO)**

```
Para Supervisores e MDO - Mais Granular

INCLUI:
────────────────────────────────────────────────────────────────────
• Drill-down por categoria (15 categorias)
• Materiais específicos fora do padrão (lista)
• Histórico temporal (últimos 6 meses)
• Comparativo mês a mês
• Top 10 materiais mais problemáticos
• Logs workflow detalhados (últimas 100 decisões)

FREQUÊNCIA: Real-time
ACESSO: MDO, Supervisores, Cadastradores
```

---

═══════════════════════════════════════════════════════════════════════════════
## 5. RELATÓRIOS AUTOMÁTICOS
═══════════════════════════════════════════════════════════════════════════════

```
╔══════════════════════════════════════════════════════════════════════╗
║ RELATÓRIO 1: DIÁRIO (OPERACIONAL)                                   ║
╚══════════════════════════════════════════════════════════════════════╝

Destinatários: Supervisor, MDO
Horário: 08:00 (início turno)
Formato: Email + PDF anexo

Conteúdo:
────────────────────────────────────────────────────────────────────
1. Resumo dia anterior:
   • Materiais cadastrados: N
   • Distribuição caminhos (%, quantidade)
   • Taxa rejeição: X%
   • SLA médio: X,X horas

2. Alertas ativos (se houver):
   • Lista KPIs abaixo meta (amarelo/vermelho)
   • Ações recomendadas

3. Casos pendentes:
   • Caminho 2 aguardando decisão: N materiais
   • Caminho 3 aguardando decisão: N materiais
   • Tempo médio espera

4. Top 5 materiais rejeitados ontem:
   • Código, motivo rejeição, cadastrador

Ação: Supervisor revisa e age sobre alertas/pendências


╔══════════════════════════════════════════════════════════════════════╗
║ RELATÓRIO 2: SEMANAL (TÁTICO)                                       ║
╚══════════════════════════════════════════════════════════════════════╝

Destinatários: MDO, Gerente Almoxarifado, Gerente Compras
Horário: Segunda-feira 08:00
Formato: Email + Dashboard interativo

Conteúdo:
────────────────────────────────────────────────────────────────────
1. Scorecard 6 Dimensões Qualidade:
   • Score cada dimensão (%) + status (verde/amarelo/vermelho)
   • Evolução vs semana anterior
   • Gráfico tendência (últimas 8 semanas)

2. Performance Workflow:
   • Distribuição caminhos (%) + comparativo
   • Aderência SLA por caminho
   • Taxa rejeição + motivos principais
   • Throughput: N materiais/dia

3. Destaques positivos:
   • KPIs que melhoraram
   • Eficiências identificadas

4. Alertas e Ações:
   • KPIs abaixo meta (detalhamento)
   • Plano ação recomendado
   • Responsáveis atribuídos

5. Duplicatas detectadas:
   • N materiais potencialmente duplicados
   • Lista para revisão MDO

Ação: MDO revisa semanal, ajusta processos se necessário


╔══════════════════════════════════════════════════════════════════════╗
║ RELATÓRIO 3: MENSAL (ESTRATÉGICO)                                   ║
╚══════════════════════════════════════════════════════════════════════╝

Destinatários: Gerência, CFO, MDO
Horário: Primeiro dia útil do mês 08:00
Formato: PowerPoint executivo (15 slides)

Conteúdo:
────────────────────────────────────────────────────────────────────
Slide 1: Capa + Executive Summary
Slide 2: Scorecard Geral (score único 94%)
Slide 3-8: Detalhe 6 Dimensões Qualidade (1 slide cada)
Slide 9: Performance Workflow + ROI
Slide 10: Aderência SLA + Tendência
Slide 11: Economia Gerada (qualidade dados)
Slide 12: Top 10 Materiais Problemáticos
Slide 13: Melhorias Implementadas
Slide 14: Plano Ação Próximo Mês
Slide 15: Conclusões + Recomendações

Anexos:
• Dashboard completo (PDF)
• Dados brutos (Excel)
• Logs críticos (se houver incidentes)

Ação: Apresentação mensal Gerência (reunião 30 min)


╔══════════════════════════════════════════════════════════════════════╗
║ RELATÓRIO 4: TRIMESTRAL (AUDITORIA)                                 ║
╚══════════════════════════════════════════════════════════════════════╝

Destinatários: Auditoria Interna, Compliance, CFO, MDO
Horário: Final de cada trimestre
Formato: Relatório formal (20-30 páginas)

Conteúdo:
────────────────────────────────────────────────────────────────────
1. Qualidade Dados (análise profunda):
   • Histórico 3 meses (todas métricas)
   • Comparativo vs trimestre anterior
   • Análise causa raiz desvios

2. Governança:
   • Aderência políticas (%)
   • Overrides realizados (detalhamento completo)
   • Exceções aprovadas (justificativas)
   • Incidentes de dados (se houver)

3. Performance:
   • ROI governança dados (economia vs custo)
   • Throughput vs manual (10× faster)
   • Eficiência workflow (%)

4. Compliance:
   • NCMs validados (%) - risco fiscal
   • Fornecedores due diligence (%)
   • Materiais Classe A auditados (%)

5. Auditoria Amostragem:
   • 100 materiais aleatórios auditados
   • Validação vs políticas
   • Não-conformidades encontradas

6. Recomendações:
   • Melhorias processo
   • Ajustes políticas
   • Investimentos TI

Ação: Auditoria valida governança, emite parecer
```

---

═══════════════════════════════════════════════════════════════════════════════
## 6. SCORECARD EXECUTIVO MDM
═══════════════════════════════════════════════════════════════════════════════

```
╔══════════════════════════════════════════════════════════════════════╗
║              SCORECARD MDM - MODELO DE PONTUAÇÃO                     ║
╚══════════════════════════════════════════════════════════════════════╝

SCORE GERAL = MÉDIA PONDERADA 6 DIMENSÕES
────────────────────────────────────────────────────────────────────

Acuracidade:    30 pontos × Score% = 30 × 0,984 = 29,52 pts
Completude:     25 pontos × Score% = 25 × 0,920 = 23,00 pts
Consistência:   15 pontos × Score% = 15 × 0,915 = 13,73 pts
Validade:       10 pontos × Score% = 10 × 1,000 = 10,00 pts
Unicidade:      10 pontos × Score% = 10 × 0,996 = 9,96 pts
Atualidade:     10 pontos × Score% = 10 × 0,870 = 8,70 pts
                                            ─────────────────
                                            TOTAL: 94,91 pts

SCORE FINAL: 94,91 / 100 = 94,91% 🟢


INTERPRETAÇÃO SCORES:
────────────────────────────────────────────────────────────────────
95-100%: 🟢 EXCELENTE (Governança madura, dados confiáveis)
90-94%:  🟢 BOM (Governança estabelecida, melhorias contínuas)
85-89%:  🟡 ADEQUADO (Governança funcional, atenção pontos)
80-84%:  🟡 ATENÇÃO (Governança frágil, ação necessária)
< 80%:   🔴 CRÍTICO (Governança falha, intervenção urgente)


EXEMPLO SCORECARD MENSAL:
────────────────────────────────────────────────────────────────────
MÊS: Março 2026
SCORE GERAL: 94,91% 🟢 BOM

Dimensão          │ Score │ Status │ Tendência │ Meta
──────────────────┼───────┼────────┼───────────┼──────
Acuracidade       │ 98,4% │  🟢    │    ⬆️     │ > 98%
Completude        │ 92,0% │  🟡    │    ➡️     │ > 95%
Consistência      │ 91,5% │  🟢    │    ⬆️     │ > 90%
Validade          │ 100%  │  🟢    │    ➡️     │ 100%
Unicidade         │ 99,6% │  🟢    │    ⬆️     │ 100%
Atualidade        │ 87,0% │  🟢    │    ⬇️     │ > 85%

AÇÕES PRIORITÁRIAS:
1. ⚠️ Completude: Preencher 280 estoques_mínimos (meta: 95%)
2. ℹ️ Atualidade: Tendência queda - monitorar próximo mês
3. ✅ Acuracidade: Manter excelência (98,4%)

ROI GOVERNANÇA MÊS: R$ 3,6M economia / R$ 15k custo = 24.000%
```

---

═══════════════════════════════════════════════════════════════════════════════
## 7. RESUMO EXECUTIVO DIA 23
═══════════════════════════════════════════════════════════════════════════════

```
╔══════════════════════════════════════════════════════════════════════╗
║           SISTEMA DE MÉTRICAS MDM - RESUMO EXECUTIVO                ║
╚══════════════════════════════════════════════════════════════════════╝

KPIs DEFINIDOS:
──────────────────────────────────────────────────────────────────
6 Dimensões DAMA: 12 KPIs principais
Workflow: 6 KPIs performance
Total: 18 KPIs formalizados

Cada KPI tem:
✅ Fórmula clara
✅ Meta objetiva
✅ Thresholds (verde/amarelo/vermelho)
✅ Frequência medição
✅ Responsável
✅ Fonte dados

THRESHOLDS:
──────────────────────────────────────────────────────────────────
Sistema 3 níveis (Verde/Amarelo/Vermelho)
18 KPIs mapeados em tabela
Alertas automáticos configurados

🟢 Normal: Monitorar
🟡 Atenção: Email Supervisor diário
🔴 Crítico: Email + SMS Gerência imediato

DASHBOARDS:
──────────────────────────────────────────────────────────────────
Executivo: Visão gerencial (4 seções)
  • Scorecard geral
  • 6 dimensões qualidade
  • Workflow performance
  • Alertas e ações

Operacional: Drill-down detalhado
  • Por categoria
  • Materiais específicos
  • Histórico temporal

RELATÓRIOS AUTOMÁTICOS:
──────────────────────────────────────────────────────────────────
Diário: Operacional (Supervisor + MDO)
Semanal: Tático (Gerência + MDO)
Mensal: Estratégico (Gerência + CFO)
Trimestral: Auditoria (Compliance)

SCORECARD EXECUTIVO:
──────────────────────────────────────────────────────────────────
Score Geral MDM: Média ponderada 6 dimensões
Interpretação: 95-100% Excelente → < 80% Crítico
Exemplo Atual: 94,91% 🟢 BOM

ROI MONITORAMENTO:
──────────────────────────────────────────────────────────────────
Custo Anual: R$ 20.000 (BI + dashboards)
Economia Habilitada: R$ 43,3M (dados qualidade)
ROI: 216.500%

╔══════════════════════════════════════════════════════════════════════╗
║  MÉTRICAS IMPLEMENTADAS: PRONTAS PARA MONITORAMENTO                 ║
║  BASE: Políticas (Dia 22) + KPIs (Dia 23)                          ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

═══════════════════════════════════════════════════════════════════════════════
FIM DO DOCUMENTO - DIA 23
═══════════════════════════════════════════════════════════════════════════════

**PRÓXIMO:** Dia 24 - Dicionário de Dados Completo (3.300 materiais)

**PROGRESSO:** 46,9% (23 de 49 dias)
**SEMANA 4:** 28,6% (2 de 7 dias)
**ECONOMIA SEMANA 4:** R$ 0 (governança + métricas = prevenção)
**TEMPO INVESTIDO DIA 23:** ~2 horas documentação

✅ **DIA 23 COMPLETO!**
