"""Motor de análise de risco SPDA conforme ABNT NBR 5419-2:2026."""
from .modelo import (
    Estrutura,
    Zona,
    Linha,
    Projeto,
    TipoLinha,
    InstalacaoLinha,
    AmbienteLinha,
    LocalizacaoEstrutura,
    NivelProtecao,
    RiscoIncendio,
    Explosao,
    PerigoEspecial,
    SuperficieSolo,
    ProvidenciasIncendio,
    TipoEstrutura,
    BlindagemLinha,
)
from .calculo import calcular_projeto, ResultadoProjeto, ResultadoZona, ResultadoComponente
from .tabelas import RT_R1, RT_R3, RT_R4
