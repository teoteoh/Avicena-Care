import os
import html
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
from datetime import datetime
import numpy as np
import time
from auth import AuthSystem

# Importar módulo de ML
try:
    from ml_predictor import predictor
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️ Módulo ML não disponível. Execute train_model.py primeiro.")

# Importar módulo de scores clínicos
from scores_clinicos import calcular_todos_scores

# Importar módulo de validação clínica
from validacao_clinica import validar_predicao_ml, formatar_alerta_override

# Configuração da página
st.set_page_config(
    page_title="Avicena Care - Sistema de Triagem",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Inicialização do sistema de autenticação
auth_system = AuthSystem()

# Importar e executar a criação de dados de exemplo
from init_data import criar_dados_exemplo

# Conexão com banco de dados - usar o mesmo banco do init_data
conn = sqlite3.connect('avicena_auth.db', check_same_thread=False)

# Criar tabela triagem se não existir (compatibilidade com código antigo)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS triagem (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Nome TEXT,
        Idade INTEGER,
        PA TEXT,
        FC INTEGER,
        FR INTEGER,
        Temp REAL,
        Comorbidade TEXT,
        Alergia TEXT,
        Queixa_Principal TEXT,
        urgencia_automatica TEXT,
        urgencia_manual TEXT,
        status TEXT DEFAULT 'AGUARDANDO',
        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

# Criar alguns dados de exemplo na tabela triagem se estiver vazia
cursor.execute('SELECT COUNT(*) FROM triagem')
if cursor.fetchone()[0] == 0:
    pacientes_exemplo = [
        ('João Silva', 45, '120/80', 75, 16, 36.5, 'Hipertensão', 'Nenhuma', 'Dor no peito', 'ALTA PRIORIDADE', 'ALTA PRIORIDADE', 'AGUARDANDO'),
        ('Maria Santos', 67, '140/90', 88, 20, 37.2, 'Diabetes', 'Penicilina', 'Febre e tosse', 'MÉDIA PRIORIDADE', 'MÉDIA PRIORIDADE', 'AGUARDANDO'),
        ('Carlos Oliveira', 29, '110/70', 68, 14, 36.0, 'Nenhuma', 'Nenhuma', 'Dor abdominal', 'BAIXA PRIORIDADE', 'BAIXA PRIORIDADE', 'AGUARDANDO'),
        ('Ana Paula', 54, '160/100', 95, 22, 37.8, 'Hipertensão', 'Nenhuma', 'Tontura intensa', 'ALTA PRIORIDADE', 'ALTA PRIORIDADE', 'AGUARDANDO'),
        ('Pedro Costa', 38, '115/75', 72, 15, 36.3, 'Nenhuma', 'Nenhuma', 'Dor de cabeça', 'MÍNIMA (ELETIVA)', 'MÍNIMA (ELETIVA)', 'AGUARDANDO'),
    ]
    
    for p in pacientes_exemplo:
        cursor.execute('''
            INSERT INTO triagem (Nome, Idade, PA, FC, FR, Temp, Comorbidade, Alergia, 
                               Queixa_Principal, urgencia_automatica, urgencia_manual, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', p)
    conn.commit()

criar_dados_exemplo()

def get_data(incluir_atendidos: bool = False):
    """Busca dados de pacientes do banco"""
    if incluir_atendidos:
        return pd.read_sql_query(
            "SELECT * FROM triagem ORDER BY data_cadastro DESC", conn
        )
    return pd.read_sql_query(
        "SELECT * FROM triagem WHERE status='AGUARDANDO' ORDER BY data_cadastro DESC",
        conn,
    )

def get_atendidos():
    """Busca pacientes já atendidos"""
    return pd.read_sql_query(
        "SELECT * FROM triagem WHERE status='ATENDIDO' ORDER BY data_atendimento DESC",
        conn,
    )

def calcular_urgencia(
    temperatura,
    pa_sistolica,
    pa_diastolica,
    freq_respiratoria,
    freq_cardiaca,
    idade,
    spo2=None,
    nivel_consciencia="Alerta",
):
    """
    Triagem por pontos ampliada, conforme parâmetros e faixas sugeridas.
    Retorna: (nivel, cor, emoji, descricao, pontuacao, alertas)
    """
    pontos = 0
    alertas = []

    # FR
    if freq_respiratoria <= 8 or freq_respiratoria >= 25:
        pontos += 3
        alertas.append("FR crítica")
    elif 9 <= freq_respiratoria <= 11:
        pontos += 1
        alertas.append("FR levemente alterada")
    elif 21 <= freq_respiratoria <= 24:
        pontos += 2
        alertas.append("FR moderada")

    # SpO2
    if spo2 is not None:
        if spo2 <= 91:
            pontos += 3
            alertas.append("SpO₂ crítica")
        elif 92 <= spo2 <= 93:
            pontos += 2
            alertas.append("SpO₂ moderada")
        elif 94 <= spo2 <= 95:
            pontos += 1
            alertas.append("SpO₂ levemente alterada")

    # PA sistólica
    if pa_sistolica <= 90 or pa_sistolica >= 220:
        pontos += 3
        alertas.append("PA sistólica crítica")
    elif 91 <= pa_sistolica <= 100:
        pontos += 2
        alertas.append("PA sistólica moderada")
    elif 101 <= pa_sistolica <= 110:
        pontos += 1
        alertas.append("PA sistólica levemente alterada")

    # FC
    if freq_cardiaca <= 40 or freq_cardiaca >= 131:
        pontos += 3
        alertas.append("FC crítica")
    elif 41 <= freq_cardiaca <= 50:
        pontos += 1
        alertas.append("FC levemente alterada")
    elif 51 <= freq_cardiaca <= 90:
        pontos += 0
    elif 91 <= freq_cardiaca <= 110:
        pontos += 1
        alertas.append("FC levemente alterada")
    elif 111 <= freq_cardiaca <= 130:
        pontos += 2
        alertas.append("FC moderada")

    # Temperatura
    if temperatura <= 35.0:
        pontos += 3
        alertas.append("Hipotermia grave")
    elif 35.1 <= temperatura <= 36.0:
        pontos += 1
        alertas.append("Temperatura levemente baixa")
    elif 36.1 <= temperatura <= 37.0:
        pontos += 0
    elif 37.1 <= temperatura <= 39.0:
        pontos += 1
        alertas.append("Temperatura levemente elevada")
    elif temperatura >= 39.1:
        pontos += 2
        alertas.append("Febre alta")

    # Nível de consciência
    if nivel_consciencia.lower() == "alerta":
        pontos += 0
    else:
        pontos += 3
        alertas.append("Alteração de consciência")

    # Regra de exceção: parâmetro crítico extremo
    if (
        freq_respiratoria <= 8
        or freq_respiratoria >= 25
        or spo2 is not None
        and spo2 <= 85
        or pa_sistolica < 80
        or freq_cardiaca < 40
        or freq_cardiaca > 150
        or nivel_consciencia.lower() != "alerta"
    ):
        return (
            "PRIORIDADE MÁXIMA",
            "#dc2626",
            "🔴",
            "Atendimento imediato",
            pontos,
            alertas,
        )

    # Classificação por faixas de pontos
    if pontos >= 7:
        return (
            "PRIORIDADE MÁXIMA",
            "#dc2626",
            "🔴",
            "Atendimento imediato",
            pontos,
            alertas,
        )
    elif pontos >= 5:
        return ("ALTA PRIORIDADE", "#ea580c", "🟠", "Muito urgente", pontos, alertas)
    elif pontos >= 3:
        return ("MÉDIA PRIORIDADE", "#eab308", "🟡", "Urgente", pontos, alertas)
    elif pontos >= 1:
        return ("BAIXA PRIORIDADE", "#16a34a", "🟢", "Pouco urgente", pontos, alertas)
    else:
        return (
            "MÍNIMA (ELETIVA)",
            "#2563eb",
            "🔵",
            "Sem sinais agudos",
            pontos,
            alertas,
        )

# ==================== FUNÇÕES AUXILIARES ====================
def mostrar_fila_pacientes(df):
    """Mostra a fila de pacientes aguardando atendimento"""
    st.markdown("### 🧾 Fila de Atendimento")
    
    # CSS para botão de atualizar urgência
    st.markdown("""
    <style>
    /* Botão de atualizar urgência mais compacto e claro */
    button[kind="secondary"] {
        height: 38px !important;
        min-height: 38px !important;
        padding: 0 12px !important;
        background-color: #f1f5f9 !important;
        color: #1e293b !important;
        border: 1px solid #cbd5e1 !important;
    }
    button[kind="secondary"]:hover {
        background-color: #e2e8f0 !important;
        border-color: #94a3b8 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    if df.empty:
        st.info("📋 Nenhum paciente na fila de atendimento no momento.")
        return
    
    # Definir ordem de prioridade
    prioridade_ordem = {
        'PRIORIDADE MÁXIMA': 1,
        'ALTA PRIORIDADE': 2,
        'MÉDIA PRIORIDADE': 3,
        'BAIXA PRIORIDADE': 4,
        'MÍNIMA (ELETIVA)': 5
    }
    
    # Adicionar coluna de ordem e ordenar
    df_ordenado = df.copy()
    df_ordenado['ordem_prioridade'] = df_ordenado['urgencia_manual'].map(prioridade_ordem).fillna(6)
    df_ordenado = df_ordenado.sort_values('ordem_prioridade')
    
    # Mapas de cores e emojis
    cor_map = {
        'PRIORIDADE MÁXIMA': '#dc2626',
        'ALTA PRIORIDADE': '#ea580c',
        'MÉDIA PRIORIDADE': '#eab308',
        'BAIXA PRIORIDADE': '#16a34a',
        'MÍNIMA (ELETIVA)': '#2563eb'
    }
    
    emoji_map = {
        'PRIORIDADE MÁXIMA': '🔴',
        'ALTA PRIORIDADE': '🟠',
        'MÉDIA PRIORIDADE': '🟡',
        'BAIXA PRIORIDADE': '🟢',
        'MÍNIMA (ELETIVA)': '🔵'
    }
    
    tempo_map = {
        'PRIORIDADE MÁXIMA': '0 min',
        'ALTA PRIORIDADE': '15 min',
        'MÉDIA PRIORIDADE': '60 min',
        'BAIXA PRIORIDADE': '120 min',
        'MÍNIMA (ELETIVA)': '240 min'
    }
    
    for idx, paciente in df_ordenado.iterrows():
        urgencia = paciente.get('urgencia_manual', 'MÉDIA PRIORIDADE')
        cor = cor_map.get(urgencia, '#64748b')
        emoji = emoji_map.get(urgencia, '⚪')
        tempo = tempo_map.get(urgencia, 'N/A')
        
        # HTML customizado para o título do expander
        header_html = f"""
        <div style='display: flex; align-items: center; gap: 10px; padding: 5px 0;'>
            <span style='font-size: 1.3em;'>{emoji}</span>
            <strong style='color: {cor}; font-size: 1.1em;'>{paciente['Nome']}</strong>
            <span style='color: {cor}; font-weight: 600;'>• {urgencia}</span>
            <span style='background: {cor}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.75em; font-weight: 600;'>⏱ {tempo}</span>
        </div>
        """
        
        with st.expander(f"{emoji} **{paciente['Nome']}** - {urgencia}", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Idade:** {paciente.get('Idade', 'N/A')} anos")
                st.write(f"**Temperatura:** {paciente.get('Temp', 'N/A')}°C")
                st.write(f"**PA:** {paciente.get('PA', 'N/A')}")
            with col2:
                st.write(f"**FC:** {paciente.get('FC', 'N/A')} bpm")
                st.write(f"**FR:** {paciente.get('FR', 'N/A')} irpm")
                st.write(f"**Queixa:** {paciente.get('Queixa_Principal', 'N/A')}")
            
            # Seção para reclassificar urgência manualmente
            st.markdown("---")
            st.markdown("**🔄 Reclassificar Urgência**")
            col_select, col_btn = st.columns([4, 1])
            
            with col_select:
                nova_urgencia = st.selectbox(
                    "Nova classificação:",
                    options=['PRIORIDADE MÁXIMA', 'ALTA PRIORIDADE', 'MÉDIA PRIORIDADE', 'BAIXA PRIORIDADE', 'MÍNIMA (ELETIVA)'],
                    index=['PRIORIDADE MÁXIMA', 'ALTA PRIORIDADE', 'MÉDIA PRIORIDADE', 'BAIXA PRIORIDADE', 'MÍNIMA (ELETIVA)'].index(urgencia),
                    key=f"urgencia_{paciente['id']}",
                    label_visibility="collapsed"
                )
            
            with col_btn:
                if st.button("✓", key=f"btn_urgencia_{paciente['id']}", help="Atualizar urgência", type="secondary"):
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE triagem SET urgencia_manual = ? WHERE id = ?",
                        (nova_urgencia, paciente['id'])
                    )
                    conn.commit()
                    st.success("✓ Atualizado")
                    time.sleep(0.3)
                    st.rerun()

def mostrar_form_novo_paciente():
    """Formulário para cadastro de novo paciente"""
    st.markdown("### ➕ Cadastrar Novo Paciente")
    
    # CSS para formulário com fundo branco
    st.markdown("""
    <style>
    /* Fundo branco para inputs de texto */
    div[data-testid="stForm"] input[type="text"],
    div[data-testid="stForm"] input[type="number"],
    div[data-testid="stForm"] textarea {
        background-color: #ffffff !important;
        color: #1e293b !important;
        border: 1px solid #cbd5e1 !important;
    }
    
    /* Fundo branco para selectbox */
    div[data-testid="stForm"] div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #1e293b !important;
    }
    
    /* Botões +/- dos campos numéricos com fundo claro - múltiplos seletores */
    div[data-testid="stForm"] button[kind="stepUpButton"],
    div[data-testid="stForm"] button[kind="stepDownButton"],
    div[data-testid="stForm"] button[data-testid="stNumberInputStepUp"],
    div[data-testid="stForm"] button[data-testid="stNumberInputStepDown"],
    div[data-testid="stForm"] div[data-testid="stNumberInput"] button {
        background-color: #f1f5f9 !important;
        color: #1e293b !important;
        border: 1px solid #cbd5e1 !important;
    }
    
    div[data-testid="stForm"] button[kind="stepUpButton"]:hover,
    div[data-testid="stForm"] button[kind="stepDownButton"]:hover,
    div[data-testid="stForm"] button[data-testid="stNumberInputStepUp"]:hover,
    div[data-testid="stForm"] button[data-testid="stNumberInputStepDown"]:hover,
    div[data-testid="stForm"] div[data-testid="stNumberInput"] button:hover {
        background-color: #e2e8f0 !important;
        color: #0f172a !important;
    }
    
    /* Forçar cores nos SVG dos botões */
    div[data-testid="stForm"] button[kind="stepUpButton"] svg,
    div[data-testid="stForm"] button[kind="stepDownButton"] svg,
    div[data-testid="stForm"] div[data-testid="stNumberInput"] button svg {
        fill: #1e293b !important;
        color: #1e293b !important;
    }
    
    /* Placeholder com cor clara */
    div[data-testid="stForm"] input::placeholder,
    div[data-testid="stForm"] textarea::placeholder {
        color: #94a3b8 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.form("form_novo_paciente"):
        # Seção: Dados Pessoais
        st.markdown("#### 👤 Dados Pessoais")
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome completo *", placeholder="Ex: João Silva")
            idade = st.number_input("Idade *", min_value=0, max_value=120, value=30)
            genero = st.selectbox("Gênero *", ["Masculino", "Feminino", "Outro"])
            peso = st.number_input("Peso (kg)", min_value=0.0, max_value=300.0, value=70.0, step=0.1)
            
        with col2:
            queixa = st.text_area("Queixa Principal *", placeholder="Descreva os sintomas...")
            altura = st.number_input("Altura/Estatura (cm)", min_value=0.0, max_value=250.0, value=170.0, step=0.1)
        
        # Seção: Sinais Vitais
        st.markdown("#### 🩺 Sinais Vitais")
        col3, col4 = st.columns(2)
        
        with col3:
            temperatura = st.number_input("Temperatura (°C) *", min_value=30.0, max_value=45.0, value=36.5, step=0.1)
            pa_sistolica = st.number_input("PA Sistólica *", min_value=50, max_value=250, value=120)
            pa_diastolica = st.number_input("PA Diastólica *", min_value=30, max_value=150, value=80)
            
        with col4:
            freq_cardiaca = st.number_input("Frequência Cardíaca (bpm) *", min_value=30, max_value=200, value=75)
            freq_respiratoria = st.number_input("Frequência Respiratória (irpm) *", min_value=5, max_value=60, value=16)
            spo2 = st.number_input("SpO₂ (%)", min_value=50, max_value=100, value=98)
        
        nivel_consciencia = st.selectbox("Nível de Consciência", ["Alerta", "Confuso", "Sonolento", "Inconsciente"])
        
        # Intensidade da Dor (Escala EVA)
        st.markdown("**Intensidade da Dor (0-10):**")
        intensidade_dor = st.slider("", min_value=0, max_value=10, value=0, 
                                     help="0 = Sem dor | 10 = Dor máxima insuportável")
        
        # Seção: Histórico Médico
        st.markdown("#### 📋 Histórico Médico")
        col5, col6 = st.columns(2)
        
        with col5:
            comorbidades = st.text_area("Comorbidades Pré-existentes", 
                                       placeholder="Ex: Diabetes, Hipertensão, Asma...",
                                       height=100)
            medicacoes = st.text_area("Medicações de Uso Contínuo", 
                                     placeholder="Ex: Losartana 50mg, Metformina 850mg...",
                                     height=100)
        
        with col6:
            alergias = st.text_area("Alergias", 
                                   placeholder="Ex: Dipirona, Penicilina, Látex...",
                                   height=100)
        
        submitted = st.form_submit_button("💾 Cadastrar Paciente", type="primary", use_container_width=True)
        
        if submitted:
            if nome and queixa:
                # Calcular urgência baseada em regras
                urgencia = calcular_urgencia(
                    temperatura, pa_sistolica, pa_diastolica,
                    freq_respiratoria, freq_cardiaca, idade,
                    spo2, nivel_consciencia
                )
                
                # Predição ML (se disponível)
                ml_prediction = None
                if ML_AVAILABLE:
                    try:
                        patient_data = {
                            'freq_cardiaca': freq_cardiaca,
                            'spo2': spo2,
                            'temperatura': temperatura,
                            'pa_sistolica': pa_sistolica,
                            'pa_diastolica': pa_diastolica,
                            'freq_respiratoria': freq_respiratoria,
                            'idade': idade,
                            'genero': genero
                        }
                        ml_prediction = predictor.predict_pcacr(patient_data)
                    except Exception as e:
                        print(f"Erro na predição ML: {e}")
                
                # Salvar no banco de dados
                try:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO triagem (
                            Nome, Idade, PA, FC, FR, Temp, Comorbidade, Alergia,
                            Queixa_Principal, urgencia_automatica, urgencia_manual, status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        nome,
                        int(idade),
                        f"{int(pa_sistolica)}/{int(pa_diastolica)}",
                        int(freq_cardiaca),
                        int(freq_respiratoria),
                        float(temperatura),
                        comorbidades if comorbidades else "Nenhuma",
                        alergias if alergias else "Nenhuma",
                        queixa,
                        urgencia[0],  # urgencia_automatica
                        urgencia[0],  # urgencia_manual (inicialmente igual)
                        'AGUARDANDO'
                    ))
conn.commit()
                    
                    st.success(f"✅ Paciente {nome} cadastrado com sucesso!")
                    
                    # === CALCULAR SCORES CLÍNICOS PRIMEIRO (necessário para validação) ===
                    scores = calcular_todos_scores(
                        freq_cardiaca=freq_cardiaca,
                        freq_respiratoria=freq_respiratoria,
                        temperatura=temperatura,
                        pa_sistolica=pa_sistolica,
                        spo2=spo2,
                        nivel_consciencia=nivel_consciencia
                    )
                    
                    # VALIDAÇÃO CLÍNICA DO ML
                    validation_result = None
                    if ml_prediction:
                        validation_result = validar_predicao_ml(
                            ml_prediction=ml_prediction,
                            scores=scores,
                            urgencia_regras=urgencia
                        )
                    
                    # Mostrar classificações
                    col_rule, col_ml = st.columns(2)
                    with col_rule:
                        st.info(f"📋 **Classificação (Regras):** {urgencia[2]} {urgencia[0]}")
                    
                    if ml_prediction and validation_result:
                        with col_ml:
                            confidence = ml_prediction['confidence'] * 100
                            # Mostrar predição original ou validada
                            if validation_result['was_overridden']:
                                st.warning(f"🤖 **ML Original:** {ml_prediction['prediction']} ({confidence:.0f}%)")
                                st.success(f"🛡️ **Classificação Final:** {validation_result['prediction_final']}")
                            else:
                                st.info(f"🤖 **Predição ML:** {ml_prediction['prediction']} ({confidence:.0f}%)")
                        
                        # ALERTA DE SOBRESCRITA
                        if validation_result['was_overridden']:
                            alerta = formatar_alerta_override(validation_result)
                            st.error(alerta)
                        
                        # Mostrar probabilidades
                        st.markdown("**📊 Probabilidades por Classe (ML):**")
                        prob_cols = st.columns(5)
                        classes_ordem = ['PRIORIDADE MÁXIMA', 'ALTA PRIORIDADE', 'MÉDIA PRIORIDADE', 'BAIXA PRIORIDADE', 'MÍNIMA (ELETIVA)']
                        for idx, classe in enumerate(classes_ordem):
                            prob = ml_prediction['probabilities'].get(classe, 0) * 100
                            with prob_cols[idx]:
                                st.metric(classe.split()[0], f"{prob:.1f}%")
                    
                    # === SCORES CLÍNICOS ===
                    st.markdown("---")
                    st.markdown("### 📊 Scores Clínicos")
                    
                    # Legenda explicativa
                    with st.expander("ℹ️ O que significa cada score?", expanded=False):
                        st.markdown("""
                        **🚨 qSOFA** (Quick SOFA - 0 a 3 pontos)
                        - **Objetivo:** Detectar rapidamente suspeita de SEPSE
                        - **Interpretação:** qSOFA ≥ 2 → Alto risco de sepse, mortalidade ~10%
                        - **Critérios:** FR ≥22/min, PAS ≤100mmHg, Alteração mental
                        
                        **📈 NEWS2** (National Early Warning Score - 0 a 20 pontos)
                        - **Objetivo:** Identificar deterioração clínica geral
                        - **Interpretação:** 0=Mínimo | 1-4=Baixo | 5-6=Médio | ≥7=Alto risco
                        - **Uso:** Padrão ouro internacional para triagem
                        
                        **🔥 SIRS** (Síndrome da Resposta Inflamatória - 0 a 3 pontos)
                        - **Objetivo:** Detectar resposta inflamatória sistêmica
                        - **Interpretação:** SIRS ≥ 2 → Provável processo inflamatório/infeccioso
                        - **Critérios:** FC >90, FR >20, Temp <36 ou >38°C
                        
                        **⚠️ MEWS** (Modified Early Warning Score - 0 a 15 pontos)
                        - **Objetivo:** Sistema de alerta precoce (muito usado em hospitais brasileiros)
                        - **Interpretação:** 0-1=Baixo | 2-3=Médio | 4-5=Alto | ≥6=Crítico
                        - **Uso:** Complementa o NEWS2 com critérios ligeiramente diferentes
                        
                        **🧠 GCS** (Glasgow Coma Scale - 3 a 15 pontos)
                        - **Objetivo:** Avaliar nível de consciência (função neurológica)
                        - **Interpretação:** 15=Normal | 13-14=Leve | 9-12=Moderado | ≤8=Coma
                        - **Uso:** Essencial para trauma, AVC, alteração do estado mental
                        
                        **😣 EVA** (Escala Visual Analógica de Dor - 0 a 10 pontos)
                        - **Objetivo:** Quantificar intensidade da dor do paciente
                        - **Interpretação:** 0=Sem dor | 1-3=Leve | 4-6=Moderada | 7-8=Intensa | 9-10=Insuportável
                        - **Uso:** Prioriza pacientes com dor aguda e indica necessidade de analgesia
                        """)
                    
                    scores = calcular_todos_scores(
                        freq_cardiaca=freq_cardiaca,
                        freq_respiratoria=freq_respiratoria,
                        temperatura=temperatura,
                        pa_sistolica=pa_sistolica,
                        spo2=spo2,
                        nivel_consciencia=nivel_consciencia
                    )
                    
                    # Importar função de dor
                    from scores_clinicos import avaliar_escala_dor
                    dor_score = avaliar_escala_dor(intensidade_dor)
                    
                    # Primeira linha: qSOFA, NEWS2, SIRS
                    col_qsofa, col_news2, col_sirs = st.columns(3)
                    
                    # qSOFA
                    with col_qsofa:
                        qsofa = scores['qsofa']
                        cor_map = {'vermelho': '🔴', 'laranja': '🟠', 'verde': '🟢'}
                        st.markdown(f"#### {cor_map.get(qsofa['cor'], '⚪')} qSOFA")
                        st.metric("Score", f"{qsofa['score']}/3")
                        st.markdown(f"**{qsofa['alerta']}**")
                        if qsofa['criterios']:
                            st.markdown("Critérios:")
                            for c in qsofa['criterios']:
                                st.markdown(f"- {c}")
                    
                    # NEWS2
                    with col_news2:
                        news2 = scores['news2']
                        cor_map = {'vermelho': '🔴', 'laranja': '🟠', 'amarelo': '🟡', 'verde': '🟢'}
                        st.markdown(f"#### {cor_map.get(news2['cor'], '⚪')} NEWS2")
                        st.metric("Score", f"{news2['score']}/20")
                        st.markdown(f"**{news2['alerta']}**")
                        st.markdown(f"Risco: {news2['risco']}")
                    
                    # SIRS
                    with col_sirs:
                        sirs = scores['sirs']
                        cor_map = {'laranja': '🟠', 'amarelo': '🟡', 'verde': '🟢'}
                        st.markdown(f"#### {cor_map.get(sirs['cor'], '⚪')} SIRS")
                        st.metric("Score", f"{sirs['score']}/3")
                        st.markdown(f"**{sirs['alerta']}**")
                        st.markdown(f"*{sirs['observacao']}*")
                    
                    # Segunda linha: MEWS, GCS, Dor
                    col_mews, col_gcs, col_dor = st.columns(3)
                    
                    # MEWS
                    with col_mews:
                        mews = scores['mews']
                        cor_map = {'vermelho': '🔴', 'laranja': '🟠', 'amarelo': '🟡', 'verde': '🟢'}
                        st.markdown(f"#### {cor_map.get(mews['cor'], '⚪')} MEWS")
                        st.metric("Score", f"{mews['score']}/15")
                        st.markdown(f"**{mews['alerta']}**")
                        st.markdown(f"Risco: {mews['risco']}")
                    
                    # GCS
                    with col_gcs:
                        gcs = scores['gcs']
                        cor_map = {'vermelho': '🔴', 'laranja': '🟠', 'amarelo': '🟡', 'verde': '🟢'}
                        st.markdown(f"#### {cor_map.get(gcs['cor'], '⚪')} GCS")
                        st.metric("Score", f"{gcs['score']}/15")
                        st.markdown(f"**{gcs['alerta']}**")
                        st.markdown(f"*{gcs['descricao']}*")
                    
                    # Escala de Dor
                    with col_dor:
                        cor_map = {'vermelho': '🔴', 'laranja': '🟠', 'amarelo': '🟡', 'verde': '🟢'}
                        st.markdown(f"#### {cor_map.get(dor_score['cor'], '⚪')} Dor (EVA)")
                        st.metric("Intensidade", f"{dor_score['emoji']} {dor_score['score']}/10")
                        st.markdown(f"**{dor_score['alerta']}**")
                        st.markdown(f"*{dor_score['categoria']}*")
                    
                    time.sleep(2)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erro ao cadastrar paciente: {str(e)}")
            else:
                st.error("❌ Preencha os campos obrigatórios (Nome e Queixa)")

def mostrar_analise_clinica(df):
    """Análise clínica com visualizações elegantes e clinicamente relevantes"""
    
    if df.empty:
        st.info("📊 Nenhum dado disponível para análise.")
        return
    
    # Configuração de tema claro para os gráficos com texto escuro
    template = "plotly_white"
    
    # Configuração global de fonte escura para TODOS os gráficos
    config_layout = {
        'plot_bgcolor': 'white',
        'paper_bgcolor': 'white',
        'font': dict(
            family='Arial, sans-serif',
            size=13,
            color='#000000'
        ),
        'title': dict(
            font=dict(size=14, color='#000000', family='Arial, sans-serif')
        ),
        'xaxis': dict(
            title_font=dict(size=13, color='#000000'),
            tickfont=dict(size=12, color='#000000'),
            color='#000000'
        ),
        'yaxis': dict(
            title_font=dict(size=13, color='#000000'),
            tickfont=dict(size=12, color='#000000'),
            color='#000000'
        ),
        'legend': dict(
            font=dict(size=12, color='#000000'),
            title=dict(font=dict(size=12, color='#000000')),
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='#cbd5e1',
            borderwidth=1
        ),
        'hoverlabel': dict(
            bgcolor='white',
            font_size=12,
            font_family='Arial, sans-serif',
            font_color='#000000',
            bordercolor='#cbd5e1'
        ),
        'coloraxis': dict(
            colorbar=dict(
                tickfont=dict(color='#000000'),
                title=dict(font=dict(color='#000000'))
            )
        )
    }
    
    # Cores PCACR
    cores_prioridade = {
        'PRIORIDADE MÁXIMA': '#dc2626',
        'ALTA PRIORIDADE': '#ea580c',
        'MÉDIA PRIORIDADE': '#eab308',
        'BAIXA PRIORIDADE': '#16a34a',
        'MÍNIMA (ELETIVA)': '#2563eb'
    }
    
    # ==================== HEADER COMPACTO ====================
    st.markdown("""
    <style>
    .analise-header h2, .analise-header p {
        color: #ffffff !important;
    }
    </style>
    <div class='analise-header' style='background: linear-gradient(135deg, #036672 0%, #059669 100%); 
                padding: 15px 20px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
        <h2 style='margin: 0; font-size: 1.4rem;'>📊 Análise Clínica e Correlações</h2>
        <p style='margin: 5px 0 0 0; font-size: 0.85rem; opacity: 0.95;'>
            Visualizações baseadas em protocolos NEWS2 e MEWS
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Calcular total de pacientes
    total = len(df)
    
    # ==================== SEÇÃO 2: PANORAMA GERAL ====================
    st.markdown("""
    <div style='background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 25px;'>
        <h3 style='color: #1e293b; margin: 0 0 15px 0; font-size: 1.1rem;'>📈 Panorama de Distribuição por Prioridade</h3>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1.3, 1], gap="medium")
    
    with col1:
        if 'urgencia_manual' in df.columns:
            # Gráfico de barras horizontal
            prioridade_counts = df['urgencia_manual'].value_counts()
            prioridade_df = pd.DataFrame({
                'Prioridade': prioridade_counts.index,
                'Pacientes': prioridade_counts.values
            })
            
            fig_barras = px.bar(
                prioridade_df, 
                y='Prioridade', 
                x='Pacientes',
                color='Prioridade',
                color_discrete_map=cores_prioridade,
                orientation='h',
                text='Pacientes',
                labels={'Pacientes': 'Pacientes'},
                template=template
            )
            
            fig_barras.update_traces(
                textposition='outside', 
                textfont=dict(size=12, color='#000000', family='Arial', weight='bold'),
                marker=dict(line=dict(color='white', width=2), opacity=0.9),
                hovertemplate='<b>%{y}</b><br>Pacientes: %{x}<extra></extra>'
            )
            
            layout_barras = config_layout.copy()
            layout_barras.pop('title', None)  # Remove título undefined
            layout_barras['yaxis'] = {
                'categoryorder': 'array', 
                'categoryarray': ['MÍNIMA (ELETIVA)', 'BAIXA PRIORIDADE', 'MÉDIA PRIORIDADE', 'ALTA PRIORIDADE', 'PRIORIDADE MÁXIMA'],
                'title': None,
                'tickfont': dict(size=10, color='#475569')
            }
            layout_barras['xaxis'] = {
                'title': dict(text='Número de Pacientes', font=dict(size=11, color='#64748b')),
                'tickfont': dict(size=10, color='#64748b'),
                'gridcolor': '#f1f5f9'
            }
            layout_barras['plot_bgcolor'] = 'white'
            layout_barras['paper_bgcolor'] = 'white'
            
            fig_barras.update_layout(
                showlegend=False,
                height=300,
                margin=dict(l=150, r=50, t=30, b=50),
                **layout_barras
            )
            
            st.plotly_chart(fig_barras, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        if 'urgencia_manual' in df.columns:
            # Pizza com proporção
            fig_pizza = px.pie(
                values=prioridade_counts.values, 
                names=prioridade_counts.index,
                color=prioridade_counts.index,
                color_discrete_map=cores_prioridade,
                template=template,
                hole=0.5  # Donut chart mais fino
            )
            
            pizza_layout = config_layout.copy()
            pizza_layout.pop('title', None)  # Remove título undefined
            pizza_layout['plot_bgcolor'] = 'white'
            pizza_layout['paper_bgcolor'] = 'white'
            pizza_layout['height'] = 300
            pizza_layout['margin'] = dict(l=20, r=120, t=30, b=20)
            pizza_layout['showlegend'] = True
            pizza_layout['legend'] = dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.05,
                font=dict(size=9, color='#475569'),
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='#e5e7eb',
                borderwidth=1
            )
            
            fig_pizza.update_layout(**pizza_layout)
            
            fig_pizza.update_traces(
                textfont=dict(size=11, color='#000000', family='Arial', weight='bold'),
                textposition='inside',
                textinfo='percent',
                marker=dict(line=dict(color='white', width=3)),
                hovertemplate='<b>%{label}</b><br>%{value} pacientes<br>%{percent}<extra></extra>'
            )
            
            st.plotly_chart(fig_pizza, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==================== SEÇÃO 3: MATRIZ DE RISCO PA × FC ====================
    st.markdown("### 💓 Matriz de Risco: PA Sistólica × Frequência Cardíaca")
    st.caption("🎯 Identifica pacientes em choque, hipertensão ou instabilidade cardiovascular")
    
    if 'PA' in df.columns and 'FC' in df.columns:
        df_hemo = df.copy()
        df_hemo['PA_Sistolica'] = df_hemo['PA'].apply(lambda x: int(str(x).split('/')[0]) if '/' in str(x) else None)
        df_hemo = df_hemo.dropna(subset=['PA_Sistolica', 'FC'])
        
        fig_matriz = px.scatter(
            df_hemo, 
            x='FC', 
            y='PA_Sistolica',
            color='urgencia_manual',
            color_discrete_map=cores_prioridade,
            size=[20]*len(df_hemo),
            hover_data=['Nome'] if 'Nome' in df.columns else None,
            labels={'FC': 'Frequência Cardíaca (bpm)', 'PA_Sistolica': 'PA Sistólica (mmHg)'},
            template=template,
            title='Correlação Hemodinâmica - Padrões de Instabilidade'
        )
        
        # Zonas de referência clínica
        fig_matriz.add_hrect(y0=90, y1=140, line_width=0, fillcolor="green", opacity=0.08, 
                            annotation_text="PA Normal", annotation_position="right")
        fig_matriz.add_hrect(y0=140, y1=200, line_width=0, fillcolor="orange", opacity=0.08, 
                            annotation_text="Hipertensão", annotation_position="right")
        fig_matriz.add_hrect(y0=0, y1=90, line_width=0, fillcolor="red", opacity=0.08, 
                            annotation_text="Hipotensão/Choque", annotation_position="right")
        
        fig_matriz.add_vrect(x0=60, x1=100, line_width=0, fillcolor="green", opacity=0.06)
        fig_matriz.add_vrect(x0=100, x1=150, line_width=0, fillcolor="orange", opacity=0.06)
        
        fig_matriz.update_layout(height=500, **config_layout)
        
        st.plotly_chart(fig_matriz, use_container_width=True)
    
    st.markdown("---")
    
    # ==================== SEÇÃO 4: RADAR CHART - PERFIL INDIVIDUAL ====================
    st.markdown("### 🎯 Radar de Sinais Vitais - Perfil Individual")
    st.caption("📋 Selecione um paciente para ver seu perfil completo de sinais vitais")
    
    if 'Nome' in df.columns and len(df) > 0:
        paciente_selecionado = st.selectbox(
            "Escolha o paciente:",
            options=df['Nome'].tolist(),
            key="select_paciente_radar"
        )
        
        if paciente_selecionado:
            paciente = df[df['Nome'] == paciente_selecionado].iloc[0]
            
            col1, col2 = st.columns([2, 3])
            
            with col1:
                # Card com dados do paciente
                urgencia = paciente.get('urgencia_manual', 'N/A')
                cor = cores_prioridade.get(urgencia, '#64748b')
                
                st.markdown(f"""
                <div style='background: white; padding: 20px; border-radius: 12px; 
                            border-left: 5px solid {cor}; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                    <h4 style='margin: 0 0 15px 0; color: #1e293b;'>👤 {paciente['Nome']}</h4>
                    <div style='margin: 8px 0;'><strong>Classificação:</strong> <span style='color: {cor};'>{urgencia}</span></div>
                    <div style='margin: 8px 0;'><strong>Idade:</strong> {paciente.get('Idade', 'N/A')} anos</div>
                    <div style='margin: 8px 0;'><strong>Temperatura:</strong> {paciente.get('Temp', 'N/A')}°C</div>
                    <div style='margin: 8px 0;'><strong>PA:</strong> {paciente.get('PA', 'N/A')}</div>
                    <div style='margin: 8px 0;'><strong>FC:</strong> {paciente.get('FC', 'N/A')} bpm</div>
                    <div style='margin: 8px 0;'><strong>FR:</strong> {paciente.get('FR', 'N/A')} irpm</div>
                    <div style='margin: 8px 0;'><strong>SpO₂:</strong> {paciente.get('SpO2', 'N/A')}%</div>
                    <div style='margin: 8px 0;'><strong>Queixa:</strong> {paciente.get('Queixa_Principal', 'N/A')}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Radar chart
                parametros = []
                valores_normalizados = []
                
                # Normalizar cada parâmetro (0-100 onde 100 = normal)
                if 'FR' in paciente and pd.notna(paciente['FR']):
                    fr = paciente['FR']
                    if fr < 12:
                        val = 100 - ((12 - fr) / 12 * 50)
                    elif fr > 20:
                        val = 100 - ((fr - 20) / 10 * 50)
                    else:
                        val = 100
                    parametros.append('FR')
                    valores_normalizados.append(max(0, min(100, val)))
                
                if 'FC' in paciente and pd.notna(paciente['FC']):
                    fc = paciente['FC']
                    if fc < 60:
                        val = 100 - ((60 - fc) / 20 * 50)
                    elif fc > 100:
                        val = 100 - ((fc - 100) / 50 * 50)
                    else:
                        val = 100
                    parametros.append('FC')
                    valores_normalizados.append(max(0, min(100, val)))
                
                if 'Temp' in paciente and pd.notna(paciente['Temp']):
                    temp = paciente['Temp']
                    if temp < 36:
                        val = 100 - ((36 - temp) / 1 * 50)
                    elif temp > 37.5:
                        val = 100 - ((temp - 37.5) / 2 * 50)
                    else:
                        val = 100
                    parametros.append('Temp')
                    valores_normalizados.append(max(0, min(100, val)))
                
                if 'PA' in paciente and pd.notna(paciente['PA']):
                    pa_sist = int(str(paciente['PA']).split('/')[0]) if '/' in str(paciente['PA']) else 120
                    if pa_sist < 90:
                        val = 100 - ((90 - pa_sist) / 20 * 50)
                    elif pa_sist > 140:
                        val = 100 - ((pa_sist - 140) / 40 * 50)
                    else:
                        val = 100
                    parametros.append('PA')
                    valores_normalizados.append(max(0, min(100, val)))
                
                if 'SpO2' in paciente and pd.notna(paciente['SpO2']):
                    spo2 = paciente['SpO2']
                    if spo2 < 95:
                        val = (spo2 / 95) * 100
                    else:
                        val = 100
                    parametros.append('SpO₂')
                    valores_normalizados.append(max(0, min(100, val)))
                
                fig_radar = go.Figure()
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=valores_normalizados,
                    theta=parametros,
                    fill='toself',
                    fillcolor=f'rgba({int(cor[1:3], 16)}, {int(cor[3:5], 16)}, {int(cor[5:7], 16)}, 0.3)',
                    line=dict(color=cor, width=3),
                    name=paciente['Nome']
                ))
                
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True, 
                            range=[0, 100],
                            tickfont=dict(size=11, color='#000000'),
                            tickvals=[50, 100],
                            ticktext=['Alterado', 'Normal']
                        ),
                        bgcolor='white',
                        angularaxis=dict(
                            tickfont=dict(size=12, color='#000000')
                        )
                    ),
                    showlegend=False,
                    height=400,
                    title=dict(
                        text='Perfil de Sinais Vitais',
                        font=dict(size=14, color='#000000')
                    ),
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(family='Arial, sans-serif', size=13, color='#000000')
                )
                
                st.plotly_chart(fig_radar, use_container_width=True)
    
    st.markdown("---")
    
    # ==================== SEÇÃO 5: ANÁLISES AVANÇADAS ====================
    st.markdown("### 🔬 Análises Clínicas Avançadas")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Distribuição de Sinais", "🌡️ Correlações", "⚠️ Alertas Clínicos", "📈 Análise Gestão"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Histograma de temperatura
            if 'Temp' in df.columns:
                fig_temp = px.histogram(
                    df, 
                    x='Temp',
                    nbins=20,
                    title='Distribuição de Temperatura',
                    labels={'Temp': 'Temperatura (°C)', 'count': 'Número de Pacientes'},
                    template=template,
                    color_discrete_sequence=['#036672']
                )
                
                fig_temp.add_vline(x=36.5, line_dash="dash", line_color="green", 
                                  annotation_text="Normal", annotation_position="top")
                fig_temp.add_vline(x=37.5, line_dash="dash", line_color="orange", 
                                  annotation_text="Febre", annotation_position="top")
                
                fig_temp.update_layout(height=350, **config_layout)
                st.plotly_chart(fig_temp, use_container_width=True)
        
        with col2:
            # Histograma de FC
            if 'FC' in df.columns:
                fig_fc_hist = px.histogram(
                    df, 
                    x='FC',
                    nbins=20,
                    title='Distribuição de Frequência Cardíaca',
                    labels={'FC': 'FC (bpm)', 'count': 'Número de Pacientes'},
                    template=template,
                    color_discrete_sequence=['#059669']
                )
                
                fig_fc_hist.add_vline(x=60, line_dash="dash", line_color="blue", 
                                     annotation_text="Bradicardia", annotation_position="top")
                fig_fc_hist.add_vline(x=100, line_dash="dash", line_color="orange", 
                                     annotation_text="Taquicardia", annotation_position="top")
                
                fig_fc_hist.update_layout(height=350, **config_layout)
                st.plotly_chart(fig_fc_hist, use_container_width=True)
    
    with tab2:
        # Box plots comparativos
        if 'urgencia_manual' in df.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                if 'Temp' in df.columns:
                    fig_box_temp = px.box(
                        df,
                        x='urgencia_manual',
                        y='Temp',
                        color='urgencia_manual',
                        color_discrete_map=cores_prioridade,
                        title='Temperatura por Prioridade',
                        labels={'urgencia_manual': 'Prioridade', 'Temp': 'Temperatura (°C)'},
                        template=template
                    )
                    fig_box_temp.update_layout(height=400, showlegend=False, **config_layout)
                    st.plotly_chart(fig_box_temp, use_container_width=True)
            
            with col2:
                if 'FC' in df.columns:
                    fig_box_fc = px.box(
                        df,
                        x='urgencia_manual',
                        y='FC',
                        color='urgencia_manual',
                        color_discrete_map=cores_prioridade,
                        title='Frequência Cardíaca por Prioridade',
                        labels={'urgencia_manual': 'Prioridade', 'FC': 'FC (bpm)'},
                        template=template
                    )
                    fig_box_fc.update_layout(height=400, showlegend=False, **config_layout)
                    st.plotly_chart(fig_box_fc, use_container_width=True)
    
    with tab3:
        st.markdown("#### ⚠️ Indicadores de Risco Clínico")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            choque = 0
            if 'PA' in df.columns and 'FC' in df.columns:
                df_temp = df.copy()
                df_temp['PA_Sist'] = df_temp['PA'].apply(lambda x: int(str(x).split('/')[0]) if '/' in str(x) else 999)
                choque = len(df_temp[(df_temp['PA_Sist'] < 90) & (df_temp['FC'] > 100)])
            
            st.metric("🩸 Choque Possível", choque, 
                     help="PA<90 + FC>100",
                     delta="Crítico" if choque > 0 else None)
        
        with col2:
            sepse = 0
            if all(col in df.columns for col in ['Temp', 'FC', 'FR']):
                sepse = len(df[(df['Temp'] > 38) & (df['FC'] > 90) & (df['FR'] > 20)])
            
            st.metric("🦠 Risco Sepse", sepse,
                     help="Febre + Taquicardia + Taquipneia",
                     delta="Atenção" if sepse > 0 else None)
        
        with col3:
            insuf_resp = 0
            if 'FR' in df.columns:
                insuf_resp = len(df[(df['FR'] < 10) | (df['FR'] > 25)])
            
            st.metric("🫁 Insuf. Respiratória", insuf_resp,
                     help="FR <10 ou >25",
                     delta="Alerta" if insuf_resp > 0 else None)
        
        with col4:
            criticos = len(df[df['urgencia_manual'] == 'PRIORIDADE MÁXIMA']) if 'urgencia_manual' in df.columns else 0
            altos = len(df[df['urgencia_manual'] == 'ALTA PRIORIDADE']) if 'urgencia_manual' in df.columns else 0
            pct_critico = (criticos / total * 100) if total > 0 else 0
            st.metric("🚨 Taxa Críticos", f"{pct_critico:.1f}%",
                     help="% vermelhos/laranjas",
                     delta=f"{criticos + altos}/{total}")
    
    with tab4:
        st.markdown("#### 📊 Análises para Gestão")
        
        # ==================== 1. TREEMAP HIERÁRQUICO ====================
        st.markdown("##### 🌳 Treemap Hierárquico de Prioridades")
        if 'urgencia_manual' in df.columns:
            prioridade_counts = df['urgencia_manual'].value_counts()
            treemap_df = pd.DataFrame({
                'Prioridade': prioridade_counts.index,
                'Pacientes': prioridade_counts.values,
                'Parent': ['Total'] * len(prioridade_counts)
            })
            
            # Adicionar linha total
            total_row = pd.DataFrame({
                'Prioridade': ['Total'],
                'Pacientes': [len(df)],
                'Parent': ['']
            })
            treemap_df = pd.concat([total_row, treemap_df], ignore_index=True)
            
            fig_treemap = px.treemap(
                treemap_df,
                names='Prioridade',
                parents='Parent',
                values='Pacientes',
                color='Prioridade',
                color_discrete_map={**cores_prioridade, 'Total': '#f1f5f9'},
                title='Proporção Visual das Prioridades'
            )
            
            treemap_layout = config_layout.copy()
            treemap_layout.pop('title', None)
            treemap_layout['height'] = 400
            treemap_layout['margin'] = dict(l=10, r=10, t=40, b=10)
            
            fig_treemap.update_traces(
                textfont=dict(size=14, color='white', family='Arial', weight='bold'),
                marker=dict(line=dict(color='white', width=2))
            )
            
            fig_treemap.update_layout(**treemap_layout)
            st.plotly_chart(fig_treemap, use_container_width=True, config={'displayModeBar': False})
        
        st.markdown("---")
        
        # ==================== 2. GAUGE CHARTS ====================
        st.markdown("##### ⏱️ Indicadores de Performance")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Taxa de ocupação crítica
            taxa_critica = (criticos / total * 100) if total > 0 else 0
            
            fig_gauge1 = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=taxa_critica,
                title={'text': "Taxa Críticos (%)", 'font': {'size': 14, 'color': '#1e293b'}},
                delta={'reference': 20, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
                gauge={
                    'axis': {'range': [None, 100], 'tickfont': {'size': 10, 'color': '#475569'}},
                    'bar': {'color': "#dc2626"},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "#e5e7eb",
                    'steps': [
                        {'range': [0, 15], 'color': '#d1fae5'},
                        {'range': [15, 30], 'color': '#fef3c7'},
                        {'range': [30, 100], 'color': '#fee2e2'}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 30
                    }
                }
            ))
            
            fig_gauge1.update_layout(
                height=250,
                margin=dict(l=20, r=20, t=50, b=20),
                paper_bgcolor='white',
                font=dict(color='#1e293b')
            )
            
            st.plotly_chart(fig_gauge1, use_container_width=True, config={'displayModeBar': False})
        
        with col2:
            # Taxa de urgências altas
            taxa_alta = ((criticos + altos) / total * 100) if total > 0 else 0
            
            fig_gauge2 = go.Figure(go.Indicator(
                mode="gauge+number",
                value=taxa_alta,
                title={'text': "Alta + Máxima (%)", 'font': {'size': 14, 'color': '#1e293b'}},
                gauge={
                    'axis': {'range': [None, 100], 'tickfont': {'size': 10, 'color': '#475569'}},
                    'bar': {'color': "#ea580c"},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "#e5e7eb",
                    'steps': [
                        {'range': [0, 30], 'color': '#d1fae5'},
                        {'range': [30, 50], 'color': '#fef3c7'},
                        {'range': [50, 100], 'color': '#fed7aa'}
                    ]
                }
            ))
            
            fig_gauge2.update_layout(
                height=250,
                margin=dict(l=20, r=20, t=50, b=20),
                paper_bgcolor='white',
                font=dict(color='#1e293b')
            )
            
            st.plotly_chart(fig_gauge2, use_container_width=True, config={'displayModeBar': False})
        
        with col3:
            # Capacidade total
            capacidade_maxima = 50  # Ajustar conforme necessário
            taxa_ocupacao = (total / capacidade_maxima * 100) if capacidade_maxima > 0 else 0
            
            fig_gauge3 = go.Figure(go.Indicator(
                mode="gauge+number",
                value=taxa_ocupacao,
                title={'text': "Taxa Ocupação (%)", 'font': {'size': 14, 'color': '#1e293b'}},
                number={'suffix': "%"},
                gauge={
                    'axis': {'range': [None, 100], 'tickfont': {'size': 10, 'color': '#475569'}},
                    'bar': {'color': "#036672"},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "#e5e7eb",
                    'steps': [
                        {'range': [0, 60], 'color': '#d1fae5'},
                        {'range': [60, 80], 'color': '#fef3c7'},
                        {'range': [80, 100], 'color': '#fee2e2'}
                    ]
                }
            ))
            
            fig_gauge3.update_layout(
                height=250,
                margin=dict(l=20, r=20, t=50, b=20),
                paper_bgcolor='white',
                font=dict(color='#1e293b')
            )
            
            st.plotly_chart(fig_gauge3, use_container_width=True, config={'displayModeBar': False})

def mostrar_relatorios(df):
    
    if df.empty:
        st.info("📊 Nenhum dado disponível para análise.")
        return
    
    # Configuração de tema claro para os gráficos com texto escuro
    template = "plotly_white"
    
    # Configuração global de fonte escura para TODOS os gráficos
    config_layout = {
        'plot_bgcolor': 'white',
        'paper_bgcolor': 'white',
        'font': dict(
            family='Arial, sans-serif',
            size=13,
            color='#000000'  # Preto puro para máxima legibilidade
        ),
        'title': dict(
            font=dict(size=14, color='#000000', family='Arial, sans-serif')
        ),
        'xaxis': dict(
            title_font=dict(size=13, color='#000000'),
            tickfont=dict(size=12, color='#000000'),
            color='#000000'
        ),
        'yaxis': dict(
            title_font=dict(size=13, color='#000000'),
            tickfont=dict(size=12, color='#000000'),
            color='#000000'
        ),
        'legend': dict(
            font=dict(size=12, color='#000000'),
            title=dict(font=dict(size=12, color='#000000')),
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='#cbd5e1',
            borderwidth=1
        ),
        'hoverlabel': dict(
            bgcolor='white',
            font_size=12,
            font_family='Arial, sans-serif',
            font_color='#000000',
            bordercolor='#cbd5e1'
        ),
        'coloraxis': dict(
            colorbar=dict(
                tickfont=dict(color='#000000'),
                title=dict(font=dict(color='#000000'))
            )
        )
    }
    
    # ========== SEÇÃO 1: PANORAMA DE RISCO ==========
    st.markdown("#### 🎯 Panorama de Risco - Distribuição por Prioridade PCACR")
    
    if 'urgencia_manual' in df.columns:
        # Contar pacientes por prioridade
        prioridade_counts = df['urgencia_manual'].value_counts()
        
        # Cores e ordem PCACR
        cores_prioridade = {
            'PRIORIDADE MÁXIMA': '#dc2626',
            'ALTA PRIORIDADE': '#ea580c',
            'MÉDIA PRIORIDADE': '#eab308',
            'BAIXA PRIORIDADE': '#16a34a',
            'MÍNIMA (ELETIVA)': '#2563eb'
        }
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Gráfico de barras horizontal com tempos-alvo
            prioridade_df = pd.DataFrame({
                'Prioridade': prioridade_counts.index,
                'Pacientes': prioridade_counts.values
            })
            
            fig_barras = px.bar(
                prioridade_df, 
                y='Prioridade', 
                x='Pacientes',
                color='Prioridade',
                color_discrete_map=cores_prioridade,
                orientation='h',
                text='Pacientes',
                labels={'Pacientes': 'Número de Pacientes'},
                template=template
            )
            
            fig_barras.update_traces(textposition='outside', textfont=dict(size=13, color='#000000'))
            
            # Merge config_layout com yaxis customizado
            layout_barras = config_layout.copy()
            layout_barras['yaxis'] = {
                'categoryorder': 'array', 
                'categoryarray': ['MÍNIMA (ELETIVA)', 'BAIXA PRIORIDADE', 'MÉDIA PRIORIDADE', 'ALTA PRIORIDADE', 'PRIORIDADE MÁXIMA'],
                'title_font': dict(size=13, color='#000000'),
                'tickfont': dict(size=12, color='#000000')
            }
            
            fig_barras.update_layout(
                showlegend=False,
                height=350,
                **layout_barras
            )
            
            st.plotly_chart(fig_barras, use_container_width=True)
        
        with col2:
            # Pizza com proporção geral
            fig_pizza = px.pie(
                values=prioridade_counts.values, 
                names=prioridade_counts.index,
                title='Proporção de Urgências',
                color=prioridade_counts.index,
                color_discrete_map=cores_prioridade,
                template=template
            )
            
            fig_pizza.update_layout(
                height=350,
                **config_layout
            )
            
            fig_pizza.update_traces(
                textfont=dict(size=14, color='#000000', family='Arial'),
                textposition='inside',
                insidetextorientation='radial',
                marker=dict(line=dict(color='white', width=2))
            )
            
            st.plotly_chart(fig_pizza, use_container_width=True)
    
    st.markdown("---")
    
    # ========== SEÇÃO 2: MATRIZ PA × FC (INSTABILIDADE HEMODINÂMICA) ==========
    st.markdown("#### 💓 Matriz PA × FC - Correlação Hemodinâmica")
    st.caption("Identifica pacientes em choque, hipertensão ou instabilidade cardiovascular")
    
    if 'PA' in df.columns and 'FC' in df.columns:
        # Extrair PA sistólica
        df_hemo = df.copy()
        df_hemo['PA_Sistolica'] = df_hemo['PA'].apply(lambda x: int(str(x).split('/')[0]) if '/' in str(x) else None)
        df_hemo = df_hemo.dropna(subset=['PA_Sistolica', 'FC'])
        
        # Scatter plot PA x FC
        fig_scatter = px.scatter(
            df_hemo, 
            x='FC', 
            y='PA_Sistolica',
            color='urgencia_manual',
            color_discrete_map=cores_prioridade if 'urgencia_manual' in df.columns else None,
            size=[15]*len(df_hemo),
            hover_data=['Nome'] if 'Nome' in df.columns else None,
            labels={'FC': 'Frequência Cardíaca (bpm)', 'PA_Sistolica': 'PA Sistólica (mmHg)'},
            template=template
        )
        
        # Adicionar zonas de referência
        fig_scatter.add_hrect(y0=90, y1=140, line_width=0, fillcolor="green", opacity=0.1, annotation_text="PA Normal", annotation_position="right")
        fig_scatter.add_hrect(y0=140, y1=200, line_width=0, fillcolor="orange", opacity=0.1, annotation_text="Hipertensão", annotation_position="right")
        fig_scatter.add_hrect(y0=0, y1=90, line_width=0, fillcolor="red", opacity=0.1, annotation_text="Hipotensão/Choque", annotation_position="right")
        
        fig_scatter.add_vrect(x0=60, x1=100, line_width=0, fillcolor="green", opacity=0.08)
        fig_scatter.add_vrect(x0=100, x1=200, line_width=0, fillcolor="orange", opacity=0.08)
        
        fig_scatter.update_layout(
            height=450,
            **config_layout
        )
        
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    st.markdown("---")
    
    # ========== SEÇÃO 3: RADAR CHART - PERFIL DE SINAIS VITAIS ==========
    st.markdown("#### 🎯 Perfil de Sinais Vitais - Radar de Alterações")
    st.caption("Mostra quais parâmetros estão mais alterados na população")
    
    # Calcular alterações por parâmetro
    alteracoes = {
        'Febre (>37.5°C)': len(df[df['Temp'] > 37.5]) if 'Temp' in df.columns else 0,
        'Taquicardia (FC>100)': len(df[df['FC'] > 100]) if 'FC' in df.columns else 0,
        'Taquipneia (FR>20)': len(df[df['FR'] > 20]) if 'FR' in df.columns else 0,
        'Hipotensão (PA<90)': len(df[df['PA'].apply(lambda x: int(str(x).split('/')[0]) < 90 if '/' in str(x) else False)]) if 'PA' in df.columns else 0,
        'Consciência Alt.': len(df[df.get('Nivel_Consciencia', 'Alerta') != 'Alerta']) if 'Nivel_Consciencia' in df.columns else 0
    }
    
    total = len(df)
    alteracoes_pct = {k: (v/total)*100 if total > 0 else 0 for k, v in alteracoes.items()}
    
    fig_radar = go.Figure()
    
    fig_radar.add_trace(go.Scatterpolar(
        r=list(alteracoes_pct.values()),
        theta=list(alteracoes_pct.keys()),
        fill='toself',
        fillcolor='rgba(3, 102, 114, 0.3)',
        line=dict(color='#036672', width=2),
        name='% Alterado'
    ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, 
                range=[0, 100], 
                ticksuffix='%',
                tickfont=dict(size=12, color='#000000')
            ),
            bgcolor='white',
            angularaxis=dict(
                tickfont=dict(size=12, color='#000000')
            )
        ),
        showlegend=False,
        height=400,
        title=dict(
            text='Percentual de Pacientes com Alterações',
            font=dict(size=14, color='#000000')
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(
            family='Arial, sans-serif',
            size=13,
            color='#000000'
        )
    )
    
    st.plotly_chart(fig_radar, use_container_width=True)
    
    st.markdown("---")
    
    # ========== SEÇÃO 4: INDICADORES CLÍNICOS CRÍTICOS ==========
    st.markdown("#### ⚠️ Indicadores Clínicos Críticos")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        choque = 0
        if 'PA' in df.columns and 'FC' in df.columns:
            df_temp = df.copy()
            df_temp['PA_Sist'] = df_temp['PA'].apply(lambda x: int(str(x).split('/')[0]) if '/' in str(x) else 999)
            choque = len(df_temp[(df_temp['PA_Sist'] < 90) & (df_temp['FC'] > 100)])
        
        st.metric("🩸 Choque Possível", choque, 
                 help="PA sistólica <90 + FC >100",
                 delta="Crítico" if choque > 0 else "Normal")
    
    with col2:
        sepse_risco = 0
        if all(col in df.columns for col in ['Temp', 'FC', 'FR']):
            sepse_risco = len(df[(df['Temp'] > 38) & (df['FC'] > 90) & (df['FR'] > 20)])
        
        st.metric("🦠 Risco de Sepse", sepse_risco,
                 help="Febre + Taquicardia + Taquipneia",
                 delta="Atenção" if sepse_risco > 0 else "Normal")
    
    with col3:
        insuf_resp = 0
        if 'FR' in df.columns:
            insuf_resp = len(df[(df['FR'] < 10) | (df['FR'] > 25)])
        
        st.metric("🫁 Insuf. Respiratória", insuf_resp,
                 help="FR <10 ou >25 irpm",
                 delta="Alerta" if insuf_resp > 0 else "Normal")
    
    with col4:
        criticos_total = 0
        if 'urgencia_manual' in df.columns:
            criticos_total = len(df[df['urgencia_manual'].isin(['PRIORIDADE MÁXIMA', 'ALTA PRIORIDADE'])])
        
        pct_critico = (criticos_total/total*100) if total > 0 else 0
        st.metric("🚨 Taxa de Críticos", f"{pct_critico:.0f}%",
                 help="% de pacientes vermelhos/laranjas",
                 delta=f"{criticos_total}/{total}")
    
    st.markdown("---")
    
    # ========== SEÇÃO 5: SCATTER PLOT COM DENSIDADE ==========
    if 'Temp' in df.columns and 'FC' in df.columns and len(df) > 3:
        st.markdown("#### 🌡️ Correlação: Temperatura × Frequência Cardíaca")
        st.caption("Distribuição de pacientes - cada ponto representa um paciente")
        
        # Criar dataframe completamente novo e limpo
        temp_data = df['Temp'].values
        fc_data = df['FC'].values
        
        # Remover NaN
        mask = ~(pd.isna(temp_data) | pd.isna(fc_data))
        temp_clean = temp_data[mask]
        fc_clean = fc_data[mask]
        
        # Adicionar prioridade se existir
        if 'urgencia_manual' in df.columns:
            prioridade_data = df['urgencia_manual'].values[mask]
            nome_data = df['Nome'].values[mask] if 'Nome' in df.columns else ['Paciente'] * len(temp_clean)
            
            scatter_df = pd.DataFrame({
                'Temperatura': temp_clean,
                'FrequenciaCardiaca': fc_clean,
                'Prioridade': prioridade_data,
                'Nome': nome_data
            })
            
            cores_prioridade = {
                'PRIORIDADE MÁXIMA': '#dc2626',
                'ALTA PRIORIDADE': '#ea580c',
                'MÉDIA PRIORIDADE': '#eab308',
                'BAIXA PRIORIDADE': '#16a34a',
                'MÍNIMA (ELETIVA)': '#2563eb'
            }
            
            fig_scatter = px.scatter(
                scatter_df, 
                x='FrequenciaCardiaca', 
                y='Temperatura',
                color='Prioridade',
                color_discrete_map=cores_prioridade,
                hover_data=['Nome'],
                size=[12]*len(scatter_df),
                labels={'FrequenciaCardiaca': 'Frequência Cardíaca (bpm)', 'Temperatura': 'Temperatura (°C)'},
                template=template
            )
        else:
            scatter_df = pd.DataFrame({
                'Temperatura': temp_clean,
                'FrequenciaCardiaca': fc_clean
            })
            
            fig_scatter = px.scatter(
                scatter_df, 
                x='FrequenciaCardiaca', 
                y='Temperatura',
                labels={'FrequenciaCardiaca': 'Frequência Cardíaca (bpm)', 'Temperatura': 'Temperatura (°C)'},
                template=template
            )
        
        # Adicionar zonas de referência
        fig_scatter.add_hrect(y0=36, y1=37.5, line_width=0, fillcolor="green", opacity=0.1, annotation_text="Normal", annotation_position="left")
        fig_scatter.add_hrect(y0=37.5, y1=100, line_width=0, fillcolor="red", opacity=0.1, annotation_text="Febre", annotation_position="left")
        
        fig_scatter.update_layout(
            height=450,
            **config_layout
        )
        
        st.plotly_chart(fig_scatter, use_container_width=True)

def mostrar_relatorios(df):
    """Relatórios e estatísticas"""
    st.markdown("### 📋 Relatórios")
    
    if df.empty:
        st.info("📋 Nenhum dado disponível para relatório.")
        return
    
    st.markdown("#### Dados Completos")
    
    # Aplicar estilo customizado ao dataframe
    st.markdown("""
    <style>
    /* Estilo da tabela de dados */
    div[data-testid="stDataFrame"] {
        background-color: white;
        border-radius: 8px;
        padding: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    
    /* Cabeçalho da tabela */
    div[data-testid="stDataFrame"] table thead th {
        background: linear-gradient(135deg, #036672 0%, #059669 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 12px 8px !important;
        border: none !important;
    }
    
    /* Linhas da tabela */
    div[data-testid="stDataFrame"] table tbody tr {
        background-color: white !important;
    }
    
    div[data-testid="stDataFrame"] table tbody tr:nth-child(even) {
        background-color: #f8fafc !important;
    }
    
    div[data-testid="stDataFrame"] table tbody tr:hover {
        background-color: #e0f2fe !important;
    }
    
    /* Células da tabela */
    div[data-testid="stDataFrame"] table tbody td {
        color: #1e293b !important;
        padding: 10px 8px !important;
        border-bottom: 1px solid #e5e7eb !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.dataframe(df, use_container_width=True)

# ========================= ESTILOS CSS - TEMA MODERNO =========================
st.markdown("""
<style>
    /* Remover elementos padrão do Streamlit */
    header[data-testid="stHeader"] {
        display: none;
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Fundo bege/off-white moderno */
    .stApp {
        background: linear-gradient(135deg, #faf8f5 0%, #f0ede8 100%);
    }
    
    .main {
        background-color: transparent;
    }
    
    /* Header moderno com degradê ciano/verde/azul - COMPACTO */
    .welcome-header {
        background: linear-gradient(135deg, #036672 0%, #047c7d 25%, #059669 75%, #0284c7 100%);
        border-radius: 0;
        padding: 25px 30px;
        margin: -80px -80px 30px -80px;
        box-shadow: 0 4px 12px rgba(3, 102, 114, 0.15);
        position: relative;
        overflow: hidden;
    }
    
    .welcome-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        border-radius: 50%;
    }
    
    .welcome-header h1 {
        color: white;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 5px 0;
        letter-spacing: -0.5px;
        position: relative;
    }
    
    .welcome-header p {
        color: rgba(255, 255, 255, 0.95);
        font-size: 0.95rem;
        margin: 0;
        position: relative;
        font-weight: 300;
    }
    
    .welcome-icon {
        font-size: 2.5rem;
        margin-bottom: 5px;
        margin-top: 8px;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
        position: relative;
    }
    
    /* Cards modernos com glassmorphism */
    .info-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 30px;
        margin: 10px 0;
        border: 1px solid rgba(3, 102, 114, 0.1);
        box-shadow: 
            0 8px 16px rgba(0, 0, 0, 0.06),
            0 2px 4px rgba(0, 0, 0, 0.04);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .info-card:hover {
        transform: translateY(-2px);
        box-shadow: 
            0 12px 24px rgba(0, 0, 0, 0.08),
            0 4px 8px rgba(0, 0, 0, 0.06);
    }
    
    .info-card h3 {
        color: #036672;
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 18px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .info-card p, .info-card li {
        color: #334155;
        line-height: 1.7;
        font-size: 0.95rem;
    }
    
    .info-card ul {
        margin: 15px 0;
        padding-left: 20px;
    }
    
    .info-card li {
        margin: 8px 0;
        position: relative;
        padding-left: 8px;
    }
    
    .info-card li::marker {
        color: #059669;
    }
    
    .info-card hr {
        border: none;
        border-top: 1px solid rgba(3, 102, 114, 0.15);
        margin: 20px 0;
    }
    
    /* Botões modernos com degradê */
    .stButton button {
        background: linear-gradient(135deg, #036672 0%, #047c7d 50%, #059669 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 16px 28px !important;
        color: white !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        box-shadow: 
            0 4px 12px rgba(3, 102, 114, 0.3),
            0 2px 4px rgba(5, 150, 105, 0.2) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        letter-spacing: 0.3px !important;
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, #047c7d 0%, #059669 50%, #0284c7 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 
            0 6px 20px rgba(3, 102, 114, 0.4),
            0 4px 8px rgba(5, 150, 105, 0.3) !important;
    }
    
    .stButton button:active {
        transform: translateY(0px) !important;
        box-shadow: 
            0 2px 8px rgba(3, 102, 114, 0.3),
            0 1px 4px rgba(5, 150, 105, 0.2) !important;
    }
    
    /* Sidebar moderno */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #faf8f5 0%, #f5f3f0 100%);
        border-right: 1px solid rgba(3, 102, 114, 0.1);
    }
    
    /* Badge de acesso restrito */
    .access-badge {
        display: inline-block;
        background: linear-gradient(135deg, rgba(3, 102, 114, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%);
        color: #036672;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        border: 1px solid rgba(3, 102, 114, 0.2);
        margin-top: 10px;
    }
    
    /* Animações suaves */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .info-card {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Scrollbar personalizada */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f5f3f0;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #036672, #059669);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #047c7d, #0284c7);
    }
    
    /* Estilos do Dashboard PCACR */
    .pcacr-wrapper {
        margin: 20px 0;
    }
    
    .pcacr-box {
        background: white;
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    
    .pcacr-box h2 {
        color: #000000 !important;
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 10px;
    }
    
    .pcacr-box > p {
        color: #334155 !important;
        font-size: 0.95rem;
        margin-bottom: 20px;
    }
    
    .pcacr-legend {
        display: flex;
        gap: 15px;
        flex-wrap: wrap;
        margin-bottom: 25px;
    }
    
    .pcacr-pillx {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #1e293b !important;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .pcacr-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        display: inline-block;
    }
    
    .pcacr-dot.d-max { background-color: #dc2626; }
    .pcacr-dot.d-alta { background-color: #ea580c; }
    .pcacr-dot.d-media { background-color: #eab308; }
    .pcacr-dot.d-baixa { background-color: #16a34a; }
    .pcacr-dot.d-min { background-color: #2563eb; }
    
    /* Dashboard Minimalista */
    .pcacr-box-minimal {
        background: white;
        border-radius: 12px;
        padding: 20px 25px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    
    .pcacr-header-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        padding-bottom: 15px;
        border-bottom: 1px solid #e5e7eb;
    }
    
    .pcacr-title-section h2 {
        color: #000000 !important;
        font-size: 1.2rem;
        font-weight: 700;
        margin: 0 0 4px 0;
    }
    
    .pcacr-title-section p {
        color: #64748b !important;
        font-size: 0.85rem;
        margin: 0;
    }
    
    .pcacr-legend-inline {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
    }
    
    .pcacr-dot-modern {
        width: 14px;
        height: 14px;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
        border: 2px solid white;
    }
    
    .pcacr-dot-modern.d-max { background-color: #dc2626; }
    .pcacr-dot-modern.d-alta { background-color: #ea580c; }
    .pcacr-dot-modern.d-media { background-color: #eab308; }
    .pcacr-dot-modern.d-baixa { background-color: #16a34a; }
    .pcacr-dot-modern.d-min { background-color: #2563eb; }
    
    .kpi-band-minimal {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 12px;
    }
    
    .kpi-box-minimal {
        background: #fafafa;
        border-radius: 8px;
        padding: 16px 12px;
        text-align: center;
        border: 1px solid #f0f0f0;
        transition: all 0.2s ease;
    }
    
    .kpi-box-minimal:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        background: white;
    }
    
    .kpi-icon-minimal {
        font-size: 1.5rem;
        margin-bottom: 8px;
    }
    
    .kpi-circle-modern {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin: 0 auto 8px auto;
        box-shadow: 0 2px 8px rgba(0,0,0,0.12);
        border: 3px solid white;
    }
    
    .kpi-circle-modern.d-max { background-color: #dc2626; }
    .kpi-circle-modern.d-alta { background-color: #ea580c; }
    .kpi-circle-modern.d-media { background-color: #eab308; }
    .kpi-circle-modern.d-baixa { background-color: #16a34a; }
    .kpi-circle-modern.d-min { background-color: #2563eb; }
    
    .kpi-value-minimal {
        font-size: 2rem;
        font-weight: 800;
        color: #000000 !important;
        margin: 8px 0;
        line-height: 1;
    }
    
    .kpi-label-minimal {
        font-size: 0.75rem;
        font-weight: 600;
        color: #475569 !important;
        margin: 6px 0;
        text-transform: uppercase;
        letter-spacing: 0.3px;
        line-height: 1.3;
    }
    
    .kpi-meta-minimal {
        font-size: 0.7rem;
        color: #94a3b8 !important;
        margin-top: 4px;
    }
    
    .kpi-band {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 15px;
    }
    
    .kpi-box {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 1px solid #e2e8f0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .kpi-box:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }
    
    .kpi-icon {
        font-size: 2rem;
        margin-bottom: 10px;
    }
    
    .kpi-value2 {
        font-size: 2.5rem;
        font-weight: 800;
        color: #000000 !important;
        margin: 10px 0;
        line-height: 1;
    }
    
    .kpi-label2 {
        font-size: 0.85rem;
        font-weight: 600;
        color: #1e293b !important;
        margin: 8px 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .kpi-meta2 {
        font-size: 0.8rem;
        color: #64748b !important;
        margin-top: 5px;
    }
    
    .pcacr-status-inline {
        display: inline-block;
        background: linear-gradient(135deg, rgba(5, 150, 105, 0.1), rgba(3, 102, 114, 0.1));
        color: #059669 !important;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 15px;
        border: 1px solid rgba(5, 150, 105, 0.3);
    }
    
    /* Header Global das interfaces - COLADO NO TOPO */
    .ac-global-header {
        background: linear-gradient(135deg, #036672 0%, #047c7d 50%, #059669 100%);
        border-radius: 0;
        padding: 30px 30px 20px 30px;
        margin: -80px -80px 25px -80px;
        box-shadow: 0 4px 12px rgba(3, 102, 114, 0.2);
    }
    
    .ac-header-wrap {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .ac-brand {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .ac-logo {
        font-size: 2.5rem;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
    }
    
    .ac-text {
        color: white;
    }
    
    .ac-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #ffffff !important;
        margin-bottom: 4px;
    }
    
    .ac-sub {
        font-size: 0.9rem;
        color: rgba(255, 255, 255, 0.9) !important;
        font-weight: 400;
    }
    
    .ac-status-pill {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        padding: 8px 16px;
        border-radius: 20px;
        color: #ffffff !important;
        font-size: 0.85rem;
        font-weight: 600;
        border: 1px solid rgba(255, 255, 255, 0.3);
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .ac-status-pill span {
        width: 8px;
        height: 8px;
        background: #10b981;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 8px #10b981;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Estilo das Abas (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 8px 8px 0 0;
        color: #1e293b !important;
        font-weight: 600;
        padding: 12px 24px;
        border: 1px solid #e2e8f0;
        border-bottom: none;
    }
    
    .stTabs [data-baseweb="tab"] span,
    .stTabs [data-baseweb="tab"] p,
    .stTabs [data-baseweb="tab"] div {
        color: #1e293b !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #036672 0%, #059669 100%) !important;
        color: white !important;
        border-color: #036672;
    }
    
    .stTabs [aria-selected="true"] span,
    .stTabs [aria-selected="true"] p,
    .stTabs [aria-selected="true"] div,
    .stTabs button[aria-selected="true"] span,
    .stTabs button[aria-selected="true"] p,
    .stTabs button[aria-selected="true"] div {
        color: white !important;
    }
    
    .stTabs [data-baseweb="tab-panel"] {
        background-color: white;
        border-radius: 0 12px 12px 12px;
        padding: 24px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Conteúdo dentro das abas */
    .stTabs [data-baseweb="tab-panel"] * {
        color: #1e293b !important;
    }
    
    /* Exceção PRIORITÁRIA: header da análise clínica deve ser branco */
    .stTabs [data-baseweb="tab-panel"] .analise-header,
    .stTabs [data-baseweb="tab-panel"] .analise-header *,
    .stTabs [data-baseweb="tab-panel"] .analise-header h2,
    .stTabs [data-baseweb="tab-panel"] .analise-header p {
        color: #ffffff !important;
    }
    
    .stTabs [data-baseweb="tab-panel"] h1,
    .stTabs [data-baseweb="tab-panel"] h2,
    .stTabs [data-baseweb="tab-panel"] h3,
    .stTabs [data-baseweb="tab-panel"] h4,
    .stTabs [data-baseweb="tab-panel"] h5,
    .stTabs [data-baseweb="tab-panel"] h6 {
        color: #0f172a !important;
    }
    
    /* Exceção: header da análise clínica deve ser branco */
    .analise-header h2,
    .analise-header p {
        color: #ffffff !important;
    }
    
    .stTabs [data-baseweb="tab-panel"] p,
    .stTabs [data-baseweb="tab-panel"] span,
    .stTabs [data-baseweb="tab-panel"] div,
    .stTabs [data-baseweb="tab-panel"] label {
        color: #334155 !important;
    }
    
    .stTabs [data-baseweb="tab-panel"] .stMarkdown {
        color: #1e293b !important;
    }
    
    /* Selectbox - Fundo claro e texto escuro */
    div[data-baseweb="select"] > div {
        background-color: white !important;
        color: #1e293b !important;
    }
    
    div[data-baseweb="select"] input {
        color: #1e293b !important;
    }
    
    div[data-baseweb="select"] span {
        color: #1e293b !important;
    }
    
    /* Dropdown do selectbox */
    ul[role="listbox"] {
        background-color: white !important;
    }
    
    ul[role="listbox"] li {
        color: #1e293b !important;
        background-color: white !important;
    }
    
    ul[role="listbox"] li:hover {
        background-color: #f1f5f9 !important;
        color: #0f172a !important;
    }
    
    /* Expanders - Correção de fundo escuro */
    .stExpander {
        background-color: white !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        margin-bottom: 10px !important;
    }
    
    .stExpander [data-testid="stExpanderDetails"] {
        background-color: white !important;
        color: #1e293b !important;
    }
    
    .stExpander summary {
        background-color: white !important;
        color: #1e293b !important;
    }
    
    .stExpander summary:hover {
        background-color: #f8fafc !important;
    }
    
    .stExpander [data-testid="stExpanderDetails"] p,
    .stExpander [data-testid="stExpanderDetails"] span,
    .stExpander [data-testid="stExpanderDetails"] div {
        color: #334155 !important;
    }
    
    /* Forçar texto preto em TODOS os gráficos Plotly */
    .js-plotly-plot .plotly text,
    .js-plotly-plot .plotly .gtitle,
    .js-plotly-plot .plotly .xtick text,
    .js-plotly-plot .plotly .ytick text,
    .js-plotly-plot .plotly .legendtext,
    .js-plotly-plot .plotly .annotation-text,
    .js-plotly-plot .plotly .legend text,
    .js-plotly-plot .plotly .g-xtitle text,
    .js-plotly-plot .plotly .g-ytitle text {
        fill: #000000 !important;
        color: #000000 !important;
    }
    
    /* Títulos de legenda */
    .js-plotly-plot .legend-title text {
        fill: #000000 !important;
    }
    
    /* FORÇAR TODOS os elementos de texto SVG no Plotly */
    .js-plotly-plot svg text {
        fill: #000000 !important;
        color: #000000 !important;
        stroke: none !important;
    }
    
    /* Labels e traces */
    .js-plotly-plot .trace text {
        fill: #000000 !important;
    }
    
    /* Garantir que percentuais e valores nos gráficos sejam pretos */
    .js-plotly-plot .slice text,
    .js-plotly-plot .surface text,
    .js-plotly-plot .textpoint text {
        fill: #000000 !important;
        font-weight: 600 !important;
    }
    
    /* Hover/Tooltip dos gráficos Plotly - Fundo branco com texto preto */
    .js-plotly-plot .hoverlayer .hovertext {
        fill: #ffffff !important;
        stroke: #e5e7eb !important;
    }
    
    .js-plotly-plot .hoverlayer .hovertext path {
        fill: #ffffff !important;
        stroke: #d1d5db !important;
    }
    
    .js-plotly-plot .hoverlayer .hovertext text {
        fill: #000000 !important;
        color: #000000 !important;
    }
    
    /* Hover box background */
    g.hovertext path {
        fill: #ffffff !important;
        stroke: #cbd5e1 !important;
        stroke-width: 1px !important;
    }
    
    /* Hover text */
    g.hovertext text {
        fill: #000000 !important;
    }
    
    /* Legendas - garantir que sempre sejam visíveis */
    .js-plotly-plot .legend {
        background: white !important;
    }
    
    .js-plotly-plot .legend .bg {
        fill: white !important;
        fill-opacity: 0.9 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================== TELA INICIAL ====================
def show_welcome_screen():
    """Tela de boas-vindas com seleção de perfil"""
    st.markdown("""
        <div class='welcome-header'>
            <div class='welcome-icon'>🏥</div>
            <h1>Bem-vindo ao Avicena Care</h1>
            <p>Sistema Integrado de Triagem Médica</p>
        </div>
    """, unsafe_allow_html=True)

    # Layout: Informações à esquerda, botões à direita
    col_info, col_acesso = st.columns([1.2, 1])
    
    with col_info:
        st.markdown("""
            <div class='info-card'>
                <h3 style='color: #036672; margin-bottom: 20px;'>
                    📋 Protocolo PCACR
                </h3>
                <p style='color: #475569; line-height: 1.8; font-size: 0.95rem;'>
                    Sistema de triagem médica baseado no <strong>Protocolo Catarinense de 
                    Acolhimento com Classificação de Risco (PCACR)</strong>, que permite 
                    a priorização de pacientes conforme urgência clínica.
                </p>
                <hr style='border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;'>
                <p style='color: #64748b; font-size: 0.9rem; margin-bottom: 10px;'>
                    <strong>Principais recursos:</strong>
                </p>
                <ul style='color: #64748b; font-size: 0.9rem; line-height: 1.6; margin-left: 20px;'>
                    <li>Classificação automática por sinais vitais</li>
                    <li>Gestão em tempo real da fila de atendimento</li>
                    <li>Dashboard com indicadores de urgência</li>
                    <li>Relatórios e análises clínicas</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    with col_acesso:
        st.markdown("""
            <div class='info-card' style='height: 100%;'>
                <h3 style='text-align: center; color: #036672; margin-bottom: 25px;'>
                    🔐 Acesso ao Sistema
                </h3>
                <p style='text-align: center; color: #64748b; margin-bottom: 30px; font-size: 0.9rem;'>
                    Selecione seu perfil profissional para acessar:
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='margin-top: -15px;'></div>", unsafe_allow_html=True)
        
        if st.button("👩‍⚕️ Sou Enfermeiro(a)", key="btn_enfermeiro", type="primary", use_container_width=True):
            st.session_state['tipo_acesso'] = 'enfermeiro'
            st.rerun()
        
        st.markdown("<div style='margin: 10px 0;'></div>", unsafe_allow_html=True)
        
        if st.button("👨‍⚕️ Sou Médico(a)", key="btn_medico", type="primary", use_container_width=True):
            st.session_state['tipo_acesso'] = 'medico'
            st.rerun()
        
        st.markdown("""
            <div style='text-align: center; margin-top: 30px;'>
                <p style='color: #94a3b8; font-size: 0.85rem;'>
                    Acesso restrito a profissionais<br>de saúde autorizados
                </p>
            </div>
        """, unsafe_allow_html=True)

# ==================== INTERFACES ESPECÍFICAS ====================
def mostrar_interface_enfermeiro_completa():
    """Interface completa para enfermeiros: Dashboard, Lista e Novo Paciente"""
    
    # Carregar dados
    df = get_data()
    
    # CSS para link de logout
    st.markdown("""
    <style>
    .logout-link {
        color: #ffffff !important;
        text-decoration: none !important;
        font-size: 0.85rem;
        font-weight: 400;
        transition: opacity 0.2s;
        cursor: pointer;
        margin-left: 20px;
    }
    .logout-link:hover {
        opacity: 0.8;
        text-decoration: underline !important;
        color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Verificar logout via query params
    if 'logout' in st.query_params:
        st.session_state['tipo_acesso'] = None
        st.query_params.clear()
        st.rerun()
    
    # Botão de logout no sidebar (funcional)
    with st.sidebar:
        st.markdown("---")
        if st.button("🚪 Sair", key="logout_enfermeiro", use_container_width=True, type="secondary"):
            st.session_state['tipo_acesso'] = None
            st.rerun()
    
    # Header principal com link visual (redireciona via URL)
    brand_header = """
    <div class='ac-global-header'>
        <div class='ac-header-wrap'>
                <div class='ac-brand'>
                        <div class='ac-logo'>🏥</div>
                        <div class='ac-text'>
                                    <div class='ac-title'>Avicena Care - Enfermagem</div>
                                    <div class='ac-sub'>Protocolo Catarinense de Acolhimento (PCACR)</div>
                        </div>
                </div>
                <div style='display: flex; align-items: center;'>
                    <div class='ac-status-pill'><span></span> PCACR Ativo</div>
                    <a href='?logout=true' class='logout-link' target='_self'>🚪 Sair</a>
                </div>
        </div>
    </div>
    """
    st.markdown(brand_header, unsafe_allow_html=True)
    
    # Dashboard com contadores de prioridade
    total_pacientes = len(df)
    urgencia_maxima = len(df[df["urgencia_manual"] == "PRIORIDADE MÁXIMA"]) if "urgencia_manual" in df.columns else 0
    urgencia_alta = len(df[df["urgencia_manual"] == "ALTA PRIORIDADE"]) if "urgencia_manual" in df.columns else 0
    urgencia_media = len(df[df["urgencia_manual"] == "MÉDIA PRIORIDADE"]) if "urgencia_manual" in df.columns else 0
    urgencia_baixa = len(df[df["urgencia_manual"] == "BAIXA PRIORIDADE"]) if "urgencia_manual" in df.columns else 0
    urgencia_minima = len(df[df["urgencia_manual"] == "MÍNIMA (ELETIVA)"]) if "urgencia_manual" in df.columns else 0
    
    protocol_html = f"""
    <div class='pcacr-wrapper'>
      <div class='pcacr-box-minimal'>
         <div class='pcacr-header-row'>
            <div class='pcacr-title-section'>
               <h2>📋 Protocolo PCACR Ativo</h2>
               <p>Classificação de risco por cores e tempos alvo</p>
            </div>
            <div class='pcacr-legend-inline'>
               <div class='pcacr-pillx'><span class='pcacr-dot-modern d-max'></span>Máxima (0min)</div>
               <div class='pcacr-pillx'><span class='pcacr-dot-modern d-alta'></span>Alta (15min)</div>
               <div class='pcacr-pillx'><span class='pcacr-dot-modern d-media'></span>Média (60min)</div>
               <div class='pcacr-pillx'><span class='pcacr-dot-modern d-baixa'></span>Baixa (120min)</div>
               <div class='pcacr-pillx'><span class='pcacr-dot-modern d-min'></span>Mínima (240min)</div>
            </div>
         </div>
         <div class='kpi-band-minimal'>
            <div class='kpi-box-minimal total'>
                <div class='kpi-icon-minimal'>📊</div>
                <div class='kpi-value-minimal'>{total_pacientes}</div>
                <div class='kpi-label-minimal'>TOTAL DE PACIENTES</div>
                <div class='kpi-meta-minimal'>Atual</div>
            </div>
            <div class='kpi-box-minimal max'>
                <div class='kpi-circle-modern d-max'></div>
                <div class='kpi-value-minimal'>{urgencia_maxima}</div>
                <div class='kpi-label-minimal'>PRIORIDADE MÁXIMA</div>
                <div class='kpi-meta-minimal'>0 minutos</div>
            </div>
            <div class='kpi-box-minimal alta'>
                <div class='kpi-circle-modern d-alta'></div>
                <div class='kpi-value-minimal'>{urgencia_alta}</div>
                <div class='kpi-label-minimal'>PRIORIDADE ALTA</div>
                <div class='kpi-meta-minimal'>15 minutos</div>
            </div>
            <div class='kpi-box-minimal media'>
                <div class='kpi-circle-modern d-media'></div>
                <div class='kpi-value-minimal'>{urgencia_media}</div>
                <div class='kpi-label-minimal'>PRIORIDADE MÉDIA</div>
                <div class='kpi-meta-minimal'>60 minutos</div>
            </div>
            <div class='kpi-box-minimal baixa'>
                <div class='kpi-circle-modern d-baixa'></div>
                <div class='kpi-value-minimal'>{urgencia_baixa}</div>
                <div class='kpi-label-minimal'>PRIORIDADE BAIXA</div>
                <div class='kpi-meta-minimal'>120 minutos</div>
            </div>
            <div class='kpi-box-minimal min'>
                <div class='kpi-circle-modern d-min'></div>
                <div class='kpi-value-minimal'>{urgencia_minima}</div>
                <div class='kpi-label-minimal'>PRIORIDADE MÍNIMA</div>
                <div class='kpi-meta-minimal'>240 minutos</div>
            </div>
         </div>
      </div>
    </div>
    """
    
    st.markdown(protocol_html, unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    
    # Tabs: Lista de Pacientes e Novo Paciente
    tab_lista, tab_novo = st.tabs(["🧾 Fila de Atendimento", "➕ Novo Paciente"])
    
    with tab_lista:
        mostrar_fila_pacientes(df)
    
    with tab_novo:
        mostrar_form_novo_paciente()

def mostrar_interface_medico_completa():
    """Interface completa para médicos: Dashboard, Lista, Análise Clínica, Relatórios e Novo Paciente"""
    
    # Carregar dados
    df = get_data()
    
    # CSS para link de logout
    st.markdown("""
    <style>
    .logout-link {
        color: #ffffff !important;
        text-decoration: none !important;
        font-size: 0.85rem;
        font-weight: 400;
        transition: opacity 0.2s;
        cursor: pointer;
        margin-left: 20px;
    }
    .logout-link:hover {
        opacity: 0.8;
        text-decoration: underline !important;
        color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Verificar logout via query params
    if 'logout' in st.query_params:
        st.session_state['tipo_acesso'] = None
        st.query_params.clear()
        st.rerun()
    
    # Botão de logout no sidebar (funcional)
    with st.sidebar:
        st.markdown("---")
        if st.button("🚪 Sair", key="logout_medico", use_container_width=True, type="secondary"):
            st.session_state['tipo_acesso'] = None
            st.rerun()
    
    # Header principal - médico tem acesso completo
    brand_header = """
    <div class='ac-global-header'>
        <div class='ac-header-wrap'>
                <div class='ac-brand'>
                        <div class='ac-logo'>🏥</div>
                        <div class='ac-text'>
                                    <div class='ac-title'>Avicena Care - Acesso Médico</div>
                                    <div class='ac-sub'>Protocolo Catarinense de Acolhimento (PCACR)</div>
                        </div>
                </div>
                <div style='display: flex; align-items: center;'>
                    <div class='ac-status-pill'><span></span> PCACR Ativo</div>
                    <a href='?logout=true' class='logout-link' target='_self'>🚪 Sair</a>
                </div>
        </div>
    </div>
    """
    st.markdown(brand_header, unsafe_allow_html=True)
    
    # Dashboard (mesmo da enfermagem)
    total_pacientes = len(df)
    urgencia_maxima = len(df[df["urgencia_manual"] == "PRIORIDADE MÁXIMA"]) if "urgencia_manual" in df.columns else 0
    urgencia_alta = len(df[df["urgencia_manual"] == "ALTA PRIORIDADE"]) if "urgencia_manual" in df.columns else 0
    urgencia_media = len(df[df["urgencia_manual"] == "MÉDIA PRIORIDADE"]) if "urgencia_manual" in df.columns else 0
    urgencia_baixa = len(df[df["urgencia_manual"] == "BAIXA PRIORIDADE"]) if "urgencia_manual" in df.columns else 0
    urgencia_minima = len(df[df["urgencia_manual"] == "MÍNIMA (ELETIVA)"]) if "urgencia_manual" in df.columns else 0
    
    protocol_html = f"""
    <div class='pcacr-wrapper'>
      <div class='pcacr-box-minimal'>
         <div class='pcacr-header-row'>
            <div class='pcacr-title-section'>
               <h2>📋 Protocolo PCACR Ativo</h2>
               <p>Classificação de risco por cores e tempos alvo</p>
            </div>
            <div class='pcacr-legend-inline'>
               <div class='pcacr-pillx'><span class='pcacr-dot-modern d-max'></span>Máxima (0min)</div>
               <div class='pcacr-pillx'><span class='pcacr-dot-modern d-alta'></span>Alta (15min)</div>
               <div class='pcacr-pillx'><span class='pcacr-dot-modern d-media'></span>Média (60min)</div>
               <div class='pcacr-pillx'><span class='pcacr-dot-modern d-baixa'></span>Baixa (120min)</div>
               <div class='pcacr-pillx'><span class='pcacr-dot-modern d-min'></span>Mínima (240min)</div>
            </div>
         </div>
         <div class='kpi-band-minimal'>
            <div class='kpi-box-minimal total'>
                <div class='kpi-icon-minimal'>📊</div>
                <div class='kpi-value-minimal'>{total_pacientes}</div>
                <div class='kpi-label-minimal'>TOTAL DE PACIENTES</div>
                <div class='kpi-meta-minimal'>Atual</div>
            </div>
            <div class='kpi-box-minimal max'>
                <div class='kpi-circle-modern d-max'></div>
                <div class='kpi-value-minimal'>{urgencia_maxima}</div>
                <div class='kpi-label-minimal'>PRIORIDADE MÁXIMA</div>
                <div class='kpi-meta-minimal'>0 minutos</div>
            </div>
            <div class='kpi-box-minimal alta'>
                <div class='kpi-circle-modern d-alta'></div>
                <div class='kpi-value-minimal'>{urgencia_alta}</div>
                <div class='kpi-label-minimal'>PRIORIDADE ALTA</div>
                <div class='kpi-meta-minimal'>15 minutos</div>
            </div>
            <div class='kpi-box-minimal media'>
                <div class='kpi-circle-modern d-media'></div>
                <div class='kpi-value-minimal'>{urgencia_media}</div>
                <div class='kpi-label-minimal'>PRIORIDADE MÉDIA</div>
                <div class='kpi-meta-minimal'>60 minutos</div>
            </div>
            <div class='kpi-box-minimal baixa'>
                <div class='kpi-circle-modern d-baixa'></div>
                <div class='kpi-value-minimal'>{urgencia_baixa}</div>
                <div class='kpi-label-minimal'>PRIORIDADE BAIXA</div>
                <div class='kpi-meta-minimal'>120 minutos</div>
            </div>
            <div class='kpi-box-minimal min'>
                <div class='kpi-circle-modern d-min'></div>
                <div class='kpi-value-minimal'>{urgencia_minima}</div>
                <div class='kpi-label-minimal'>PRIORIDADE MÍNIMA</div>
                <div class='kpi-meta-minimal'>240 minutos</div>
            </div>
         </div>
      </div>
    </div>
    """
    
    st.markdown(protocol_html, unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    
    # Tabs: Lista, Análise Clínica, Análise Preditiva e Relatórios (médico não tem acesso a Novo Paciente)
    if ML_AVAILABLE:
        tab_lista, tab_analise, tab_ml, tab_relatorios = st.tabs([
            "🧾 Fila de Atendimento", 
            "📊 Análise Clínica",
            "🤖 Análise Preditiva",
            "📋 Relatórios"
        ])
    else:
        tab_lista, tab_analise, tab_relatorios = st.tabs([
            "🧾 Fila de Atendimento", 
            "📊 Análise Clínica",
            "📋 Relatórios"
        ])
    
    with tab_lista:
        mostrar_fila_pacientes(df)
    
    with tab_analise:
        mostrar_analise_clinica(df)
    
    if ML_AVAILABLE:
        with tab_ml:
            st.markdown("### 🤖 Análise Preditiva Baseada em ML")
            
            if df.empty:
                st.info("📋 Nenhum paciente na fila para análise.")
            else:
                # Seletor de paciente
                paciente_options = [f"{row['Nome']} - {row['urgencia_manual']}" for _, row in df.iterrows()]
                selected = st.selectbox("Selecione um paciente para análise:", paciente_options)
                
                if selected:
                    idx = paciente_options.index(selected)
                    paciente = df.iloc[idx]
                    
                    # Extrair sinais vitais
                    pa_parts = paciente['PA'].split('/')
                    pa_sistolica = int(pa_parts[0]) if len(pa_parts) > 0 else 120
                    pa_diastolica = int(pa_parts[1]) if len(pa_parts) > 1 else 80
                    
                    patient_data = {
                        'freq_cardiaca': int(paciente['FC']),
                        'spo2': 95,  # Valor padrão se não disponível
                        'temperatura': float(paciente['Temp']),
                        'pa_sistolica': pa_sistolica,
                        'pa_diastolica': pa_diastolica,
                        'freq_respiratoria': int(paciente['FR']),
                        'idade': int(paciente['Idade'])
                    }
                    
                    try:
                        # Fazer predição
                        resultado = predictor.predict_pcacr(patient_data)
                        
                        # Card do paciente
                        st.markdown(f"#### 👤 {paciente['Nome']} ({paciente['Idade']} anos)")
                        st.markdown(f"**Queixa:** {paciente['Queixa_Principal']}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**📋 Classificação Atual:**")
                            st.markdown(f"### {paciente['urgencia_manual']}")
                        with col2:
                            confidence = resultado['confidence'] * 100
                            st.markdown("**🤖 Predição ML:**")
                            st.markdown(f"### {resultado['prediction']}")
                            st.markdown(f"*Confiança: {confidence:.1f}%*")
                        
                        st.markdown("---")
                        
                        # Probabilidades
                        st.markdown("### 📊 Distribuição de Probabilidades")
                        prob_cols = st.columns(5)
                        classes_ordem = ['PRIORIDADE MÁXIMA', 'ALTA PRIORIDADE', 'MÉDIA PRIORIDADE', 'BAIXA PRIORIDADE', 'MÍNIMA (ELETIVA)']
                        cores = ['🔴', '🟠', '🟡', '🟢', '🔵']
                        
                        for idx, (classe, cor) in enumerate(zip(classes_ordem, cores)):
                            prob = resultado['probabilities'].get(classe, 0) * 100
                            with prob_cols[idx]:
                                st.metric(
                                    f"{cor} {classe.split()[0]}", 
                                    f"{prob:.1f}%",
                                    delta=None
                                )
                        
                        st.markdown("---")
                        
                        # Interpretação Clínica
                        st.markdown("### 🩺 Interpretação Clínica")
                        explicacao = predictor.explain_prediction(patient_data)
                        
                        col_sinais, col_interpretacao = st.columns([1, 1])
                        
                        with col_sinais:
                            st.markdown("**Sinais Vitais:**")
                            for linha in explicacao.split('\n'):
                                if linha.strip():
                                    st.markdown(linha)
                        
                        with col_interpretacao:
                            st.markdown("**💡 Recomendações:**")
                            if resultado['confidence'] > 0.7:
                                st.success("✅ Modelo tem alta confiança na predição")
                            elif resultado['confidence'] > 0.5:
                                st.warning("⚠️ Confiança moderada - revisar sinais vitais")
                            else:
                                st.error("⚠️ Baixa confiança - avaliar clinicamente")
                            
                            # Alerta de sepse
                            if resultado['prediction'] in ['PRIORIDADE MÁXIMA', 'ALTA PRIORIDADE']:
                                st.error("🚨 **ALERTA:** Risco elevado - considerar sepse")
                        
                        st.markdown("---")
                        
                        # Feature Importance
                        st.markdown("### 📈 Importância dos Fatores Clínicos")
                        feature_importance = predictor.get_feature_importance()
                        
                        # Ordenar por importância
                        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:10]
                        
                        import pandas as pd
                        df_importance = pd.DataFrame(sorted_features, columns=['Fator', 'Importância'])
                        
                        # Traduzir nomes
                        traducao = {
                            'HR': 'Freq. Cardíaca',
                            'Temp': 'Temperatura',
                            'SBP': 'PA Sistólica',
                            'DBP': 'PA Diastólica',
                            'Resp': 'Freq. Respiratória',
                            'O2Sat': 'Saturação O2',
                            'Age': 'Idade',
                            'MAP': 'PAM',
                            'Glucose': 'Glicose',
                            'Lactate': 'Lactato'
                        }
                        df_importance['Fator'] = df_importance['Fator'].map(lambda x: traducao.get(x, x))
                        
                        st.bar_chart(df_importance.set_index('Fator'))
                        
                    except Exception as e:
                        st.error(f"❌ Erro na análise preditiva: {str(e)}")
    
    with tab_relatorios:
        mostrar_relatorios(df)

# Inicializar estado da sessão para controle da tela
if 'tipo_acesso' not in st.session_state:
    st.session_state['tipo_acesso'] = None
    
# ==================== FLUXO PRINCIPAL DA APLICAÇÃO ====================
if st.session_state['tipo_acesso'] is None:
    show_welcome_screen()
else:
    # Cabeçalho do sistema
    tipo_profissional = "Médico(a)" if st.session_state['tipo_acesso'] == 'medico' else "Enfermeiro(a)"
    emoji_profissional = "👨‍⚕️" if st.session_state['tipo_acesso'] == 'medico' else "👩‍⚕️"
    
    # Sidebar com opção de trocar acesso
    with st.sidebar:
        st.markdown(f"""
        <div style='background-color: #f8fafc; padding: 15px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #e2e8f0;'>
            <h3 style='margin: 0; color: #036672;'>{emoji_profissional} Acesso {tipo_profissional}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        if st.button("🔄 Trocar Tipo de Acesso", key="btn_trocar_acesso", type="secondary", use_container_width=True):
            st.session_state['tipo_acesso'] = None
            st.rerun()
    
    # Interface baseada no tipo de acesso
    if st.session_state['tipo_acesso'] == 'enfermeiro':
        mostrar_interface_enfermeiro_completa()
    else:  # medico
        mostrar_interface_medico_completa()
