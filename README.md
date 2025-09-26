# 🏥 Avicena Care - Sistema de Triagem Médica

Sistema inteligente de triagem médica desenvolvido em Python com Streamlit para monitoramento em tempo real, alertas automáticos e gestão eficiente de pacientes.

## 📁 Estrutura do Projeto

```
Avicena Care/
├── app_triagem.py          # Aplicação principal
├── styles.css              # Estilos CSS separados
├── iniciar_app.bat         # Script de inicialização
├── requirements.txt        # Dependências Python
├── README.md              # Documentação
├── .streamlit/            # Configurações do Streamlit
└── .vscode/               # Configurações do VS Code
```

## 🚀 Funcionalidades

### 📊 Dashboard Interativo
- Gráficos de temperatura em tempo real
- Distribuição de comorbidades e alergias
- Histograma de idades dos pacientes
- Métricas principais automatizadas

### 👥 Gestão de Pacientes
- Lista completa com filtros avançados
- Visualização em tabela ou cards
- Sistema de cores por nível de temperatura
- Busca por nome e múltiplos filtros

### 🌡️ Monitoramento de Febre
- Central específica para pacientes com febre
- Alertas automáticos por níveis de gravidade
- Classificação visual por temperatura
- Estatísticas detalhadas

### ⚕️ Análise de Comorbidades
- Distribuição gráfica de comorbidades
- Análise de alergias conhecidas
- Correlação com temperatura
- Relatórios detalhados

### ➕ Cadastro de Pacientes
- Formulário completo com validação
- Campos condicionais dinâmicos
- Alertas automáticos pós-cadastro
- Dados em tempo real

## 💻 Tecnologias Utilizadas

- **Python 3.8+**
- **Streamlit** - Interface web interativa
- **Pandas** - Manipulação de dados
- **Plotly** - Gráficos interativos
- **SQLite** - Banco de dados em memória
- **CSS3** - Estilização avançada

## 🛠️ Instalação e Uso

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Instalação
1. **Clone ou baixe o projeto** para sua máquina
2. **Navegue até a pasta** do projeto
3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

### Execução
#### Opção 1 - Script Automático (Recomendado)
- Duplo clique no arquivo `iniciar_app.bat`

#### Opção 2 - Linha de Comando
```bash
cd "caminho/para/Avicena Care"
streamlit run app_triagem.py
```

#### Opção 3 - Python Direto
```bash
python -m streamlit run app_triagem.py
```

### Acesso
- Abra seu navegador e acesse: `http://localhost:8501`
- A aplicação abrirá automaticamente

## 🎨 Personalização CSS

O projeto agora utiliza um arquivo CSS separado (`styles.css`) para melhor organização:

### Vantagens da Separação:
- ✅ **Manutenção facilitada** dos estilos
- ✅ **Reutilização** de código CSS
- ✅ **Organização melhorada** do projeto
- ✅ **Performance otimizada** com cache
- ✅ **Colaboração facilitada** entre desenvolvedores

### Estrutura do CSS:
- **Cabeçalhos e layouts** principais
- **Cards e métricas** responsivos
- **Alertas e notificações** visuais
- **Responsividade** para dispositivos móveis
- **Animações suaves** e transições

## 📋 Funcionalidades Detalhadas

### Sistema de Alertas
- 🟢 **Normal**: Temperatura ≤ 37.0°C
- 🟡 **Atenção**: Temperatura 37.1-37.5°C
- 🔴 **Febre**: Temperatura 37.6-39.0°C
- 🔥 **Febre Alta**: Temperatura ≥ 39.0°C

### Validações Automáticas
- Campos obrigatórios marcados com *
- Validação de ranges de valores
- Verificação de consistência de dados
- Campos condicionais para "Outra" opção

### Filtros Avançados
- **Por idade**: Slider de faixa etária
- **Por temperatura**: Range de temperatura
- **Por comorbidade**: Seleção múltipla
- **Por alergia**: Filtro de alergias
- **Por nome**: Busca textual

## 🔧 Configurações

### Streamlit
Arquivo `.streamlit/config.toml`:
```toml
[server]
headless = true
```

### Customização
- Modifique `styles.css` para alterar aparência
- Edite `app_triagem.py` para funcionalidades
- Ajuste `iniciar_app.bat` para configurações de execução

## 📊 Dados de Exemplo

O sistema inclui dados de exemplo para demonstração:
- 8 pacientes com perfis variados
- Diferentes comorbidades e alergias
- Faixas etárias diversas
- Casos de febre e temperatura normal

## 🆘 Solução de Problemas

### Erro de Porta em Uso
```bash
# Matar processos Python
taskkill /f /im python.exe

# Ou usar porta diferente
streamlit run app_triagem.py --server.port 8502
```

### Erro de Dependências
```bash
# Reinstalar dependências
pip install --upgrade -r requirements.txt
```

### CSS não Carregando
- Verifique se `styles.css` está na mesma pasta
- Limpe cache do Streamlit: `Ctrl+F5`

## 📝 Changelog

### Versão 2.0 (Atual)
- ✅ Separação do CSS em arquivo externo
- ✅ Melhoria na organização do código
- ✅ Performance otimizada
- ✅ Campos condicionais funcionais
- ✅ Interface mais responsiva
- ✅ Consolidação em único arquivo principal (`app_triagem.py`) e remoção de variante antiga

### Nota de Consolidação
Anteriormente existia um arquivo alternativo `app_triagem_profissional.py`. Toda a lógica foi integrada e ampliada em `app_triagem.py`. Caso o arquivo antigo volte a surgir (ex: restauração do OneDrive), o próprio app exibirá um aviso destacando que ele pode ser removido com segurança. Apenas mantenha e execute:

```
streamlit run app_triagem.py
```

Se precisar criar uma variação futura, copie `app_triagem.py` e renomeie de forma clara (ex: `app_triagem_experimental.py`).

### Versão 1.0
- ✅ Sistema básico de triagem
- ✅ Dashboard interativo
- ✅ Cadastro de pacientes
- ✅ Alertas de febre

## 🤝 Contribuição

Para contribuir com o projeto:
1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Faça commit das mudanças
4. Abra um Pull Request

## 📄 Licença

Este projeto é de uso livre para fins educacionais e de saúde.

## 👨‍⚕️ Sobre o Avicena Care

Sistema desenvolvido para facilitar o processo de triagem médica, oferecendo uma interface intuitiva e funcionalidades avançadas para profissionais de saúde.

**Desenvolvido com ❤️ para a comunidade médica**