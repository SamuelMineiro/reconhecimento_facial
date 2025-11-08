from flask import Flask, render_template, request, redirect, jsonify, url_for
import sqlite3, os, base64
from PIL import Image
from io import BytesIO
import numpy as np
import face_recognition
from werkzeug.utils import secure_filename
from urllib.parse import quote, unquote
from datetime import datetime
import re


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/imagens'

# Rota principal
@app.route('/')
def principal():
    return render_template('principal.html')

# Verificação facial manual
@app.route('/verificar', methods=['POST'])
def verificar():
    print("🔍 Recebendo imagem para verificação facial...")

    data = request.get_json()
    imagem_base64 = data['imagem'].split(',')[1]
    imagem_bytes = base64.b64decode(imagem_base64)

    try:
        imagem = Image.open(BytesIO(imagem_bytes)).convert('RGB')
        imagem.save("debug_recebida.png")  # salva para inspeção
        imagem_np = np.array(imagem.resize((320, 240)))  # resolução ajustada
    except Exception as e:
        print(f"❌ Erro ao processar imagem recebida: {e}")
        return jsonify({'mensagem': 'Erro ao processar imagem. Tente novamente.'})

    rosto_desconhecido = face_recognition.face_encodings(imagem_np)
    print(f"👀 Número de rostos detectados: {len(rosto_desconhecido)}")

    if not rosto_desconhecido:
        print("⚠️ Nenhum rosto detectado na imagem.")
        return jsonify({'mensagem': 'Nenhum rosto foi detectado. Certifique-se de estar em frente à câmera com boa iluminação.'})

    rosto_desconhecido = rosto_desconhecido[0]

    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    cursor.execute('SELECT nome, cargo, nivel_acesso, imagem FROM funcionarios')
    funcionarios = cursor.fetchall()
    conn.close()

    for nome, cargo, nivel, imagem_nome in funcionarios:
        try:
            print(f"🔄 Comparando com: {nome}")
            caminho = os.path.join(app.config['UPLOAD_FOLDER'], imagem_nome)
            if not os.path.exists(caminho):
                print(f"⚠️ Imagem não encontrada: {caminho}")
                continue

            imagem_conhecida = face_recognition.load_image_file(caminho)
            encodings = face_recognition.face_encodings(imagem_conhecida)

            if not encodings:
                print(f"⚠️ Nenhum encoding encontrado para {nome}.")
                continue

            if face_recognition.compare_faces([encodings[0]], rosto_desconhecido, tolerance=0.49)[0]:
                
                # Registro da tentativa bem-sucedida
                conn = sqlite3.connect('banco.db')
                cursor = conn.cursor()
                cursor.execute('SELECT id FROM funcionarios WHERE nome = ?', (nome,))
                resultado = cursor.fetchone()
                id_funcionario = resultado[0] if resultado else None

                cursor.execute('INSERT INTO acessos (funcionario_id, data_hora, sucesso) VALUES (?, ?, ?)',
                            (id_funcionario, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 1))
                conn.commit()
                conn.close()

                print(f"✅ Rosto reconhecido: {nome}")
                nome_url = quote(nome)
                cargo_url = quote(cargo)
                nivel_url = quote(nivel)
                imagem_url = quote(imagem_nome)

                return jsonify({
                    'redirect': f'/acesso/{nome_url}/{cargo_url}/{nivel_url}/{imagem_url}'
                })
            else:
                print(f"❌ Rosto não reconhecido: {nome}")
        except Exception as e:
            print(f"❌ Erro ao comparar rosto de {nome}: {e}")
            continue
        
    # Registro da tentativa fracassada
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO acessos (funcionario_id, data_hora, sucesso) VALUES (?, ?, ?)',
                (None, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 0))
    conn.commit()
    conn.close()

    print("❌ Nenhum rosto reconhecido.")
    return jsonify({'mensagem': 'Rosto não reconhecido. Verifique se está cadastrado corretamente ou tente novamente com melhor enquadramento.'})

# tela de segurança p/ cadastro
@app.route('/seguranca', methods=['GET', 'POST'])
def seguranca():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']

        if usuario == 'admin' and senha == '1234':
            return redirect('/cadastro')
        else:
            erro = 'Usuário ou senha incorretos.'
            return render_template('seguranca.html', erro=erro)

    return render_template('seguranca.html')

# Tela de acesso
@app.route('/acesso/<nome>/<cargo>/<nivel>/<imagem>')
def acesso(nome, cargo, nivel, imagem):
    nome = unquote(nome)
    cargo = unquote(cargo)
    nivel = unquote(nivel)
    imagem = unquote(imagem)

    # Extrai o número do nível usando regex
    match = re.search(r'Nivel\s*([1-3])', nivel)
    nivel_num = int(match.group(1)) if match else 0

    # Define os níveis permitidos
    niveis_permitidos = tuple(i for i in range(1, nivel_num + 1))

    # Conecta ao banco
    conn = sqlite3.connect('toxinas.db')
    cursor = conn.cursor()

    # Consulta filtrada
    query = f"""
        SELECT nome, tipo, descricao, fonte, efeitos_saude, via_exposicao,
               quantidade, estado_fisico, data_registro, nivel_acesso
        FROM toxinas
        WHERE nivel_acesso IN ({','.join(['?'] * len(niveis_permitidos))})
    """
    cursor.execute(query, niveis_permitidos)
    resultados = cursor.fetchall()
    conn.close()

    # Formata os dados
    toxinas_formatadas = []
    for r in resultados:
        toxinas_formatadas.append({
            'nome': r[0],
            'tipo': r[1],
            'descricao': r[2],
            'fonte': r[3],
            'efeitos_saude': r[4],
            'via_exposicao': r[5],
            'quantidade': r[6],
            'estado_fisico': r[7],
            'data_registro': r[8],
            'nivel_acesso': r[9]
        })

    return render_template('acesso.html',
                           nome=nome,
                           cargo=cargo,
                           nivel=nivel,
                           imagem=imagem,
                           toxinas=toxinas_formatadas)

# tela de cadastro
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        nome = request.form['nome'].upper()
        cargo = request.form['cargo']
        nivel = request.form['nivel']
        imagem = request.files['imagem']

        filename = secure_filename(imagem.filename)
        imagem.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        cursor.execute('INSERT INTO funcionarios (nome, cargo, nivel_acesso, imagem) VALUES (?, ?, ?, ?)',
                       (nome, cargo, nivel, filename))
        conn.commit()

    cursor.execute('SELECT id, nome, cargo, nivel_acesso FROM funcionarios')
    funcionarios = cursor.fetchall()
    conn.close()

    return render_template('cadastro.html', funcionarios=funcionarios)

# funcionalidade de editar
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        nome = request.form['nome'].upper()
        cargo = request.form['cargo']
        nivel = request.form['nivel']
        imagem = request.files.get('imagem')

        if imagem and imagem.filename != '':
            filename = secure_filename(imagem.filename)
            imagem.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cursor.execute('UPDATE funcionarios SET nome=?, cargo=?, nivel_acesso=?, imagem=? WHERE id=?',
                           (nome, cargo, nivel, filename, id))
        else:
            cursor.execute('UPDATE funcionarios SET nome=?, cargo=?, nivel_acesso=? WHERE id=?',
                           (nome, cargo, nivel, id))

        conn.commit()
        conn.close()
        return redirect('/cadastro')

    cursor.execute('SELECT nome, cargo, nivel_acesso FROM funcionarios WHERE id=?', (id,))
    funcionario = cursor.fetchone()
    conn.close()
    return render_template('editar.html', funcionario=funcionario, id=id)

# funcionalidade de excluir
@app.route('/excluir/<int:id>')
def excluir(id):
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM funcionarios WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect('/cadastro')

# tela de seguranca-relatorios 
@app.route('/seguranca-relatorios', methods=['GET', 'POST'])
def seguranca_relatorios():
    erro = None
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        
        # Verificação
        if usuario == 'admin' and senha == '1234':
            return redirect(url_for('relatorios'))
        else:
            erro = 'Usuário ou senha incorretos.'

    return render_template('seguranca_relatorios.html', erro=erro)

# tela de relatorios 
@app.route('/relatorios')
def relatorios():
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()

    # Total de usuários
    cursor.execute('SELECT COUNT(*) FROM funcionarios')
    total_usuarios = cursor.fetchone()[0]

    # Tentativas de acesso
    cursor.execute('SELECT COUNT(*) FROM acessos')
    total_tentativas = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM acessos WHERE sucesso = 1")
    tentativas_sucesso = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM acessos WHERE sucesso = 0")
    tentativas_falha = cursor.fetchone()[0]

    # Distribuição por nível
    cursor.execute("SELECT COUNT(*) FROM funcionarios WHERE nivel_acesso LIKE 'Nivel 1%'")
    nivel1 = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM funcionarios WHERE nivel_acesso LIKE 'Nivel 2%'")
    nivel2 = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM funcionarios WHERE nivel_acesso LIKE 'Nivel 3%'")
    nivel3 = cursor.fetchone()[0]

    # Últimas tentativas
    cursor.execute("""
        SELECT data_hora, sucesso, nome, nivel_acesso
        FROM acessos
        LEFT JOIN funcionarios ON acessos.funcionario_id = funcionarios.id
        ORDER BY data_hora DESC
        LIMIT 10
    """)
    ultimos_acessos = cursor.fetchall()

    conn.close()

    return render_template('relatorios.html',
                           total_usuarios=total_usuarios,
                           total_tentativas=total_tentativas,
                           tentativas_sucesso=tentativas_sucesso,
                           tentativas_falha=tentativas_falha,
                           nivel1=nivel1,
                           nivel2=nivel2,
                           nivel3=nivel3,
                           ultimos_acessos=ultimos_acessos)

# Inicializa banco de dados
def init_db():
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()

    # Tabela de funcionários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS funcionarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cargo TEXT NOT NULL,
            nivel_acesso TEXT NOT NULL,
            imagem TEXT NOT NULL
        )
    ''')

    # Tabela de tentativas de acesso
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS acessos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            funcionario_id INTEGER,
            data_hora TEXT NOT NULL,
            sucesso INTEGER NOT NULL,
            FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id)
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)