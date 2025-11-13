#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para atualizar paciente Leli com dados corretos"""

import sqlite3

# Conectar ao banco
conn = sqlite3.connect('avicena_auth.db')
cursor = conn.cursor()

# Atualizar paciente Leli
cursor.execute('''
    UPDATE triagem 
    SET SpO2 = 96,
        nivel_consciencia = 'Sonolento',
        genero = 'Feminino',
        intensidade_dor = 5
    WHERE Nome = 'Leli'
''')

conn.commit()

# Verificar
cursor.execute('SELECT Nome, Idade, nivel_consciencia, SpO2, genero FROM triagem WHERE Nome = "Leli"')
result = cursor.fetchone()

if result:
    print(f"✅ Paciente atualizado:")
    print(f"   Nome: {result[0]}")
    print(f"   Idade: {result[1]}")
    print(f"   Consciência: {result[2]}")
    print(f"   SpO2: {result[3]}%")
    print(f"   Gênero: {result[4]}")
else:
    print("❌ Paciente Leli não encontrado")

conn.close()
