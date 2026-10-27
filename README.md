# Central de Controle de Eficiência Logística

<p align="center">
  <img src="https://img.shields.io/badge/Portfolio-Log%C3%ADstica-blue?style=for-the-badge" alt="Portfolio Logística" />
  <img src="https://img.shields.io/badge/SQL-Queries-5865F2?style=for-the-badge" alt="SQL Queries" />
  <img src="https://img.shields.io/badge/Dashboard-Professional-34D399?style=for-the-badge" alt="Dashboard Premium" />
</p>

Uma solução de análise de operação logística criada para identificar os maiores ofensores da expedição, mapear causas de atrasos e apoiar decisões de liderança com base em dados.

## Visão geral

Este projeto simula um centro de distribuição com pedidos, etapas logísticas, prazos, status, atrasos e motivos de falha. A análise foca em responder três perguntas centrais da liderança:

- Onde os atrasos estão concentrados?
- Qual etapa, turno ou motivo impacta mais a operação?
- Quais ações devem ser priorizadas primeiro?

## Problema de negócio

O centro de distribuição está registrando atrasos na expedição e a liderança precisa saber onde agir primeiro. O projeto ajuda a diagnosticar os principais gargalos e a entregar um diagnóstico executivo com foco em causa raiz e priorização.

## KPIs principais

- Taxa de atraso por etapa logística
- Volume de pedidos por turno
- Percentual de cumprimento do SLA
- Taxa de retrabalho
- Taxa de inconsistências
- Participação por motivo de atraso
- Top 3 ofensores da operação

## Snapshot de resultado

| Indicador | Valor |
| --- | ---: |
| Total de pedidos | 1.800 |
| Pedidos atrasados | 758 |
| Taxa de atraso geral | 42.11% |
| Cumprimento do SLA | 57.89% |
| Taxa de retrabalho | 18.44% |
| Taxa de inconsistência | 12.33% |

## Estrutura do projeto

```text
central_eficiencia_logistica/
├── LICENSE
├── .gitignore
├── README.md
├── data/
│   ├── pedidos.csv
│   ├── ocorrencias.csv
│   └── central_eficiencia_logistica.sqlite
├── docs/
│   ├── dashboard-premium.html
│   ├── relatorio_executivo.md
│   └── assets/
│       ├── dashboard.css
│       └── dashboard.js
├── scripts/
│   ├── generate_logistics_data.py
│   └── validate_metrics.py
└── sql/
    └── consultas_central_eficiencia_logistica.sql
```

## Dashboard premium

Uma versão visual mais profissional foi criada em HTML/CSS/JS para simular um dashboard executivo com:

- cards de KPI
- gráficos de barras por etapa
- ranking de motivos de atraso
- tabela de top ofensores
- recomendações de ação para liderança

Acesse em:

- [docs/dashboard-premium.html](docs/dashboard-premium.html)

## Como executar

### 1) Verificar dados

```bash
python scripts/validate_metrics.py
```

### 2) Abrir dashboard

Abra o arquivo HTML diretamente no navegador:

```text
docs/dashboard-premium.html
```

### 3) Usar consultas SQL

Importe o arquivo de consulta para o banco de dados:

- [sql/consultas_central_eficiencia_logistica.sql](sql/consultas_central_eficiencia_logistica.sql)

## Entrega para portfólio

Este projeto foi pensado para ser apresentado como um case realista de análise operacional em logística, com foco em:

- causa raiz
- priorização por impacto
- dashboard executivo
- atenção à liderança
- storytelling analítico

## Próximos passos

- importar os dados para Excel ou Google Sheets
- criar uma versão em Looker Studio
- exportar um painel para apresentação em reunião executiva
- preparar a versão final para GitHub Pages ou LinkedIn

## Licença

Este projeto está sob a licença MIT. Consulte [LICENSE](LICENSE).
