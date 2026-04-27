"""Modelo de dados para análise de risco SPDA conforme ABNT NBR 5419-2:2026.

Hierarquia:
  Projeto
    ├── Estrutura (dimensões, localização, NG)
    ├── Zona[]   (subdivisões com características homogêneas)
    └── Linha[]  (linhas de energia/sinal conectadas)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# =============================================================================
# Enums - escolhas categóricas com chaves estáveis
# =============================================================================
class TipoLinha(str, Enum):
    ENERGIA = "energia"
    SINAL = "sinal"


class InstalacaoLinha(str, Enum):
    AEREA = "aerea"
    ENTERRADA = "enterrada"
    ENTERRADA_EM_MALHA = "enterrada_em_malha"


class AmbienteLinha(str, Enum):
    RURAL = "rural"
    SUBURBANO = "suburbano"
    URBANO = "urbano"
    URBANO_ALTO = "urbano_alto"


class LocalizacaoEstrutura(str, Enum):
    CERCADA_OBJETOS_MAIS_ALTOS = "cercada_objetos_mais_altos"
    CERCADA_MESMA_ALTURA_OU_MENOR = "cercada_mesma_altura_ou_menor"
    ISOLADA = "isolada"
    ISOLADA_NO_TOPO_DE_COLINA = "isolada_no_topo_de_colina"


class NivelProtecao(str, Enum):
    SEM_SPDA = "sem_spda"
    NPIV = "npiv"
    NPIII = "npiii"
    NPII = "npii"
    NPI = "npi"
    NPI_CAPACAO_NATURAL = "npi_capacao_natural"
    COBERTURA_METALICA_NATURAL = "cobertura_metalica_natural"


class RiscoIncendio(str, Enum):
    NENHUM = "nenhum"
    BAIXO = "incendio_baixo"
    NORMAL = "incendio_normal"
    ALTO = "incendio_alto"


class Explosao(str, Enum):
    NENHUMA = "nenhum"
    Z2_Z22 = "explosao_z2_z22"
    Z1_Z21 = "explosao_z1_z21"
    Z0_Z20_SOLIDOS = "explosao_z0_z20_solidos"


class PerigoEspecial(str, Enum):
    SEM_PERIGO = "sem_perigo"
    BAIXO_PANICO = "baixo_panico"
    MEDIO_PANICO = "medio_panico"
    DIFICULDADE_EVACUACAO = "dificuldade_evacuacao"
    ALTO_PANICO = "alto_panico"


class SuperficieSolo(str, Enum):
    TERRA_CONCRETO = "terra_concreto"
    MARMORE_CERAMICA = "marmore_ceramica"
    BRITA_TAPETE_CARPETE = "brita_tapete_carpete"
    ASFALTO_LINOLEO_MADEIRA = "asfalto_linoleo_madeira"


class ProvidenciasIncendio(str, Enum):
    NENHUMA = "nenhuma_ou_explosao"
    MANUAIS = "manuais_basicas"
    AUTOMATICAS = "automaticas"


class TipoEstrutura(str, Enum):
    SIMPLES = "simples"
    ROBUSTA = "robusta"


class BlindagemLinha(str, Enum):
    NAO_BLINDADA = "nao_blindada"
    BLINDADA_5A20 = "blindada_5a20"
    BLINDADA_1A5 = "blindada_1a5"
    BLINDADA_MENOR_1 = "blindada_menor_1"


# =============================================================================
# Entidades
# =============================================================================
@dataclass
class Estrutura:
    """Estrutura sob análise.

    Dimensões em metros. NG em raios/km²/ano (consultar Anexo F ou Tabela F.1).
    """
    nome: str = "Estrutura sob análise"
    municipio: str = ""
    uf: str = ""
    L: float = 20.0  # comprimento (m)
    W: float = 10.0  # largura (m)
    H: float = 6.0   # altura (m)
    HP: float = 0.0  # altura de saliência elevada na cobertura (0 se não houver)
    AD_manual: Optional[float] = None  # se preenchido, sobrescreve cálculo via Eq A.1 (m²)
    NG: float = 5.0  # densidade de descargas atmosféricas (raios/km²/ano)
    localizacao: LocalizacaoEstrutura = LocalizacaoEstrutura.ISOLADA
    estrutura_adjacente_AD: float = 0.0  # AD da estrutura adjacente (NDJ)
    n_total_pessoas: int = 1  # nt - usado para razão nz/nt nas perdas

    # Características da construção
    tipo_construcao: TipoEstrutura = TipoEstrutura.ROBUSTA  # rs

    # SPDA
    nivel_protecao_spda: NivelProtecao = NivelProtecao.SEM_SPDA
    pta_medidas: list[str] = field(default_factory=lambda: ["nenhuma"])  # combináveis

    # Sistema coordenado de DPS (B.4)
    pspd_nivel: str = "nenhum"  # chave da tabela PSPD_VALORES

    # Fator KS1 do SPDA (B.4.12) - largura da malha (m). 0 = não calcular, usar PMS=1
    spda_largura_malha: float = 0.0  # wm1 (m); KS1 = 0,12 * wm1; cont. metálica → KS1=1e-4
    spda_blindagem_continua: bool = False  # se True, KS1 = 1e-4

    # Patrimônio cultural (R3)?
    patrimonio_cultural: bool = False
    valor_patrimonio_zona_cz: float = 0.0  # cz / ct será calculado se cultural


@dataclass
class Zona:
    """Zona de estudo da estrutura (6.7).

    Cada zona tem características homogêneas: piso, compartimentação, sistemas internos.
    """
    nome: str
    n_pessoas: int = 1  # nz
    horas_presenca_ano: float = 8760  # tz (h/ano), máx 8760

    # Reduções/aumentos para perdas L1
    superficie_solo: SuperficieSolo = SuperficieSolo.TERRA_CONCRETO  # rt
    risco_incendio: RiscoIncendio = RiscoIncendio.BAIXO  # rf
    explosao: Explosao = Explosao.NENHUMA  # rf (sobrescreve incêndio se != NENHUMA)
    providencias_incendio: ProvidenciasIncendio = ProvidenciasIncendio.NENHUMA  # rp
    perigo_especial: PerigoEspecial = PerigoEspecial.SEM_PERIGO  # hz

    # Tipo da estrutura para classificar LF (Tabela C.2)
    tipo_para_LF: str = "outros"
    tipo_para_LO: str = "outros"

    # KS2 (B.4.12) - blindagem espacial interna (m). 0 = sem blindagem extra
    blindagem_largura_malha: float = 0.0  # wm2 (m)
    blindagem_continua: bool = False  # KS2 = 1e-4

    # KS3 - fiação interna (Tabela B.5)
    fiacao_interna: str = "nao_blindado_sem_preocupacao"

    # Comprimento da fiação interna (m). KS3 escala proporcionalmente p/ <100m
    fiacao_comprimento: float = 100.0

    # KS4 - tensão suportável de impulso UW (kV) do sistema interno
    UW: float = 2.5

    # Para R3 (patrimônio cultural) - valor relativo da zona
    cz: float = 0.0  # valor do patrimônio cultural na zona

    # === Seção 7 — Frequência de danos F ===
    sistema_critico: bool = False
    """Sistemas internos críticos (afetam comunidade): FT = 0,1/ano (fixo).
    Sistemas não críticos: FT = 1/ano (representativo)."""

    equipamentos_em_ZPR0A: bool = False
    """Se True, FB é calculado (equipamento exposto a descarga direta).
    Se False, FB = 0 (equipamentos em ZPR subsequentes). Padrão: False (7.1.5)."""


@dataclass
class Linha:
    """Linha elétrica conectada à estrutura (energia ou sinal)."""
    nome: str
    tipo: TipoLinha = TipoLinha.ENERGIA
    instalacao: InstalacaoLinha = InstalacaoLinha.AEREA
    ambiente: AmbienteLinha = AmbienteLinha.URBANO
    bt_ou_at: str = "bt_ou_sinal"  # CT (chave da Tabela A.3)
    LL: float = 1000.0  # comprimento do trecho (m); padrão norma se desconhecido
    UW: float = 2.5  # tensão suportável de impulso (kV) do equipamento

    # Tipo de blindagem/EQP da linha (Tabela B.4)
    blindagem_eqp: str = "aerea_nao_blindada"  # CLD/CLI

    # PLD - blindagem para a tabela B.8
    blindagem_pld: BlindagemLinha = BlindagemLinha.NAO_BLINDADA

    # Medidas contra tensão de toque na entrada (PTU - Tabela B.6)
    ptu_medida: str = "nenhuma"

    # DPS classe I para EQP (PEB - Tabela B.7)
    peb_nivel: str = "sem_dps"


@dataclass
class Projeto:
    """Projeto completo de análise de risco."""
    nome: str = "Projeto NBR 5419-2"
    estrutura: Estrutura = field(default_factory=Estrutura)
    zonas: list[Zona] = field(default_factory=lambda: [Zona(nome="Zona única")])
    linhas: list[Linha] = field(default_factory=list)

    # Avaliar R4 (econômico)?
    avaliar_R4: bool = False
    valor_total_ct: float = 1.0  # para Anexo D
