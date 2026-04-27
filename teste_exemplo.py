"""Teste rápido do motor de cálculo — caso exemplo de uma residência simples.

Executar: python teste_exemplo.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from nbr5419 import (
    AmbienteLinha,
    BlindagemLinha,
    Estrutura,
    InstalacaoLinha,
    Linha,
    LocalizacaoEstrutura,
    NivelProtecao,
    Projeto,
    RT_R1,
    SuperficieSolo,
    TipoEstrutura,
    TipoLinha,
    Zona,
    calcular_projeto,
)


def main():
    # Caso exemplo: residência 2 andares, 4 pessoas, em área urbana
    projeto = Projeto(
        nome="Residência exemplo",
        estrutura=Estrutura(
            nome="Casa",
            municipio="São Paulo",
            uf="SP",
            L=15.0,
            W=10.0,
            H=6.0,
            NG=8.0,  # típico SP capital
            localizacao=LocalizacaoEstrutura.CERCADA_MESMA_ALTURA_OU_MENOR,
            n_total_pessoas=4,
            tipo_construcao=TipoEstrutura.ROBUSTA,
            nivel_protecao_spda=NivelProtecao.SEM_SPDA,
        ),
        zonas=[
            Zona(
                nome="Residência interior",
                n_pessoas=4,
                horas_presenca_ano=8000,
                superficie_solo=SuperficieSolo.MARMORE_CERAMICA,
                tipo_para_LF="outros",
                tipo_para_LO="outros",
                UW=2.5,
            ),
        ],
        linhas=[
            Linha(
                nome="Energia BT (concessionária)",
                tipo=TipoLinha.ENERGIA,
                instalacao=InstalacaoLinha.AEREA,
                ambiente=AmbienteLinha.URBANO,
                bt_ou_at="bt_ou_sinal",
                LL=200,
                UW=2.5,
                blindagem_eqp="aerea_nao_blindada",
                blindagem_pld=BlindagemLinha.NAO_BLINDADA,
            ),
        ],
    )

    res = calcular_projeto(projeto)

    print("=" * 60)
    print(f"PROJETO: {projeto.nome}")
    print("=" * 60)
    print(f"AD = {res.AD:,.0f} m²    AM = {res.AM:,.0f} m²")
    print(f"ND = {res.ND:.3e}        NM = {res.NM:.3e}")
    print(f"NL = {res.NL_total:.3e}  NI = {res.NI_total:.3e}")
    print()
    for rz in res.zonas:
        print(f"Zona: {rz.nome}")
        print(f"  {'Comp':<6} {'N':>12} {'P':>12} {'L':>12} {'R':>12}")
        for nome, c in rz.componentes.items():
            print(f"  {nome:<6} {c.N:>12.3e} {c.P:>12.3e} {c.L:>12.3e} {c.R:>12.3e}")
        print(f"  R1 zona: {rz.R1:.3e}")
    print()
    print(f"R1 total:   {res.R1:.3e}")
    print(f"RT (R1):    {RT_R1:.0e}")
    print(f"Status:     {'NECESSITA PROTEÇÃO' if res.R1 > RT_R1 else 'ACEITÁVEL'}")

    # Sanity checks
    assert res.AD > 0, "AD deve ser positivo"
    assert res.ND > 0, "ND deve ser positivo"
    assert res.NM > 0, "NM deve ser positivo"
    assert res.R1 > 0, "R1 deve ser positivo"
    print("\n[OK] Todos os sanity checks passaram.")


if __name__ == "__main__":
    main()
