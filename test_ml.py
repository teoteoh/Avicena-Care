"""Script para testar o modelo ML treinado"""
from ml_predictor import predictor

# Dados de teste: paciente com sinais vitais normais
patient_data = {
    'freq_cardiaca': 95,
    'spo2': 98,
    'temperatura': 37.2,
    'pa_sistolica': 130,
    'pa_diastolica': 85,
    'freq_respiratoria': 18,
    'idade': 45,
    'genero': 'Masculino'  # Novo campo!
}

print("🧪 Testando predição ML...")
print("\n📋 Dados do paciente:")
for key, value in patient_data.items():
    print(f"   {key}: {value}")

# Fazer predição
result = predictor.predict_pcacr(patient_data)

print("\n🤖 Resultado da predição:")
print(f"   Classificação: {result['prediction']}")
print(f"   Confiança: {result['confidence']*100:.1f}%")

print("\n📊 Probabilidades por classe:")
for classe, prob in result['probabilities'].items():
    print(f"   {classe}: {prob*100:.1f}%")

print("\n🩺 Interpretação clínica:")
explicacao = predictor.explain_prediction(patient_data)
print(explicacao)

print("\n✅ Teste concluído com sucesso!")
