# 🏥 Avicena Care - Sistema Inteligente de Triagem com Machine Learning

Sistema avançado de triagem médica desenvolvido em Python com Streamlit, integrando **Machine Learning**, **Scores Clínicos Validados** e **Protocolo PCACR** para classificação automatizada de risco e priorização de atendimento.

---

## 🎯 Visão Geral

O **Avicena Care** é uma solução completa para serviços de emergência e triagem hospitalar que combina:

- 🤖 **Inteligência Artificial** com modelo Random Forest (93.85% de acurácia)
- 📊 **6 Scores Clínicos Validados** (qSOFA, NEWS2, SIRS, MEWS, GCS, EVA)
- 🛡️ **Validação Clínica Inteligente** que sobrescreve o ML em casos críticos
- 🎨 **Interface Moderna** e intuitiva para profissionais de saúde
- 📈 **Análise Preditiva** com explicações clínicas detalhadas
- 📋 **Gestão Completa** de fila de atendimento e histórico

---

## ✨ Funcionalidades Principais

### 🔴 Classificação PCACR (Manchester)
Sistema baseado no Protocolo de Classificação de Risco que categoriza pacientes em 5 níveis:

- **🔴 PRIORIDADE MÁXIMA** - Atendimento imediato (0 min)
- **🟠 ALTA PRIORIDADE** - Muito urgente (15 min)
- **🟡 MÉDIA PRIORIDADE** - Urgente (60 min)
- **🟢 BAIXA PRIORIDADE** - Pouco urgente (120 min)
- **🔵 MÍNIMA (ELETIVA)** - Não urgente (240 min)

### 🤖 Machine Learning com Validação Clínica

#### Modelo Preditivo
- **Algoritmo:** Random Forest Classifier
- **Acurácia:** 93.85% (teste) | 95.61% (treino)
- **Features:** 9 parâmetros vitais + demográficos
  - Frequência Cardíaca, Saturação O2, Temperatura
  - PA Sistólica, PA Diastólica, PAM
  - Frequência Respiratória, Idade, Gênero

#### Camada de Segurança Clínica
O sistema **valida automaticamente** as predições do ML e sobrescreve quando detecta:
- 🧠 **GCS ≤ 8** → Coma (intubação)
- 🧠 **GCS 9-14** + ML baixo → Rebaixamento de consciência
- 🚨 **qSOFA ≥ 2** → Suspeita de SEPSE
- 📈 **NEWS2 ≥ 10** → Deterioração grave
- ⚠️ **Confiança ML < 40%** → Prioriza avaliação clínica

### 📊 Scores Clínicos Validados

#### 1. qSOFA (Quick SOFA)
- **Objetivo:** Detecção rápida de sepse
- **Critérios:** FR ≥22, PAS ≤100, Alteração mental
- **Alerta:** qSOFA ≥ 2 = Alto risco de morte

#### 2. NEWS2 (National Early Warning Score)
- **Objetivo:** Identificar deterioração clínica
- **Escala:** 0-20 pontos
- **Uso:** Padrão ouro internacional

#### 3. SIRS (Síndrome da Resposta Inflamatória)
- **Objetivo:** Detectar resposta inflamatória sistêmica
- **Critérios:** FC >90, FR >20, Temp anormal
- **Alerta:** SIRS ≥ 2 = Processo infeccioso

#### 4. MEWS (Modified Early Warning Score)
- **Objetivo:** Sistema de alerta precoce
- **Escala:** 0-15 pontos
- **Uso:** Amplamente usado no Brasil

#### 5. GCS (Glasgow Coma Scale)
- **Objetivo:** Avaliar nível de consciência
- **Componentes:** Abertura ocular + Resposta verbal + Resposta motora
- **Crítico:** GCS ≤ 8 indica necessidade de intubação

#### 6. EVA (Escala Visual Analógica)
- **Objetivo:** Quantificar dor do paciente
- **Escala:** 0-10 pontos
- **Uso:** Priorização e analgesia

### 🎯 Interfaces por Perfil

#### 👨‍⚕️ Enfermagem
- 🧾 Fila de atendimento com classificação automática
- ➕ Cadastro completo de pacientes
- 🔄 Reclassificação manual de urgência
- ✅ Marcar pacientes como atendidos
- 📋 Histórico de atendimentos

#### 👨‍⚕️ Médico
Inclui tudo da Enfermagem, mais:
- 🤖 Análise preditiva com ML
- 📊 Análise clínica com gráficos
- 📈 Dashboard com métricas
- 📑 Relatórios estatísticos
- 🔍 Explicabilidade do modelo

---

## 💻 Tecnologias Utilizadas

### Backend
- **Python 3.8+**
- **Streamlit 1.28+** - Framework web
- **Scikit-learn** - Machine Learning
- **Pandas** - Manipulação de dados
- **Databricks** - Plataforma de dados e banco de dados

### Frontend
- **Plotly** - Gráficos interativos
- **CSS3** - Estilização responsiva
- **Streamlit Components** - Interface moderna

### Machine Learning
- **Random Forest Classifier**
- **StandardScaler** - Normalização
- **Train/Test Split** - Validação
- **Feature Importance** - Interpretabilidade

---

## 🚀 Instalação e Execução

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes)

### 1. Configuração do Databricks

- Crie um **SQL Warehouse** no seu workspace Databricks.
- Gere um **Personal Access Token (PAT)** em *User Settings > Developer*.

### 2. Instalação Local

```bash
# 1. Clone o repositório
git clone https://github.com/magosheimus/Avicena-Care.git
cd avicena-care

# 2. Crie o arquivo de segredos
# Crie o arquivo .streamlit/secrets.toml e adicione suas credenciais:
[databricks]
server_hostname = "adb-xxxxxxxx.azuredatabricks.net"
http_path = "/sql/1.0/warehouses/xxxxxxxx"
access_token = "dapixxxxxxxx"

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute o sistema
streamlit run app_triagem.py
```

### Execução Alternativa (Windows)
```bash
# Duplo clique no arquivo
iniciar_app.bat
```

### Primeira Execução
O sistema irá automaticamente:
1. Conectar-se ao Databricks e criar a tabela `avicena_care.triagem` se ela não existir.
2. Carregar o modelo de ML treinado.
3. Inicializar os módulos de scores clínicos e abrir o navegador em `http://localhost:8501`.

---

## 📁 Estrutura do Projeto

```
Avicena-Care/
├── app_triagem.py              # Aplicação principal (3214 linhas)
├── ml_predictor.py             # Módulo de predição ML (224 linhas)
├── train_model.py              # Treinamento do modelo (218 linhas)
├── scores_clinicos.py          # Scores clínicos (550+ linhas)
├── validacao_clinica.py        # Validação de segurança (117 linhas)
├── auth.py                     # Autenticação
├── requirements.txt            # Dependências do projeto
├── iniciar_app.bat            # Script de inicialização
├── avicena_auth.db            # Banco de dados (apenas para autenticação de usuários)
├── data/
│   └── Dataset.csv            # Dataset de treino (153MB)
├── models/
│   ├── pcacr_model.pkl        # Modelo treinado
│   └── pcacr_scaler.pkl       # Normalizador
└── README.md                  # Esta documentação
```

---

## 🎓 Guia de Uso

### 1. Login no Sistema
Escolha o perfil de acesso:
- **Enfermagem:** Triagem e gestão da fila
- **Médico:** Acesso completo + análises avançadas

### 2. Cadastro de Paciente

#### Dados Obrigatórios
- Nome completo
- Idade
- Sinais vitais (PA, FC, FR, Temp, SpO2)
- Queixa principal
- Nível de consciência

#### Dados Opcionais
- Comorbidades
- Alergias
- Intensidade de dor (0-10)
- Gênero

#### Após o Cadastro
O sistema exibe automaticamente:
- ✅ Classificação por regras (PCACR)
- 🤖 Predição do ML com confiança
- 🛡️ Validação clínica (se necessário)
- 📊 6 Scores clínicos calculados
- ⚠️ Alertas de risco (sepse, hipoxemia, etc.)

### 3. Gestão da Fila

#### Visualização
- Pacientes ordenados por prioridade
- Tempo máximo de espera por categoria
- Sinais vitais resumidos
- Queixa principal

#### Ações Disponíveis
- 🔄 Reclassificar urgência manualmente
- 🏥 Marcar como atendido
- 📋 Ver histórico completo

### 4. Análise Preditiva (Médicos)

Selecione um paciente para ver:
- 📊 Distribuição de probabilidades (5 classes)
- 🩺 Interpretação clínica dos sinais vitais
- 📈 Importância dos fatores clínicos
- 📊 6 Scores clínicos validados
- 💡 Recomendações baseadas em confiança

### 5. Histórico de Atendimentos

- 📅 Filtro por período (Hoje, Semana, Mês)
- 🔍 Busca por nome
- ↩️ Retornar paciente à fila (se necessário)
- 📊 Estatísticas de atendimento

---

## 🔬 Detalhes Técnicos

### Modelo de Machine Learning

#### Treinamento
```python
# Dados: 50.000 pacientes do Dataset.csv
# Features: 9 variáveis clínicas
# Target: 5 classes de prioridade PCACR
# Método: Random Forest (100 árvores, max_depth=10)
# Validação: 80/20 train/test split
```

#### Performance
- **Acurácia Geral:** 93.85%
- **Precisão Balanceada:** class_weight='balanced'
- **Feature Importance:**
  - Frequência Respiratória: 27.7%
  - PA Sistólica: 16.0%
  - Idade: 15.5%
  - Frequência Cardíaca: 14.9%
  - Saturação O2: 13.3%

#### Explicabilidade
O modelo fornece:
- Probabilidades para cada classe
- Nível de confiança da predição
- Interpretação clínica dos sinais vitais
- Alertas automáticos de desvios

### Validação Clínica

#### Critérios de Sobrescrita
A camada de segurança intervém quando:
1. **Consciência crítica:** GCS ≤8 ou GCS <15 + ML baixo
2. **Sepse:** qSOFA ≥2 (sempre sobrescreve)
3. **Deterioração:** NEWS2 ≥10 + ML muito baixo
4. **Incerteza:** Confiança <40% + regras sugerem urgência

#### Logs e Transparência
Toda sobrescrita gera:
- ⚠️ Alerta visual destacado
- 📝 Motivo clínico detalhado
- 📊 Scores que justificaram a decisão
- 🤖 Predição original do ML (para comparação)

### Banco de Dados

#### Tabela: `avicena_care.triagem` (em Databricks)
```sql
CREATE TABLE avicena_care.triagem (
    id STRING,
    Nome STRING,
    Idade INT,
    PA STRING,
    FC INT,
    FR INT,
    Temp DOUBLE,
    SpO2 INT,
    nivel_consciencia STRING,
    genero STRING,
    intensidade_dor INT,
    Comorbidade STRING,
    Alergia STRING,
    Queixa_Principal STRING,
    urgencia_automatica STRING,
    urgencia_manual STRING,
    status STRING,
    data_cadastro TIMESTAMP,
    data_atendimento TIMESTAMP
)
```

---

## 📊 Interpretação Clínica Automática

### Sinais Vitais - Valores de Referência

#### Frequência Cardíaca
- **Normal:** 60-100 bpm
- **Bradicardia:** <60 bpm (grave <40)
- **Taquicardia:** >100 bpm (grave >120)

#### Pressão Arterial (AHA/ACC 2017)
- **Normal:** <120/80 mmHg
- **Elevada:** 120-129/<80 mmHg
- **HAS Estágio 1:** 130-139/80-89 mmHg
- **HAS Estágio 2:** ≥140/90 mmHg
- **Crise:** ≥180/120 mmHg

#### Temperatura
- **Normal:** 36.0-37.4°C
- **Febrícula:** 37.5-37.9°C
- **Febre:** 38.0-39.0°C
- **Febre Alta:** >39.0°C
- **Hipotermia:** <36.0°C

#### Frequência Respiratória
- **Normal:** 12-20 irpm
- **Bradipneia:** <12 irpm (grave <10)
- **Taquipneia:** >20 irpm (grave ≥30)

#### Saturação de O2
- **Normal:** ≥95%
- **Limítrofe:** 92-94%
- **Hipoxemia:** 88-91% (necessita O2)
- **Hipoxemia Severa:** <88% (O2 urgente!)

---

## 🎨 Interface e UX

### Design System
- **Cores PCACR:** Sistema de cores padronizado Manchester
- **Tipografia:** Arial, sans-serif para legibilidade clínica
- **Ícones:** Emojis para rápida identificação visual
- **Responsivo:** Adaptável a tablets e desktops

### Acessibilidade
- Alto contraste para ambientes hospitalares
- Feedback visual imediato em todas as ações
- Mensagens de erro claras e acionáveis
- Interface intuitiva para profissionais sob pressão

---

## 🔧 Configuração Avançada

### Customizar Thresholds de Validação

Edite `validacao_clinica.py`:

```python
# Exemplo: Tornar validação mais conservadora
elif news2 >= 8 and ml_class in ['BAIXA PRIORIDADE', 'MÍNIMA (ELETIVA)']:
    should_override = True
    new_classification = "ALTA PRIORIDADE"
```

### Retreinar o Modelo

```bash
# Com seus próprios dados
python train_model.py

# O sistema criará novos arquivos:
# - models/pcacr_model.pkl
# - models/scaler.pkl
```

### Ajustar Scores Clínicos

Edite `scores_clinicos.py` para modificar critérios ou adicionar novos scores.

---

## 🐛 Solução de Problemas

### Erro: "Modelo ML não disponível"
```bash
# Treinar o modelo
python train_model.py
```

### Erro: "Módulo não encontrado"
```bash
# Reinstalar dependências
pip install --upgrade -r requirements.txt
```

### Erro: "Porta 8501 em uso"
```bash
# Usar porta alternativa
streamlit run app_triagem.py --server.port 8502
```

### Banco de dados corrompido
```bash
# Deletar e reiniciar
del avicena_auth.db
streamlit run app_triagem.py
```

---

## 📈 Roadmap Futuro

- [ ] Integração com PACS/RIS
- [ ] API REST para integração com outros sistemas
- [ ] App mobile para enfermeiros
- [ ] Suporte multi-idioma
- [ ] Dashboard administrativo
- [ ] Exportação de relatórios (PDF/Excel)
- [ ] Integração com prontuário eletrônico
- [ ] Notificações push para médicos

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

### Áreas para Contribuição
- 🐛 Correção de bugs
- ✨ Novas features
- 📝 Melhorias na documentação
- 🎨 Aprimoramentos de UI/UX
- 🔬 Validação clínica adicional
- 🧪 Testes unitários

---

## 📄 Licença

Este projeto é de código aberto para fins educacionais e de saúde. Sinta-se livre para usar, modificar e distribuir, mantendo os créditos originais.

**⚠️ IMPORTANTE:** Este sistema é uma ferramenta de apoio à decisão clínica. A avaliação e decisão final sempre devem ser realizadas por profissional de saúde habilitado.

---

## 🏆 Agradecimentos

- **Protocolo Manchester** - Inspiração para classificação PCACR
- **NEWS2** - Royal College of Physicians
- **Glasgow Coma Scale** - Universidade de Glasgow
- **Comunidade Python** - Bibliotecas e ferramentas
- **Streamlit** - Framework web incrível

---

## 📞 Contato e Suporte

Para dúvidas, sugestões ou reportar problemas:
- 📧 Email: [seu-email]
- 🐛 Issues: [GitHub Issues]
- 💬 Discussões: [GitHub Discussions]

---

## 📊 Estatísticas do Projeto

- **Linhas de Código:** ~5.000+
- **Módulos:** 6 principais
- **Scores Clínicos:** 6 validados
- **Acurácia ML:** 93.85%
- **Dataset:** 50.000 pacientes
- **Tempo de Desenvolvimento:** Novembro 2025

---

**Desenvolvido com ❤️ para salvar vidas através da tecnologia**

🏥 **Avicena Care** - Triagem Inteligente, Atendimento Eficiente