"""Teste dos scores clínicos"""
from scores_clinicos import calcular_todos_scores

print("="*70)
print("🧪 TESTE DOS SCORES CLÍNICOS")
print("="*70)

# Teste 1: Paciente com perfil de SEPSE
print("\n\n🔴 TESTE 1: PACIENTE COM PERFIL DE SEPSE")
print("-"*70)
print("Sinais vitais:")
print("  - FC: 125 bpm (Taquicardia)")
print("  - FR: 28 irpm (Taquipneia)")
print("  - Temp: 38.8°C (Febre)")
print("  - PAS: 88 mmHg (Hipotensão)")
print("  - SpO2: 91% (Hipoxemia)")
print("  - Consciência: Confuso")

scores = calcular_todos_scores(
    freq_cardiaca=125,
    freq_respiratoria=28,
    temperatura=38.8,
    pa_sistolica=88,
    spo2=91,
    nivel_consciencia="Confuso"
)

print(f"\n📊 Resultados:")
print(f"  qSOFA: {scores['qsofa']['score']}/3 - {scores['qsofa']['alerta']}")
print(f"  NEWS2: {scores['news2']['score']}/20 - {scores['news2']['alerta']}")
print(f"  SIRS: {scores['sirs']['score']}/3 - {scores['sirs']['alerta']}")

# Teste 2: Paciente NORMAL
print("\n\n🟢 TESTE 2: PACIENTE NORMAL")
print("-"*70)
print("Sinais vitais:")
print("  - FC: 75 bpm")
print("  - FR: 16 irpm")
print("  - Temp: 36.5°C")
print("  - PAS: 120 mmHg")
print("  - SpO2: 98%")
print("  - Consciência: Alerta")

scores = calcular_todos_scores(
    freq_cardiaca=75,
    freq_respiratoria=16,
    temperatura=36.5,
    pa_sistolica=120,
    spo2=98,
    nivel_consciencia="Alerta"
)

print(f"\n📊 Resultados:")
print(f"  qSOFA: {scores['qsofa']['score']}/3 - {scores['qsofa']['alerta']}")
print(f"  NEWS2: {scores['news2']['score']}/20 - {scores['news2']['alerta']}")
print(f"  SIRS: {scores['sirs']['score']}/3 - {scores['sirs']['alerta']}")

# Teste 3: Paciente com risco MODERADO
print("\n\n🟡 TESTE 3: PACIENTE COM RISCO MODERADO")
print("-"*70)
print("Sinais vitais:")
print("  - FC: 105 bpm (Taquicardia leve)")
print("  - FR: 24 irpm (Taquipneia leve)")
print("  - Temp: 37.8°C (Subfebril)")
print("  - PAS: 110 mmHg (Normal baixo)")
print("  - SpO2: 94%")
print("  - Consciência: Alerta")

scores = calcular_todos_scores(
    freq_cardiaca=105,
    freq_respiratoria=24,
    temperatura=37.8,
    pa_sistolica=110,
    spo2=94,
    nivel_consciencia="Alerta"
)

print(f"\n📊 Resultados:")
print(f"  qSOFA: {scores['qsofa']['score']}/3 - {scores['qsofa']['alerta']}")
print(f"  NEWS2: {scores['news2']['score']}/20 - {scores['news2']['alerta']}")
print(f"  SIRS: {scores['sirs']['score']}/3 - {scores['sirs']['alerta']}")

print("\n" + "="*70)
print("✅ Todos os testes concluídos!")
print("="*70)
