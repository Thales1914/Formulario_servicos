import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
import io

st.set_page_config(page_title="Conexão Ômega", layout="centered")


st.markdown("""
    <style>
        body {
            background-color: #111111;
        }
        .main {
            background-color: #1e1e1e;
        }
        input, select, textarea {
            background-color: #262730 !important;
            color: white !important;
            border-radius: 6px !important;
            padding: 6px !important;
        }
        .stButton>button {
            background-color: #ff6600;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 16px;
        }
        .stDownloadButton>button {
            background-color: #0099ff;
            color: white;
            border-radius: 6px;
            padding: 8px 16px;
        }
    </style>
""", unsafe_allow_html=True)

st.image("logo_acao_omega.png", use_container_width=True)

def init_db():
    conn = sqlite3.connect("cadastros.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cadastros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            telefone TEXT,
            endereco TEXT,
            nascimento TEXT,
            instagram TEXT,
            bairro TEXT,
            servico TEXT,
            data_hora TEXT
        )
    """)
    conn.commit()
    conn.close()

def inserir_dados(nome, telefone, endereco, nascimento, instagram, bairro, servico):
    conn = sqlite3.connect("cadastros.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO cadastros (nome, telefone, endereco, nascimento, instagram, bairro, servico, data_hora)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        nome, telefone, endereco, nascimento, instagram, bairro, servico,
        datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    ))
    conn.commit()
    conn.close()

init_db()

if st.session_state.get("clear_fields", False):
    st.session_state["nome"] = ""
    st.session_state["telefone"] = ""
    st.session_state["endereco"] = ""
    st.session_state["nascimento"] = ""
    st.session_state["instagram"] = ""
    st.session_state["bairro"] = ""
    st.session_state["servico"] = "Massoterapia"
    st.session_state["clear_fields"] = False

with st.form("form_servico"):
    nome = st.text_input("Nome completo", key="nome")
    telefone = st.text_input("Telefone (com DDD)", key="telefone")
    endereco = st.text_input("Endereço", key="endereco")
    nascimento = st.text_input("Data de Nascimento (DD/MM/AAAA)", key="nascimento")
    bairro = st.text_input("Bairro", key="bairro")
    instagram = st.text_input("Instagram", key="instagram")

    servico = st.selectbox(
        "Selecione o serviço desejado:",
        [
            "Massoterapia",
            "Apoio Psicológico 1",
            "Apoio Psicológico 2",
            "Odontoarte",
            "OdontoSistem",
            "Enfermagem",
            "Hemoce (Doação de Sangue)",
            "Himunização",
            "Apoio Jurídico",
            "Credencial Estacionamento",
            "Corte de Cabelo"
        ],
        key="servico"
    )

    submitted = st.form_submit_button("Enviar")

if submitted:
    try:
        datetime.strptime(nascimento.strip(), "%d/%m/%Y")

        if nome and telefone and endereco and bairro:
            inserir_dados(nome, telefone, endereco, nascimento.strip(), instagram, bairro, servico)
            st.success("Cadastro realizado com sucesso!")

            st.session_state["clear_fields"] = True
            st.rerun()
        else:
            st.error("Por favor, preencha todos os campos obrigatórios.")
    except ValueError:
        st.error("Data de nascimento inválida. Use o formato DD/MM/AAAA.")

st.markdown("---")
st.subheader("Exportar cadastros para Excel")

if st.button("📥 Baixar Excel"):
    conn = sqlite3.connect("cadastros.db")
    df = pd.read_sql_query("SELECT * FROM cadastros", conn)
    conn.close()

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Cadastros')
    output.seek(0)

    st.download_button(
        label="Clique aqui para baixar o arquivo Excel",
        data=output,
        file_name="cadastros.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
