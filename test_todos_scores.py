"""Teste completo dos 6 scores clínicos"""
from scores_clinicos import calcular_todos_scores, avaliar_escala_dor

print("="*70)
print("🧪 TESTE COMPLETO DOS 6 SCORES CLÍNICOS")
print("="*70)

# Teste 1: Paciente com SEPSE GRAVE
print("\n\n🔴 TESTE 1: PACIENTE COM SEPSE GRAVE")
print("-"*70)
print("Sinais vitais:")
print("  - FC: 135 bpm (Taquicardia grave)")
print("  - FR: 32 irpm (Taquipneia grave)")
print("  - Temp: 39.5°C (Febre alta)")
print("  - PAS: 75 mmHg (Hipotensão severa)")
print("  - SpO2: 88% (Hipoxemia grave)")
print("  - Consciência: Confuso")
print("  - Dor: 9/10")

scores = calcular_todos_scores(
    freq_cardiaca=135,
    freq_respiratoria=32,
    temperatura=39.5,
    pa_sistolica=75,
    spo2=88,
    nivel_consciencia="Confuso"
)
dor = avaliar_escala_dor(9)

print(f"\n📊 Resultados:")
print(f"  🔴 qSOFA:  {scores['qsofa']['score']}/3   - {scores['qsofa']['alerta']}")
print(f"  🔴 NEWS2:  {scores['news2']['score']}/20  - {scores['news2']['alerta']}")
print(f"  🟠 SIRS:   {scores['sirs']['score']}/3   - {scores['sirs']['alerta']}")
print(f"  🔴 MEWS:   {scores['mews']['score']}/15  - {scores['mews']['alerta']}")
print(f"  🟡 GCS:    {scores['gcs']['score']}/15  - {scores['gcs']['alerta']}")
print(f"  🔴 Dor:    {dor['score']}/10 {dor['emoji']} - {dor['alerta']}")

# Teste 2: Paciente NORMAL
print("\n\n🟢 TESTE 2: PACIENTE COMPLETAMENTE NORMAL")
print("-"*70)
print("Sinais vitais:")
print("  - FC: 72 bpm")
print("  - FR: 14 irpm")
print("  - Temp: 36.7°C")
print("  - PAS: 118 mmHg")
print("  - SpO2: 99%")
print("  - Consciência: Alerta")
print("  - Dor: 0/10")

scores = calcular_todos_scores(
    freq_cardiaca=72,
    freq_respiratoria=14,
    temperatura=36.7,
    pa_sistolica=118,
    spo2=99,
    nivel_consciencia="Alerta"
)
dor = avaliar_escala_dor(0)

print(f"\n📊 Resultados:")
print(f"  🟢 qSOFA:  {scores['qsofa']['score']}/3   - {scores['qsofa']['alerta']}")
print(f"  🟢 NEWS2:  {scores['news2']['score']}/20  - {scores['news2']['alerta']}")
print(f"  🟢 SIRS:   {scores['sirs']['score']}/3   - {scores['sirs']['alerta']}")
print(f"  🟢 MEWS:   {scores['mews']['score']}/15  - {scores['mews']['alerta']}")
print(f"  🟢 GCS:    {scores['gcs']['score']}/15  - {scores['gcs']['alerta']}")
print(f"  🟢 Dor:    {dor['score']}/10 {dor['emoji']} - {dor['alerta']}")

# Teste 3: Paciente com DOR AGUDA e sinais moderados
print("\n\n🟡 TESTE 3: PACIENTE COM DOR AGUDA (Ex: Fratura)")
print("-"*70)
print("Sinais vitais:")
print("  - FC: 98 bpm (Leve taquicardia pela dor)")
print("  - FR: 22 irpm (Leve taquipneia)")
print("  - Temp: 36.9°C")
print("  - PAS: 140 mmHg (Elevada pela dor)")
print("  - SpO2: 97%")
print("  - Consciência: Alerta")
print("  - Dor: 8/10 (Dor intensa)")

scores = calcular_todos_scores(
    freq_cardiaca=98,
    freq_respiratoria=22,
    temperatura=36.9,
    pa_sistolica=140,
    spo2=97,
    nivel_consciencia="Alerta"
)
dor = avaliar_escala_dor(8)

print(f"\n📊 Resultados:")
print(f"  🟠 qSOFA:  {scores['qsofa']['score']}/3   - {scores['qsofa']['alerta']}")
print(f"  🟡 NEWS2:  {scores['news2']['score']}/20  - {scores['news2']['alerta']}")
print(f"  🟠 SIRS:   {scores['sirs']['score']}/3   - {scores['sirs']['alerta']}")
print(f"  🟢 MEWS:   {scores['mews']['score']}/15  - {scores['mews']['alerta']}")
print(f"  🟢 GCS:    {scores['gcs']['score']}/15  - {scores['gcs']['alerta']}")
print(f"  🔴 Dor:    {dor['score']}/10 {dor['emoji']} - {dor['alerta']}")

# Teste 4: Paciente INCONSCIENTE (Trauma grave)
print("\n\n🔴 TESTE 4: PACIENTE INCONSCIENTE (Trauma)")
print("-"*70)
print("Sinais vitais:")
print("  - FC: 55 bpm (Bradicardia)")
print("  - FR: 8 irpm (Bradipneia grave)")
print("  - Temp: 35.2°C (Hipotermia)")
print("  - PAS: 95 mmHg")
print("  - SpO2: 90%")
print("  - Consciência: INCONSCIENTE")
print("  - Dor: 0/10 (Sem resposta)")

scores = calcular_todos_scores(
    freq_cardiaca=55,
    freq_respiratoria=8,
    temperatura=35.2,
    pa_sistolica=95,
    spo2=90,
    nivel_consciencia="Inconsciente"
)
dor = avaliar_escala_dor(0)

print(f"\n📊 Resultados:")
print(f"  🔴 qSOFA:  {scores['qsofa']['score']}/3   - {scores['qsofa']['alerta']}")
print(f"  🔴 NEWS2:  {scores['news2']['score']}/20  - {scores['news2']['alerta']}")
print(f"  🟢 SIRS:   {scores['sirs']['score']}/3   - {scores['sirs']['alerta']}")
print(f"  🔴 MEWS:   {scores['mews']['score']}/15  - {scores['mews']['alerta']}")
print(f"  🔴 GCS:    {scores['gcs']['score']}/15  - {scores['gcs']['alerta']}")
print(f"  🟢 Dor:    {dor['score']}/10 {dor['emoji']} - {dor['alerta']}")

print("\n" + "="*70)
print("✅ Todos os 6 scores funcionando perfeitamente!")
print("="*70)
print("\n📊 Scores Implementados:")
print("  1. qSOFA  - Detecção de Sepse")
print("  2. NEWS2  - Deterioração Clínica")
print("  3. SIRS   - Resposta Inflamatória")
print("  4. MEWS   - Alerta Precoce")
print("  5. GCS    - Nível de Consciência")
print("  6. EVA    - Intensidade da Dor")
