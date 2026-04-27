"""Motor de cálculo da análise de risco — ABNT NBR 5419-2:2026.

Implementa:
- Áreas equivalentes AD, AM, AL, AI (Anexo A)
- Número de eventos perigosos ND, NM, NL, NI, NDJ (Anexo A)
- Probabilidades PA, PB, PC, PM, PU, PV, PW, PZ (Anexo B)
- Perdas LA, LB, LC, LM, LU, LV, LW, LZ (Anexo C / Anexo D)
- Componentes RA, RB, RC, RM, RU, RV, RW, RZ (Seção 6)
- Riscos R1, R3 (Seção 4.3) e R4 (Anexo D)

A composição é multiplicativa: RX = NX * PX * LX (Eq. 3).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from math import pi
from typing import Optional

from . import tabelas as T
from .modelo import (
    BlindagemLinha,
    Estrutura,
    Linha,
    Projeto,
    TipoLinha,
    Zona,
)


# =============================================================================
# Áreas equivalentes (Anexo A)
# =============================================================================
def area_AD(L: float, W: float, H: float) -> float:
    """Eq. A.1 — área de exposição equivalente da estrutura (m²)."""
    return L * W + 2 * (3 * H) * (L + W) + pi * (3 * H) ** 2


def area_AD_saliencia(HP: float) -> float:
    """Eq. A.2 — área da saliência elevada na cobertura (m²)."""
    return pi * (3 * HP) ** 2


def area_AM(L: float, W: float) -> float:
    """Eq. A.6 — área de exposição equivalente para descargas próximas (m²)."""
    return 2 * 500 * (L + W) + pi * 500 ** 2


def area_AL(LL: float) -> float:
    """Eq. A.8 — área de exposição equivalente da linha (m²)."""
    return 40.0 * LL


def area_AI(LL: float) -> float:
    """Eq. A.10 — área de exposição equivalente próximo da linha (m²)."""
    return 4000.0 * LL


# =============================================================================
# Número de eventos perigosos (Anexo A)
# =============================================================================
def calcular_ND(NG: float, AD: float, CD: float) -> float:
    """Eq. A.3 — eventos por ano devido a descargas na estrutura."""
    return NG * AD * CD * 1e-6


def calcular_NM(NG: float, AM: float, AD: float, CD: float) -> float:
    """Eq. A.5 — eventos por ano devido a descargas próximas.

    Nota interpretativa: a área AM exclui a área da própria estrutura AD
    para evitar dupla contagem. A norma usa AM como anel ao redor.
    Implementação conservadora: NM = NG * (AM - AD * CD) * 1e-6, mas
    a equação literal é NM = NG * AM * 1e-6. Usamos a forma literal.
    """
    _ = AD, CD  # parâmetros mantidos para futura calibração
    return NG * AM * 1e-6


def calcular_NL(NG: float, AL: float, CI: float, CE: float, CT: float) -> float:
    """Eq. A.7 — eventos por ano devido a descargas na linha."""
    return NG * AL * CI * CE * CT * 1e-6


def calcular_NI(NG: float, AI: float, CI: float, CE: float, CT: float) -> float:
    """Eq. A.9 — eventos por ano devido a descargas próximas da linha."""
    return NG * AI * CI * CE * CT * 1e-6


def calcular_NDJ(NG: float, ADJ: float, CDJ: float, CT: float) -> float:
    """Eq. A.4 — eventos na estrutura adjacente."""
    return NG * ADJ * CDJ * CT * 1e-6


# =============================================================================
# Probabilidades (Anexo B)
# =============================================================================
def calcular_PTA(medidas: list[str]) -> float:
    """B.2.2 — produto dos PTA quando há múltiplas medidas."""
    if not medidas:
        return 1.0
    p = 1.0
    for m in medidas:
        p *= T.PTA_VALORES.get(m, 1.0)
    return p


def calcular_PA(estrutura: Estrutura) -> float:
    """Eq. B.1 — PA = PTA × PB."""
    pta = calcular_PTA(estrutura.pta_medidas)
    pb = T.PB_VALORES[estrutura.nivel_protecao_spda.value]
    return pta * pb


def calcular_PB(estrutura: Estrutura) -> float:
    """Tabela B.2 — função apenas do nível do SPDA."""
    return T.PB_VALORES[estrutura.nivel_protecao_spda.value]


def calcular_KS1(estrutura: Estrutura) -> float:
    """Eq. B.5 — eficiência de blindagem do SPDA. Limitado a 1."""
    if estrutura.spda_blindagem_continua:
        return 1e-4
    if estrutura.spda_largura_malha <= 0:
        return 1.0
    return min(1.0, 0.12 * estrutura.spda_largura_malha)


def calcular_KS2(zona: Zona) -> float:
    """Eq. B.6 — eficiência de blindagem espacial interna. Limitado a 1."""
    if zona.blindagem_continua:
        return 1e-4
    if zona.blindagem_largura_malha <= 0:
        return 1.0
    return min(1.0, 0.12 * zona.blindagem_largura_malha)


def calcular_KS3(zona: Zona) -> float:
    """Tabela B.5, com escala proporcional para circuitos < 100 m (nota e)."""
    base = T.KS3_VALORES[zona.fiacao_interna]
    if zona.fiacao_comprimento <= 0:
        return base
    fator = min(1.0, zona.fiacao_comprimento / 100.0)
    return base * fator


def calcular_KS4(UW: float) -> float:
    """Eq. B.7 — KS4 = 1/UW, limitado a 1."""
    if UW <= 0:
        return 1.0
    return min(1.0, 1.0 / UW)


def calcular_PMS(estrutura: Estrutura, zona: Zona) -> float:
    """Eq. B.4 — PMS = (KS1 × KS2 × KS3 × KS4)²."""
    ks1 = calcular_KS1(estrutura)
    ks2 = calcular_KS2(zona)
    ks3 = calcular_KS3(zona)
    ks4 = calcular_KS4(zona.UW)
    return (ks1 * ks2 * ks3 * ks4) ** 2


def calcular_PM(estrutura: Estrutura, zona: Zona) -> float:
    """B.4.7-9 — PM depende do PSPD e PMS."""
    pms = calcular_PMS(estrutura, zona)
    if estrutura.pspd_nivel == "nenhum":
        return min(1.0, pms)
    pspd = T.PSPD_VALORES[estrutura.pspd_nivel]
    return min(1.0, pspd * pms)


def calcular_PC_linha(estrutura: Estrutura, linha: Linha) -> float:
    """Eq. B.2 — PC = PSPD × CLD para uma linha individual."""
    pspd = T.PSPD_VALORES[estrutura.pspd_nivel]
    cld, _ = T.CLD_CLI_VALORES[linha.blindagem_eqp]
    return pspd * cld


def calcular_PC(estrutura: Estrutura, linhas: list[Linha]) -> float:
    """Eq. 12 — PC composto: PC = 1 - Π(1 - PCi).

    Quando não há linhas, mantém PSPD × 1 (CLD = 1 para sistema interno
    não blindado conectado).
    """
    if not linhas:
        # Mesmo sem linha externa, sistema interno pode falhar por descarga direta
        # via acoplamento. PC = PSPD com CLD = 1 (caso conservador).
        pspd = T.PSPD_VALORES[estrutura.pspd_nivel]
        return pspd
    p_acumulada = 1.0
    for linha in linhas:
        pc_i = calcular_PC_linha(estrutura, linha)
        p_acumulada *= (1.0 - pc_i)
    return 1.0 - p_acumulada


def _PLD_lookup(blindagem: BlindagemLinha, UW: float) -> float:
    """Tabela B.8 - interpolação por UW (nível superior mais próximo)."""
    valores = T.PLD_TABELA[blindagem.value]
    # Encontra o índice do menor UW da tabela >= UW do equipamento
    for i, uw_tabela in enumerate(T.UW_NIVEIS):
        if UW <= uw_tabela:
            return valores[i]
    return valores[-1]  # UW > 6 kV → usa o último valor


def _PLI_lookup(tipo: TipoLinha, UW: float) -> float:
    """Tabela B.9 - tipo de linha × UW."""
    chave = "energia" if tipo == TipoLinha.ENERGIA else "sinal"
    valores = T.PLI_TABELA[chave]
    for i, uw_tabela in enumerate(T.UW_NIVEIS_PLI):
        if UW <= uw_tabela:
            return valores[i]
    return valores[-1]


def calcular_PU(linha: Linha) -> float:
    """Eq. B.8 — PU = PTU × PEB × PLD × CLD."""
    ptu = T.PTU_VALORES[linha.ptu_medida]
    peb = T.PEB_VALORES[linha.peb_nivel]
    pld = _PLD_lookup(linha.blindagem_pld, linha.UW)
    cld, _ = T.CLD_CLI_VALORES[linha.blindagem_eqp]
    return ptu * peb * pld * cld


def calcular_PV(linha: Linha) -> float:
    """Eq. B.9 — PV = PEB × PLD × CLD."""
    peb = T.PEB_VALORES[linha.peb_nivel]
    pld = _PLD_lookup(linha.blindagem_pld, linha.UW)
    cld, _ = T.CLD_CLI_VALORES[linha.blindagem_eqp]
    return peb * pld * cld


def calcular_PW(estrutura: Estrutura, linha: Linha) -> float:
    """Eq. B.10 — PW = PSPD × PLD × CLD."""
    pspd = T.PSPD_VALORES[estrutura.pspd_nivel]
    pld = _PLD_lookup(linha.blindagem_pld, linha.UW)
    cld, _ = T.CLD_CLI_VALORES[linha.blindagem_eqp]
    return pspd * pld * cld


def calcular_PZ(estrutura: Estrutura, linha: Linha) -> float:
    """Eq. B.11 — PZ = PSPD × PLI × CLI."""
    pspd = T.PSPD_VALORES[estrutura.pspd_nivel]
    pli = _PLI_lookup(linha.tipo, linha.UW)
    _, cli = T.CLD_CLI_VALORES[linha.blindagem_eqp]
    return pspd * pli * cli


# =============================================================================
# Perdas (Anexo C — L1; Anexo D — L4)
# =============================================================================
def _fator_rf(zona: Zona) -> float:
    """rf considerando explosão (sobrescreve incêndio se != NENHUMA)."""
    if zona.explosao.value != "nenhum":
        return T.RF_VALORES[zona.explosao.value]
    return T.RF_VALORES[zona.risco_incendio.value]


def _fator_rp(zona: Zona) -> float:
    """rp = 1 se há risco de explosão, ainda que medidas existam (C.3.4)."""
    if zona.explosao.value != "nenhum":
        return 1.0
    return T.RP_VALORES[zona.providencias_incendio.value]


def calcular_LA_L1(estrutura: Estrutura, zona: Zona) -> float:
    """Eq. C.1 — LA = rt × LT × nz/nt × tz/8760 × rs."""
    rt = T.RT_VALORES[zona.superficie_solo.value]
    LT = T.LT_VALORES["risco_explosao"] if zona.explosao.value != "nenhum" else T.LT_VALORES["todos_tipos"]
    rs = T.RS_VALORES[estrutura.tipo_construcao.value]
    nz_nt = zona.n_pessoas / max(estrutura.n_total_pessoas, 1)
    tz = min(zona.horas_presenca_ano, 8760) / 8760.0
    return rt * LT * nz_nt * tz * rs


def calcular_LU_L1(estrutura: Estrutura, zona: Zona) -> float:
    """Eq. C.2 — idêntico a LA."""
    return calcular_LA_L1(estrutura, zona)


def calcular_LB_L1(estrutura: Estrutura, zona: Zona) -> float:
    """Eq. C.3 — LB = rp × rf × hz × LF × nz/nt × tz/8760 × rs."""
    rp = _fator_rp(zona)
    rf = _fator_rf(zona)
    hz = T.HZ_VALORES[zona.perigo_especial.value]
    LF = T.LF_VALORES_L1[zona.tipo_para_LF]
    if zona.explosao.value != "nenhum":
        LF = T.LF_VALORES_L1["risco_explosao"]
    rs = T.RS_VALORES[estrutura.tipo_construcao.value]
    nz_nt = zona.n_pessoas / max(estrutura.n_total_pessoas, 1)
    tz = min(zona.horas_presenca_ano, 8760) / 8760.0
    return rp * rf * hz * LF * nz_nt * tz * rs


def calcular_LV_L1(estrutura: Estrutura, zona: Zona) -> float:
    """LV = LB para L1."""
    return calcular_LB_L1(estrutura, zona)


def calcular_LC_L1(estrutura: Estrutura, zona: Zona) -> float:
    """Eq. C.4 — LC = LO × nz/nt × tz/8760 × rs."""
    LO = T.LO_VALORES_L1[zona.tipo_para_LO]
    if zona.explosao.value != "nenhum":
        LO = T.LO_VALORES_L1["risco_explosao"]
    rs = T.RS_VALORES[estrutura.tipo_construcao.value]
    nz_nt = zona.n_pessoas / max(estrutura.n_total_pessoas, 1)
    tz = min(zona.horas_presenca_ano, 8760) / 8760.0
    return LO * nz_nt * tz * rs


def calcular_LM_L1(estrutura: Estrutura, zona: Zona) -> float:
    return calcular_LC_L1(estrutura, zona)


def calcular_LW_L1(estrutura: Estrutura, zona: Zona) -> float:
    return calcular_LC_L1(estrutura, zona)


def calcular_LZ_L1(estrutura: Estrutura, zona: Zona) -> float:
    return calcular_LC_L1(estrutura, zona)


def calcular_LB_L3(zona: Zona, ct: float) -> float:
    """Eq. C.7 — LB para patrimônio cultural = rp × rf × LF × cz/ct."""
    if ct <= 0:
        return 0.0
    rp = _fator_rp(zona)
    rf = _fator_rf(zona)
    LF = T.LF_VALORES_L3["museus_galerias"]
    return rp * rf * LF * (zona.cz / ct)


# =============================================================================
# Componentes de risco (Seção 6) e composição (Seção 4.3)
# =============================================================================
@dataclass
class ResultadoComponente:
    nome: str
    N: float
    P: float
    L: float
    R: float
    descricao: str = ""


@dataclass
class ResultadoFrequencia:
    """Frequência de danos F por zona (Seção 7).

    F = FB + FC + FM + FV + FW + FZ (Eq. 14)
    Cada FX = NX × PX (Eq. 15 + Tabela 7).
    """
    FB: float = 0.0
    FC: float = 0.0
    FM: float = 0.0
    FV: float = 0.0
    FW: float = 0.0
    FZ: float = 0.0
    F: float = 0.0
    FT: float = 1.0  # tolerável (0,1 crítico; 1 não crítico)
    sistema_critico: bool = False


@dataclass
class ResultadoZona:
    nome: str
    componentes: dict[str, ResultadoComponente] = field(default_factory=dict)
    R1: float = 0.0
    R3: float = 0.0
    R4: float = 0.0
    frequencia: ResultadoFrequencia = field(default_factory=ResultadoFrequencia)


@dataclass
class ResultadoProjeto:
    R1: float = 0.0
    R3: float = 0.0
    R4: float = 0.0
    zonas: list[ResultadoZona] = field(default_factory=list)
    # Eventos N por categoria (independem da zona)
    ND: float = 0.0
    NM: float = 0.0
    NDJ: float = 0.0
    NL_total: float = 0.0
    NI_total: float = 0.0
    NL_por_linha: dict[str, float] = field(default_factory=dict)
    NI_por_linha: dict[str, float] = field(default_factory=dict)
    AD: float = 0.0
    AM: float = 0.0


def calcular_projeto(projeto: Projeto) -> ResultadoProjeto:
    """Calcula todos os componentes de risco e os totais R1/R3/R4."""
    e = projeto.estrutura

    # --- Áreas equivalentes ---
    if e.AD_manual is not None and e.AD_manual > 0:
        # Usuário forneceu AD calculado por método gráfico (A.2.1.3) ou outro meio
        AD = e.AD_manual
    else:
        AD_principal = area_AD(e.L, e.W, e.H)
        AD_sal = area_AD_saliencia(e.HP) if e.HP > 0 else 0.0
        AD = max(AD_principal, AD_sal)
    AM = area_AM(e.L, e.W)

    # --- CD/CDJ ---
    CD = T.CD_VALORES[e.localizacao.value]

    # --- Eventos N (independentes de zona) ---
    ND = calcular_ND(e.NG, AD, CD)
    NM = calcular_NM(e.NG, AM, AD, CD)
    NDJ = 0.0
    if e.estrutura_adjacente_AD > 0:
        # Assumindo CDJ = CD e CT = 1 (ajustar quando expandir modelo)
        NDJ = calcular_NDJ(e.NG, e.estrutura_adjacente_AD, CD, 1.0)

    NL_por_linha: dict[str, float] = {}
    NI_por_linha: dict[str, float] = {}
    NL_total = 0.0
    NI_total = 0.0
    for linha in projeto.linhas:
        AL = area_AL(linha.LL)
        AI = area_AI(linha.LL)
        CI = T.CI_VALORES[linha.instalacao.value]
        CE = T.CE_VALORES[linha.ambiente.value]
        CT = T.CT_VALORES[linha.bt_ou_at]
        NL = calcular_NL(e.NG, AL, CI, CE, CT)
        NI = calcular_NI(e.NG, AI, CI, CE, CT)
        NL_por_linha[linha.nome] = NL
        NI_por_linha[linha.nome] = NI
        NL_total += NL
        NI_total += NI

    resultado = ResultadoProjeto(
        ND=ND, NM=NM, NDJ=NDJ,
        NL_total=NL_total, NI_total=NI_total,
        NL_por_linha=NL_por_linha, NI_por_linha=NI_por_linha,
        AD=AD, AM=AM,
    )

    # --- Por zona ---
    R1_total = 0.0
    R3_total = 0.0
    R4_total = 0.0
    for zona in projeto.zonas:
        rz = ResultadoZona(nome=zona.nome)

        # === Probabilidades por zona ===
        PA = calcular_PA(e)
        PB = calcular_PB(e)
        PC = calcular_PC(e, projeto.linhas)
        PM = calcular_PM(e, zona)

        # === Perdas L1 (vida humana) ===
        LA = calcular_LA_L1(e, zona)
        LU = calcular_LU_L1(e, zona)
        LB = calcular_LB_L1(e, zona)
        LV = calcular_LV_L1(e, zona)
        LC = calcular_LC_L1(e, zona)
        LM = calcular_LM_L1(e, zona)
        LW = calcular_LW_L1(e, zona)
        LZ = calcular_LZ_L1(e, zona)

        # === Componentes (Eqs. 4-11) ===
        RA = ND * PA * LA
        RB = ND * PB * LB
        RC = ND * PC * LC
        RM = NM * PM * LM

        rz.componentes["RA"] = ResultadoComponente("RA", ND, PA, LA, RA, "Ferimentos por choque (S1)")
        rz.componentes["RB"] = ResultadoComponente("RB", ND, PB, LB, RB, "Danos físicos (S1)")
        rz.componentes["RC"] = ResultadoComponente("RC", ND, PC, LC, RC, "Falhas em sistemas internos (S1)")
        rz.componentes["RM"] = ResultadoComponente("RM", NM, PM, LM, RM, "Falhas em sistemas internos (S2)")

        # Componentes RU/RV/RW/RZ - somatório por linha
        RU_total = 0.0
        RV_total = 0.0
        RW_total = 0.0
        RZ_total = 0.0

        for linha in projeto.linhas:
            NL = NL_por_linha[linha.nome]
            NI = NI_por_linha[linha.nome]
            N_para_RU_RV_RW = NL + NDJ

            PU = calcular_PU(linha)
            PV = calcular_PV(linha)
            PW = calcular_PW(e, linha)
            PZ = calcular_PZ(e, linha)

            RU_l = N_para_RU_RV_RW * PU * LU
            RV_l = N_para_RU_RV_RW * PV * LV
            RW_l = N_para_RU_RV_RW * PW * LW
            RZ_l = NI * PZ * LZ

            RU_total += RU_l
            RV_total += RV_l
            RW_total += RW_l
            RZ_total += RZ_l

        rz.componentes["RU"] = ResultadoComponente("RU", NL_total + NDJ, 0.0, LU, RU_total,
                                                    "Ferimentos por choque (S3) — somatório")
        rz.componentes["RV"] = ResultadoComponente("RV", NL_total + NDJ, 0.0, LV, RV_total,
                                                    "Danos físicos (S3) — somatório")
        rz.componentes["RW"] = ResultadoComponente("RW", NL_total + NDJ, 0.0, LW, RW_total,
                                                    "Falhas em sistemas internos (S3) — somatório")
        rz.componentes["RZ"] = ResultadoComponente("RZ", NI_total, 0.0, LZ, RZ_total,
                                                    "Falhas em sistemas internos (S4) — somatório")

        # === Frequência de danos F (Seção 7) — sempre calculada ===
        # FX = NX × PX (Eq. 15). Valores da Tabela 7.
        FB = (ND * PB) if zona.equipamentos_em_ZPR0A else 0.0
        FC = ND * PC
        FM = NM * PM

        # FV usa PEB (Tabela 7) — diferente de PV usado em RV.
        # FW usa PW. Somatório por linha (linhas com mesmo roteamento → pior caso).
        FV_total = 0.0
        FW_total = 0.0
        FZ_total = 0.0
        for linha in projeto.linhas:
            NL_l = NL_por_linha[linha.nome]
            NI_l = NI_por_linha[linha.nome]
            peb = T.PEB_VALORES[linha.peb_nivel]
            FV_total += (NL_l + NDJ) * peb
            FW_total += (NL_l + NDJ) * calcular_PW(e, linha)
            FZ_total += NI_l * calcular_PZ(e, linha)

        F_total = FB + FC + FM + FV_total + FW_total + FZ_total
        FT = 0.1 if zona.sistema_critico else 1.0
        rz.frequencia = ResultadoFrequencia(
            FB=FB, FC=FC, FM=FM, FV=FV_total, FW=FW_total, FZ=FZ_total,
            F=F_total, FT=FT, sistema_critico=zona.sistema_critico,
        )

        # === R1: vida humana ===
        # Para R1, RC/RM/RW/RZ só entram para risco de explosão ou
        # estruturas onde falhas internas comprometem vida (Tabela 2)
        explosao_ou_critico = (
            zona.explosao.value != "nenhum" or
            zona.tipo_para_LO in ("uti_bloco_cirurgico", "outras_partes_hospital")
        )
        R1_zona = RA + RB + RU_total + RV_total
        if explosao_ou_critico:
            R1_zona += RC + RM + RW_total + RZ_total
        rz.R1 = R1_zona
        R1_total += R1_zona

        # === R3: patrimônio cultural ===
        if e.patrimonio_cultural and zona.cz > 0:
            ct_total = sum(z.cz for z in projeto.zonas) or 1.0
            LB_L3 = calcular_LB_L3(zona, ct_total)
            LV_L3 = LB_L3
            RB_L3 = ND * PB * LB_L3
            RV_L3 = (NL_total + NDJ) * sum(calcular_PV(l) for l in projeto.linhas) / max(len(projeto.linhas), 1) * LV_L3 if projeto.linhas else 0.0
            rz.R3 = RB_L3 + RV_L3
            R3_total += rz.R3

        # === R4: perda econômica (Anexo D) — simplificado ===
        if projeto.avaliar_R4:
            # Para protótipo: aplica a fórmula equivalente a L1 mas com perdas L4
            # Implementação completa exigiria ca/cb/cc/cs por zona
            LB_L4 = _fator_rp(zona) * _fator_rf(zona) * T.LF_VALORES_L4.get(zona.tipo_para_LF, 0.1)
            LC_L4 = T.LO_VALORES_L4.get(zona.tipo_para_LO, 1e-4)
            LA_L4 = T.RT_VALORES[zona.superficie_solo.value] * T.LT_VALORES_L4["todos_tipos_animais"]

            R4_estrutura = (
                ND * PB * LB_L4 +
                ND * PC * LC_L4 +
                NM * PM * LC_L4 +
                ND * T.PB_VALORES[e.nivel_protecao_spda.value] * LA_L4
            )
            R4_linhas = 0.0
            if projeto.linhas:
                for linha in projeto.linhas:
                    NL_l = NL_por_linha[linha.nome]
                    NI_l = NI_por_linha[linha.nome]
                    R4_linhas += (NL_l + NDJ) * calcular_PV(linha) * LB_L4
                    R4_linhas += (NL_l + NDJ) * calcular_PW(e, linha) * LC_L4
                    R4_linhas += NI_l * calcular_PZ(e, linha) * LC_L4
            rz.R4 = R4_estrutura + R4_linhas
            R4_total += rz.R4

        resultado.zonas.append(rz)

    resultado.R1 = R1_total
    resultado.R3 = R3_total
    resultado.R4 = R4_total
    return resultado
