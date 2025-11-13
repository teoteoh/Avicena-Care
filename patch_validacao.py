#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para aplicar patch de validação clínica no app_triagem.py"""

import re

# Ler arquivo
with open('app_triagem.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Padrão a procurar (aproximado para lidar com caracteres especiais)
pattern = r'(conn\.commit\(\)\s+st\.success\(f"✅ Paciente \{nome\} cadastrado com sucesso!"\)\s+# Mostrar classificações\s+col_rule, col_ml = st\.columns\(2\)\s+with col_rule:\s+st\.info\(f"[^"]*\*\*Classificação \(Regras\):\*\* \{urgencia\[2\]\} \{urgencia\[0\]\}"\)\s+if ml_prediction:\s+with col_ml:\s+confidence = ml_prediction\[\'confidence\'\] \* 100\s+st\.info\(f"🤖 \*\*Predição ML:\*\* \{ml_prediction\[\'prediction\'\]\} \(\{confidence:\.0f\}%\)"\)\s+# Mostrar probabilidades\s+st\.markdown\("\*\*📊 Probabilidades por Classe:\*\*"\)\s+prob_cols = st\.columns\(5\)\s+classes_ordem = \[\'PRIORIDADE MÁXIMA\', \'ALTA PRIORIDADE\', \'MÉDIA PRIORIDADE\', \'BAIXA PRIORIDADE\', \'MÍNIMA \(ELETIVA\)\'\]\s+for idx, classe in enumerate\(classes_ordem\):\s+prob = ml_prediction\[\'probabilities\'\]\.get\(classe, 0\) \* 100\s+with prob_cols\[idx\]:\s+st\.metric\(classe\.split\(\)\[0\], f"\{prob:\.1f\}%"\))'

# Substituição
replacement = r'''conn.commit()
                    
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
                                st.metric(classe.split()[0], f"{prob:.1f}%")'''

# Tentar com busca por linhas específicas
lines = content.split('\n')
start_idx = None
end_idx = None

for i, line in enumerate(lines):
    if 'st.success(f"✅ Paciente {nome} cadastrado com sucesso!")' in line:
        start_idx = i - 2  # Incluir conn.commit()
    if start_idx and 'st.metric(classe.split()[0], f"{prob:.1f}%")' in line and i > start_idx:
        end_idx = i
        break

if start_idx and end_idx:
    print(f"Encontrado bloco nas linhas {start_idx+1} a {end_idx+1}")
    # Reconstruir arquivo
    new_lines = lines[:start_idx] + replacement.split('\n') + lines[end_idx+1:]
    new_content = '\n'.join(new_lines)
    
    # Salvar
    with open('app_triagem_new.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("✅ Arquivo app_triagem_new.py criado com sucesso!")
    print("Execute: mv app_triagem.py app_triagem_backup.py && mv app_triagem_new.py app_triagem.py")
else:
    print("❌ Não foi possível encontrar o bloco para substituição")
    print(f"start_idx: {start_idx}, end_idx: {end_idx}")
