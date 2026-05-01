"""Análise de Risco SPDA — ABNT NBR 5419-2:2026.

Aplicativo Streamlit (protótipo). Para executar:
    pip install -r requirements.txt
    streamlit run app.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Garante que o pacote local seja encontrado
sys.path.insert(0, str(Path(__file__).parent / "src"))

from nbr5419.auth import exigir_login, botao_logout, is_admin, hash_senha
from nbr5419 import (
    AmbienteLinha,
    BlindagemLinha,
    Estrutura,
    Explosao,
    InstalacaoLinha,
    Linha,
    LocalizacaoEstrutura,
    NivelProtecao,
    PerigoEspecial,
    Projeto,
    ProvidenciasIncendio,
    RiscoIncendio,
    SuperficieSolo,
    TipoEstrutura,
    TipoLinha,
    Zona,
    calcular_projeto,
    RT_R1,
    RT_R3,
    RT_R4,
)
from nbr5419 import tabelas as T


# =============================================================================
# Configuração
# =============================================================================
st.set_page_config(
    page_title="Análise de Risco SPDA — NBR 5419-2",
    page_icon="⚡",
    layout="wide",
)

# === LOGIN GATE — bloqueia tudo até o usuário se autenticar ===
usuario_logado = exigir_login()

DATA_DIR = Path(__file__).parent / "data"
NG_CSV = DATA_DIR / "ng_municipios.csv"


@st.cache_data
def carregar_ng() -> pd.DataFrame:
    if not NG_CSV.exists():
        return pd.DataFrame(columns=["municipio", "uf", "ng"])
    return pd.read_csv(NG_CSV)


def init_state():
    if "projeto" not in st.session_state:
        st.session_state.projeto = Projeto()


init_state()
ng_df = carregar_ng()


# =============================================================================
# Sidebar — navegação
# =============================================================================
st.sidebar.title("⚡ NBR 5419-2")
st.sidebar.caption("Análise de Risco SPDA")
st.sidebar.markdown("---")

opcoes_menu = [
    "1. Localização e NG",
    "2. Estrutura",
    "3. Zonas de estudo",
    "4. Linhas conectadas",
    "5. Medidas de proteção",
    "6. Resultados",
    "📚 Glossário",
]
if is_admin():
    opcoes_menu.append("🛡️ Painel Admin")

etapa = st.sidebar.radio(
    "Etapas",
    opcoes_menu,
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Referências normativas**")
st.sidebar.caption(
    "ABNT NBR 5419-1: Princípios gerais\n\n"
    "ABNT NBR 5419-2: Análise de risco\n\n"
    "ABNT NBR 5419-3: Danos físicos\n\n"
    "ABNT NBR 5419-4: Sistemas internos"
)


# =============================================================================
# Helpers de UI
# =============================================================================
def select_from_dict(label: str, options: dict[str, str], chave_atual: str,
                     help: str | None = None, key: str | None = None) -> str:
    """Selectbox que mostra labels mas retorna a chave."""
    chaves = list(options.keys())
    labels = list(options.values())
    idx = chaves.index(chave_atual) if chave_atual in chaves else 0
    label_escolhido = st.selectbox(label, labels, index=idx, help=help, key=key)
    return chaves[labels.index(label_escolhido)]


def numero_cientifico(x: float, casas: int = 3) -> str:
    if x == 0:
        return "0"
    return f"{x:.{casas}e}"


# =============================================================================
# ETAPA 1 — Localização e NG
# =============================================================================
def etapa_localizacao():
    st.header("1️⃣ Localização e densidade de descargas atmosféricas")
    st.markdown(
        "A densidade de descargas atmosféricas **NG (raios/km²/ano)** vem da "
        "**Tabela F.1 do Anexo F** da NBR 5419-2. Selecione o município ou "
        "informe NG manualmente."
    )

    e = st.session_state.projeto.estrutura

    col1, col2 = st.columns(2)
    with col1:
        e.nome = st.text_input("Nome da estrutura/projeto", value=e.nome)
        if not ng_df.empty:
            ufs = ["—"] + sorted(ng_df["uf"].unique().tolist())
            uf_atual_idx = ufs.index(e.uf) if e.uf in ufs else 0
            uf = st.selectbox("UF", ufs, index=uf_atual_idx)
            e.uf = uf if uf != "—" else ""

            if e.uf:
                municipios = ng_df[ng_df["uf"] == e.uf]["municipio"].sort_values().tolist()
                mun_atual_idx = municipios.index(e.municipio) if e.municipio in municipios else 0
                e.municipio = st.selectbox("Município", municipios, index=mun_atual_idx)
                ng_lookup = ng_df[
                    (ng_df["uf"] == e.uf) & (ng_df["municipio"] == e.municipio)
                ]["ng"].values
                if len(ng_lookup) > 0:
                    e.NG = float(ng_lookup[0])
        else:
            st.warning("Base NG não encontrada — informe manualmente.")

    with col2:
        e.NG = st.number_input(
            "NG (raios/km²/ano)",
            min_value=0.0, max_value=100.0, value=float(e.NG), step=0.5,
            help="Densidade de descargas atmosféricas para a terra. "
                 "Tabela F.1 da NBR 5419-2:2026 (Anexo F).",
        )
        if e.NG > 0:
            st.metric("NG selecionado", f"{e.NG} raios/km²/ano")
            if e.NG <= 4:
                nivel = "🟢 Baixo"
            elif e.NG <= 12:
                nivel = "🟡 Médio"
            elif e.NG <= 20:
                nivel = "🟠 Alto"
            else:
                nivel = "🔴 Muito alto"
            st.caption(f"Nível de exposição: **{nivel}**")

    st.info(
        "ℹ️ A norma exige uso exclusivo dos valores do Anexo F — "
        "outras fontes não podem ser utilizadas para a análise de risco normativa."
    )


# =============================================================================
# ETAPA 2 — Estrutura
# =============================================================================
def etapa_estrutura():
    st.header("2️⃣ Características da estrutura")

    e = st.session_state.projeto.estrutura

    st.subheader("Dimensões")
    col1, col2, col3 = st.columns(3)
    with col1:
        e.L = st.number_input(
            "Comprimento L (m)", min_value=0.1, value=float(e.L), step=1.0,
            help="Maior dimensão horizontal da estrutura.",
        )
    with col2:
        e.W = st.number_input(
            "Largura W (m)", min_value=0.1, value=float(e.W), step=1.0,
            help="Menor dimensão horizontal.",
        )
    with col3:
        e.H = st.number_input(
            "Altura H (m)", min_value=0.1, value=float(e.H), step=0.5,
            help="Altura total da estrutura.",
        )

    e.HP = st.number_input(
        "Altura de saliência elevada (HP, m)",
        min_value=0.0, value=float(e.HP), step=0.5,
        help="Apenas se houver saliência (caixa d'água, antena) significativamente "
             "mais alta que o resto da cobertura. Eq. A.2 da norma. 0 = sem saliência.",
    )

    st.subheader("Área de exposição equivalente AD (Ae)")
    usar_ad_manual = st.checkbox(
        "Informar AD manualmente (método gráfico — Seção A.2.1.3)",
        value=(e.AD_manual is not None),
        help="Marque se você já calculou AD por método gráfico (estruturas com forma "
             "complexa, saliências múltiplas, perfis irregulares). Se desmarcado, "
             "AD é calculado automaticamente pela Eq. A.1 a partir de L, W e H.",
    )

    if usar_ad_manual:
        valor_inicial = float(e.AD_manual) if e.AD_manual is not None else 0.0
        e.AD_manual = st.number_input(
            "AD manual (m²)",
            min_value=0.0, value=valor_inicial, step=10.0,
            help="Área de exposição equivalente determinada graficamente. "
                 "Substitui o cálculo por Eq. A.1.",
        )
        if e.AD_manual > 0:
            from nbr5419.calculo import area_AD as _calc_AD
            ad_eq = _calc_AD(e.L, e.W, e.H)
            delta = (e.AD_manual - ad_eq) / ad_eq * 100 if ad_eq > 0 else 0
            st.caption(
                f"ℹ️ AD pela Eq. A.1 com L×W×H seria {ad_eq:,.0f} m² — "
                f"sua entrada difere em {delta:+.1f}%."
            )
    else:
        e.AD_manual = None

    st.subheader("Localização e construção")
    col1, col2 = st.columns(2)
    with col1:
        loc_chave = select_from_dict(
            "Localização relativa (Tabela A.1 — fator CD)",
            T.CD_LABELS,
            e.localizacao.value,
            help="Posição da estrutura em relação às edificações vizinhas. "
                 "Estruturas isoladas em colinas captam mais raios.",
        )
        e.localizacao = LocalizacaoEstrutura(loc_chave)

    with col2:
        tipo_chave = select_from_dict(
            "Tipo de construção (Tabela C.7 — fator rs)",
            T.RS_LABELS,
            e.tipo_construcao.value,
            help="Construções simples têm maior probabilidade de propagação de fogo.",
        )
        e.tipo_construcao = TipoEstrutura(tipo_chave)

    st.subheader("Pessoas")
    e.n_total_pessoas = st.number_input(
        "Número total de pessoas na estrutura (nt)",
        min_value=1, value=int(e.n_total_pessoas), step=1,
        help="Usado para calcular a razão nz/nt em cada zona.",
    )

    st.subheader("Patrimônio cultural (R3)")
    e.patrimonio_cultural = st.checkbox(
        "Estrutura possui patrimônio cultural relevante (calcular R3)",
        value=e.patrimonio_cultural,
    )

    # Preview áreas
    from nbr5419.calculo import area_AD, area_AM
    if e.AD_manual is not None and e.AD_manual > 0:
        AD = e.AD_manual
        AD_label = "Área AD (manual)"
    else:
        AD = area_AD(e.L, e.W, e.H)
        AD_label = "Área AD (Eq. A.1)"
    AM = area_AM(e.L, e.W)
    col1, col2, col3 = st.columns(3)
    col1.metric(AD_label, f"{AD:,.0f} m²")
    col2.metric("Área AM (Eq. A.6)", f"{AM:,.0f} m²")
    col3.metric("CD (Tabela A.1)", T.CD_VALORES[e.localizacao.value])


# =============================================================================
# ETAPA 3 — Zonas de estudo
# =============================================================================
def etapa_zonas():
    st.header("3️⃣ Zonas de estudo")
    st.markdown(
        "Divida a estrutura em **zonas de estudo (ZS)** — áreas com "
        "características homogêneas (piso, compartimentação, sistemas internos). "
        "Para uma análise simples, **uma zona única** já é suficiente. "
        "Hospitais, indústrias e edifícios mistos costumam exigir múltiplas zonas."
    )

    p = st.session_state.projeto

    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"**{len(p.zonas)} zona(s) cadastrada(s)**")
    with col2:
        if st.button("➕ Adicionar zona"):
            p.zonas.append(Zona(nome=f"Zona {len(p.zonas) + 1}"))
            st.rerun()

    for idx, zona in enumerate(p.zonas):
        with st.expander(f"📍 {zona.nome}", expanded=(len(p.zonas) == 1)):
            col1, col2 = st.columns([3, 1])
            with col1:
                zona.nome = st.text_input("Nome da zona", value=zona.nome, key=f"zn_{idx}")
            with col2:
                if len(p.zonas) > 1 and st.button("🗑️ Remover", key=f"rmz_{idx}"):
                    p.zonas.pop(idx)
                    st.rerun()

            col1, col2 = st.columns(2)
            with col1:
                zona.n_pessoas = st.number_input(
                    "Pessoas na zona (nz)", min_value=0, value=int(zona.n_pessoas),
                    key=f"nz_{idx}",
                    help="Quantas pessoas frequentam esta zona.",
                )
            with col2:
                zona.horas_presenca_ano = st.number_input(
                    "Tempo de presença (tz, h/ano)",
                    min_value=0.0, max_value=8760.0, value=float(zona.horas_presenca_ano),
                    step=100.0, key=f"tz_{idx}",
                    help="Total de horas/ano que pessoas estão na zona. Máx 8760.",
                )

            st.markdown("**Características físicas (afetam perdas L1)**")
            col1, col2 = st.columns(2)
            with col1:
                solo_chave = select_from_dict(
                    "Superfície do solo/piso (Tabela C.3 — rt)",
                    T.RT_LABELS,
                    zona.superficie_solo.value,
                    help="Resistência de contato — afeta tensão de toque/passo.",
                    key=f"solo_{idx}",
                )
                zona.superficie_solo = SuperficieSolo(solo_chave)

                inc_chave = select_from_dict(
                    "Risco de incêndio (Tabela C.5 — rf)",
                    {k: v for k, v in T.RF_LABELS.items() if k.startswith("incendio") or k == "nenhum"},
                    zona.risco_incendio.value,
                    help="Carga de incêndio: alto ≥ 800 MJ/m², normal 400-800, baixo < 400.",
                    key=f"inc_{idx}",
                )
                zona.risco_incendio = RiscoIncendio(inc_chave)

            with col2:
                exp_chave = select_from_dict(
                    "Risco de explosão (Tabela C.5 — rf, sobrescreve incêndio)",
                    {k: v for k, v in T.RF_LABELS.items() if k.startswith("explosao") or k == "nenhum"},
                    zona.explosao.value,
                    help="Zonas conforme NBR IEC 60079-10. 'Nenhum' = sem explosão.",
                    key=f"exp_{idx}",
                )
                zona.explosao = Explosao(exp_chave)

                prov_chave = select_from_dict(
                    "Providências contra incêndio (Tabela C.4 — rp)",
                    T.RP_LABELS,
                    zona.providencias_incendio.value,
                    key=f"prov_{idx}",
                )
                zona.providencias_incendio = ProvidenciasIncendio(prov_chave)

            perigo_chave = select_from_dict(
                "Perigo especial (Tabela C.6 — hz)",
                T.HZ_LABELS,
                zona.perigo_especial.value,
                key=f"hz_{idx}",
                help="Pânico ou dificuldade de evacuação aumentam a perda relativa.",
            )
            zona.perigo_especial = PerigoEspecial(perigo_chave)

            st.markdown("**Tipo da zona (define LF e LO da Tabela C.2)**")
            col1, col2 = st.columns(2)
            with col1:
                zona.tipo_para_LF = select_from_dict(
                    "Tipo para LF (danos físicos)",
                    T.LF_VALORES_L1_LABELS,
                    zona.tipo_para_LF,
                    key=f"lf_{idx}",
                )
            with col2:
                zona.tipo_para_LO = select_from_dict(
                    "Tipo para LO (falha de sistemas internos)",
                    T.LO_VALORES_L1_LABELS,
                    zona.tipo_para_LO,
                    key=f"lo_{idx}",
                )

            st.markdown("**Sistemas internos (afetam PM e PC)**")
            col1, col2 = st.columns(2)
            with col1:
                fiacao_chave = select_from_dict(
                    "Fiação interna (Tabela B.5 — KS3)",
                    T.KS3_LABELS,
                    zona.fiacao_interna,
                    key=f"fi_{idx}",
                )
                zona.fiacao_interna = fiacao_chave
                zona.fiacao_comprimento = st.number_input(
                    "Comprimento da fiação interna (m)",
                    min_value=0.0, value=float(zona.fiacao_comprimento), step=10.0,
                    key=f"fi_l_{idx}",
                    help="Para circuitos < 100 m, KS3 é reduzido proporcionalmente.",
                )
            with col2:
                zona.UW = st.number_input(
                    "Tensão suportável de impulso UW (kV)",
                    min_value=0.35, value=float(zona.UW), step=0.5,
                    key=f"uw_{idx}",
                    help="Menor UW entre os equipamentos da zona. Valores típicos: "
                         "0,35 (eletrônica sensível); 1,5 (TI); 2,5 (eletrodomésticos); "
                         "4,0 (motores BT); 6,0 (entrada de serviço).",
                )

            with st.expander("🔧 Blindagem espacial interna (avançado — KS2)"):
                zona.blindagem_largura_malha = st.number_input(
                    "Largura da malha de blindagem (wm2, m). 0 = sem blindagem extra",
                    min_value=0.0, value=float(zona.blindagem_largura_malha), step=0.5,
                    key=f"bl_{idx}",
                )
                zona.blindagem_continua = st.checkbox(
                    "Blindagem metálica contínua (KS2 = 1e-4)",
                    value=zona.blindagem_continua,
                    key=f"blc_{idx}",
                )

            if st.session_state.projeto.estrutura.patrimonio_cultural:
                zona.cz = st.number_input(
                    "Valor relativo do patrimônio cultural na zona (cz)",
                    min_value=0.0, value=float(zona.cz), step=1.0,
                    key=f"cz_{idx}",
                    help="Valor monetário ou relativo. Será dividido pela soma de todas as zonas (ct).",
                )

            st.markdown("**Frequência de danos F (Seção 7) — independente da análise R**")
            col1, col2 = st.columns(2)
            with col1:
                zona.sistema_critico = st.checkbox(
                    "Sistema interno crítico (FT = 0,1/ano)",
                    value=zona.sistema_critico,
                    key=f"sc_{idx}",
                    help="Sistema crítico: falha pode afetar uma comunidade (cidade, "
                         "região, bairro etc.) com perdas irreversíveis ou danos físicos. "
                         "FT = 0,1/ano (fixo). Não crítico: FT = 1/ano (representativo).",
                )
            with col2:
                zona.equipamentos_em_ZPR0A = st.checkbox(
                    "Equipamentos em ZPR0A (calcular FB)",
                    value=zona.equipamentos_em_ZPR0A,
                    key=f"zpr0a_{idx}",
                    help="Marque se há equipamentos isolados ou no topo da estrutura "
                         "expostos a descarga atmosférica direta. Caso contrário, FB = 0 "
                         "(NBR 5419-2, item 7.1.5).",
                )


# =============================================================================
# ETAPA 4 — Linhas
# =============================================================================
def etapa_linhas():
    st.header("4️⃣ Linhas elétricas conectadas")
    st.markdown(
        "Linhas conectadas (energia, sinal/dados) são a principal porta de entrada de "
        "surtos. **Considere todas as linhas que entram na estrutura.** "
        "Se não houver linha externa (estrutura isolada), pode-se prosseguir sem cadastrar nenhuma."
    )

    p = st.session_state.projeto

    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"**{len(p.linhas)} linha(s) cadastrada(s)**")
    with col2:
        if st.button("➕ Adicionar linha"):
            p.linhas.append(Linha(nome=f"Linha {len(p.linhas) + 1}"))
            st.rerun()

    for idx, linha in enumerate(p.linhas):
        with st.expander(f"⚡ {linha.nome}", expanded=(len(p.linhas) == 1)):
            col1, col2 = st.columns([3, 1])
            with col1:
                linha.nome = st.text_input("Nome", value=linha.nome, key=f"ln_{idx}")
            with col2:
                if st.button("🗑️ Remover", key=f"rml_{idx}"):
                    p.linhas.pop(idx)
                    st.rerun()

            col1, col2, col3 = st.columns(3)
            with col1:
                tipo = st.selectbox(
                    "Tipo", ["Energia", "Sinal/Dados"],
                    index=0 if linha.tipo == TipoLinha.ENERGIA else 1,
                    key=f"tp_{idx}",
                )
                linha.tipo = TipoLinha.ENERGIA if tipo == "Energia" else TipoLinha.SINAL
            with col2:
                linha.LL = st.number_input(
                    "Comprimento LL (m)",
                    min_value=0.0, value=float(linha.LL), step=100.0,
                    key=f"ll_{idx}",
                    help="Comprimento até o próximo nó/transformador. Padrão da norma se desconhecido: 1000 m.",
                )
            with col3:
                linha.UW = st.number_input(
                    "UW do equipamento (kV)",
                    min_value=0.35, value=float(linha.UW), step=0.5,
                    key=f"luw_{idx}",
                )

            col1, col2 = st.columns(2)
            with col1:
                inst_chave = select_from_dict(
                    "Instalação (Tabela A.2 — CI)",
                    T.CI_LABELS,
                    linha.instalacao.value,
                    key=f"inst_{idx}",
                )
                linha.instalacao = InstalacaoLinha(inst_chave)

                amb_chave = select_from_dict(
                    "Ambiente (Tabela A.4 — CE)",
                    T.CE_LABELS,
                    linha.ambiente.value,
                    key=f"amb_{idx}",
                )
                linha.ambiente = AmbienteLinha(amb_chave)

            with col2:
                bt_chave = select_from_dict(
                    "Tipo da linha (Tabela A.3 — CT)",
                    T.CT_LABELS,
                    linha.bt_ou_at,
                    key=f"bt_{idx}",
                )
                linha.bt_ou_at = bt_chave

                blind_eqp_chave = select_from_dict(
                    "Blindagem e ligação equipotencial (Tabela B.4 — CLD/CLI)",
                    T.CLD_CLI_LABELS,
                    linha.blindagem_eqp,
                    key=f"be_{idx}",
                    help="Caracteriza como a linha entra na estrutura e se há equipotencialização.",
                )
                linha.blindagem_eqp = blind_eqp_chave

            blindagem_pld_labels = {
                BlindagemLinha.NAO_BLINDADA.value: T.PLD_LABELS["nao_blindada"],
                BlindagemLinha.BLINDADA_5A20.value: T.PLD_LABELS["blindada_5a20"],
                BlindagemLinha.BLINDADA_1A5.value: T.PLD_LABELS["blindada_1a5"],
                BlindagemLinha.BLINDADA_MENOR_1.value: T.PLD_LABELS["blindada_menor_1"],
            }
            blind_pld_chave = select_from_dict(
                "Resistência da blindagem (Tabela B.8 — PLD)",
                blindagem_pld_labels,
                linha.blindagem_pld.value,
                key=f"bp_{idx}",
            )
            linha.blindagem_pld = BlindagemLinha(blind_pld_chave)

            st.markdown("**Medidas na entrada da linha**")
            col1, col2 = st.columns(2)
            with col1:
                linha.ptu_medida = select_from_dict(
                    "Proteção contra tensão de toque na entrada (Tabela B.6 — PTU)",
                    T.PTU_LABELS,
                    linha.ptu_medida,
                    key=f"ptu_{idx}",
                )
            with col2:
                linha.peb_nivel = select_from_dict(
                    "DPS classe I para equipotencialização (Tabela B.7 — PEB)",
                    T.PEB_LABELS,
                    linha.peb_nivel,
                    key=f"peb_{idx}",
                )


# =============================================================================
# ETAPA 5 — Medidas globais
# =============================================================================
def etapa_medidas():
    st.header("5️⃣ Medidas de proteção globais (SPDA + DPS coordenado)")

    e = st.session_state.projeto.estrutura

    st.subheader("SPDA — Sistema de Proteção contra Descargas Atmosféricas")
    npiv_chave = select_from_dict(
        "Nível de proteção do SPDA (Tabela B.2 — PB)",
        T.PB_LABELS,
        e.nivel_protecao_spda.value,
        help="NP I é o mais rigoroso (PB = 0,02). Sem SPDA: PB = 1,0.",
    )
    e.nivel_protecao_spda = NivelProtecao(npiv_chave)

    st.subheader("Medidas adicionais contra tensão de toque/passo (PTA)")
    st.caption("Selecione todas as medidas aplicáveis (combinam multiplicativamente)")
    medidas_disponiveis = list(T.PTA_LABELS.keys())
    medidas_disponiveis.remove("nenhuma")  # 'nenhuma' é o default quando nada é selecionado
    selecionadas = st.multiselect(
        "Medidas adicionais (Tabela B.1 — PTA)",
        medidas_disponiveis,
        default=[m for m in e.pta_medidas if m != "nenhuma"],
        format_func=lambda k: T.PTA_LABELS[k],
    )
    e.pta_medidas = selecionadas if selecionadas else ["nenhuma"]

    st.subheader("Sistema coordenado de DPS (PSPD)")
    pspd_chave = select_from_dict(
        "Nível do sistema coordenado de DPS (Tabela B.3 — PSPD)",
        T.PSPD_LABELS,
        e.pspd_nivel,
        help="Reduz PC e PM. Sem DPS coordenado: PSPD = 1,0.",
    )
    e.pspd_nivel = pspd_chave

    with st.expander("🔧 Blindagem do SPDA (avançado — KS1)"):
        st.caption(
            "Para reduzir PM, o SPDA externo do tipo malha pode atuar como blindagem. "
            "Informe a largura da malha (wm1) ou marque blindagem contínua."
        )
        col1, col2 = st.columns(2)
        with col1:
            e.spda_largura_malha = st.number_input(
                "Largura da malha do SPDA (wm1, m). 0 = não calcular",
                min_value=0.0, value=float(e.spda_largura_malha), step=0.5,
                help="KS1 = 0,12 × wm1, limitado a 1.",
            )
        with col2:
            e.spda_blindagem_continua = st.checkbox(
                "Blindagem metálica contínua (KS1 = 1e-4)",
                value=e.spda_blindagem_continua,
            )


# =============================================================================
# ETAPA 6 — Resultados
# =============================================================================
def etapa_resultados():
    st.header("6️⃣ Resultados — Análise de Risco")

    p = st.session_state.projeto
    res = calcular_projeto(p)

    # ---- Dashboard principal ----
    st.subheader("📊 Riscos totais")
    col1, col2, col3 = st.columns(3)
    with col1:
        delta_r1 = (res.R1 - RT_R1) / RT_R1
        st.metric(
            "R1 — Vida humana",
            numero_cientifico(res.R1),
            f"{'+' if delta_r1 > 0 else ''}{delta_r1*100:.0f}% vs RT",
            delta_color="inverse",
        )
        st.caption(f"Tolerável RT = {numero_cientifico(RT_R1)} y⁻¹")
        if res.R1 > RT_R1:
            st.error("🔴 **Proteção necessária** — R1 > RT")
        else:
            st.success("🟢 **Aceitável** — R1 ≤ RT")

    with col2:
        if p.estrutura.patrimonio_cultural:
            delta_r3 = (res.R3 - RT_R3) / RT_R3 if RT_R3 > 0 else 0
            st.metric(
                "R3 — Patrimônio cultural",
                numero_cientifico(res.R3),
                f"{'+' if delta_r3 > 0 else ''}{delta_r3*100:.0f}% vs RT",
                delta_color="inverse",
            )
            st.caption(f"Tolerável RT = {numero_cientifico(RT_R3)} y⁻¹")
            if res.R3 > RT_R3:
                st.error("🔴 Proteção necessária")
            else:
                st.success("🟢 Aceitável")
        else:
            st.metric("R3 — Patrimônio cultural", "n/a")
            st.caption("Não aplicável (patrimônio cultural desligado)")

    with col3:
        if p.avaliar_R4:
            st.metric("R4 — Perda econômica", numero_cientifico(res.R4))
            st.caption(f"Referência RT = {numero_cientifico(RT_R4)} y⁻¹ (informativo)")
        else:
            p.avaliar_R4 = st.checkbox("Calcular R4 (perda econômica - Anexo D)")

    # ---- Eventos N ----
    st.subheader("⚡ Eventos perigosos por ano (Anexo A)")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("ND", numero_cientifico(res.ND), help="Descargas na estrutura")
    col2.metric("NM", numero_cientifico(res.NM), help="Descargas próximas (até 500 m)")
    col3.metric("NL total", numero_cientifico(res.NL_total), help="Descargas em linhas conectadas")
    col4.metric("NI total", numero_cientifico(res.NI_total), help="Descargas próximas a linhas")

    st.caption(f"Áreas: AD = {res.AD:,.0f} m² | AM = {res.AM:,.0f} m²")

    # ---- Decomposição por componente ----
    st.subheader("🔬 Decomposição por componente de risco")
    if res.zonas:
        zona_idx = 0
        if len(res.zonas) > 1:
            zona_idx = st.selectbox(
                "Zona",
                range(len(res.zonas)),
                format_func=lambda i: res.zonas[i].nome,
            )
        rz = res.zonas[zona_idx]

        comp_data = []
        for nome, comp in rz.componentes.items():
            comp_data.append({
                "Componente": nome,
                "Descrição": comp.descricao,
                "N": comp.N,
                "P": comp.P,
                "L": comp.L,
                "R": comp.R,
                "% R1": (comp.R / rz.R1 * 100) if rz.R1 > 0 else 0,
            })
        df_comp = pd.DataFrame(comp_data)

        st.dataframe(
            df_comp.style.format({
                "N": "{:.3e}", "P": "{:.3e}", "L": "{:.3e}",
                "R": "{:.3e}", "% R1": "{:.1f}%",
            }),
            use_container_width=True,
            hide_index=True,
        )

        # Gráfico de pizza dos componentes
        df_comp_nz = df_comp[df_comp["R"] > 0]
        if not df_comp_nz.empty:
            fig = px.pie(
                df_comp_nz, names="Componente", values="R",
                title=f"Contribuição de cada componente para R1 — {rz.nome}",
                hover_data=["Descrição"],
            )
            st.plotly_chart(fig, use_container_width=True)

    # ---- Frequência de danos F (Seção 7) ----
    st.subheader("📡 Frequência de danos F (Seção 7)")
    st.caption(
        "Análise complementar para perdas de serviço (D3). "
        "F = FB + FC + FM + FV + FW + FZ (Eq. 14). "
        "Cada FX = NX × PX (Eq. 15)."
    )

    freq_data = []
    for rz in res.zonas:
        f = rz.frequencia
        freq_data.append({
            "Zona": rz.nome,
            "Crítico?": "Sim" if f.sistema_critico else "Não",
            "FB": f.FB, "FC": f.FC, "FM": f.FM,
            "FV": f.FV, "FW": f.FW, "FZ": f.FZ,
            "F (total)": f.F,
            "FT": f.FT,
            "Status": "❌ F > FT" if f.F > f.FT else "✅ F ≤ FT",
        })
    df_freq = pd.DataFrame(freq_data)
    st.dataframe(
        df_freq.style.format({
            "FB": "{:.3e}", "FC": "{:.3e}", "FM": "{:.3e}",
            "FV": "{:.3e}", "FW": "{:.3e}", "FZ": "{:.3e}",
            "F (total)": "{:.3e}", "FT": "{:.3f}",
        }),
        use_container_width=True,
        hide_index=True,
    )

    # Avisos por zona
    for rz in res.zonas:
        f = rz.frequencia
        if f.F > f.FT:
            ratio = f.F / f.FT if f.FT > 0 else float("inf")
            st.error(
                f"**{rz.nome}** — F = {f.F:.3e}/ano supera FT = {f.FT}/ano "
                f"em {ratio:.1f}×. Medidas adicionais são necessárias para "
                "reduzir a frequência de falhas dos sistemas internos."
            )
        else:
            st.success(
                f"**{rz.nome}** — F = {f.F:.3e}/ano ≤ FT = {f.FT}/ano. "
                "Frequência de danos aceitável."
            )

    # ---- Comparativo R vs RT ----
    st.subheader("📈 Comparativo R × RT (escala log)")
    riscos_data = []
    riscos_data.append({"Risco": "R1", "Valor": max(res.R1, 1e-12), "Tipo": "Calculado"})
    riscos_data.append({"Risco": "R1 tolerável", "Valor": RT_R1, "Tipo": "Tolerável"})
    if p.estrutura.patrimonio_cultural:
        riscos_data.append({"Risco": "R3", "Valor": max(res.R3, 1e-12), "Tipo": "Calculado"})
        riscos_data.append({"Risco": "R3 tolerável", "Valor": RT_R3, "Tipo": "Tolerável"})
    if p.avaliar_R4:
        riscos_data.append({"Risco": "R4", "Valor": max(res.R4, 1e-12), "Tipo": "Calculado"})
        riscos_data.append({"Risco": "R4 referência", "Valor": RT_R4, "Tipo": "Tolerável"})
    df_riscos = pd.DataFrame(riscos_data)
    fig = px.bar(
        df_riscos, x="Risco", y="Valor", color="Tipo",
        log_y=True, barmode="group",
        title="Risco calculado vs. risco tolerável (escala logarítmica)",
        color_discrete_map={"Calculado": "#d62728", "Tolerável": "#2ca02c"},
    )
    st.plotly_chart(fig, use_container_width=True)

    # ---- Recomendações ----
    st.subheader("💡 Diagnóstico e recomendações")
    if rz.componentes:
        comp_ordenados = sorted(rz.componentes.values(), key=lambda c: c.R, reverse=True)
        principais = [c for c in comp_ordenados if c.R > 0][:3]

        if res.R1 > RT_R1:
            st.warning(
                f"**R1 está {res.R1/RT_R1:.1f}× acima do tolerável.** "
                "As componentes que mais contribuem são:"
            )
            for c in principais:
                pct = c.R / rz.R1 * 100 if rz.R1 > 0 else 0
                st.markdown(f"- **{c.nome}** ({c.descricao}): {pct:.0f}% do R1 — "
                            f"reduzir através de "
                            + _sugestao_componente(c.nome))
        else:
            st.success(
                "**R1 dentro do tolerável.** Nenhuma medida adicional é obrigatória "
                "para esta análise. Avalie a frequência de danos (Seção 7) se aplicável."
            )

    # ---- Exportar memorial ----
    st.subheader("📄 Memorial de cálculo")
    st.caption("Baixe o memorial em qualquer formato. PDF e Word são recomendados para entrega ao cliente.")

    nome_base = p.estrutura.nome.replace(' ', '_').replace('/', '-')

    col1, col2, col3 = st.columns(3)
    with col1:
        try:
            from nbr5419.relatorio import gerar_pdf
            pdf_bytes = gerar_pdf(p, res)
            st.download_button(
                "📕 Baixar PDF",
                pdf_bytes,
                file_name=f"memorial_{nome_base}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as ex:
            st.error(f"Erro ao gerar PDF: {ex}")

    with col2:
        try:
            from nbr5419.relatorio import gerar_docx
            docx_bytes = gerar_docx(p, res)
            st.download_button(
                "📘 Baixar Word",
                docx_bytes,
                file_name=f"memorial_{nome_base}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        except Exception as ex:
            st.error(f"Erro ao gerar Word: {ex}")

    with col3:
        memorial_md = _gerar_memorial(p, res)
        st.download_button(
            "📝 Baixar Markdown",
            memorial_md,
            file_name=f"memorial_{nome_base}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with st.expander("👁️ Visualizar memorial (Markdown)"):
        st.markdown(memorial_md)


def _sugestao_componente(nome: str) -> str:
    sugestoes = {
        "RA": "medidas de tensão de toque/passo (avisos, malha de equipotencialização, isolação) ou SPDA.",
        "RB": "instalar SPDA com nível adequado (Tabela B.2). NP I reduz PB para 0,02.",
        "RC": "DPS coordenado (Tabela B.3) e blindagem das linhas internas.",
        "RM": "DPS coordenado, blindagem espacial (KS1), ou aumentar UW dos equipamentos.",
        "RU": "DPS classe I para EQP, blindagem da linha externa, restrições físicas na entrada.",
        "RV": "DPS classe I para EQP (PEB), blindagem da linha externa.",
        "RW": "DPS coordenado, blindagem ou interface isolante na entrada.",
        "RZ": "DPS coordenado e blindagem da linha externa.",
    }
    return sugestoes.get(nome, "medidas técnicas conforme Tabela 3 da norma.")


def _gerar_memorial(p: Projeto, res) -> str:
    e = p.estrutura
    md = f"""# Memorial de Análise de Risco SPDA

**Projeto:** {e.nome}
**Norma:** ABNT NBR 5419-2:2026
**Localização:** {e.municipio}/{e.uf} — NG = {e.NG} raios/km²/ano

## 1. Estrutura
- Dimensões: L = {e.L} m × W = {e.W} m × H = {e.H} m
- Área AD = {res.AD:,.0f} m² (Eq. A.1)
- Área AM = {res.AM:,.0f} m² (Eq. A.6)
- Localização: {T.CD_LABELS[e.localizacao.value]} (CD = {T.CD_VALORES[e.localizacao.value]})
- Tipo de construção: {T.RS_LABELS[e.tipo_construcao.value]}
- Pessoas (nt): {e.n_total_pessoas}

## 2. Eventos perigosos (Anexo A)
| Símbolo | Valor | Descrição |
|---|---|---|
| ND | {res.ND:.3e} | Descargas na estrutura |
| NM | {res.NM:.3e} | Descargas próximas |
| NL (total) | {res.NL_total:.3e} | Descargas em linhas |
| NI (total) | {res.NI_total:.3e} | Descargas próximas a linhas |

## 3. Medidas de proteção
- SPDA: {T.PB_LABELS[e.nivel_protecao_spda.value]}
- DPS coordenado: {T.PSPD_LABELS[e.pspd_nivel]}
- Medidas adicionais (PTA): {", ".join(T.PTA_LABELS[m] for m in e.pta_medidas)}

## 4. Linhas conectadas
"""
    for linha in p.linhas:
        md += f"- **{linha.nome}**: {linha.tipo.value}, {T.CI_LABELS[linha.instalacao.value]}, " \
              f"{T.CE_LABELS[linha.ambiente.value]}, LL = {linha.LL} m, UW = {linha.UW} kV\n"

    md += "\n## 5. Resultados por zona\n"
    for rz in res.zonas:
        md += f"\n### {rz.nome}\n"
        md += "| Componente | N | P | L | R |\n|---|---|---|---|---|\n"
        for nome, c in rz.componentes.items():
            md += f"| {nome} | {c.N:.3e} | {c.P:.3e} | {c.L:.3e} | {c.R:.3e} |\n"
        md += f"\n**R1 da zona = {rz.R1:.3e}** y⁻¹\n"

        f = rz.frequencia
        md += f"\n#### Frequência de danos F (Seção 7)\n"
        md += f"- Sistema {'crítico (FT = 0,1/ano)' if f.sistema_critico else 'não crítico (FT = 1/ano)'}\n"
        md += f"- FB = {f.FB:.3e} | FC = {f.FC:.3e} | FM = {f.FM:.3e}\n"
        md += f"- FV = {f.FV:.3e} | FW = {f.FW:.3e} | FZ = {f.FZ:.3e}\n"
        md += f"- **F = {f.F:.3e}/ano** | FT = {f.FT}/ano — "
        md += "❌ Necessita medidas\n" if f.F > f.FT else "✅ Aceitável\n"

    md += f"\n## 6. Riscos totais\n"
    md += f"- **R1 = {res.R1:.3e}** y⁻¹ (Tolerável = {RT_R1:.0e})"
    md += f" — {'❌ NECESSITA PROTEÇÃO' if res.R1 > RT_R1 else '✅ ACEITÁVEL'}\n"
    if e.patrimonio_cultural:
        md += f"- **R3 = {res.R3:.3e}** y⁻¹ (Tolerável = {RT_R3:.0e})\n"
    if p.avaliar_R4:
        md += f"- **R4 = {res.R4:.3e}** y⁻¹ (Referência = {RT_R4:.0e})\n"

    md += "\n---\n*Gerado por Aplicativo de Análise de Risco SPDA — Vertec / NBR 5419-2:2026*\n"
    return md


# =============================================================================
# Glossário
# =============================================================================
def etapa_glossario():
    st.header("📚 Glossário e referências rápidas")

    with st.expander("Componentes de risco (Seção 6)"):
        st.markdown("""
- **RA** — Ferimentos a seres vivos por choque elétrico devido a descarga na estrutura (S1, D1)
- **RB** — Danos físicos devido a descarga na estrutura (S1, D2)
- **RC** — Falha em sistemas internos devido a descarga na estrutura (S1, D3)
- **RM** — Falha em sistemas internos devido a descarga próxima (S2, D3)
- **RU** — Ferimentos por choque devido a descarga na linha (S3, D1)
- **RV** — Danos físicos devido a descarga na linha (S3, D2)
- **RW** — Falha em sistemas internos devido a descarga na linha (S3, D3)
- **RZ** — Falha em sistemas internos devido a descarga próxima da linha (S4, D3)
        """)

    with st.expander("Riscos totais (Seção 4.3)"):
        st.markdown(f"""
- **R1** = RA + RB + RC* + RM* + RU + RV + RW* + RZ*
  - Perda de vida humana / ferimentos permanentes — RT = {RT_R1:.0e}
  - *RC, RM, RW e RZ apenas para risco de explosão ou estruturas onde
    falhas de sistemas internos colocam vida em risco (UTI, hospital, etc.)*
- **R3** = RB + RV
  - Perda de patrimônio cultural — RT = {RT_R3:.0e}
- **R4** = todos os componentes (Anexo D — informativo)
  - Perda econômica — RT referencial = {RT_R4:.0e}
        """)

    with st.expander("Equação geral (6.1)"):
        st.markdown("""
$$R_X = N_X \\times P_X \\times L_X$$

Onde:
- $N_X$ = número anual de eventos perigosos (Anexo A)
- $P_X$ = probabilidade de dano (Anexo B)
- $L_X$ = perda consequente (Anexo C / D)
        """)

    with st.expander("Frequência de danos F (Seção 7)"):
        st.markdown("""
A **frequência de danos F** é o número anual esperado de eventos prejudiciais
nos sistemas internos. É **independente da análise de risco R** — enquanto
R = N × P × L (com perda L), F = N × P (Eq. 15).

**Componentes (Tabela 7):**
- **FB** = ND × PB *(apenas equipamentos em ZPR0A — exposição direta)*
- **FC** = ND × PC
- **FM** = NM × PM
- **FV** = (NL + NDJ) × PEB *(usa PEB direto, não PV)*
- **FW** = (NL + NDJ) × PW
- **FZ** = NI × PZ
- **F = FB + FC + FM + FV + FW + FZ** (Eq. 14)

**Frequência tolerável FT:**
- Sistema **crítico** (afeta comunidade): FT = 0,1/ano *(fixo, não pode ser alterado)*
- Sistema **não crítico**: FT = 1/ano *(representativo)*

A análise F deve ser feita para todos os estudos com perdas D3 (falhas em sistemas internos).
        """)

    with st.expander("Fontes de dano e tipos de dano"):
        st.markdown("""
**Fontes (S):**
- S1 — Descarga na estrutura
- S2 — Descarga próxima da estrutura (até 500 m)
- S3 — Descarga na linha conectada
- S4 — Descarga próxima de linha conectada (até 4 km)

**Tipos de dano (D):**
- D1 — Ferimentos em seres vivos (choque, tensão de toque/passo)
- D2 — Danos físicos (incêndio, explosão, mecânicos)
- D3 — Falha de sistemas internos (eletroeletrônicos)

**Tipos de perda (L):**
- L1 — Perda de vida humana
- L3 — Perda de patrimônio cultural
- L4 — Perda econômica (Anexo D)
        """)


# =============================================================================
# Painel Admin
# =============================================================================
def etapa_admin():
    """Painel restrito a administradores."""
    if not is_admin():
        st.error("Acesso restrito a administradores.")
        return

    st.header("🛡️ Painel do Administrador")
    st.caption(
        "Gerar credenciais de novos usuários, listar usuários ativos, "
        "e preparar bloco TOML para sincronizar com Streamlit Cloud."
    )

    tab1, tab2, tab3 = st.tabs([
        "👥 Usuários ativos",
        "➕ Cadastrar novo usuário",
        "📋 Bloco TOML para Streamlit Cloud",
    ])

    # ---- Tab 1: Listar usuários ----
    with tab1:
        from datetime import date as _date
        st.subheader("Usuários cadastrados em produção")
        st.caption(
            "ℹ️ Lista lida de `st.secrets` (Streamlit Cloud). "
            "Para alterar, use a aba **Cadastrar** ou o CLI "
            "`python scripts/gerenciar_acessos.py`, e sincronize via aba 3."
        )

        try:
            hashes = dict(st.secrets.get("auth_hashes", {}))
            expiras = dict(st.secrets.get("auth_expira", {}))
            roles = dict(st.secrets.get("auth_roles", {}))
        except Exception:
            hashes, expiras, roles = {}, {}, {}

        if not hashes:
            st.warning("Nenhum usuário encontrado em st.secrets.")
        else:
            linhas = []
            hoje = _date.today()
            for email in sorted(hashes.keys()):
                exp_str = str(expiras.get(email, "2099-12-31"))
                try:
                    exp = _date.fromisoformat(exp_str)
                except ValueError:
                    exp = _date(2099, 12, 31)

                role = (roles.get(email, "user") or "user").lower()
                if exp < hoje:
                    status = "🔴 Expirado"
                elif exp == _date(2099, 12, 31):
                    status = "🟢 Ativo (indeterminado)"
                else:
                    dias = (exp - hoje).days
                    status = f"🟡 Expira em {dias}d" if dias <= 30 else f"🟢 Até {exp_str}"

                linhas.append({
                    "E-mail": email,
                    "Role": "🛡️ admin" if role == "admin" else "👤 user",
                    "Expira em": exp_str,
                    "Status": status,
                })

            st.dataframe(
                pd.DataFrame(linhas),
                use_container_width=True,
                hide_index=True,
            )
            st.caption(
                f"Total: **{len(linhas)}** usuários "
                f"({sum(1 for l in linhas if 'admin' in l['Role'])} admins, "
                f"{sum(1 for l in linhas if 'user' in l['Role'])} users)"
            )

    # ---- Tab 2: Cadastrar novo usuário ----
    with tab2:
        st.subheader("Gerar credenciais para novo usuário")
        st.caption(
            "Esta tela **gera o hash localmente** e mostra o bloco TOML pronto "
            "para colar no Streamlit Cloud Secrets. **Não salva nada automaticamente** — "
            "você deve aplicar manualmente para ativar o acesso."
        )

        with st.form("cadastrar_usuario"):
            col1, col2 = st.columns(2)
            with col1:
                novo_email = st.text_input(
                    "E-mail do novo usuário",
                    placeholder="usuario@empresa.com",
                )
                novo_role = st.selectbox(
                    "Role",
                    ["user", "admin"],
                    help="user = projetista comum. admin = pode gerenciar usuários.",
                )
            with col2:
                novo_senha = st.text_input(
                    "Senha (provisória — usuário deve trocar)",
                    type="password",
                )
                novo_expira = st.date_input(
                    "Expira em",
                    value=__import__("datetime").date(2099, 12, 31),
                    help="Para acesso 'indeterminado' deixe 2099-12-31.",
                )
            gerar = st.form_submit_button("🔐 Gerar credenciais", type="primary")

        if gerar:
            if not novo_email or "@" not in novo_email:
                st.error("E-mail inválido.")
            elif len(novo_senha) < 6:
                st.error("Senha muito curta (mínimo 6 caracteres).")
            else:
                novo_email_norm = novo_email.strip().lower()
                novo_hash = hash_senha(novo_email_norm, novo_senha)
                bloco = (
                    f'\n[auth_hashes]\n'
                    f'"{novo_email_norm}" = "{novo_hash}"\n\n'
                    f'[auth_expira]\n'
                    f'"{novo_email_norm}" = "{novo_expira.isoformat()}"\n\n'
                    f'[auth_roles]\n'
                    f'"{novo_email_norm}" = "{novo_role}"\n'
                )
                st.success("✅ Credencial gerada. Siga os 3 passos abaixo.")
                st.markdown(
                    f"**1. Bloco TOML para mesclar no Streamlit Cloud Secrets:**"
                )
                st.code(bloco, language="toml")
                st.markdown(
                    f"**2. Comunique a senha** para `{novo_email_norm}` por canal seguro "
                    "(Teams DM, e-mail criptografado), **separadamente do login**:"
                )
                st.code(novo_senha, language="text")
                st.warning(
                    "⚠️ **Esta senha aparece somente nesta tela** e não fica salva. "
                    "Anote agora se precisar consultar depois."
                )
                st.markdown(
                    "**3. Aplique no Streamlit Cloud:** "
                    "https://share.streamlit.io → seu app → **⋮ → Settings → Secrets** → "
                    "**adicione** as 3 linhas (uma em cada seção existente) → **Save**."
                )

    # ---- Tab 3: Bloco TOML completo ----
    with tab3:
        st.subheader("Bloco TOML completo dos usuários atuais")
        st.caption(
            "Útil para refazer todos os Secrets do zero (ex.: migração entre Streamlit "
            "Cloud apps)."
        )
        try:
            hashes = dict(st.secrets.get("auth_hashes", {}))
            expiras = dict(st.secrets.get("auth_expira", {}))
            roles = dict(st.secrets.get("auth_roles", {}))
        except Exception:
            hashes, expiras, roles = {}, {}, {}

        if hashes:
            linhas_h = ["[auth_hashes]"] + [
                f'"{e}" = "{hashes[e]}"' for e in sorted(hashes.keys())
            ]
            linhas_e = ["[auth_expira]"] + [
                f'"{e}" = "{expiras.get(e, "2099-12-31")}"'
                for e in sorted(hashes.keys())
            ]
            linhas_r = ["[auth_roles]"] + [
                f'"{e}" = "{roles.get(e, "user")}"' for e in sorted(hashes.keys())
            ]
            bloco = "\n".join(linhas_h + [""] + linhas_e + [""] + linhas_r)
            st.code(bloco, language="toml")
        else:
            st.info("Sem usuários cadastrados ainda.")


# =============================================================================
# Roteamento
# =============================================================================
ROTAS = {
    "1. Localização e NG": etapa_localizacao,
    "2. Estrutura": etapa_estrutura,
    "3. Zonas de estudo": etapa_zonas,
    "4. Linhas conectadas": etapa_linhas,
    "5. Medidas de proteção": etapa_medidas,
    "6. Resultados": etapa_resultados,
    "📚 Glossário": etapa_glossario,
    "🛡️ Painel Admin": etapa_admin,
}

ROTAS[etapa]()

# Botão de logout
botao_logout()

# Debug pane
with st.sidebar.expander("🛠️ Estado do projeto (debug)"):
    p = st.session_state.projeto
    st.json({
        "estrutura": p.estrutura.nome,
        "L×W×H": f"{p.estrutura.L}×{p.estrutura.W}×{p.estrutura.H}",
        "NG": p.estrutura.NG,
        "n_zonas": len(p.zonas),
        "n_linhas": len(p.linhas),
        "SPDA": p.estrutura.nivel_protecao_spda.value,
    })
