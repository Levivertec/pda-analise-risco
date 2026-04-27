# Análise de Risco SPDA — ABNT NBR 5419-2:2026

Protótipo de aplicativo web para análise de risco de Sistema de Proteção contra
Descargas Atmosféricas (SPDA) conforme **ABNT NBR 5419-2:2026**.

## ✨ O que está implementado (V1)

- ✅ Cobertura completa da Parte 2 da norma
- ✅ Cálculo de R1 (vida humana), R3 (patrimônio cultural) e R4 (econômico — Anexo D)
- ✅ Todos os 8 componentes de risco (RA, RB, RC, RM, RU, RV, RW, RZ)
- ✅ Anexo A — áreas equivalentes AD, AM, AL, AI e fatores CD, CI, CT, CE
- ✅ Anexo B — todas as 9 tabelas de probabilidade (PTA, PB, PSPD, CLD/CLI, KS3, PTU, PEB, PLD, PLI)
- ✅ Anexo C — perdas L1 com fatores rt, rp, rf, hz, rs e razão nz/nt × tz/8760
- ✅ Anexo F — base de NG por município (5404 municípios extraídos da Tabela F.1)
- ✅ Múltiplas zonas de estudo
- ✅ Múltiplas linhas conectadas (energia + sinal)
- ✅ Dashboard com decomposição por componente, gráficos e diagnóstico
- ✅ Memorial de cálculo exportável em Markdown

## 🚀 Como executar

### Pré-requisitos
- Python 3.10 ou superior

### Instalação
```bash
pip install -r requirements.txt
```

### Executar a aplicação web
```bash
streamlit run app.py
```
A aplicação abrirá no navegador (geralmente http://localhost:8501).

### Executar teste do motor (sem UI)
```bash
python teste_exemplo.py
```

## 📁 Estrutura do projeto

```
.
├── app.py                      # Aplicativo Streamlit (UI)
├── teste_exemplo.py            # Teste rápido do motor
├── requirements.txt
├── data/
│   └── ng_municipios.csv       # NG por município (Anexo F, Tabela F.1)
└── src/nbr5419/
    ├── __init__.py
    ├── modelo.py               # Modelo de dados (Projeto, Estrutura, Zona, Linha)
    ├── tabelas.py              # Constantes normativas (todas as tabelas)
    └── calculo.py              # Motor de cálculo (componentes RA-RZ → R1, R3, R4)
```

## ⚠️ Limitações conhecidas (V1 / protótipo)

1. **Base NG**: 5404 municípios extraídos automaticamente do PDF.
   ~85 municípios podem estar faltando ou ter NG ligeiramente trocado entre
   colunas próximas no PDF original. **Validar contra a norma para projetos reais.**
2. **Anexo D (R4)** — implementado de forma simplificada. As razões ca/cb/cc/cs
   por zona não estão modeladas; valores por tipo de estrutura usam médias.
3. **Sub-zonas de estudo (6.7)** — implementadas, mas a frequência de danos F
   (Seção 7) não foi exposta na UI ainda.
4. **NDJ (estrutura adjacente)** — modelo de dados pronto, mas UI ainda não
   coleta dimensões da estrutura adjacente (entrada via campo numérico de AD).
5. **Errata 1 (abril/2026)** — não aplicada ainda. Recomenda-se revisar
   contra os PDFs de errata da ABNT antes de uso em produção.

## 🛣️ Próximos passos sugeridos (V2)

### Curto prazo (uso interno Vertec)
- [ ] Validar resultados contra exemplos resolvidos da edição anterior (NBR 5419-2:2015 Anexo H)
- [ ] Revisar e corrigir base NG completa (cruzar com fontes do INPE)
- [ ] Aplicar errata 1 onde aplicável
- [ ] Salvar/carregar projetos em JSON
- [ ] Memorial em PDF/DOCX (ao invés de só Markdown)

### Médio prazo (produto)
- [ ] Frequência de danos F (Seção 7) com UI
- [ ] Simulador "e se" para comparar custo das medidas (Anexo D - eficiência)
- [ ] Templates por tipo (residencial, hospital, industrial, escola...)
- [ ] Banco de equipamentos com UW típicos
- [ ] Multi-projeto + login + multi-tenant
- [ ] Geração de ART (cálculo + responsabilidade técnica)
- [ ] Integração com geocoding (puxar UF/município do CEP)
- [ ] Cálculo automático de NG por coordenadas via API do INPE

### Longo prazo (comercialização)
- [ ] SaaS com assinatura mensal por engenheiro/escritório
- [ ] Tier free (1 projeto/mês) + pago (ilimitado + memorial PDF)
- [ ] Marketplace de templates entre engenheiros
- [ ] API para integração com BIM/CAD

## 📚 Como o motor está organizado (para devs)

A separação **motor puro × UI** é proposital — o motor (`src/nbr5419/`) não
depende do Streamlit e pode ser reutilizado em outras interfaces (CLI, API REST,
desktop, planilha).

### Fluxo de cálculo
```
Projeto → calcular_projeto() → ResultadoProjeto
            │
            ├─ Áreas (AD, AM, AL, AI) — Anexo A
            ├─ Eventos N (ND, NM, NL, NI, NDJ)
            ├─ Por zona:
            │    ├─ Probabilidades P (PA-PZ) — Anexo B
            │    ├─ Perdas L (LA-LZ) — Anexo C
            │    └─ Componentes R = N × P × L (Eq. 3)
            └─ Soma R1/R3/R4 — Seção 4.3
```

Cada constante em `tabelas.py` cita a Tabela/Seção da norma para rastreabilidade.

## 📖 Referência da norma

- **ABNT NBR 5419-1:2026** — Princípios gerais
- **ABNT NBR 5419-2:2026** — Análise de risco *(esta aplicação)*
- **ABNT NBR 5419-3:2026** — Danos físicos a estruturas e perigos à vida
- **ABNT NBR 5419-4:2026** — Sistemas elétricos e eletrônicos internos

## ⚖️ Aviso legal

Este protótipo destina-se a apoiar engenheiros qualificados na análise de risco
conforme NBR 5419-2. Os cálculos devem ser validados pelo profissional
responsável (com ART). A interpretação final de zonas, fatores e medidas é de
responsabilidade do projetista.

---
*Vertec Energia — Análise de Risco SPDA*
