"""
Módulo de Scores Clínicos para Triagem
Implementa qSOFA, NEWS2 e SIRS
"""

def calcular_qsofa(pa_sistolica, freq_respiratoria, nivel_consciencia="Alerta"):
    """
    qSOFA (Quick Sequential Organ Failure Assessment)
    Score para detecção rápida de sepse
    
    Critérios (0-3 pontos):
    - FR ≥ 22/min = 1 ponto
    - PAS ≤ 100 mmHg = 1 ponto
    - Alteração do estado mental = 1 ponto
    
    Interpretação:
    - qSOFA ≥ 2: Alto risco de sepse, mortalidade ~10%
    - qSOFA < 2: Baixo risco
    """
    score = 0
    criterios = []
    
    # Critério 1: Frequência Respiratória
    if freq_respiratoria >= 22:
        score += 1
        criterios.append("FR ≥ 22/min")
    
    # Critério 2: Pressão Arterial Sistólica
    if pa_sistolica <= 100:
        score += 1
        criterios.append("PAS ≤ 100 mmHg")
    
    # Critério 3: Alteração do estado mental
    if nivel_consciencia != "Alerta":
        score += 1
        criterios.append("Alteração mental")
    
    # Interpretação
    if score >= 2:
        risco = "ALTO"
        alerta = "🚨 SUSPEITA DE SEPSE"
        cor = "vermelho"
    elif score == 1:
        risco = "MODERADO"
        alerta = "⚠️ Monitorar sinais"
        cor = "laranja"
    else:
        risco = "BAIXO"
        alerta = "✅ Baixo risco"
        cor = "verde"
    
    return {
        'score': score,
        'max_score': 3,
        'criterios': criterios,
        'risco': risco,
        'alerta': alerta,
        'cor': cor
    }


def calcular_news2(freq_respiratoria, spo2, pa_sistolica, freq_cardiaca, 
                   temperatura, nivel_consciencia="Alerta"):
    """
    NEWS2 (National Early Warning Score 2)
    Score para detecção de deterioração clínica
    
    Faixas de pontuação (0-20 pontos):
    - 0: Mínimo
    - 1-4: Baixo
    - 5-6: Médio (aumentar frequência de monitoramento)
    - 7+: Alto (resposta urgente)
    """
    score = 0
    detalhes = []
    
    # Frequência Respiratória
    if freq_respiratoria <= 8:
        score += 3
        detalhes.append("FR ≤8: +3")
    elif freq_respiratoria <= 11:
        score += 1
        detalhes.append("FR 9-11: +1")
    elif freq_respiratoria >= 25:
        score += 3
        detalhes.append("FR ≥25: +3")
    elif freq_respiratoria >= 21:
        score += 2
        detalhes.append("FR 21-24: +2")
    
    # SpO2
    if spo2 <= 91:
        score += 3
        detalhes.append("SpO2 ≤91%: +3")
    elif spo2 <= 93:
        score += 2
        detalhes.append("SpO2 92-93%: +2")
    elif spo2 <= 95:
        score += 1
        detalhes.append("SpO2 94-95%: +1")
    
    # Pressão Arterial Sistólica
    if pa_sistolica <= 90:
        score += 3
        detalhes.append("PAS ≤90: +3")
    elif pa_sistolica <= 100:
        score += 2
        detalhes.append("PAS 91-100: +2")
    elif pa_sistolica <= 110:
        score += 1
        detalhes.append("PAS 101-110: +1")
    elif pa_sistolica >= 220:
        score += 3
        detalhes.append("PAS ≥220: +3")
    
    # Frequência Cardíaca
    if freq_cardiaca <= 40:
        score += 3
        detalhes.append("FC ≤40: +3")
    elif freq_cardiaca <= 50:
        score += 1
        detalhes.append("FC 41-50: +1")
    elif freq_cardiaca >= 131:
        score += 3
        detalhes.append("FC ≥131: +3")
    elif freq_cardiaca >= 111:
        score += 2
        detalhes.append("FC 111-130: +2")
    elif freq_cardiaca >= 91:
        score += 1
        detalhes.append("FC 91-110: +1")
    
    # Temperatura
    if temperatura <= 35.0:
        score += 3
        detalhes.append("Temp ≤35°C: +3")
    elif temperatura >= 39.1:
        score += 2
        detalhes.append("Temp ≥39.1°C: +2")
    elif temperatura >= 38.1:
        score += 1
        detalhes.append("Temp 38.1-39°C: +1")
    elif temperatura <= 36.0:
        score += 1
        detalhes.append("Temp 35.1-36°C: +1")
    
    # Nível de Consciência
    if nivel_consciencia != "Alerta":
        score += 3
        detalhes.append("Confusão/Sonolência: +3")
    
    # Interpretação
    if score >= 7:
        risco = "ALTO"
        alerta = "🚨 RESPOSTA URGENTE"
        cor = "vermelho"
    elif score >= 5:
        risco = "MÉDIO"
        alerta = "⚠️ Aumentar monitoramento"
        cor = "laranja"
    elif score >= 1:
        risco = "BAIXO"
        alerta = "⚠️ Monitorar"
        cor = "amarelo"
    else:
        risco = "MÍNIMO"
        alerta = "✅ Normal"
        cor = "verde"
    
    return {
        'score': score,
        'max_score': 20,
        'detalhes': detalhes,
        'risco': risco,
        'alerta': alerta,
        'cor': cor
    }


def calcular_sirs(freq_cardiaca, freq_respiratoria, temperatura):
    """
    SIRS (Síndrome da Resposta Inflamatória Sistêmica)
    Critérios para resposta inflamatória
    
    Critérios (0-4 pontos):
    - FC > 90 bpm = 1 ponto
    - FR > 20/min = 1 ponto
    - Temp < 36°C ou > 38°C = 1 ponto
    - Leucócitos (não disponível) = 1 ponto
    
    Interpretação:
    - SIRS ≥ 2: Provável resposta inflamatória
    - SIRS < 2: Improvável
    """
    score = 0
    criterios = []
    
    # Frequência Cardíaca
    if freq_cardiaca > 90:
        score += 1
        criterios.append("FC > 90 bpm")
    
    # Frequência Respiratória
    if freq_respiratoria > 20:
        score += 1
        criterios.append("FR > 20/min")
    
    # Temperatura
    if temperatura < 36.0 or temperatura > 38.0:
        score += 1
        if temperatura < 36.0:
            criterios.append("Temp < 36°C (Hipotermia)")
        else:
            criterios.append("Temp > 38°C (Febre)")
    
    # Interpretação
    if score >= 2:
        risco = "POSITIVO"
        alerta = "⚠️ SIRS presente"
        cor = "laranja"
        observacao = "Resposta inflamatória detectada"
    elif score == 1:
        risco = "INCERTO"
        alerta = "⚠️ 1 critério presente"
        cor = "amarelo"
        observacao = "Monitorar evolução"
    else:
        risco = "NEGATIVO"
        alerta = "✅ SIRS ausente"
        cor = "verde"
        observacao = "Sem resposta inflamatória"
    
    return {
        'score': score,
        'max_score': 3,  # Só temos 3 critérios (leucócitos não disponível)
        'criterios': criterios,
        'risco': risco,
        'alerta': alerta,
        'cor': cor,
        'observacao': observacao
    }


def calcular_todos_scores(freq_cardiaca, freq_respiratoria, temperatura, 
                          pa_sistolica, spo2, nivel_consciencia="Alerta"):
    """
    Calcula todos os scores clínicos de uma vez
    """
    qsofa = calcular_qsofa(pa_sistolica, freq_respiratoria, nivel_consciencia)
    news2 = calcular_news2(freq_respiratoria, spo2, pa_sistolica, 
                          freq_cardiaca, temperatura, nivel_consciencia)
    sirs = calcular_sirs(freq_cardiaca, freq_respiratoria, temperatura)
    mews = calcular_mews(freq_cardiaca, freq_respiratoria, temperatura, 
                        pa_sistolica, nivel_consciencia)
    gcs = calcular_gcs_simplificado(nivel_consciencia)
    
    return {
        'qsofa': qsofa,
        'news2': news2,
        'sirs': sirs,
        'mews': mews,
        'gcs': gcs
    }


def calcular_mews(freq_cardiaca, freq_respiratoria, temperatura, 
                  pa_sistolica, nivel_consciencia="Alerta"):
    """
    MEWS (Modified Early Warning Score)
    Score de alerta precoce muito usado em hospitais
    
    Parâmetros (0-3 pontos cada):
    - Frequência Cardíaca
    - Frequência Respiratória
    - Pressão Arterial Sistólica
    - Temperatura
    - Nível de Consciência
    
    Total: 0-15 pontos
    Interpretação:
    - 0-1: Baixo risco
    - 2-3: Médio risco
    - 4-5: Alto risco
    - ≥6: Risco crítico
    """
    score = 0
    detalhes = []
    
    # Frequência Cardíaca
    if freq_cardiaca < 40:
        score += 3
        detalhes.append("FC <40: +3")
    elif freq_cardiaca < 50:
        score += 2
        detalhes.append("FC 40-50: +2")
    elif freq_cardiaca < 60:
        score += 1
        detalhes.append("FC 50-60: +1")
    elif freq_cardiaca >= 130:
        score += 3
        detalhes.append("FC ≥130: +3")
    elif freq_cardiaca >= 120:
        score += 2
        detalhes.append("FC 120-129: +2")
    elif freq_cardiaca >= 110:
        score += 1
        detalhes.append("FC 110-119: +1")
    
    # Frequência Respiratória
    if freq_respiratoria < 9:
        score += 3
        detalhes.append("FR <9: +3")
    elif freq_respiratoria >= 30:
        score += 3
        detalhes.append("FR ≥30: +3")
    elif freq_respiratoria >= 21:
        score += 2
        detalhes.append("FR 21-29: +2")
    elif freq_respiratoria <= 11:
        score += 1
        detalhes.append("FR 9-11: +1")
    
    # Pressão Arterial Sistólica
    if pa_sistolica < 70:
        score += 3
        detalhes.append("PAS <70: +3")
    elif pa_sistolica < 80:
        score += 2
        detalhes.append("PAS 70-79: +2")
    elif pa_sistolica < 100:
        score += 1
        detalhes.append("PAS 80-99: +1")
    elif pa_sistolica >= 200:
        score += 2
        detalhes.append("PAS ≥200: +2")
    
    # Temperatura
    if temperatura < 35.0:
        score += 3
        detalhes.append("Temp <35°C: +3")
    elif temperatura >= 38.5:
        score += 2
        detalhes.append("Temp ≥38.5°C: +2")
    elif temperatura >= 38.0:
        score += 1
        detalhes.append("Temp 38-38.4°C: +1")
    
    # Nível de Consciência
    if nivel_consciencia == "Inconsciente":
        score += 3
        detalhes.append("Inconsciente: +3")
    elif nivel_consciencia in ["Confuso", "Sonolento"]:
        score += 1
        detalhes.append("Confuso/Sonolento: +1")
    
    # Interpretação
    if score >= 6:
        risco = "CRÍTICO"
        alerta = "🚨 RISCO CRÍTICO"
        cor = "vermelho"
    elif score >= 4:
        risco = "ALTO"
        alerta = "🔴 ALTO RISCO"
        cor = "laranja"
    elif score >= 2:
        risco = "MÉDIO"
        alerta = "⚠️ MÉDIO RISCO"
        cor = "amarelo"
    else:
        risco = "BAIXO"
        alerta = "✅ BAIXO RISCO"
        cor = "verde"
    
    return {
        'score': score,
        'max_score': 15,
        'detalhes': detalhes,
        'risco': risco,
        'alerta': alerta,
        'cor': cor
    }


def calcular_gcs_completo(abertura_ocular=4, resposta_verbal=5, resposta_motora=6):
    """
    Escala de Coma de Glasgow COMPLETA
    
    ABERTURA OCULAR (1-4 pontos):
    - Espontânea: 4
    - À voz: 3
    - À dor: 2
    - Nenhuma: 1
    
    RESPOSTA VERBAL (1-5 pontos):
    - Orientada: 5
    - Confusa: 4
    - Palavras inapropriadas: 3
    - Palavras incompreensivas: 2
    - Nenhuma: 1
    
    RESPOSTA MOTORA (1-6 pontos):
    - Obedece comandos: 6
    - Localiza dor: 5
    - Movimento de retirada: 4
    - Flexão anormal: 3
    - Extensão anormal: 2
    - Nenhuma: 1
    
    SCORE TOTAL: 3-15 pontos
    INTUBAÇÃO: ≤8 pontos
    """
    score = abertura_ocular + resposta_verbal + resposta_motora
    
    # Interpretação
    if score == 15:
        categoria = "NORMAL"
        alerta = "✅ Consciente e orientado"
        cor = "verde"
        risco = "Mínimo"
    elif score >= 13:
        categoria = "LEVE"
        alerta = "⚠️ Alteração leve"
        cor = "amarelo"
        risco = "Baixo"
    elif score >= 9:
        categoria = "MODERADO"
        alerta = "🟠 Rebaixamento moderado"
        cor = "laranja"
        risco = "Médio - Monitorar"
    else:
        categoria = "GRAVE/COMA"
        alerta = "🔴 COMA - Intubação indicada (≤8)"
        cor = "vermelho"
        risco = "Crítico - Via aérea em risco"
    
    return {
        'score': score,
        'max_score': 15,
        'categoria': categoria,
        'alerta': alerta,
        'cor': cor,
        'risco': risco,
        'componentes': {
            'abertura_ocular': abertura_ocular,
            'resposta_verbal': resposta_verbal,
            'resposta_motora': resposta_motora
        },
        'intubacao': score <= 8
    }


def calcular_gcs_simplificado(nivel_consciencia="Alerta"):
    """
    Escala de Glasgow Simplificada
    Baseada no nível de consciência coletado no formulário
    
    Esta é uma APROXIMAÇÃO quando não se tem os 3 componentes detalhados.
    Mapeia estados mentais para scores aproximados de GCS.
    
    Mapeamento baseado em correlação clínica típica:
    - Alerta: 15 (O:4 V:5 M:6)
    - Confuso: 13 (O:4 V:4 M:5) - Desorientação
    - Sonolento: 10 (O:3 V:3 M:4) - Responde a estímulos verbais
    - Inconsciente: 6 (O:1 V:1 M:4) - Não responde, só reflexos
    
    Interpretação:
    - 15: Normal
    - 13-14: Leve
    - 9-12: Moderado
    - ≤8: Grave (Coma, indicação de intubação)
    """
    mapeamento = {
        "Alerta": 15,
        "Confuso": 13,
        "Sonolento": 10,
        "Inconsciente": 6
    }
    
    score = mapeamento.get(nivel_consciencia, 15)
    
    # Interpretação
    if score == 15:
        categoria = "NORMAL"
        alerta = "✅ Consciente e orientado"
        cor = "verde"
        risco = "Mínimo"
    elif score >= 13:
        categoria = "LEVE"
        alerta = "⚠️ Confusão/Desorientação leve"
        cor = "amarelo"
        risco = "Baixo - Avaliar causa"
    elif score >= 9:
        categoria = "MODERADO"
        alerta = "🟠 Rebaixamento moderado"
        cor = "laranja"
        risco = "Médio - Monitoramento contínuo"
    else:
        categoria = "GRAVE/COMA"
        alerta = "🔴 COMA - Intubação indicada (≤8)"
        cor = "vermelho"
        risco = "Crítico - Via aérea em risco"
    
    descricao = {
        15: "Alerta, orientado no tempo/espaço",
        13: "Confuso, desorientado",
        10: "Sonolento, responde a estímulos verbais",
        6: "Inconsciente, resposta motora apenas"
    }
    
    return {
        'score': score,
        'max_score': 15,
        'categoria': categoria,
        'alerta': alerta,
        'cor': cor,
        'risco': risco,
        'descricao': descricao.get(score, "Avaliação pendente"),
        'intubacao': score <= 8
    }


def avaliar_escala_dor(intensidade_dor):
    """
    Escala de Dor - EVA (Escala Visual Analógica)
    0-10 pontos
    
    Interpretação:
    - 0: Sem dor
    - 1-3: Dor leve
    - 4-6: Dor moderada
    - 7-8: Dor intensa
    - 9-10: Dor insuportável
    """
    if intensidade_dor == 0:
        categoria = "SEM DOR"
        alerta = "✅ Sem queixas álgicas"
        cor = "verde"
        emoji = "😊"
    elif intensidade_dor <= 3:
        categoria = "DOR LEVE"
        alerta = "🟡 Dor tolerável"
        cor = "amarelo"
        emoji = "😐"
    elif intensidade_dor <= 6:
        categoria = "DOR MODERADA"
        alerta = "🟠 Requer analgesia"
        cor = "laranja"
        emoji = "😣"
    elif intensidade_dor <= 8:
        categoria = "DOR INTENSA"
        alerta = "🔴 Analgesia urgente"
        cor = "vermelho"
        emoji = "😖"
    else:
        categoria = "DOR INSUPORTÁVEL"
        alerta = "🚨 EMERGÊNCIA - Dor crítica"
        cor = "vermelho"
        emoji = "😭"
    
    return {
        'score': intensidade_dor,
        'max_score': 10,
        'categoria': categoria,
        'alerta': alerta,
        'cor': cor,
        'emoji': emoji
    }
