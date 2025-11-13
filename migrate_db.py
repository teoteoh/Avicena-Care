#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para adicionar colunas ao banco de dados"""

import sqlite3

# Conectar ao banco
conn = sqlite3.connect('avicena_auth.db')
cursor = conn.cursor()

# Adicionar novas colunas
try:
    cursor.execute('ALTER TABLE triagem ADD COLUMN SpO2 INTEGER DEFAULT 95')
    print("✅ Coluna SpO2 adicionada")
except sqlite3.OperationalError as e:
    print(f"⚠️ SpO2: {e}")

try:
    cursor.execute('ALTER TABLE triagem ADD COLUMN nivel_consciencia TEXT DEFAULT "Alerta"')
    print("✅ Coluna nivel_consciencia adicionada")
except sqlite3.OperationalError as e:
    print(f"⚠️ nivel_consciencia: {e}")

try:
    cursor.execute('ALTER TABLE triagem ADD COLUMN genero TEXT DEFAULT "Feminino"')
    print("✅ Coluna genero adicionada")
except sqlite3.OperationalError as e:
    print(f"⚠️ genero: {e}")

try:
    cursor.execute('ALTER TABLE triagem ADD COLUMN intensidade_dor INTEGER DEFAULT 0')
    print("✅ Coluna intensidade_dor adicionada")
except sqlite3.OperationalError as e:
    print(f"⚠️ intensidade_dor: {e}")

conn.commit()
conn.close()

print("\n✅ Migração concluída!")
