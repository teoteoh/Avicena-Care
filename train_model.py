"""
Script para treinar modelo de Machine Learning para predição de classificação PCACR
Baseado em sinais vitais e características do paciente
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os
from databricks import sql

# Mapeamento de sepse para classificação PCACR
# SepsisLabel: 0 (sem sepse) -> prioridades mais baixas
# SepsisLabel: 1 (com sepse) -> prioridades mais altas
def map_to_pcacr(row):
    """
    Mapeia dados clínicos para classificação PCACR
    Baseado em critérios NEWS2 e MEWS
    """
    # Features críticas
    hr = row.get('HR', 75)
    temp = row.get('Temp', 36.5)
    sbp = row.get('SBP', 120)
    resp = row.get('Resp', 16)
    o2sat = row.get('O2Sat', 98)
    age = row.get('Age', 50)
    sepsis = row.get('SepsisLabel', 0)
    
    score = 0
    
    # Sistema de pontuação baseado em NEWS2
    # Frequência Cardíaca
    if pd.notna(hr):
        if hr <= 40 or hr >= 131:
            score += 3
        elif hr <= 50 or hr >= 111:
            score += 2
        elif hr >= 91:
            score += 1
    
    # Temperatura
    if pd.notna(temp):
        if temp <= 35.0 or temp >= 39.1:
            score += 3
        elif temp >= 38.1:
            score += 1
    
    # Pressão Arterial Sistólica
    if pd.notna(sbp):
        if sbp <= 90:
            score += 3
        elif sbp <= 100:
            score += 2
        elif sbp <= 110:
            score += 1
        elif sbp >= 220:
            score += 3
    
    # Frequência Respiratória
    if pd.notna(resp):
        if resp <= 8 or resp >= 25:
            score += 3
        elif resp <= 11 or resp >= 21:
            score += 2
        elif resp >= 21:
            score += 1
    
    # Saturação de O2
    if pd.notna(o2sat):
        if o2sat <= 91:
            score += 3
        elif o2sat <= 93:
            score += 2
        elif o2sat <= 95:
            score += 1
    
    # Idade (fator de risco)
    if pd.notna(age):
        if age >= 65:
            score += 1
        if age >= 75:
            score += 1
    
    # Sepse é um fator crítico
    if sepsis == 1:
        score += 5
    
    # Classificação PCACR baseada no score
    if score >= 10:
        return 'PRIORIDADE MÁXIMA'
    elif score >= 7:
        return 'ALTA PRIORIDADE'
    elif score >= 5:
        return 'MÉDIA PRIORIDADE'
    elif score >= 3:
        return 'BAIXA PRIORIDADE'
    else:
        return 'MÍNIMA (ELETIVA)'

def prepare_features(df):
    """
    Prepara features para o modelo.
    APENAS SINAIS VITAIS coletados no formulário de triagem!
    """
    # Selecionar APENAS colunas disponíveis no formulário
    feature_cols = [
        'HR',      # Frequência Cardíaca
        'O2Sat',   # SpO2 (%)
        'Temp',    # Temperatura (°C)
        'SBP',     # PA Sistólica
        'DBP',     # PA Diastólica
        'MAP',     # PAM (calculado)
        'Resp',    # Frequência Respiratória
        'Age',     # Idade
        'Gender'   # Gênero (0=Feminino, 1=Masculino)
    ]
    
    # Criar dataframe de features
    X = df[feature_cols].copy()
    
    return X, feature_cols

def train_pcacr_model():
    """Treina o modelo de classificação PCACR"""
    print("🏥 Iniciando treinamento do modelo PCACR...")
    
    # Carregar dataset
    print("📊 Carregando dados de treinamento do Databricks...")
    
    # Inicializar conexão com Databricks SQL Warehouse
    with sql.connect(
        server_hostname=st.secrets["databricks"]["server_hostname"],
        http_path=st.secrets["databricks"]["http_path"],
        access_token=st.secrets["databricks"]["access_token"],
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM avicena_care.triagem")
            df = cursor.fetchall_pandas()
    
    print(f"   Dataset carregado: {len(df)} registros")
    
    # Criar classificação PCACR baseada nos dados clínicos

    print("🎯 Criando classificações PCACR...")
    df['PCACR_Class'] = df.apply(map_to_pcacr, axis=1)
    
    # Verificar distribuição de classes
    print("\n📈 Distribuição de classes:")
    print(df['PCACR_Class'].value_counts())
    
    # Preparar features
    print("\n🔧 Preparando features...")

    X, feature_cols = prepare_features(df)
    y = df['PCACR_Class']
    
    # Split treino/teste
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Normalizar features
    print("⚖️  Normalizando features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Treinar Random Forest (parâmetros otimizados para velocidade)
    print("\n🌲 Treinando Random Forest...")
    model = RandomForestClassifier(
        n_estimators=100,      # Número de árvores na floresta.
        max_depth=10,          # Profundidade máxima de cada árvore. Limita a complexidade.
        min_samples_split=20,  # Mínimo de amostras para dividir um nó. Evita overfitting.
        min_samples_leaf=10,   # Mínimo de amostras em um nó folha. Suaviza o modelo.
        random_state=42,
        n_jobs=-1,             # Usar todos os processadores disponíveis.
        class_weight='balanced', # Ajusta os pesos das classes para lidar com desbalanceamento.
        verbose=1  # Mostrar progresso
    )
    
    model.fit(X_train_scaled, y_train)
    
    # Avaliar modelo
    train_score = model.score(X_train_scaled, y_train)
    test_score = model.score(X_test_scaled, y_test)
    
    print(f"\n✅ Modelo treinado!")
    print(f"   Acurácia Treino: {train_score:.2%}")
    print(f"   Acurácia Teste: {test_score:.2%}")
    
    # Feature importance
    print("\n🎯 Features mais importantes:")
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    for idx, row in feature_importance.head(10).iterrows():
        print(f"   {row['feature']}: {row['importance']:.4f}")
    
    # Salvar modelo e scaler
    print("\n💾 Salvando modelo e scaler...")
    os.makedirs('models', exist_ok=True)
    joblib.dump(model, 'models/pcacr_model.pkl')
    joblib.dump(scaler, 'models/pcacr_scaler.pkl')
    joblib.dump(feature_cols, 'models/pcacr_features.pkl')
    
    print("\n✨ Treinamento concluído com sucesso!")
    print("   Arquivos salvos em: models/")
    print("   - pcacr_model.pkl")
    print("   - pcacr_scaler.pkl")
    print("   - pcacr_features.pkl")
    
    return model, scaler, feature_cols, feature_importance

if __name__ == "__main__":
    try:
        model, scaler, features, importance = train_pcacr_model()
    except Exception as e:
        print(f"\n❌ Erro durante treinamento: {str(e)}")
        import traceback
        traceback.print_exc()
