"""
Módulo de Validação Clínica
Camada de segurança que valida e ajusta predições do ML baseado em critérios clínicos críticos
"""

def validar_predicao_ml(ml_prediction, scores, urgencia_regras):
    """
    Valida a predição do ML contra critérios clínicos de segurança.
    Sobrescreve o ML quando há sinais críticos inequívocos.
    
    Args:
        ml_prediction: Predição do modelo ML
        scores: Dicionário com todos os scores clínicos
        urgencia_regras: Tupla com (classificação, emoji, texto) das regras
    
    Returns:
        dict: {
            'prediction_final': classificação final,
            'was_overridden': bool (True se ML foi sobrescrito),
            'override_reason': motivo da sobrescrita,
            'ml_original': predição original do ML
        }
    """
    
    # Extrair scores
    qsofa = scores['qsofa']['score']
    news2 = scores['news2']['score']
    mews = scores['mews']['score']
    gcs = scores['gcs']['score']
    
    # Classificação original do ML
    ml_class = ml_prediction['prediction']
    confidence = ml_prediction['confidence']
    
    # REGRAS DE SEGURANÇA CRÍTICAS
    override_reason = None
    should_override = False
    new_classification = ml_class
    
    # 1. GCS CRÍTICO (≤8 = Coma)
    if gcs <= 8:
        should_override = True
        new_classification = "PRIORIDADE MÁXIMA"
        override_reason = f"🧠 GCS Crítico ({gcs}/15) - COMA - Emergência neurológica"
    
    # 2. GCS ALTERADO (9-14) + ML sugere baixa prioridade
    elif gcs < 15 and ml_class in ['BAIXA PRIORIDADE', 'MÍNIMA (ELETIVA)']:
        should_override = True
        if gcs <= 12:
            new_classification = "PRIORIDADE MÁXIMA"
            override_reason = f"🧠 GCS Moderado ({gcs}/15) - Rebaixamento significativo do nível de consciência"
        else:
            new_classification = "ALTA PRIORIDADE"
            override_reason = f"🧠 GCS Leve ({gcs}/15) - Alteração do estado mental requer avaliação urgente"
    
    # 3. qSOFA ≥ 2 (SUSPEITA DE SEPSE) - SEMPRE SOBRESCREVER
    elif qsofa >= 2:
        should_override = True
        new_classification = "PRIORIDADE MÁXIMA"
        override_reason = f"🚨 qSOFA {qsofa}/3 - SUSPEITA DE SEPSE - Risco de morte iminente"
    
    # 4. NEWS2 ≥ 10 (RISCO MUITO ALTO) - Só sobrescreve se ML subestimar muito
    elif news2 >= 10 and ml_class in ['BAIXA PRIORIDADE', 'MÍNIMA (ELETIVA)']:
        should_override = True
        new_classification = "PRIORIDADE MÁXIMA"
        override_reason = f"📈 NEWS2 Muito Alto ({news2}/20) - Deterioração clínica grave"
    
    # 5. NEWS2 7-9 + Confiança baixa (<40%) - Sugerir aumento apenas se ML muito incerto
    elif news2 >= 7 and ml_class == 'MÍNIMA (ELETIVA)' and confidence < 0.5:
        should_override = True
        new_classification = "MÉDIA PRIORIDADE"
        override_reason = f"📈 NEWS2 Alto ({news2}/20) + Confiança ML baixa ({confidence*100:.0f}%) - Ajuste conservador"
    
    # 6. MEWS ≥ 6 (RISCO CRÍTICO) - Só para casos realmente subestimados
    elif mews >= 6 and ml_class == 'MÍNIMA (ELETIVA)':
        should_override = True
        new_classification = "BAIXA PRIORIDADE"
        override_reason = f"⚠️ MEWS Crítico ({mews}/15) - Alerta precoce de deterioração"
    
    # 7. CONFIANÇA MUITO BAIXA DO ML (<40%) + Regras sugerem urgência maior
    elif confidence < 0.4 and urgencia_regras[0] in ['PRIORIDADE MÁXIMA', 'ALTA PRIORIDADE']:
        should_override = True
        new_classification = urgencia_regras[0]
        override_reason = f"⚠️ ML com baixa confiança ({confidence*100:.0f}%) - Priorizando avaliação clínica das regras"
    
    return {
        'prediction_final': new_classification,
        'was_overridden': should_override,
        'override_reason': override_reason,
        'ml_original': ml_class,
        'confidence_original': confidence
    }


def formatar_alerta_override(validation_result):
    """
    Formata mensagem de alerta quando ML foi sobrescrito
    """
    if not validation_result['was_overridden']:
        return None
    
    return f"""
    ⚠️ **ALERTA CLÍNICO - Classificação Ajustada**
    
    **ML Sugeriu:** {validation_result['ml_original']} ({validation_result['confidence_original']*100:.0f}% confiança)
    
    **Classificação Final:** {validation_result['prediction_final']}
    
    **Motivo:** {validation_result['override_reason']}
    
    *A segurança do paciente sempre prevalece sobre algoritmos. Esta decisão foi baseada em critérios clínicos validados.*
    """
