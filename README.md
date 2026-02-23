# 📊 Sistema Inteligente de Governança de Dados Mestre em Logística

![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

> **MDM Analytics** - Sistema de Análise e Qualidade de Cadastro Mestre Logístico
> 
> Framework completo de governança para dados mestres de materiais em ambiente supply chain

---

## 🎯 Sobre o Projeto

Este projeto implementa um **sistema inteligente de governança de dados mestres (MDM)** aplicado ao contexto de **supply chain e logística**, com foco em:

- ✅ **Qualidade de Dados** - Identificação e correção de problemas em cadastros
- ✅ **Duplicatas** - Detecção de materiais duplicados no sistema
- ✅ **Completude** - Análise de campos obrigatórios faltantes
- ✅ **Curva ABC** - Classificação de materiais por importância
- ✅ **Materiais Parados** - Identificação de itens sem movimentação
- ✅ **Dashboards Executivos** - Visualizações para tomada de decisão
- ✅ **ROI Calculado** - Impacto financeiro mensurável

### 💰 Impacto Esperado

```
Eliminação duplicatas:      R$ 20.000/ano
Completude cadastral:       R$ 12.000/ano
Materiais parados:          R$ 35.000/ano
Acuracidade compras:        R$ 10.000/ano
Produtividade equipe:       R$ 8.000/ano
─────────────────────────────────────────
TOTAL:                      R$ 85.000/ano
ROI:                        10:1
Payback:                    1-2 meses
```

---

## 📂 Estrutura do Projeto

```
mdm-supply-chain-project/
│
├── README.md                    # Documentação principal
├── requirements.txt             # Dependências Python
├── LICENSE                      # Licença MIT
│
├── data/                        # Dados do projeto
│   ├── raw/                     # Dados originais
│   ├── processed/               # Dados processados
│   └── sample/                  # Dados de exemplo
│
├── scripts/                     # Scripts Python
│   ├── 01_identificar_duplicatas.py
│   ├── 02_calcular_completude.py
│   ├── 03_curva_abc.py
│   ├── 04_materiais_parados.py
│   ├── 05_acuracia_dados.py
│   ├── 06_consistencia_dados.py
│   ├── 07_linhagem_dados.py
│   └── utils.py                 # Funções auxiliares
│
├── sql/                         # Queries SQL
│   ├── 01_duplicatas.sql
│   ├── 02_completude.sql
│   ├── 03_curva_abc.sql
│   ├── 04_materiais_parados.sql
│   ├── 05_acuracia.sql
│   ├── 06_consistencia.sql
│   └── 07_linhagem.sql
│
├── notebooks/                   # Jupyter Notebooks
│   ├── 01_exploratory_analysis.ipynb
│   ├── 02_data_quality_assessment.ipynb
│   └── 03_final_analysis.ipynb
│
├── dashboards/                  # Dashboards
│   ├── excel/                   # Excel dashboards
│   ├── powerbi/                 # Power BI dashboards
│   └── screenshots/             # Capturas de tela
│
├── visualizations/              # Visualizações PNG
│   └── *.png
│
├── docs/                        # Documentação
│   ├── metodologia.md
│   ├── dicionario_dados.md
│   ├── processo_analise.md
│   └── apresentacao_executiva.pptx
│
├── tests/                       # Testes unitários
│   └── test_*.py
│
└── references/                  # Materiais de referência
    └── *.pdf
```

---

## 🛠️ Tech Stack

### Linguagens e Frameworks
- **Python 3.9+** - Linguagem principal
- **SQL** - Queries de análise
- **Markdown** - Documentação

### Bibliotecas Python
- **Pandas** - Manipulação de dados
- **NumPy** - Computação numérica
- **Matplotlib/Seaborn** - Visualizações
- **Plotly** - Gráficos interativos
- **Jupyter** - Notebooks

### Ferramentas
- **Excel** - Dashboards executivos
- **Power BI** - Business Intelligence
- **Git** - Controle de versão
- **pytest** - Testes unitários

---

## 🚀 Começando

### Pré-requisitos

```bash
# Python 3.9 ou superior
python --version

# pip atualizado
pip --version
```

### Instalação

1. **Clone o repositório**
```bash
git clone https://github.com/Lcjuniornet/mdm-supply-chain-project.git
cd mdm-supply-chain-project
```

2. **Instale as dependências**
```bash
pip install -r requirements.txt
```

3. **Verifique a instalação**
```bash
python -c "import pandas; import numpy; print('OK!')"
```

### Execução

```bash
# 1. Gerar dados simulados
python scripts/00_gerar_dados.py

# 2. Executar análises
python scripts/01_identificar_duplicatas.py
python scripts/02_calcular_completude.py
python scripts/03_curva_abc.py

# 3. Gerar dashboards
python scripts/08_gerar_dashboards.py

# 4. Abrir notebooks
jupyter notebook
```

---

## 📊 Análises Disponíveis

### 1. Identificação de Duplicatas
Detecta materiais duplicados no cadastro com base em:
- Código de material
- Descrição (similaridade > 90%)
- Especificações técnicas

**Output**: Lista de duplicatas, economia potencial

### 2. Análise de Completude
Calcula percentual de preenchimento de campos obrigatórios:
- Descrição
- Unidade de medida
- NCM
- Fornecedor
- Localização

**Output**: Heatmap de completude, lista de gaps

### 3. Curva ABC
Classifica materiais por:
- Valor de estoque (A: 80%, B: 15%, C: 5%)
- Frequência de movimentação
- Criticidade para operação

**Output**: Gráfico Pareto, lista classificada

### 4. Materiais Parados
Identifica itens sem movimentação em:
- 6 meses
- 12 meses
- 24+ meses

**Output**: Lista priorizada, capital imobilizado

### 5. Acuracidade de Dados
Valida precisão de:
- Preços unitários
- Códigos NCM
- Saldos de estoque
- Localizações físicas

**Output**: Score de qualidade, plano de ação

### 6. Consistência de Dados
Verifica padrões de:
- Nomenclatura (convenções)
- Unidades de medida
- Categorização
- Codificação

**Output**: Relatório de inconsistências

### 7. Linhagem de Dados
Mapeia origem e fluxo de:
- Dados de materiais
- Atualizações cadastrais
- Responsáveis por alterações

**Output**: Diagrama de linhagem

---

## 📈 Dashboards

### Excel Dashboard
- KPIs principais
- Gráficos executivos
- Tabelas dinâmicas
- Alertas visuais

### Power BI Dashboard
- 15+ KPIs interativos
- Drill-down por categoria
- Filtros dinâmicos
- Atualização automática

### Screenshots
Disponíveis em `dashboards/screenshots/`

---

## 📚 Documentação

- **[Metodologia](docs/metodologia.md)** - Framework de governança aplicado
- **[Dicionário de Dados](docs/dicionario_dados.md)** - Campos e definições
- **[Processo de Análise](docs/processo_analise.md)** - Fluxo detalhado
- **[Apresentação Executiva](docs/apresentacao_executiva.pptx)** - Slides para stakeholders

---

## 🧪 Testes

```bash
# Executar todos os testes
pytest tests/

# Executar com cobertura
pytest --cov=scripts tests/

# Testes específicos
pytest tests/test_utils.py
```

---

## 🎯 Roadmap

### Fase 1: Setup ✅
- [x] Estrutura de pastas
- [x] Dependências instaladas
- [x] Dados simulados gerados

### Fase 2: Análises Core (Semanas 1-3) 🔄
- [x] Scripts 1-5 completos
- [x] Jupyter Notebooks
- [x] Visualizações profissionais

### Fase 3: Dashboards (Semana 4-5) 📅
- [ ] Dashboard Excel
- [ ] Dashboard Power BI
- [ ] Screenshots

### Fase 4: Documentação (Semana 6) 📅
- [ ] README completo
- [ ] Metodologia
- [ ] Apresentação executiva

### Fase 5: Publicação (Semana 7) 📅
- [ ] GitHub publicado
- [ ] LinkedIn post
- [ ] Portfolio atualizado

---

## 💼 Sobre o Autor

**Luiz Carlos Junior**  
Master Data Owner | Supply Chain Analytics | Data Governance

- 🎓 Google Data Analytics Professional Certificate
- 💼 alguns anos experiência Supply Chain
- 🎯 Especialização: Master Data Management
- 🐍 Stack: Python, SQL, Power BI, Excel

### Conecte-se
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/seu-perfil)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Lcjuniornet)

---

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para:
- 🐛 Reportar bugs
- 💡 Sugerir melhorias
- 📖 Melhorar documentação
- ⭐ Dar uma estrela no projeto

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja [LICENSE](LICENSE) para detalhes.

---

## 🙏 Agradecimentos

- **Google Data Analytics Certificate** - Fundamentos de análise
- **Comunidade Data Hackers** - Suporte e networking
- **Supply Chain Community** - Insights do setor

---

<div align="center">

**⭐ Se este projeto te ajudou, considere dar uma estrela!**

Feito com ❤️ e ☕ por [Luiz Carlos Junior](https://github.com/Lcjuniornet)

**#MDM #DataGovernance #SupplyChain #DataQuality #Python #DataAnalytics**

</div>
