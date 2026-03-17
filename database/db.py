import sqlite3
import json
from datetime import datetime

DB_PATH = "hosting.db"

def init_db():
    """Создает таблицы, если их нет"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS instances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            type TEXT,  -- 'vm' или 'container'
            os TEXT,
            cpu INTEGER,
            ram INTEGER,
            disk INTEGER,
            status TEXT,  -- 'running', 'stopped', 'expired'
            created_at TIMESTAMP,
            expires_at TIMESTAMP,
            pid INTEGER,  -- для QEMU процессов
            container_id TEXT,  -- для Docker
            ssh_port INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()
    print("База данных инициализирована")

def add_instance(data):
    """Добавляет запись о новой ВМ/контейнере"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO instances 
        (name, type, os, cpu, ram, disk, status, created_at, expires_at, pid, container_id, ssh_port)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('name'),
        data.get('type'),
        data.get('os'),
        data.get('cpu'),
        data.get('ram'),
        data.get('disk'),
        'running',
        datetime.now(),
        data.get('expires_at'),
        data.get('pid'),
        data.get('container_id'),
        data.get('ssh_port')
    ))
    
    instance_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return instance_id

def get_instance_by_id(instance_id):
    """Получает один инстанс по ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM instances WHERE id = ?", (instance_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def get_all_instances():
    """Получает список всех инстансов"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM instances ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_instance_status(instance_id, status):
    """Обновляет статус"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE instances SET status = ? WHERE id = ?", (status, instance_id))
    conn.commit()
    conn.close()

def delete_instance(instance_id):
    """Удаляет запись"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM instances WHERE id = ?", (instance_id,))
    conn.commit()
    conn.close()