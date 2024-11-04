# setup_db.py
import hashlib
import sqlite3
import os

# Eliminar la base de datos existente si existe
if os.path.exists('usuarios.db'):
    os.remove('usuarios.db')

conexion = sqlite3.connect('usuarios.db')
cursor = conexion.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    cedula TEXT UNIQUE NOT NULL CHECK(length(cedula) BETWEEN 8 AND 10),
    correo TEXT UNIQUE NOT NULL,
    numero_celular TEXT NOT NULL,
    direccion TEXT NOT NULL,
    contrasena TEXT NOT NULL,
    rol TEXT NOT NULL DEFAULT 'usuario' CHECK(rol IN ('usuario', 'admin'))
)
''')

# Opcionalmente, crear un usuario admin por defecto
cursor.execute('''
INSERT OR IGNORE INTO usuarios (nombre, apellido, cedula, correo, numero_celular, direccion, contrasena, rol)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', ('admin', 'admin', '12345678', 'admin@example.com', '123456789', 'Admin Address', 
      hashlib.sha256('admin123'.encode()).hexdigest(), 'admin'))

conexion.commit()
conexion.close()