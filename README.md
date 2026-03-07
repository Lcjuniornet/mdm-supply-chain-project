# 📊 Projeto MDM Supply Chain - Análise de Dados Mestres

[![Status](https://img.shields.io/badge/status-65%25%20completo-yellow)](https://github.com/seu-usuario/mdm-supply-chain-project)
[![Python](https://img.shields.io/badge/python-3.9+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**Sistema de Análise e Governança de Dados Mestres para Supply Chain**

Projeto de análise de qualidade de dados mestres de materiais, com foco em identificação de problemas, quantificação de impacto financeiro e implementação de governança.O projeto foi criado para aprendizado no futuro da carreira.

---

## 🎯 Sobre o Projeto

Este projeto implementa análises de qualidade de dados mestres (MDM) aplicadas ao contexto de supply chain e logística, desenvolvido como projeto de portfólio para demonstrar competências em:

- **Análise de Dados** - Python, Pandas, NumPy
- **SQL** - Queries básicas e intermediárias
- **Visualização** - Matplotlib, Seaborn, dashboards
- **Governança de Dados** - Políticas, KPIs, workflows
- **Impacto de Negócio** - ROI, NPV, caso de negócio

---

## 💰 Resultados Principais

### Economia Identificada
```
Duplicatas:              R$ 18,2M/ano
Completude:              R$  2,5M/ano
Acuracidade:             R$ 17,9M/ano
Sazonalidade:            R$  4,4M/ano
Outros:                  R$  0,3M/ano
────────────────────────────────────
TOTAL:                   R$ 43,3M/ano
```

### Caso de Negócio
```
Investimento:            R$ 57.375
ROI (70% realização):    54.743%
Payback:                 < 1 mês
NPV (5 anos):            R$ 113,4M
Score QA:                97% (28/29 testes)
```

### Implementações
```
✅ Workflow 3 níveis governança (73% auto-aprovação)
✅ Script correções batch (9.000 correções)
✅ Suite QA automatizada (29 testes)
✅ Dashboard executivo HTML interativo
✅ Roadmap implementação 90 dias
```

---

## 📂 Estrutura do Projeto

```
mdm-supply-chain-project/
│
├── README.md                    # Este arquivo
├── requirements.txt             # Dependências Python
│
├── data/
│   ├── raw/                     # Dados simulados (3.300 materiais)
│   └── processed/               # Dados processados por scripts
│
├── scripts/                     # 12 scripts Python principais
│   ├── 01_analise_exploratoria.py
│   ├── 02_analise_duplicatas.py
│   ├── 03_analise_completude.py
│   ├── 04_analise_acuracidade.py
│   ├── 05_analise_padronizacao.py
│   ├── 06_analise_fornecedores.py
│   ├── 07_analise_movimentacoes.py
│   ├── 08_analise_outliers.py
│   ├── 09_analise_sazonalidade.py
│   ├── 10_implementacao_correcoes.py
│   ├── 11_workflow_governanca.py
│   └── 12_qa_automatizado.py
│
├── sql/                         # Queries SQL
│   └── *.sql                    # 20+ queries práticas
│
├── visualizations/              # Dashboards PNG
│   └── *.png                    # 11 dashboards gerados
│
├── docs/                        # Documentação técnica
│   ├── 22_documentacao_governanca_mdm.md
│   ├── 23_slas_metricas_processo.md
│   ├── 24_dicionario_dados_completo.md
│   ├── 25_politicas_validacao.md
│   ├── 28_dashboard_executivo.html
│   ├── 29_roi_detalhado.md
│   └── 30_roadmap_implementacao.md
│
└── checkpoints/                 # PowerPoints executivos
    ├── checkpoint_semana1.pptx
    ├── checkpoint_semana2.pptx
    ├── checkpoint_semana3.pptx
    └── apresentacao_final.pptx
```

---

## 🛠️ Tecnologias Utilizadas

### Linguagens
- **Python 3.9+** - Análise de dados
- **SQL** - Queries analíticas (SELECT, JOINs, subqueries)
- **HTML/CSS/JavaScript** - Dashboard interativo

### Bibliotecas Python
```python
pandas          # Manipulação de dados
numpy           # Computação numérica
matplotlib      # Visualizações
seaborn         # Gráficos estatísticos
datetime        # Manipulação datas
json            # Exportação dados
```

### Ferramentas
- **Git** - Controle de versão
- **Jupyter** - Notebooks exploratórios (conceitual)
- **NotebookLM** - Resumos e revisão
- **Chart.js** - Gráficos interativos web

---

## 🚀 Como Executar

### Pré-requisitos

```bash
# Python 3.9+
python --version

# pip atualizado
pip --version
```

### Instalação

```bash
# 1. Clonar repositório
git clone https://github.com/seu-usuario/mdm-supply-chain-project.git
cd mdm-supply-chain-project

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Verificar instalação
python -c "import pandas; import numpy; print('OK!')"
```

### Execução

```bash
# Análises principais (executar em ordem)
python scripts/02_analise_duplicatas.py
python scripts/03_analise_completude.py
python scripts/04_analise_acuracidade.py
python scripts/09_analise_sazonalidade.py

# Implementação
python scripts/10_implementacao_correcoes.py
python scripts/11_workflow_governanca.py

# QA e consolidação
python scripts/12_qa_automatizado.py
```

### Dashboard Interativo

```bash
# Abrir dashboard HTML no navegador
# Arquivo: visualizations/DIA28_Dashboard_Executivo.html
```

---

## 📊 Análises Realizadas

### 1. Duplicatas (R$ 18,2M economia)
- **Método:** Fuzzy matching similaridade > 95%
- **Resultado:** 299 pares duplicados identificados
- **Impacto:** R$ 18,2M/ano eliminando pedidos duplicados

### 2. Completude (R$ 2,5M economia)
- **Método:** Análise campos obrigatórios vs preenchidos
- **Resultado:** Score 93% → 99%+ após correções
- **Impacto:** R$ 2,5M/ano reduzindo retrabalho

### 3. Acuracidade (R$ 17,9M economia)
- **Método:** Validação preços vs mediana categoria
- **Resultado:** 99 materiais preço zero, 741 outliers
- **Impacto:** R$ 17,9M/ano corrigindo dados incorretos

### 4. Sazonalidade (R$ 4,4M economia)
- **Método:** Análise temporal movimentações
- **Resultado:** 14 categorias com padrão sazonal
- **Impacto:** R$ 4,4M/ano otimizando planejamento

### 5. Workflow Governança (R$ 125k ops)
- **Método:** Pipeline 3 níveis (auto/supervisor/MDO)
- **Resultado:** 73% auto-aprovação, SLA 5h vs 48h
- **Impacto:** 10× throughput, 200 mat/dia vs 20

### 6. QA Automatizado (97% aprovado)
- **Método:** Suite 29 testes automatizados
- **Resultado:** 28 PASS / 1 FAIL (não crítico)
- **Impacto:** Garantia qualidade produção

---

## 📈 Dashboards e Visualizações

### Dashboard Executivo HTML
- **KPIs principais:** Completude, NCM, Preço, Fornecedor
- **Gráficos:** Savings acumulados, Curva ABC, Pipeline aprovação
- **Interativo:** Chart.js, tooltips, responsivo
- **Arquivo:** `visualizations/DIA28_Dashboard_Executivo.html`

### Dashboards PNG (11 total)
1. Duplicatas (8 gráficos)
2. Completude (8 gráficos)
3. Acuracidade (6 gráficos)
4. Outliers (8 gráficos)
5. Sazonalidade (8 gráficos)
6. QA Score (6 gráficos)
7. Dashboard Executivo (consolidado)

---

## 📚 Documentação Técnica

### Governança MDM (40+ páginas)
- 4 princípios fundamentais
- 6 dimensões DAMA
- Workflow 3 níveis detalhado
- Matriz RACI (10 processos)
- 15 regras validação

### SLAs e Métricas (18 KPIs)
- 12 dimensões qualidade dados
- 6 métricas workflow
- Thresholds 3 níveis (verde/amarelo/vermelho)
- 4 relatórios automáticos

### Dicionário de Dados (21 campos)
- 65 regras validação (22 bloqueantes + 28 alertas + 15 críticas)
- Tipos, obrigatoriedade, relacionamentos
- Exemplos válidos/inválidos

### Roadmap Implementação (12 iniciativas, 90 dias)
- Fase 1: Correções imediatas (4 iniciativas)
- Fase 2: Melhorias estruturais (4 iniciativas)
- Fase 3: Governança contínua (4 iniciativas)
- 340h esforço total, R$ 40,4M saving

---

## 🎯 Status do Projeto

**Progresso:** 65% completo (32 de 49 dias planejados)

### ✅ Completado
- [x] Análises principais (duplicatas, completude, acuracidade, sazonalidade)
- [x] Script correções batch (9.000 correções)
- [x] Workflow governança 3 níveis
- [x] Suite QA automatizada (29 testes)
- [x] Documentação governança (100+ páginas)
- [x] Dashboard executivo HTML
- [x] Caso de negócio completo (ROI, NPV, TIR)
- [x] Roadmap implementação 90 dias
- [x] Apresentação executiva final

### 📅 Pendente (opcional)
- [ ] Pipeline integrado (documento teórico)
- [ ] Best practices MDM (lições aprendidas)
- [ ] Análises complementares (dias 32-49)

**Decisão:** Projeto pausado estrategicamente em 65% (retorno decrescente aplicado - Lei de Pareto). Material suficiente para demonstrar competências técnicas e impacto de negócio.

---

## 💼 Competências Demonstradas

### Técnicas
- ✅ **Python:** Pandas, NumPy, Matplotlib, Seaborn
- ✅ **SQL:** SELECT, WHERE, GROUP BY, JOINs, Subqueries
- ✅ **Análise de Dados:** Estatística descritiva, outliers, distribuições
- ✅ **Visualização:** Dashboards executivos, gráficos interativos
- ✅ **Automação:** Scripts batch, workflows, testes automatizados

### Negócio
- ✅ **Governança de Dados:** Políticas, KPIs, SLAs, validações
- ✅ **Caso de Negócio:** ROI, NPV, Payback, TIR, análise sensibilidade
- ✅ **Gestão de Projetos:** Roadmap, sequenciamento, dependências
- ✅ **Comunicação Executiva:** Apresentações, dashboards, relatórios

---

## 🎓 Sobre o Autor

**Luiz Carlos Silva Junior**

Profissional em transição de carreira de **Almoxarife → Master Data Owner**, com foco em dados aplicados ao supply chain.

### Formação
- 🎓 Pós-graduação: Tecnologia Aplicada em Logística (Anhanguera, cursando)
- 🎓 Bootcamp: Excel e Power BI Dashboards (Klabin/DIO, 90h)
- 🎓 Bootcamp: Fundamentos Engenharia de Dados e ML (TOTVS/DIO, 61h)

### Experiência
- 📦 3+ anos: Almoxarifado e logística (operações supply chain)
- 💻 SQL: Básico → Intermediário (JOINs, subqueries, agregações)
- 🐍 Python: Básico (pandas, numpy, visualizações)
- 📊 Governança: Políticas qualidade dados, workflows, KPIs

### Contato
- 💼 [LinkedIn](https://www.linkedin.com/in/luiz-carlos-silva-junior-a38922219/)
- 🐙 [GitHub](https://github.com/Lcjuniornet)
- 📧 Email: luizcjunior470@gmail.com

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja [LICENSE](LICENSE) para detalhes.

---

## 🙏 Agradecimentos

- **Comunidade Data Hackers** - Suporte e networking
- **Supply Chain Community** - Insights do setor
- **Klabin/TOTVS/DIO** - Bootcamps e certificações
- **NotebookLM** - Ferramenta estudo e revisão

---

## ⚠️ Nota de Transparência

Este projeto foi desenvolvido como **portfólio de aprendizado** e **demonstração de competências**. 

**Dados:** Simulados (não reais de empresa)  
**Código:** Desenvolvido com auxílio de IA e documentação (aprendizado ativo)  
**Foco:** Demonstrar capacidade de análise, impacto de negócio e governança de dados

O objetivo é mostrar **entendimento de conceitos**, **capacidade de aplicação prática** e **visão de impacto de negócio**, não expertise completa em todas as tecnologias utilizadas.

---

## 📞 Contato e Oportunidades

Estou aberto a oportunidades como:
- **Master Data Owner Júnior**
- **Analista de Dados Mestres Júnior**
- **Analista de Qualidade de Dados Júnior**
- **Analista BI Júnior** (Supply Chain)

Se este projeto demonstrou competências relevantes para sua organização, entre em contato!

---

⭐ **Se este projeto foi útil ou interessante, considere dar uma estrela!**

---

*Última atualização: Março 2026*  
*Status: Pausado estrategicamente (65% completo)*  
*Feito com ☕ e 💪 por Luiz Carlos Junior*