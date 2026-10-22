import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="SUPERMATINAL", layout="wide")

# ==========================================
# DADOS DE HIERARQUIA E ACESSO
# ==========================================
GVS_CONFIG = {
    "30503": {"unidade": "GP7 JEQUIÉ", "gv": "GV 1", "rns": list(range(101, 110))},
    "09581": {"unidade": "GP7 JEQUIÉ", "gv": "GV 2", "rns": list(range(201, 209))},
    "00500": {"unidade": "GP7 ITAPETINGA", "gv": "GV 1", "rns": list(range(101, 111))}
}

# ==========================================
# INICIALIZAÇÃO DO BANCO DE DADOS TEMPORÁRIO
# ==========================================
if 'focos_diarios' not in st.session_state:
    st.session_state.focos_diarios = {} 
if 'metas_rns' not in st.session_state:
    st.session_state.metas_rns = pd.DataFrame()
if 'execucoes' not in st.session_state:
    st.session_state.execucoes = pd.DataFrame(columns=['Unidade', 'GV', 'RN', 'Desafio', 'PDV', 'Data'])

st.title("🚀 SUPERMATINAL - Acompanhamento Comercial")
aba_selecionada = st.sidebar.radio("Selecione seu Perfil:", ["Aba RN (Operação)", "Aba GV (Gestão)"])

# ==========================================
# ABA GV - GESTÃO
# ==========================================
if aba_selecionada == "Aba GV (Gestão)":
    st.header("🔒 Área do Gerente de Vendas")
    
    senha_input = st.text_input("Digite os 5 últimos dígitos do seu CPF:", type="password")
    
    if senha_input in GVS_CONFIG:
        meu_gv = GVS_CONFIG[senha_input]
        unidade_gv = meu_gv['unidade']
        nome_gv = meu_gv['gv']
        rns_gv = meu_gv['rns']
        chave_gv = f"{unidade_gv}_{nome_gv}"
        
        st.success(f"Acesso Liberado! Bem-vindo, {nome_gv} ({unidade_gv})")
        st.markdown("---")
        
        col1, col2 = st.columns([1, 1.2])
        
        with col1:
            st.subheader("1. Indicadores Foco do Dia")
            d1 = st.text_input("Desafio 1 (Ex: TASK LITRINHO)", key="d1")
            d2 = st.text_input("Desafio 2 (Ex: TASK NAB)", key="d2")
            d3 = st.text_input("Desafio 3", key="d3")
            d4 = st.text_input("Desafio 4", key="d4")
            
            focos_preenchidos = [d for d in [d1, d2, d3, d4] if d]
            
            if st.button("Definir Focos e Abrir Desdobramento"):
                st.session_state.focos_diarios[chave_gv] = focos_preenchidos
                
                # Prepara a tabela inicial de metas com os RNs da equipe e valores zerados
                df_metas = pd.DataFrame({"RN": rns_gv})
                for foco in focos_preenchidos:
                    df_metas[f"Meta: {foco}"] = 0
                st.session_state.metas_rns = df_metas
                st.rerun()

            # Exibe a tabela para desdobrar metas agrupada no st.form para evitar o lag
            if chave_gv in st.session_state.focos_diarios and not st.session_state.metas_rns.empty:
                st.subheader("2. Desdobrar Metas por RN")
                st.caption("Altere os valores na tabela abaixo para definir a meta de cada RN.")
                
                with st.form("form_metas"):
                    tabela_editada = st.data_editor(st.session_state.metas_rns, hide_index=True, use_container_width=True)
                    salvar_metas = st.form_submit_button("Enviar Metas 🎯")
                    
                    if salvar_metas:
                        st.session_state.metas_rns = tabela_editada
                        st.success("Metas salvas e prontas para acompanhamento!")
        
        with col2:
            st.subheader("📊 Entregas da sua Equipe (Tempo Real)")
            
            df_exec = st.session_state.execucoes
            df_minha_equipe = df_exec[(df_exec['Unidade'] == unidade_gv) & (df_exec['GV'] == nome_gv)]
            
            if not df_minha_equipe.empty:
                df_resumo = df_minha_equipe.groupby(['RN', 'Desafio'])['PDV'].apply(list).reset_index()
                df_resumo['Qtd Realizada'] = df_resumo['PDV'].apply(len)
                
                for index, row in df_resumo.iterrows():
                    st.markdown(f"**RN {row['RN']}:** {row['Qtd Realizada']} {row['Desafio']} | **PDVS:** {', '.join(row['PDV'])}")
                
                st.write("Histórico Completo:")
                st.dataframe(df_minha_equipe, hide_index=True, use_container_width=True)
            else:
                st.info("Nenhuma baixa realizada pela sua equipe hoje ainda.")
                
    elif senha_input != "":
        st.error("Senha Incorreta. Verifique os 5 últimos dígitos do seu CPF.")

# ==========================================
# ABA RN - OPERAÇÃO
# ==========================================
elif aba_selecionada == "Aba RN (Operação)":
    st.header("🎯 Registro de Execução - RN")
    
    with st.form("form_rn"):
        col1, col2, col3 = st.columns(3)
        with col1:
            unidade_sel = st.selectbox("Unidade", ["GP7 JEQUIÉ", "GP7 ITAPETINGA"])
        with col2:
            opcoes_gv = ["GV 1", "GV 2"] if unidade_sel == "GP7 JEQUIÉ" else ["GV 1"]
            gv_sel = st.selectbox("Qual o seu GV?", opcoes_gv)
        with col3:
            # Puxa os RNs baseados na Unidade e GV selecionados
            senha_gv = [k for k, v in GVS_CONFIG.items() if v['unidade'] == unidade_sel and v['gv'] == gv_sel][0]
            rns_disponiveis = GVS_CONFIG[senha_gv]['rns']
            rn_sel = st.selectbox("Seu Setor / RN", rns_disponiveis)
            
        st.markdown("---")
        st.subheader("Adicionar Marco / Baixa")
        
        chave_gv_sel = f"{unidade_sel}_{gv_sel}"
        desafios_atuais = st.session_state.focos_diarios.get(chave_gv_sel, [])
        
        if not desafios_atuais:
            st.warning("Seu GV ainda não liberou os desafios de hoje.")
            submit = st.form_submit_button("Dar Baixa", disabled=True)
        else:
            desafio_selecionado = st.selectbox("Qual desafio você está batendo agora?", desafios_atuais)
            pdv = st.text_input("Código do PDV (Ex: 3034)")
            
            submit = st.form_submit_button("Dar Baixa no Desafio 🚀")
            
            if submit:
                if pdv.strip():
                    nova_linha = pd.DataFrame([{
                        'Unidade': unidade_sel, 
                        'GV': gv_sel,
                        'RN': rn_sel, 
                        'Desafio': desafio_selecionado, 
                        'PDV': pdv,
                        'Data': date.today()
                    }])
                    st.session_state.execucoes = pd.concat([st.session_state.execucoes, nova_linha], ignore_index=True)
                    st.success(f"Show! Baixa do {desafio_selecionado} no PDV {pdv} enviada para o {gv_sel}!")
                else:
                    st.error("Informe o código do PDV antes de dar baixa.")
