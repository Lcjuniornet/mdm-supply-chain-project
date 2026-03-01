# DASHBOARD MDM — POWER BI
## Projeto MDM Supply Chain Analytics · Dia 13

---

## 📁 CONTEÚDO DESTA PASTA

| Arquivo | Descrição |
|---------|-----------|
| `README_POWERBI.md` | Este arquivo |
| `dashboard_powerbi_mdm.html` | Dashboard interativo (abrir no navegador) |
| `13_powerbi_pag1_dashboard.png` | Página 1 — Visão Geral MDM |
| `13_powerbi_pag2_risco.png` | Página 2 — Análise de Risco |

> **Nota:** O arquivo `dashboard_mdm.pbix` é gerado manualmente no Power BI Desktop  
> seguindo o guia `DIA13_POWERBI_GUIA_CORRIGIDO.md` na raiz do projeto.

---

## 📊 VISUALS DO DASHBOARD

### Página 1 — Dashboard MDM
| # | Visual | Tipo | Medida Principal |
|---|--------|------|-----------------|
| 1 | Total de Materiais | Cartão KPI | `Total Materiais = 3.300` |
| 2 | Valor em Estoque | Cartão KPI | `Valor Total = R$ 1,83B` |
| 3 | Preço Médio | Cartão KPI | `Preço Médio = R$ 220,58` |
| 4 | Materiais Ativos | Cartão KPI | `Ativos = 2.454 (74,4%)` |
| 5 | Sem Fornecedor | Cartão KPI | `Sem Forn. = 660 (20%)` |
| 6 | Valor por Categoria | Barras horizontais | `Valor Total Estoque` por `categoria` |
| 7 | Status dos Materiais | Pizza | `Total Materiais` por `status` |
| 8 | Curva ABC | Barras agrupadas | `Qtd` e `Valor` por `classe_abc` |
| 9 | Top Fornecedores | Barras horizontais | `Valor Total` por `fornecedor` |
| 10 | Com/Sem Fornecedor | Pizza | `Total Materiais` por `tem_fornecedor` |

### Página 2 — Análise de Risco
| # | Visual | Tipo | Valor |
|---|--------|------|-------|
| 1 | Valor em Risco | Cartão KPI | `R$ 394M` (sem fornecedor) |
| 2 | Materiais Parados | Cartão KPI | `1.054` (>365 dias) |
| 3 | Capital Imobilizado | Cartão KPI | `R$ 531M` |
| 4 | Abaixo do Mínimo | Cartão KPI | `128 materiais` |
| 5 | Abaixo do Mínimo por Cat. | Barras | `Abaixo do Minimo` por `categoria` |
| 6 | Materiais Parados por Cat. | Barras | `Materiais Parados 365d` por `categoria` |
| 7 | Top 20 Sem Fornecedor | Tabela | Filtro: `tem_fornecedor = Sem Fornecedor` |

---

## 🔢 MEDIDAS DAX CRIADAS

```dax
Total Materiais       = COUNTROWS(materiais_raw)
Valor Total Estoque   = SUMX(materiais_raw, preco_unitario * estoque_atual)
Preco Medio           = AVERAGE(materiais_raw[preco_unitario])
Materiais Ativos      = CALCULATE(COUNTROWS(materiais_raw), status = "Ativo")
Sem Fornecedor        = CALCULATE(COUNTROWS(materiais_raw), ISBLANK(fornecedor_principal))
Pct Sem Fornecedor    = DIVIDE([Sem Fornecedor], [Total Materiais], 0)
Abaixo do Minimo      = CALCULATE(COUNTROWS(materiais_raw), estoque_atual < estoque_minimo, NOT ISBLANK(estoque_minimo))
Valor Sem Fornecedor  = CALCULATE(SUMX(...), ISBLANK(fornecedor_principal))
Materiais Parados 365d= CALCULATE(COUNTROWS(materiais_raw), dias_sem_movimento > 365)
Capital Imobilizado   = CALCULATE(SUMX(...), dias_sem_movimento > 365)
```

---

## 📈 FONTE DE DADOS

| Tabela | Arquivo | Registros |
|--------|---------|-----------|
| `materiais_raw` | `data/raw/materiais_raw.csv` | 3.300 |

---

## 🏁 STATUS DO DIA 13

- [x] Guia Power BI (CORRIGIDO) documentado
- [x] Dashboard HTML interativo gerado
- [x] Imagens PNG de alta resolução geradas (2 páginas)
- [x] Script Python `06_powerbi_graficos.py` criado e testado
- [ ] Arquivo `.pbix` (gerado manualmente no Power BI Desktop)

---

*Projeto MDM Supply Chain · Dia 13 · 28/02/2026*
