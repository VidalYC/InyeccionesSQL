from flask import Flask, request, render_template, redirect, url_for, session
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = 'NEkPNMHbXoeeLCfYDeRviBGuKYyVQMKO'

def cifrar_contrasena(contrasena):
    return hashlib.sha256(contrasena.encode()).hexdigest()

@app.route('/', methods=['GET', 'POST'])
def login():
    mensaje_error = None

    if request.method == 'POST':
        nombre = request.form['nombre']
        contrasena = request.form['contrasena']
        contrasena_cifrada = cifrar_contrasena(contrasena)

        conexion = sqlite3.connect('usuarios.db')
        cursor = conexion.cursor()
        
        cursor.execute('SELECT id, nombre, rol FROM usuarios WHERE nombre = ? AND contrasena = ?', 
                      (nombre, contrasena_cifrada))
        resultado = cursor.fetchone()
        conexion.close()

        if resultado:
            # Guardar información del usuario en la sesión
            session['usuario_id'] = resultado[0]
            session['nombre'] = resultado[1]
            session['rol'] = resultado[2]
            
            # Redirigir según el rol
            if resultado[2] == 'admin':
                return redirect(url_for('dashboard_admin'))
            else:
                return redirect(url_for('dashboard_usuario'))
        else:
            mensaje_error = "Credenciales incorrectas"

    return render_template('login.html', mensaje_error=mensaje_error)

@app.route('/dashboard/usuario')
def dashboard_usuario():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    usuario_id = session['usuario_id']
    
    conexion = sqlite3.connect('usuarios.db')
    cursor = conexion.cursor()
    
    try:
        # Consulta vulnerable a inyección SQL (para propósitos educativos)
        query = f"SELECT nombre, apellido, cedula, correo, numero_celular, direccion FROM usuarios WHERE id = {usuario_id}"
        cursor.execute(query)
        usuario = cursor.fetchone()
        
        if usuario:
            return render_template('dashboard.html', 
                                   nombre=usuario[0],
                                   apellido=usuario[1],
                                   cedula=usuario[2],
                                   correo=usuario[3],
                                   numero_celular=usuario[4],
                                   direccion=usuario[5])
        else:
            return "Usuario no encontrado", 404
    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
        return "Error al acceder a la información del usuario", 500
    finally:
        conexion.close()
        
@app.route('/dashboard/admin')
def dashboard_admin():
    if 'usuario_id' not in session or session['rol'] != 'admin':
        return redirect(url_for('login'))
        
    conexion = sqlite3.connect('usuarios.db')
    cursor = conexion.cursor()
    
    try:
        # Obtener todos los usuarios
        cursor.execute('SELECT id, nombre, apellido, cedula, correo, numero_celular, direccion, rol FROM usuarios')
        usuarios = cursor.fetchall()
        
        # Agregar print para debugging
        print("Usuarios encontrados:", usuarios)
        
        return render_template('dashAdmin.html', nombre=session['nombre'], usuarios=usuarios)
    except sqlite3.Error as e:
        print("Error en la base de datos:", e)
        return "Error al acceder a la base de datos"
    finally:
        conexion.close()

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        cedula = request.form['cedula']
        correo = request.form['correo']
        numero_celular = request.form['numero_celular']
        direccion = request.form['direccion']
        contrasena = request.form['contrasena']
        contrasena_cifrada = cifrar_contrasena(contrasena)
        rol = 'usuario'  

        if not cedula.isdigit() or not (8 <= len(cedula) <= 10):
            return "Error: La cédula debe ser un número entre 8 y 10 dígitos"

        conexion = sqlite3.connect('usuarios.db')
        cursor = conexion.cursor()

        try:
            # Verificar si el correo ya existe
            cursor.execute('SELECT correo FROM usuarios WHERE correo = ?', (correo,))
            if cursor.fetchone():
                return "Error: El correo electrónico ya está registrado"

            # Verificar si la cédula ya existe
            cursor.execute('SELECT cedula FROM usuarios WHERE cedula = ?', (cedula,))
            if cursor.fetchone():
                return "Error: La cédula ya está registrada"

            # Si no existe, proceder con el registro
            cursor.execute('''
                INSERT INTO usuarios (nombre, apellido, cedula, correo, numero_celular, direccion, contrasena, rol)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (nombre, apellido, cedula, correo, numero_celular, direccion, contrasena_cifrada, rol))

            conexion.commit()
            conexion.close()
            return redirect(url_for('login'))

        except sqlite3.Error as e:
            return f"Error en la base de datos: {str(e)}"
        finally:
            conexion.close()

    return render_template('registro.html')

if __name__ == '__main__':
    app.run(debug=True)