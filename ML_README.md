# 🤖 Sistema de Machine Learning - Avicena Care

## Sobre o Sistema

Este módulo adiciona capacidades de **Machine Learning** ao sistema Avicena Care para predição automática e inteligente da classificação PCACR baseada em sinais vitais.

## 📊 O que o Modelo Faz?

O modelo aprende a sugerir a cor/prioridade PCACR com base em:
- **Sinais Vitais**: FC, FR, Temp, PA, SpO₂
- **Dados do Paciente**: Idade
- **Exames (quando disponíveis)**: Glicose, Lactato, Eletrólitos, Hemograma

## 🚀 Como Usar

### 1. Treinar o Modelo (Primeira Vez)

```bash
python train_model.py
```

Este comando irá:
- Carregar o Dataset.csv (153MB com dados clínicos reais)
- Criar classificações PCACR baseadas em critérios NEWS2/MEWS
- Treinar um Random Forest com 50.000 registros
- Salvar o modelo treinado em `models/`

**Tempo estimado**: 2-5 minutos

### 2. Arquivos Gerados

Após o treinamento, serão criados:
- `models/pcacr_model.pkl` - Modelo Random Forest treinado
- `models/pcacr_scaler.pkl` - Normalizador de features
- `models/pcacr_features.pkl` - Lista de features usadas

### 3. Usar no Sistema

O modelo é integrado automaticamente ao cadastrar novos pacientes. A predição ML será exibida junto com a classificação baseada em regras.

## 📈 Performance Esperada

- **Acurácia de Treino**: ~85-90%
- **Acurácia de Teste**: ~80-85%
- **Features Mais Importantes**:
  1. Frequência Cardíaca (HR)
  2. Pressão Arterial Sistólica (SBP)
  3. Saturação de O₂ (O2Sat)
  4. Temperatura (Temp)
  5. Frequência Respiratória (Resp)

## 🔄 Retreinamento

Para retreinar o modelo com novos dados:

```bash
python train_model.py
```

O sistema lerá os dados atualizados e regerará os modelos.

## 🎯 Funcionalidades

### ✅ Implementadas
- [x] Treinamento do modelo Random Forest
- [x] Predição de classificação PCACR
- [x] Cálculo de probabilidades por classe
- [x] Feature importance
- [x] Explicação de predições

### 🚧 Planejadas
- [ ] Interface visual "Análise Preditiva"
- [ ] Gráficos SHAP para interpretabilidade
- [ ] Retreinamento incremental com dados dos médicos
- [ ] Detecção de sepse em tempo real
- [ ] Alertas automáticos para deterioração

## 📝 Notas Técnicas

### Mapeamento de Sinais Vitais para PCACR

O modelo usa um sistema de pontuação baseado em NEWS2:

| Sinal Vital | Valor Anormal | Pontos |
|-------------|---------------|--------|
| FC | <40 ou >130 bpm | +3 |
| Temp | <35°C ou >39°C | +3 |
| PA | <90 mmHg | +3 |
| FR | <8 ou >25 irpm | +3 |
| SpO₂ | <92% | +3 |
| Idade | >65 anos | +1 |

**Classificação Final:**
- Score ≥10: PRIORIDADE MÁXIMA
- Score 7-9: ALTA PRIORIDADE
- Score 5-6: MÉDIA PRIORIDADE
- Score 3-4: BAIXA PRIORIDADE
- Score <3: MÍNIMA (ELETIVA)

## 🛠️ Dependências

```
scikit-learn
pandas
numpy
joblib
```

Já incluídas em `requirements.txt`

## 📞 Suporte

Para dúvidas ou problemas, verifique:
1. Se o arquivo `data/Dataset.csv` existe
2. Se as dependências estão instaladas
3. Se há espaço em disco para os modelos (~50MB)

---

**Desenvolvido para Avicena Care** 🏥
Sistema de Triagem Inteligente com PCACR
