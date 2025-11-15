# 🔐 Sistema de Autenticação com Reconhecimento Facial

## 📘 Descrição do Sistema

Sistema de autenticação desenvolvido em Python utilizando reconhecimento facial para controle de acesso hierárquico a informações sobre toxinas ambientais. A aplicação web oferece diferentes níveis de permissão baseados na identificação facial dos usuários.

---

## 🛠 Tecnologias Utilizadas

- **Backend:** Python Flask  
- **Reconhecimento Facial:** Face Recognition + dlib  
- **Processamento de Imagens:** OpenCV + Pillow  
- **Banco de Dados:** SQLite3  
- **Frontend:** HTML + Jinja2 Templates  

---

## 💻 Requisitos do Sistema

- **Processador:** Intel i3 ou equivalente  
- **Memória RAM:** 4 GB  
- **Armazenamento:** 500 MB livres  
- **Webcam:** Qualquer modelo funcional  
- **Sistema Operacional:** Windows 7+, Ubuntu 16.04+, macOS 10.12+  
- **Python:** Versão 3.8 ou superior (**recomendado: [Python 3.11.9](https://www.python.org/downloads/release/python-3119/)**)  
- **Navegador:** [Google Chrome](https://www.google.com/chrome/), [Mozilla Firefox](https://www.mozilla.org/firefox/), ou [Microsoft Edge](https://www.microsoft.com/edge)  
- **Git (para clonagem):** [Download Git](https://git-scm.com/downloads)  
- **Editor de Código (opcional):** [Visual Studio Code](https://code.visualstudio.com/)  

> ⚠️ **Para usuários Windows:**  
Para instalar `dlib` e `face_recognition`, é necessário instalar o [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/).  
Durante a instalação, selecione:
- "Desenvolvimento para Desktop com C++"
- "Ferramentas de Build do C++ CMake"  
Espaço necessário: ~19 GB

---

## 🚀 Instalação e Execução

> 💡 **Observação importante:**  
> Se o comando `python` não funcionar no seu terminal, tente usar `py` no lugar.  
> Exemplo: `py -m venv venv` em vez de `python -m venv venv`  
>  
> ⚠️ **Importante:** A criação do ambiente virtual e a instalação das bibliotecas (`pip install -r requirements.txt`) devem ser feitas **dentro do terminal do Visual Studio Build Tools**, para garantir a correta instalação do `dlib` e `face_recognition`.  
> Após a instalação das dependências, a execução do sistema pode ser feita normalmente pelo **CMD** ou **PowerShell**.

### 📦 Opção 1: Executando via Arquivo `.zip` (Para o Professor)

> ⚠️ **Importante:** Caso tenha recebido o projeto como arquivo `.zip`, siga este tutorial:

1. **Extraia o conteúdo do `.zip`** para uma pasta local.
2. **Abra o terminal (CMD ou PowerShell)** e navegue até a pasta extraída:
   ```bash
   cd caminho\para\a\pasta\extraída
   ```
3. **Crie o ambiente virtual:**
   ```bash
   python -m venv venv
   ```
4. **Ative o ambiente virtual (Windows):**
   ```bash
   venv\Scripts\activate
   ```
5. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```
6. **Execute o programa:**
   ```bash
   python -u app.py
   ```
7. **Acesse o sistema no navegador:**
   ```
   http://localhost:5000
   ```

---

### 🔁 Opção 2: Clonando o Repositório (Git)

1. **Clonar o repositório:**
   ```bash
   git clone https://github.com/SamuelMineiro/reconhecimento_facial.git
   ```
2. **Entrar na pasta do projeto:**
   ```bash
   cd reconhecimento_facial
   ```
3. **Criar ambiente virtual:**
   ```bash
   python -m venv venv
   ```
4. **Ativar ambiente virtual (Windows):**
   ```bash
   venv\Scripts\activate
   ```
5. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   ```
6. **Executar o programa:**
   ```bash
   python -u app.py
   ```
7. **Acessar o sistema no navegador:**
   ```
   http://localhost:5000
   ```

---

## 🔐 Funcionalidades

### 👤 Usuários Comuns
- Autenticação por reconhecimento facial  
- Visualização de dados conforme nível de acesso  
- Três níveis hierárquicos: Geral, Gerente, Ministro  

### 🛡 Administradores
- Login: `admin`  
- Senha: `1234`  
- Cadastro e edição de funcionários  
- Relatórios de acesso  
- Auditoria do sistema  
- Acesso administrativo completo  

---
