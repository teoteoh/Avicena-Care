# 🤖 Como Usar os Recursos de Machine Learning

## ✅ Implementações Completas

### 1. **Predição ML no Cadastro de Pacientes**
Quando um enfermeiro cadastra um novo paciente, o sistema agora mostra:
- 📋 Classificação baseada em regras (sistema original)
- 🤖 Predição do modelo ML com percentual de confiança
- 📊 Probabilidades para cada classe de PCACR

### 2. **Nova Aba "🤖 Análise Preditiva" (Médicos)**
Aba exclusiva para médicos com:
- Seleção de paciente para análise detalhada
- Comparação: Classificação atual vs Predição ML
- Distribuição de probabilidades para todas as classes
- Interpretação clínica dos sinais vitais
- Alertas de risco de sepse
- Gráfico de importância dos fatores clínicos

## 🚀 Como Ativar

### Passo 1: Instalar Dependências
```powershell
pip install -r requirements.txt
```

Isso instalará:
- `scikit-learn` (modelo ML)
- `numpy` (cálculos numéricos)
- `joblib` (salvar/carregar modelos)

### Passo 2: Treinar o Modelo
```powershell
python train_model.py
```

**Tempo estimado:** 2-5 minutos  
**Resultado:** Cria 3 arquivos na pasta `models/`:
- `pcacr_model.pkl` (modelo treinado)
- `pcacr_scaler.pkl` (normalizador de dados)
- `pcacr_features.pkl` (lista de features)

**Saída esperada:**
```
📊 Dataset carregado: 50000 amostras
🎯 Criando labels PCACR...
   - PRIORIDADE MÁXIMA: 15%
   - ALTA PRIORIDADE: 20%
   - MÉDIA PRIORIDADE: 30%
   - BAIXA PRIORIDADE: 25%
   - MÍNIMA (ELETIVA): 10%
🧠 Treinando Random Forest...
   [Parallel(n_jobs=2)]: Done 100 out of 100 | elapsed: 45.2s finished
✅ Modelo treinado! Acurácia: 0.82
💾 Modelo salvo em models/
```

### Passo 3: Iniciar o Sistema
```powershell
streamlit run app_triagem.py
```

O sistema detectará automaticamente se o modelo está disponível e habilitará os recursos ML.

## 📋 Funcionalidades

### Para Enfermeiros
- **Cadastro Inteligente:** Ao adicionar um paciente, veja a sugestão do ML junto com a classificação por regras
- **Validação Cruzada:** Compare a urgência calculada com a predição do modelo
- **Confiança:** Veja o nível de confiança do modelo (0-100%)

### Para Médicos
- **Análise Preditiva:** Aba dedicada com visualizações avançadas
- **Probabilidades:** Veja a distribuição de risco para todas as classes
- **Interpretação Clínica:** Análise automática dos sinais vitais
- **Alertas de Sepse:** Avisos automáticos para pacientes de alto risco
- **Feature Importance:** Entenda quais fatores mais influenciaram a predição

## 🎯 Classificações PCACR

O modelo aprende a sugerir 5 níveis de prioridade:

| Cor | Classe | Descrição |
|-----|--------|-----------|
| 🔴 | PRIORIDADE MÁXIMA | Risco iminente de morte |
| 🟠 | ALTA PRIORIDADE | Condições críticas |
| 🟡 | MÉDIA PRIORIDADE | Situação estável com urgência |
| 🟢 | BAIXA PRIORIDADE | Condições leves |
| 🔵 | MÍNIMA (ELETIVA) | Casos não urgentes |

## 🧠 Como o Modelo Funciona

### Entrada (17 Parâmetros Clínicos)
- **Sinais Vitais:** FC, Temp, PA (sistólica/diastólica), FR, SpO2, PAM
- **Dados Demográficos:** Idade
- **Exames Laboratoriais:** Glicose, Lactato, Cálcio, Cloreto, Potássio, Leucócitos, Hematócrito, Hemoglobina, Plaquetas

### Algoritmo
- **Random Forest Classifier** com 100 árvores
- Treinado em 50.000 casos clínicos reais
- Baseado no score NEWS2 (National Early Warning Score)
- Acurácia esperada: 80-85%

### Saída
- Classe PCACR prevista
- Probabilidade para cada classe (0-100%)
- Nível de confiança geral
- Interpretação dos sinais vitais

## ⚠️ Observações Importantes

### Sem Modelo Treinado
Se você não executar `train_model.py`, o sistema funcionará normalmente mas:
- ❌ Não mostrará predições ML no cadastro
- ❌ A aba "Análise Preditiva" não aparecerá para médicos
- ✅ Classificação por regras continuará funcionando

### Retrainamento
Para atualizar o modelo com novos dados:
```powershell
python train_model.py
```

### Performance
- **Primeira execução:** 2-5 minutos (treina o modelo)
- **Uso no sistema:** < 1 segundo (predição instantânea)
- **Memória:** ~50MB (modelo carregado)

## 🔧 Resolução de Problemas

### Erro: "No module named 'sklearn'"
```powershell
pip install scikit-learn
```

### Erro: "Dataset.csv not found"
Certifique-se de que `data/Dataset.csv` existe no diretório do projeto.

### Erro: "Model file not found"
Execute `python train_model.py` para criar os arquivos do modelo.

### Modelo não aparece no sistema
1. Verifique se os arquivos `.pkl` estão em `models/`
2. Reinicie o Streamlit
3. Confirme que não há erros no terminal

## 📊 Próximas Melhorias (Roadmap)

- [ ] Visualizações SHAP para interpretabilidade
- [ ] Retreinamento incremental com feedback médico
- [ ] Alertas em tempo real para deterioração
- [ ] Análise de tendências temporais
- [ ] Integração com mais fontes de dados

## 📚 Documentação Técnica

Para detalhes sobre a implementação, veja:
- `ML_README.md` - Documentação completa do sistema ML
- `train_model.py` - Script de treinamento
- `ml_predictor.py` - Módulo de predição
