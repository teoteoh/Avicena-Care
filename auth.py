# auth.py - Sistema de Autenticação para Avicena Care
# Desenvolvido para controle de acesso de médicos e enfermeiros
# Versão: 1.0 - 2025

import sqlite3
import hashlib
import secrets
from datetime import datetime
import streamlit as st

class AuthSystem:
    """Sistema de autenticação com controle de acesso por perfil"""
    
    # PINs padrão por tipo de profissional
    DEFAULT_PINS = {
        'medico': 'Med123',
        'enfermeiro': 'Enf123'
    }
    
    # Senhas padrão por tipo de profissional
    DEFAULT_PASSWORDS = {
        'medico': 'medico123',
        'enfermeiro': 'enfermeiro123'
    }
    
    # Lista de usuários padrão
    DEFAULT_USERS = [
        ('medico1', 'medico123', 'Dr. Carlos Silva', 'medico', 'CRM 12345'),
        ('medico2', 'medico123', 'Dra. Ana Santos', 'medico', 'CRM 23456'),
        ('medico3', 'medico123', 'Dr. João Oliveira', 'medico', 'CRM 34567'),
        ('enfermeiro1', 'enfermeiro123', 'Enf. Maria Lima', 'enfermeiro', 'COREN 45678'),
        ('enfermeiro2', 'enfermeiro123', 'Enf. Pedro Costa', 'enfermeiro', 'COREN 56789'),
        ('enfermeiro3', 'enfermeiro123', 'Enf. Julia Ferreira', 'enfermeiro', 'COREN 67890')
    ]
    
    def __init__(self, db_path="avicena_auth.db"):
        """Inicializa o sistema de autenticação"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa o banco de dados de autenticação"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                nome TEXT NOT NULL,
                tipo TEXT NOT NULL,
                registro_profissional TEXT,
                ativo INTEGER DEFAULT 1,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ultimo_acesso TIMESTAMP
            )
        ''')
        
        # Criar usuários padrão se a tabela estiver vazia
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        if cursor.fetchone()[0] == 0:
            for username, senha, nome, tipo, registro in self.DEFAULT_USERS:
                password_hash = hashlib.sha256(senha.encode()).hexdigest()
                user_id = secrets.token_hex(16)
                cursor.execute('''
                    INSERT INTO usuarios (id, username, password_hash, nome, tipo, registro_profissional)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, username, password_hash, nome, tipo, registro))
        
        conn.commit()
        conn.close()
    
    def authenticate(self, username, password, pin=None):
        """Autentica um usuário com base no username e senha."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, password_hash, nome, tipo, registro_profissional
            FROM usuarios
            WHERE username = ? AND ativo = 1
        """, (username,)) # type: ignore
        
        user = cursor.fetchone()
        if not user:
            conn.close()
            return None

        # Validar senha
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if password_hash != user[2]:
            conn.close()
            return None
            
        # Atualiza último acesso
        cursor.execute("""
            UPDATE usuarios
            SET ultimo_acesso = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (user[0],)) # type: ignore
        
        conn.commit()
        conn.close()
        
        return {
            'id': user[0],
            'username': user[1],
            'nome': user[3],
            'tipo': user[4],
            'registro': user[5]
        }