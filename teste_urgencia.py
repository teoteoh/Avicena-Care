# Teste da função de urgência

# Função para calcular urgência baseada em sinais vitais
def calcular_urgencia(temperatura, pa_sistolica, pa_diastolica, freq_respiratoria, freq_cardiaca, idade):
    """
    Calcula o nível de urgência baseado nos sinais vitais
    Retorna: (nivel, cor, emoji, descricao, pontuacao)
    """
    pontuacao = 0
    alertas = []
    
    # TEMPERATURA - Valores normais: 36.1-37.2°C
    if temperatura >= 39.0:
        pontuacao += 3
        alertas.append("Febre alta")
    elif temperatura >= 37.5:
        pontuacao += 2
        alertas.append("Febre")
    elif temperatura >= 37.3:
        pontuacao += 1
        alertas.append("Temperatura elevada")
    elif temperatura <= 35.0:
        pontuacao += 3
        alertas.append("Hipotermia")
    
    # PRESSÃO ARTERIAL - Valores normais: Sistólica 90-139, Diastólica 60-89
    if pa_sistolica >= 180 or pa_diastolica >= 110:
        pontuacao += 3
        alertas.append("Hipertensão severa")
    elif pa_sistolica >= 160 or pa_diastolica >= 100:
        pontuacao += 2
        alertas.append("Hipertensão moderada")
    elif pa_sistolica >= 140 or pa_diastolica >= 90:
        pontuacao += 1
        alertas.append("Hipertensão leve")
    elif pa_sistolica <= 90 or pa_diastolica <= 60:
        pontuacao += 2
        alertas.append("Hipotensão")
    
    # FREQUÊNCIA RESPIRATÓRIA - Valores normais por idade
    # Adultos: 12-20 rpm, Idosos (>65): 12-25 rpm, Crianças: varia por idade
    if idade >= 65:
        fr_min, fr_max = 12, 25
    elif idade >= 18:
        fr_min, fr_max = 12, 20
    elif idade >= 12:
        fr_min, fr_max = 12, 25
    else:
        fr_min, fr_max = 15, 30  # Crianças
    
    if freq_respiratoria >= fr_max + 10:
        pontuacao += 3
        alertas.append("Taquipneia severa")
    elif freq_respiratoria >= fr_max + 5:
        pontuacao += 2
        alertas.append("Taquipneia moderada")
    elif freq_respiratoria > fr_max:
        pontuacao += 1
        alertas.append("Taquipneia leve")
    elif freq_respiratoria < fr_min - 5:
        pontuacao += 2
        alertas.append("Bradipneia")
    
    # FREQUÊNCIA CARDÍACA - Valores normais: 60-100 bpm (adultos)
    if idade >= 18:
        fc_min, fc_max = 60, 100
    elif idade >= 12:
        fc_min, fc_max = 70, 110
    else:
        fc_min, fc_max = 80, 120  # Crianças
    
    if freq_cardiaca >= fc_max + 20:
        pontuacao += 3
        alertas.append("Taquicardia severa")
    elif freq_cardiaca >= fc_max + 10:
        pontuacao += 2
        alertas.append("Taquicardia moderada")
    elif freq_cardiaca > fc_max:
        pontuacao += 1
        alertas.append("Taquicardia leve")
    elif freq_cardiaca < fc_min - 10:
        pontuacao += 2
        alertas.append("Bradicardia")
    elif freq_cardiaca < fc_min:
        pontuacao += 1
        alertas.append("FC baixa")
    
    # Determinar nível de urgência baseado na pontuação
    if pontuacao >= 7:
        return ("CRÍTICA", "#8B0000", "🚨", "Urgência crítica - atendimento imediato", pontuacao, alertas)
    elif pontuacao >= 4:
        return ("ALTA", "#FF4500", "🔴", "Urgência alta - atendimento prioritário", pontuacao, alertas)
    elif pontuacao >= 2:
        return ("MODERADA", "#FF8C00", "🟡", "Urgência moderada - acompanhar", pontuacao, alertas)
    elif pontuacao >= 1:
        return ("BAIXA", "#32CD32", "🟢", "Urgência baixa - monitorar", pontuacao, alertas)
    else:
        return ("NORMAL", "#228B22", "✅", "Sinais vitais normais", pontuacao, alertas)

# Testes
print("=== TESTE DA FUNÇÃO DE URGÊNCIA ===\n")

# Teste 1: Paciente normal
print("Teste 1: Paciente normal")
resultado = calcular_urgencia(36.5, 120, 80, 16, 72, 30)
print(f"Resultado: {resultado[2]} {resultado[0]} - {resultado[3]}")
print(f"Pontuação: {resultado[4]} | Alertas: {resultado[5]}\n")

# Teste 2: Paciente com febre alta
print("Teste 2: Paciente com febre alta")
resultado = calcular_urgencia(39.5, 120, 80, 16, 72, 30)
print(f"Resultado: {resultado[2]} {resultado[0]} - {resultado[3]}")
print(f"Pontuação: {resultado[4]} | Alertas: {resultado[5]}\n")

# Teste 3: Paciente com hipertensão severa
print("Teste 3: Paciente com hipertensão severa")
resultado = calcular_urgencia(36.5, 190, 115, 16, 72, 30)
print(f"Resultado: {resultado[2]} {resultado[0]} - {resultado[3]}")
print(f"Pontuação: {resultado[4]} | Alertas: {resultado[5]}\n")

# Teste 4: Paciente com múltiplos problemas (crítico)
print("Teste 4: Paciente crítico (múltiplos problemas)")
resultado = calcular_urgencia(39.2, 185, 110, 35, 125, 45)
print(f"Resultado: {resultado[2]} {resultado[0]} - {resultado[3]}")
print(f"Pontuação: {resultado[4]} | Alertas: {resultado[5]}\n")

# Teste 5: Idoso com sinais moderados
print("Teste 5: Idoso com sinais moderados")
resultado = calcular_urgencia(37.8, 150, 95, 22, 85, 70)
print(f"Resultado: {resultado[2]} {resultado[0]} - {resultado[3]}")
print(f"Pontuação: {resultado[4]} | Alertas: {resultado[5]}\n")

print("=== TESTE CONCLUÍDO ===")