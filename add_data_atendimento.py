#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para adicionar coluna de data de atendimento"""

import sqlite3

# Conectar ao banco
conn = sqlite3.connect('avicena_auth.db')
cursor = conn.cursor()

# Adicionar coluna data_atendimento
try:
    cursor.execute('ALTER TABLE triagem ADD COLUMN data_atendimento TIMESTAMP')
    print("✅ Coluna data_atendimento adicionada")
except sqlite3.OperationalError as e:
    print(f"⚠️ data_atendimento: {e}")

conn.commit()
conn.close()

print("\n✅ Migração concluída!")
