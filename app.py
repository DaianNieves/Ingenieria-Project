import bcrypt
from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.security import check_password_hash
from config import Config
import mysql.connector
from functools import wraps

app = Flask(__name__, template_folder='Templates')
app.config.from_object(Config)

# Conexión a la base de datos
def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='sistema_citas',
        port=3306
    )

# Decorador para proteger las rutas que requieren roles
def login_required(rol):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('rol') != rol:
                flash('Acceso denegado. No tienes permisos.', 'error')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return wrapper

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login_admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password']

        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE correo = %s AND rol = 'administrador'", (correo,))
            admin = cursor.fetchone()

            if admin and bcrypt.checkpw(password.encode('utf-8'), admin['contraseña'].encode('utf-8')):
                session['rol'] = 'administrador'
                session['nombre'] = admin['nombre']
                session['usuario_id'] = admin['id']
                return redirect(url_for('panel_admin'))
            else:
                flash('Correo o contraseña incorrectos', 'error')
        except mysql.connector.Error as e:
            flash(f'Error al conectar con la base de datos: {e}', 'error')
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()

    return render_template('Administrador/login_administrador.html')

@app.route('/login/dentista', methods=['GET', 'POST'])
def login_doctor():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password']

        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE correo = %s AND rol = 'doctor'", (correo,))
            doctor = cursor.fetchone()

            if doctor and bcrypt.checkpw(password.encode('utf-8'), doctor['contraseña'].encode('utf-8')):
                session['rol'] = 'doctor'
                session['nombre'] = doctor['nombre']
                session['usuario_id'] = doctor['id']
                return redirect(url_for('panel_doctor')) 
            else:
                flash('Correo o contraseña incorrectos', 'error')
        except mysql.connector.Error as e:
            flash(f'Error al conectar con la base de datos: {e}', 'error')
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()

    return render_template('Dentista/login_dentista.html')

@app.route('/panel/administrador')
@login_required('administrador')
def panel_admin():
    return render_template('Administrador/panel_admin.html')

@app.route('/panel/dentista')
@login_required('doctor')
def panel_doctor():
    return render_template('Dentista/panel_dentista.html')

@app.route('/tratamientos/registrar/<int:cita_id>', methods=['GET', 'POST'])
@login_required('doctor')
def registrar_tratamiento(cita_id):
    if request.method == 'POST':
        diagnostico = request.form['diagnostico']
        tratamiento = request.form['tratamiento']
        observaciones = request.form['observaciones']

        try:
            conn = get_connection()
            cursor = conn.cursor()
            query = """
                INSERT INTO tratamientos (cita_id, diagnostico, tratamiento_aplicado, observaciones)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (cita_id, diagnostico, tratamiento, observaciones))
            conn.commit()
            flash('✅ Tratamiento registrado con éxito.', 'success')
            return redirect(url_for('panel_doctor'))
        except mysql.connector.Error as e:
            flash(f'❌ Error al registrar tratamiento: {e}', 'error')
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()

    return render_template('Dentista/registrar_tratamiento.html', cita_id=cita_id)

@app.route('/panel/administrador/doctores')
@login_required('administrador')
def panel_admin_doc():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT d.id, u.nombre, u.correo, d.especialidad, d.telefono, d.fecha_registro
            FROM doctores d
            JOIN usuarios u ON d.usuario_id = u.id
            WHERE u.rol = 'doctor'
        """
        cursor.execute(query)
        doctores = cursor.fetchall()
    except mysql.connector.Error as e:
        flash(f'Error al obtener doctores: {e}', 'error')
        doctores = []
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals() and conn.is_connected(): conn.close()

    return render_template('Administrador/panel_admin_doc.html', doctores=doctores)

@app.route('/panel/administrador/doctores/registrar', methods=['GET', 'POST'])
@login_required('administrador')
def registrar_doctor():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        contraseña = request.form['contraseña']
        especialidad = request.form['especialidad']
        telefono = request.form['telefono']

        # Axioma: Validar que el correo no esté registrado
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM usuarios WHERE correo = %s", (correo,))
            if cursor.fetchone():
                flash('❌ El correo ya está registrado.', 'error')
                return redirect(url_for('registrar_doctor'))
        except mysql.connector.Error as e:
            flash(f'❌ Error al verificar el correo: {e}', 'error')
            return redirect(url_for('registrar_doctor'))
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()

        # Axioma: La contraseña debe tener al menos 8 caracteres
        if len(contraseña) < 8:
            flash('❌ La contraseña debe tener al menos 8 caracteres.', 'error')
            return redirect(url_for('registrar_doctor'))

        # Hashear la contraseña
        hashed_password = bcrypt.hashpw(contraseña.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        try:
            conn = get_connection()
            cursor = conn.cursor()

            query_usuario = """
                INSERT INTO usuarios (nombre, correo, contraseña, rol)
                VALUES (%s, %s, %s, 'doctor')
            """
            cursor.execute(query_usuario, (nombre, correo, hashed_password))
            usuario_id = cursor.lastrowid

            query_doctor = """
                INSERT INTO doctores (usuario_id, especialidad, telefono, fecha_registro)
                VALUES (%s, %s, %s, NOW())
            """
            cursor.execute(query_doctor, (usuario_id, especialidad, telefono))

            conn.commit()
            flash('✅ Doctor registrado correctamente.', 'success')
            return redirect(url_for('panel_admin_doc'))

        except mysql.connector.Error as e:
            flash(f'❌ Error al registrar doctor: {e}', 'error')

        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()

    return render_template('Administrador/registrar_doctor.html')

@app.route('/editar_doctor/<int:id>')
@login_required('administrador')
def editar_doctor(id):
    # Lógica para editar
    ...

@app.route('/eliminar_doctor/<int:id>', methods=['POST'])
@login_required('administrador')
def eliminar_doctor(id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT usuario_id FROM doctores WHERE id = %s", (id,))
        result = cursor.fetchone()

        if not result:
            flash('❌ Doctor no encontrado.', 'error')
            return redirect(url_for('panel_admin_doc'))

        usuario_id = result[0]
        cursor.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))
        conn.commit()

        flash('✅ Doctor eliminado correctamente.', 'success')

    except mysql.connector.Error as e:
        flash(f'❌ Error al eliminar doctor: {e}', 'error')

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals() and conn.is_connected(): conn.close()

    return redirect(url_for('panel_admin_doc'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)