"""Tabelas normativas da ABNT NBR 5419-2:2026.

Cada constante está anotada com a Tabela/Seção de origem para rastreabilidade.
Valores extraídos diretamente do texto da norma.
"""
from __future__ import annotations

# =============================================================================
# Tabela 4 - Valores típicos de risco tolerável RT (Seção 5.3)
# =============================================================================
RT_R1 = 1e-5  # Perda de vida humana ou ferimentos permanentes
RT_R3 = 1e-4  # Perda de patrimônio cultural
RT_R4 = 1e-3  # Perda de valor econômico (Anexo D, informativo - referencial)


# =============================================================================
# Tabela A.1 - Fator de localização da estrutura CD (e CDJ)
# =============================================================================
CD_VALORES = {
    "cercada_objetos_mais_altos": 0.25,
    "cercada_mesma_altura_ou_menor": 0.5,
    "isolada": 1.0,
    "isolada_no_topo_de_colina": 2.0,
}

CD_LABELS = {
    "cercada_objetos_mais_altos": "Estrutura cercada por objetos significativamente mais altos",
    "cercada_mesma_altura_ou_menor": "Estrutura cercada por objetos da mesma altura ou ligeiramente mais baixos",
    "isolada": "Estrutura isolada: nenhum outro objeto nas vizinhanças ou cercada por objetos significativamente mais baixos",
    "isolada_no_topo_de_colina": "Estrutura isolada no topo de uma colina ou monte",
}


# =============================================================================
# Tabela A.2 - Fator de instalação da linha elétrica CI
# =============================================================================
CI_VALORES = {
    "aerea": 1.0,
    "enterrada": 0.5,
    "enterrada_em_malha": 0.01,
}

CI_LABELS = {
    "aerea": "Aéreo",
    "enterrada": "Enterrado",
    "enterrada_em_malha": "Enterrado dentro de eletrodo de aterramento em malha (ABNT NBR 5419-4)",
}


# =============================================================================
# Tabela A.3 - Fator do tipo de linha elétrica CT
# =============================================================================
CT_VALORES = {
    "bt_ou_sinal": 1.0,
    "at_com_trafo": 0.2,
}

CT_LABELS = {
    "bt_ou_sinal": "Linha de energia em BT ou linha de sinal",
    "at_com_trafo": "Linha de energia em AT com transformador AT/BT (enrolamentos eletricamente separados)",
}


# =============================================================================
# Tabela A.4 - Fator ambiental da linha elétrica CE
# =============================================================================
CE_VALORES = {
    "rural": 1.0,
    "suburbano": 0.5,
    "urbano": 0.1,
    "urbano_alto": 0.01,
}

CE_LABELS = {
    "rural": "Rural",
    "suburbano": "Suburbano",
    "urbano": "Urbano",
    "urbano_alto": "Urbano com estruturas acima de 20 m de altura",
}


# =============================================================================
# Tabela B.1 - Probabilidade PTA (medidas adicionais contra tensão de toque/passo)
# =============================================================================
PTA_VALORES = {
    "nenhuma": 1.0,
    "avisos_alerta": 1e-1,
    "isolacao_eletrica": 1e-2,
    "malha_equipotencializacao_solo": 1e-2,
    "estrutura_metalica_descida_natural": 1e-3,
    "restricoes_fisicas": 0.0,
}

PTA_LABELS = {
    "nenhuma": "Nenhuma medida de proteção adicional",
    "avisos_alerta": "Avisos de alerta (após análise de viabilidade)",
    "isolacao_eletrica": "Isolação elétrica (≥3 mm polietileno reticulado nos condutores de descida) — só toque",
    "malha_equipotencializacao_solo": "Malha de equipotencialização do solo — só passo",
    "estrutura_metalica_descida_natural": "Estrutura metálica contínua ou concreto armado como descida natural",
    "restricoes_fisicas": "Restrições físicas fixas (toque e passo)",
}


# =============================================================================
# Tabela B.2 - Probabilidade PB (nível de proteção do SPDA)
# =============================================================================
PB_VALORES = {
    "sem_spda": 1.0,
    "npiv": 0.2,
    "npiii": 0.1,
    "npii": 0.05,
    "npi": 0.02,
    "npi_capacao_natural": 0.01,
    "cobertura_metalica_natural": 0.001,
}

PB_LABELS = {
    "sem_spda": "Estrutura não protegida por SPDA",
    "npiv": "SPDA Nível IV",
    "npiii": "SPDA Nível III",
    "npii": "SPDA Nível II",
    "npi": "SPDA Nível I",
    "npi_capacao_natural": "SPDA NP I + estrutura metálica/concreto armado como descida natural",
    "cobertura_metalica_natural": "Cobertura metálica como captação natural + descida natural",
}


# =============================================================================
# Tabela B.3 - Probabilidade PSPD (DPS coordenado por NP)
# =============================================================================
PSPD_VALORES = {
    "nenhum": 1.0,
    "iii_iv": 0.05,
    "ii": 0.02,
    "i": 0.01,
    "melhor_que_i": 0.005,  # faixa 0,005 a 0,001 — usar valor superior por segurança
}

PSPD_LABELS = {
    "nenhum": "Nenhum sistema coordenado de DPS",
    "iii_iv": "DPS coordenado projetado para NP III-IV",
    "ii": "DPS coordenado projetado para NP II",
    "i": "DPS coordenado projetado para NP I",
    "melhor_que_i": "DPS com características melhores que NP I (0,005 a 0,001)",
}


# =============================================================================
# Tabela B.4 - Fatores CLD e CLI (blindagem/aterramento da linha)
# =============================================================================
# Chave: (tipo_linha, ligacao_equipotencial)
CLD_CLI_VALORES: dict[str, tuple[float, float]] = {
    # (CLD, CLI)
    "aerea_nao_blindada": (1.0, 1.0),
    "subterranea_nao_blindada": (1.0, 1.0),
    "energia_neutro_multiaterrado": (1.0, 0.2),
    "subterranea_blindada_nao_interligada": (1.0, 0.3),
    "aerea_blindada_nao_interligada": (1.0, 0.1),
    "blindada_interligada_mesmo_bel": (1.0, 0.0),
    "cabo_de_protecao_em_eletroduto_metalico": (0.0, 0.0),
    "sem_linha_externa_ou_fibra": (0.0, 0.0),
    "interfaces_isolantes_5419_4": (0.0, 0.0),
}

CLD_CLI_LABELS = {
    "aerea_nao_blindada": "Linha aérea não blindada — sem ligação equipotencial",
    "subterranea_nao_blindada": "Linha subterrânea não blindada — sem ligação equipotencial",
    "energia_neutro_multiaterrado": "Linha de energia com neutro multiaterrado — sem EQP",
    "subterranea_blindada_nao_interligada": "Linha subterrânea blindada — blindagem não interligada ao mesmo BEL",
    "aerea_blindada_nao_interligada": "Linha aérea blindada — blindagem não interligada ao mesmo BEL",
    "blindada_interligada_mesmo_bel": "Linha aérea/subterrânea blindada — blindagem interligada ao mesmo BEL",
    "cabo_de_protecao_em_eletroduto_metalico": "Cabo de proteção em duto/eletroduto metálico — interligado ao mesmo BEL",
    "sem_linha_externa_ou_fibra": "Sem linha externa ou linha não metálica (ex.: fibra óptica)",
    "interfaces_isolantes_5419_4": "Interfaces isolantes conforme ABNT NBR 5419-4",
}


# =============================================================================
# Tabela B.5 - Fator KS3 (fiação interna)
# =============================================================================
KS3_VALORES = {
    "nao_blindado_sem_preocupacao": 1.0,
    "nao_blindado_evitar_grandes_lacos": 0.5,
    "nao_blindado_evitar_lacos_medios": 0.2,
    "nao_blindado_evitar_pequenos_lacos": 0.01,
    "blindado_ou_em_conduto_metalico": 1e-4,
}

KS3_LABELS = {
    "nao_blindado_sem_preocupacao": "Cabo não blindado — sem preocupação no roteamento (laços ~50 m²)",
    "nao_blindado_evitar_grandes_lacos": "Cabo não blindado — evita grandes laços (~25 m²)",
    "nao_blindado_evitar_lacos_medios": "Cabo não blindado — evita laços médios (~10 m²)",
    "nao_blindado_evitar_pequenos_lacos": "Cabo não blindado — evita laços pequenos (~0,5 m²)",
    "blindado_ou_em_conduto_metalico": "Cabo blindado ou em conduto metálico (interligado nas duas pontas)",
}


# =============================================================================
# Tabela B.6 - Probabilidade PTU (medidas contra tensão de toque na entrada)
# =============================================================================
PTU_VALORES = {
    "nenhuma": 1.0,
    "avisos_alerta": 1e-1,
    "isolacao_eletrica": 1e-2,
    "restricoes_fisicas": 0.0,
}

PTU_LABELS = {
    "nenhuma": "Nenhuma medida de proteção",
    "avisos_alerta": "Avisos visíveis de alerta",
    "isolacao_eletrica": "Isolação elétrica",
    "restricoes_fisicas": "Restrições físicas",
}


# =============================================================================
# Tabela B.7 - Probabilidade PEB (DPS classe I para EQP)
# =============================================================================
PEB_VALORES = {
    "sem_dps": 1.0,
    "iii_iv": 0.05,
    "ii": 0.02,
    "i": 0.01,
    "melhor_que_i": 0.005,
}

PEB_LABELS = {
    "sem_dps": "Sem DPS classe I",
    "iii_iv": "DPS classe I projetado para NP III-IV",
    "ii": "DPS classe I projetado para NP II",
    "i": "DPS classe I projetado para NP I",
    "melhor_que_i": "DPS classe I com Iimp maior que NP I (0,005 a 0,001)",
}


# =============================================================================
# Tabela B.8 - Probabilidade PLD (resistência da blindagem RS × UW)
# UW em kV, valores: 0,35; 0,5; 1; 1,5; 2,5; 4; 6
# =============================================================================
UW_NIVEIS = [0.35, 0.5, 1.0, 1.5, 2.5, 4.0, 6.0]

PLD_TABELA = {
    # Linha aérea/subterrânea não blindada OU blindagem não interligada ao mesmo ref. de equip.
    "nao_blindada": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
    # Blindada, aérea ou subterrânea, blindagem interligada — 5 Ω/km < RS ≤ 20 Ω/km
    "blindada_5a20": [1.0, 1.0, 1.0, 1.0, 0.95, 0.9, 0.8],
    # Blindada, blindagem interligada — 1 Ω/km < RS ≤ 5 Ω/km
    "blindada_1a5": [1.0, 1.0, 0.9, 0.8, 0.6, 0.3, 0.1],
    # Blindada, blindagem interligada — RS ≤ 1 Ω/km
    "blindada_menor_1": [1.0, 0.85, 0.6, 0.4, 0.2, 0.04, 0.02],
}

PLD_LABELS = {
    "nao_blindada": "Linha não blindada ou blindagem não interligada ao mesmo BEL",
    "blindada_5a20": "Linha blindada, blindagem interligada — 5 < RS ≤ 20 Ω/km",
    "blindada_1a5": "Linha blindada, blindagem interligada — 1 < RS ≤ 5 Ω/km",
    "blindada_menor_1": "Linha blindada, blindagem interligada — RS ≤ 1 Ω/km",
}


# =============================================================================
# Tabela B.9 - Probabilidade PLI (tipo de linha × UW)
# UW em kV: 1; 1,5; 2,5; 4; 6
# =============================================================================
UW_NIVEIS_PLI = [1.0, 1.5, 2.5, 4.0, 6.0]

PLI_TABELA = {
    "energia": [1.0, 0.6, 0.3, 0.16, 0.1],
    "sinal": [1.0, 0.5, 0.2, 0.08, 0.04],
}


# =============================================================================
# Tabela C.2 - Valores típicos de LT, LF, LO (perda L1 - vida humana)
# =============================================================================
LT_VALORES = {
    "todos_tipos": 1e-2,
    "risco_explosao": 1e-1,
}

LF_VALORES_L1 = {
    "hospital_hotel_escola_civico": 1e-1,
    "entretenimento_igreja_museu": 5e-2,
    "industrial_comercial": 5e-2,
    "outros": 2e-2,
    "risco_explosao": 1e-1,
}

LO_VALORES_L1 = {
    "risco_explosao": 1e-1,
    "uti_bloco_cirurgico": 1e-2,
    "outras_partes_hospital": 1e-3,
    "outros": 0.0,
}

LF_VALORES_L1_LABELS = {
    "hospital_hotel_escola_civico": "Hospital, hotel, escola, edifício cívico",
    "entretenimento_igreja_museu": "Entretenimento público, igreja, museu",
    "industrial_comercial": "Industrial, comercial",
    "outros": "Outros",
    "risco_explosao": "Estrutura com risco de explosão",
}

LO_VALORES_L1_LABELS = {
    "risco_explosao": "Estrutura com risco de explosão",
    "uti_bloco_cirurgico": "UTI ou bloco cirúrgico de hospital",
    "outras_partes_hospital": "Outras partes de hospital",
    "outros": "Outros (não aplicável - falha sem risco à vida)",
}


# =============================================================================
# Tabela C.3 - Fator rt (tipo de superfície do solo/piso)
# =============================================================================
RT_VALORES = {
    "terra_concreto": 1e-2,
    "marmore_ceramica": 1e-3,
    "brita_tapete_carpete": 1e-4,
    "asfalto_linoleo_madeira": 1e-5,
}

RT_LABELS = {
    "terra_concreto": "Terra, concreto (≤ 1 kΩ)",
    "marmore_ceramica": "Mármore, cerâmica (1 a 10 kΩ)",
    "brita_tapete_carpete": "Brita, tapete, carpete (10 a 100 kΩ)",
    "asfalto_linoleo_madeira": "Asfalto, linóleo, madeira (≥ 100 kΩ)",
}


# =============================================================================
# Tabela C.4 - Fator rp (providências contra incêndio)
# =============================================================================
RP_VALORES = {
    "nenhuma_ou_explosao": 1.0,
    "manuais_basicas": 0.5,
    "automaticas": 0.2,
}

RP_LABELS = {
    "nenhuma_ou_explosao": "Nenhuma providência ou estrutura com risco de explosão",
    "manuais_basicas": "Extintores, hidrantes, alarme manual, compartimentos contra fogo, rotas de escape",
    "automaticas": "Instalações fixas operadas automaticamente ou alarme automático (protegidas contra surtos)",
}


# =============================================================================
# Tabela C.5 - Fator rf (risco de incêndio ou explosão)
# =============================================================================
RF_VALORES = {
    "explosao_z0_z20_solidos": 1.0,
    "explosao_z1_z21": 1e-1,
    "explosao_z2_z22": 1e-3,
    "incendio_alto": 1e-1,
    "incendio_normal": 1e-2,
    "incendio_baixo": 1e-3,
    "nenhum": 0.0,
}

RF_LABELS = {
    "explosao_z0_z20_solidos": "Explosão — Zonas 0, 20 ou explosivos sólidos",
    "explosao_z1_z21": "Explosão — Zonas 1, 21",
    "explosao_z2_z22": "Explosão — Zonas 2, 22",
    "incendio_alto": "Incêndio — Alto risco (carga ≥ 800 MJ/m² ou material combustível)",
    "incendio_normal": "Incêndio — Normal (carga 400-800 MJ/m²)",
    "incendio_baixo": "Incêndio — Baixo (carga < 400 MJ/m²)",
    "nenhum": "Nenhum risco de incêndio ou explosão",
}


# =============================================================================
# Tabela C.6 - Fator hz (perigo especial)
# =============================================================================
HZ_VALORES = {
    "sem_perigo": 1.0,
    "baixo_panico": 2.0,
    "medio_panico": 5.0,
    "dificuldade_evacuacao": 5.0,
    "alto_panico": 10.0,
}

HZ_LABELS = {
    "sem_perigo": "Sem perigo especial",
    "baixo_panico": "Baixo nível de pânico (≤ 2 andares e ≤ 100 pessoas)",
    "medio_panico": "Médio pânico (eventos com 100-1000 pessoas)",
    "dificuldade_evacuacao": "Dificuldade de evacuação (pessoas imobilizadas, hospitais)",
    "alto_panico": "Alto pânico (eventos com > 1000 pessoas)",
}


# =============================================================================
# Tabela C.7 - Fator rS (tipo de construção)
# =============================================================================
RS_VALORES = {
    "simples": 2.0,  # madeira ou alvenaria simples
    "robusta": 1.0,  # estrutura metálica ou concreto armado
}

RS_LABELS = {
    "simples": "Simples: madeira ou alvenaria simples",
    "robusta": "Robusta: estrutura metálica ou concreto armado",
}


# =============================================================================
# Tabela C.9 - LF para L3 (patrimônio cultural)
# =============================================================================
LF_VALORES_L3 = {
    "museus_galerias": 1e-1,
}


# =============================================================================
# Tabela D.2 - LT, LF, LO para L4 (perda econômica)
# =============================================================================
LT_VALORES_L4 = {
    "todos_tipos_animais": 1e-2,
}

LF_VALORES_L4 = {
    "risco_explosao": 1.0,
    "hospital_industrial_museu_agricultura": 0.5,
    "hotel_escola_escritorio_igreja_entretenimento_comercial": 0.2,
    "outros": 1e-1,
}

LO_VALORES_L4 = {
    "risco_explosao": 1e-1,
    "hospital_industrial_escritorio_hotel_comercial": 1e-2,
    "museu_agricultura_escola_igreja_entretenimento": 1e-3,
    "outros": 1e-4,
}
