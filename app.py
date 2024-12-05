#--------------------------------------------------
# 1-CONFIGURAÇÃO DO BANCO DE DADOS

import sqlite3

# Criar ou conectar ao banco de dados
conn = sqlite3.connect('auriculoterapia.db')
cursor = conn.cursor()

# Tabela de sintomas e padrões de MTC
cursor.execute('''
CREATE TABLE IF NOT EXISTS sintomas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sintoma TEXT NOT NULL,
    padrao_mtc TEXT NOT NULL
)
''')

# Tabela de padrões de MTC e pontos auriculares
cursor.execute('''
CREATE TABLE IF NOT EXISTS padroes_mtc (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    padrao TEXT NOT NULL,
    ponto_auricular TEXT NOT NULL
)
''')

# Tabela de pontos auriculares e funções
cursor.execute('''
CREATE TABLE IF NOT EXISTS pontos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ponto TEXT NOT NULL,
    funcao TEXT NOT NULL
)
''')

print("Banco de dados configurado com sucesso!")

# Fechar conexão
conn.commit()
conn.close()

#-------------------------------------------------------
# 2- INSERIR DADOS

# Inserir dados no banco de dados
def inserir_dados_iniciais():
    conn = sqlite3.connect('auriculoterapia.db')
    cursor = conn.cursor()

    # Sintomas e padrões
    sintomas = [
        ('Dor de cabeça', 'Estagnação de Qi do Fígado'),
        ('Falta de apetite', 'Deficiência de Qi do Baço'),
        ('Tontura', 'Deficiência de Sangue do Fígado'),
        # Adicione mais sintomas aqui
    ]
    cursor.executemany('INSERT INTO sintomas (sintoma, padrao_mtc) VALUES (?, ?)', sintomas)

    # Padrões e pontos
    padroes = [
        ('Deficiência de Sangue do Fígado', 'Fígado'),
        ('Estagnação de Qi do Fígado', 'Vesícula Biliar'),
        ('Deficiência de Qi do Baço', 'Estômago'),
        # Adicione mais padrões e pontos aqui
    ]
    cursor.executemany('INSERT INTO padroes_mtc (padrao, ponto_auricular) VALUES (?, ?)', padroes)

    # Pontos e funções
    pontos = [
        ('Estômago', 'Ajuda na digestão e melhora o apetite.'),
        ('Vesícula Biliar', 'Reduz a dor de cabeça e alivia a raiva.'),
        # Adicione mais pontos e funções aqui
    ]
    cursor.executemany('INSERT INTO pontos (ponto, funcao) VALUES (?, ?)', pontos)

    conn.commit()
    conn.close()
    print("Dados iniciais inseridos com sucesso!")


#--------------------------------------------------------------------
# 3-FORMULARIO DE ENTRADA E DIAGNOSTICO

def diagnosticar():
    conn = sqlite3.connect('auriculoterapia.db')
    cursor = conn.cursor()

    # Entrada de sintomas
    print("Preencha o formulário com os sintomas do paciente.")
    sintomas_informados = input("Digite os sintomas separados por vírgula: ").split(',')

    # Diagnóstico
    diagnostico = {}
    for sintoma in sintomas_informados:
        sintoma = sintoma.strip()
        cursor.execute('SELECT padrao_mtc FROM sintomas WHERE sintoma = ?', (sintoma,))
        padrao = cursor.fetchone()
        if padrao:
            padrao = padrao[0]
            cursor.execute('SELECT ponto_auricular FROM padroes_mtc WHERE padrao = ?', (padrao,))
            pontos = cursor.fetchall()
            diagnostico[padrao] = [p[0] for p in pontos]

    # Geração do protocolo
    print("\nDiagnóstico e Protocolo:")
    for padrao, pontos in diagnostico.items():
        print(f"\nPadrão de MTC: {padrao}")
        for ponto in pontos:
            cursor.execute('SELECT funcao FROM pontos WHERE ponto = ?', (ponto,))
            funcao = cursor.fetchone()[0]
            print(f" - Ponto: {ponto} | Função: {funcao}")

    conn.close()

# Executar o diagnóstico
diagnosticar()

#-------------------------------------------------------------
# 4-IMPLEMENTAR O BACKEND

from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# Rota principal - Exibe o formulário de anamnese
@app.route('/')
def index():
    return render_template('index.html')

# Rota para processar o diagnóstico
@app.route('/diagnostico', methods=['POST'])
def diagnostico():
    # Obter sintomas do formulário
    sintomas_informados = request.form.get('sintomas').split(',')

    # Conectar ao banco de dados
    conn = sqlite3.connect('auriculoterapia.db')
    cursor = conn.cursor()

    # Diagnóstico
    diagnostico = {}
    for sintoma in sintomas_informados:
        sintoma = sintoma.strip()
        cursor.execute('SELECT padrao_mtc FROM sintomas WHERE sintoma = ?', (sintoma,))
        padrao = cursor.fetchone()
        if padrao:
            padrao = padrao[0]
            cursor.execute('SELECT ponto_auricular FROM padroes_mtc WHERE padrao = ?', (padrao,))
            pontos = cursor.fetchall()
            diagnostico[padrao] = [p[0] for p in pontos]

    # Montar o protocolo
    protocolo = []
    for padrao, pontos in diagnostico.items():
        for ponto in pontos:
            cursor.execute('SELECT funcao FROM pontos WHERE ponto = ?', (ponto,))
            funcao = cursor.fetchone()[0]
            protocolo.append({'padrao': padrao, 'ponto': ponto, 'funcao': funcao})

    conn.close()
    return render_template('resultado.html', protocolo=protocolo)

if __name__ == '__main__':
    app.run(debug=True)

#-------------------------------------------------------------------
# 5- SALVAR HISTÓRICO DO PACIENTE - ARMAZENA PACIENTES E SEUS DIAGNOSTICO

cursor.execute('''
CREATE TABLE IF NOT EXISTS pacientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    sintomas TEXT NOT NULL,
    protocolo TEXT NOT NULL,
    data TEXT DEFAULT CURRENT_TIMESTAMP
)
''')

#--------------------------------------------------------------------
# 6-SALVAMENTO DOS DADOS NO DIAGNOSTICO

@app.route('/diagnostico', methods=['POST'])
def diagnostico():
    # Obter nome do paciente e sintomas do formulário
    nome_paciente = request.form.get('nome')
    sintomas_informados = request.form.get('sintomas').split(',')

    # (O código de diagnóstico permanece igual)
    # ...
    protocolo_formatado = "; ".join([f"{item['ponto']} - {item['funcao']}" for item in protocolo])

    # Salvar no banco de dados
    cursor.execute(
        'INSERT INTO pacientes (nome, sintomas, protocolo) VALUES (?, ?, ?)',
        (nome_paciente, ", ".join(sintomas_informados), protocolo_formatado)
    )
    conn.commit()
    conn.close()

    return render_template('resultado.html', protocolo=protocolo)


