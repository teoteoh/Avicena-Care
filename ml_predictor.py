"""
Módulo de predição ML para classificação PCACR
Carrega modelo treinado e faz predições em tempo real
"""

import joblib
import numpy as np
import pandas as pd
import os

class PCACRPredictor:
    """Classe para predições de classificação PCACR usando ML"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.features = None
        self.model_loaded = False
        
    def load_model(self):
        """Carrega modelo treinado"""
        try:
            if not os.path.exists('models/pcacr_model.pkl'):
                print("⚠️ Modelo não encontrado. Execute train_model.py primeiro.")
                return False
            
            self.model = joblib.load('models/pcacr_model.pkl')
            self.scaler = joblib.load('models/pcacr_scaler.pkl')
            self.features = joblib.load('models/pcacr_features.pkl')
            self.model_loaded = True
            return True
        except Exception as e:
            print(f"❌ Erro ao carregar modelo: {str(e)}")
            return False
    
    def predict_pcacr(self, patient_data):
        """
        Prediz classificação PCACR para um paciente
        
        Args:
            patient_data (dict): Dados do paciente com sinais vitais
            
        Returns:
            dict: {
                'prediction': str (classificação PCACR),
                'probabilities': dict (probabilidade de cada classe),
                'confidence': float (confiança da predição)
            }
        """
        if not self.model_loaded:
            if not self.load_model():
                return None
        
        # Mapear dados do paciente para features do modelo
        # APENAS SINAIS VITAIS coletados no formulário!
        feature_vector = []
        
        # Converter gênero para binário (0=Feminino, 1=Masculino)
        genero_str = patient_data.get('genero', 'Masculino')
        genero_bin = 1 if genero_str == 'Masculino' else 0
        
        patient_features = {
            'HR': patient_data.get('freq_cardiaca', 75),
            'O2Sat': patient_data.get('spo2', 98),
            'Temp': patient_data.get('temperatura', 36.5),
            'SBP': patient_data.get('pa_sistolica', 120),
            'DBP': patient_data.get('pa_diastolica', 80),
            'MAP': patient_data.get('pa_media', (patient_data.get('pa_sistolica', 120) + 2*patient_data.get('pa_diastolica', 80))/3),
            'Resp': patient_data.get('freq_respiratoria', 16),
            'Age': patient_data.get('idade', 50),
            'Gender': genero_bin
        }
        
        # Construir vetor de features na ordem correta
        for feature in self.features:
            feature_vector.append(patient_features.get(feature, 0))
        
        # Converter para array numpy
        X = np.array(feature_vector).reshape(1, -1)
        
        # Normalizar
        X_scaled = self.scaler.transform(X)
        
        # Fazer predição
        prediction = self.model.predict(X_scaled)[0]
        probabilities = self.model.predict_proba(X_scaled)[0]
        
        # Mapear probabilidades para classes
        classes = self.model.classes_
        prob_dict = {classe: float(prob) for classe, prob in zip(classes, probabilities)}
        
        # Calcular confiança (máxima probabilidade)
        confidence = float(max(probabilities))
        
        return {
            'prediction': prediction,
            'probabilities': prob_dict,
            'confidence': confidence
        }
    
    def get_feature_importance(self, patient_data):
        """
        Retorna importância das features para a predição deste paciente
        
        Args:
            patient_data (dict): Dados do paciente
            
        Returns:
            dict: Features e suas importâncias
        """
        if not self.model_loaded:
            if not self.load_model():
                return None
        
        feature_importance = {}
        for feature, importance in zip(self.features, self.model.feature_importances_):
            feature_importance[feature] = float(importance)
        
        return feature_importance
    
    def explain_prediction(self, patient_data):
        """
        Explica a predição mostrando status clínico dos sinais vitais.
        APENAS SINAIS VITAIS coletados no formulário!
        
        Args:
            patient_data (dict): Dados do paciente
            
        Returns:
            str: Texto formatado com interpretação clínica
        """
        if not self.model_loaded:
            if not self.load_model():
                return "Modelo não disponível"
        
        # Mapear dados (APENAS sinais vitais do form)
        hr = patient_data.get('freq_cardiaca', 75)
        temp = patient_data.get('temperatura', 36.5)
        sbp = patient_data.get('pa_sistolica', 120)
        dbp = patient_data.get('pa_diastolica', 80)
        resp = patient_data.get('freq_respiratoria', 16)
        o2 = patient_data.get('spo2', 98)
        idade = patient_data.get('idade', 50)
        
        # Avaliar cada sinal vital
        interpretacao = []
        
        # Frequência Cardíaca (adultos em repouso)
        if hr < 40:
            interpretacao.append(f"- **FC:** {hr} bpm 🔴 Bradicardia grave")
        elif hr < 60:
            interpretacao.append(f"- **FC:** {hr} bpm ⚠️ Bradicardia leve")
        elif hr > 120:
            interpretacao.append(f"- **FC:** {hr} bpm 🔴 Taquicardia grave")
        elif hr > 100:
            interpretacao.append(f"- **FC:** {hr} bpm ⚠️ Taquicardia")
        else:
            interpretacao.append(f"- **FC:** {hr} bpm ✅ Normal")
        
        # Temperatura (axilar/oral)
        if temp < 35:
            interpretacao.append(f"- **Temp:** {temp}°C 🔴 Hipotermia severa")
        elif temp < 36:
            interpretacao.append(f"- **Temp:** {temp}°C ⚠️ Hipotermia leve")
        elif temp > 39:
            interpretacao.append(f"- **Temp:** {temp}°C 🔴 Febre alta")
        elif temp >= 38:
            interpretacao.append(f"- **Temp:** {temp}°C ⚠️ Febre")
        elif temp >= 37.5:
            interpretacao.append(f"- **Temp:** {temp}°C ⚠️ Febrícula")
        else:
            interpretacao.append(f"- **Temp:** {temp}°C ✅ Normal")
        
        # Pressão Arterial (classificação AHA/ACC 2017 - prevalece o maior valor)
        if sbp < 90 or dbp < 60:
            interpretacao.append(f"- **PA:** {sbp}/{dbp} mmHg 🔴 Hipotensão")
        elif sbp >= 180 or dbp >= 120:
            interpretacao.append(f"- **PA:** {sbp}/{dbp} mmHg 🔴 Crise Hipertensiva")
        elif sbp >= 140 or dbp >= 90:
            interpretacao.append(f"- **PA:** {sbp}/{dbp} mmHg ⚠️ Hipertensão Estágio 2 (≥140/90)")
        elif sbp >= 130 or dbp > 80:  # DBP > 80 (não igual)
            interpretacao.append(f"- **PA:** {sbp}/{dbp} mmHg ⚠️ Hipertensão Estágio 1 (130-139/81-89)")
        elif sbp >= 120 and dbp < 80:
            interpretacao.append(f"- **PA:** {sbp}/{dbp} mmHg ⚠️ Elevada (120-129/<80)")
        elif sbp == 120 and dbp == 80:
            interpretacao.append(f"- **PA:** {sbp}/{dbp} mmHg ✅ Normal (limite superior)")
        else:
            interpretacao.append(f"- **PA:** {sbp}/{dbp} mmHg ✅ Normal (<120/80)")
        
        # Frequência Respiratória (adultos)
        if resp < 10:
            interpretacao.append(f"- **FR:** {resp} irpm 🔴 Bradipneia grave")
        elif resp < 12:
            interpretacao.append(f"- **FR:** {resp} irpm ⚠️ Bradipneia")
        elif resp >= 30:
            interpretacao.append(f"- **FR:** {resp} irpm 🔴 Taquipneia grave")
        elif resp > 20:
            interpretacao.append(f"- **FR:** {resp} irpm ⚠️ Taquipneia")
        else:
            interpretacao.append(f"- **FR:** {resp} irpm ✅ Normal")
        
        # Saturação O2
        if o2 < 88:
            interpretacao.append(f"- **SpO₂:** {o2}% 🔴 Hipoxemia severa - O2 urgente!")
        elif o2 < 92:
            interpretacao.append(f"- **SpO₂:** {o2}% ⚠️ Hipoxemia - Necessita O2")
        elif o2 < 95:
            interpretacao.append(f"- **SpO₂:** {o2}% ⚠️ Limítrofe - Monitorar")
        else:
            interpretacao.append(f"- **SpO₂:** {o2}% ✅ Normal")
        
        # Idade (fator de risco)
        if idade >= 80:
            interpretacao.append(f"- **Idade:** {idade} anos ⚠️ Idoso (risco muito elevado)")
        elif idade >= 65:
            interpretacao.append(f"- **Idade:** {idade} anos ⚠️ Idoso (fator de risco)")
        elif idade >= 60:
            interpretacao.append(f"- **Idade:** {idade} anos ⚠️ Pré-idoso")
        else:
            interpretacao.append(f"- **Idade:** {idade} anos")
        
        return "\n".join(interpretacao)

# Instância global do preditor
predictor = PCACRPredictor()
