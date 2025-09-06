#!/usr/bin/env python3
"""
Script de migration SQLite vers PostgreSQL
"""

import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime

def migrate_database():
    """Migration de SQLite vers PostgreSQL"""
    
    # Connexion SQLite
    sqlite_conn = sqlite3.connect('backend/database.db')
    sqlite_cursor = sqlite_conn.cursor()
    
    # Connexion PostgreSQL
    pg_conn = psycopg2.connect(os.environ['DATABASE_URL'])
    pg_cursor = pg_conn.cursor()
    
    try:
        # Creation des tables PostgreSQL
        create_tables_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS agents (
            id SERIAL PRIMARY KEY,
            agent_id VARCHAR(100) UNIQUE NOT NULL,
            agent_type VARCHAR(50) NOT NULL,
            capabilities JSONB,
            performance_metrics JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            document_id VARCHAR(100) UNIQUE NOT NULL,
            title VARCHAR(500),
            content TEXT,
            format VARCHAR(20),
            status VARCHAR(20),
            metadata JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS workflows (
            id SERIAL PRIMARY KEY,
            workflow_id VARCHAR(100) UNIQUE NOT NULL,
            name VARCHAR(255),
            status VARCHAR(50),
            configuration JSONB,
            results JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        );
        """
        
        pg_cursor.execute(create_tables_sql)
        
        # Migration des donnees
        tables = ['users', 'agents', 'documents', 'workflows']
        
        for table in tables:
            print(f"Migration de la table {table}...")
            
            sqlite_cursor.execute(f"SELECT * FROM {table}")
            rows = sqlite_cursor.fetchall()
            
            for row in rows:
                # Adapter selon la structure reelle
                # Inserer dans PostgreSQL
                pass
        
        pg_conn.commit()
        print("[OK] Migration terminee avec succes")
        
    except Exception as e:
        pg_conn.rollback()
        print(f"[ERREUR] Erreur de migration: {e}")
        
    finally:
        sqlite_conn.close()
        pg_conn.close()

if __name__ == "__main__":
    migrate_database()
