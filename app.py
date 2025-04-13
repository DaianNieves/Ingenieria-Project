import bcrypt
from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.security import check_password_hash
from config import Config
import mysql.connector

app = Flask(__name__, template_folder='Templates')
app.config.from_object(Config)

def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='sistema_citas',
        port=3306
    )

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
            # Buscar en usuarios donde rol sea 'administrador'
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
            # Buscar en usuarios donde el rol sea 'doctor'
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
def panel_admin():
    if session.get('rol') != 'administrador':
        flash('Acceso denegado. Inicia sesión como administrador.', 'error')
        return redirect(url_for('login_admin'))
    return render_template('Administrador/panel_admin.html')

@app.route('/panel/dentista')
def panel_doctor():
    if session.get('rol') != 'doctor':
        flash('Acceso denegado. Inicia sesión como dentista.', 'error')
        return redirect(url_for('login_doctor'))
    return render_template('Dentista/panel_dentista.html')

@app.route('/tratamientos/registrar/<int:cita_id>', methods=['GET', 'POST'])
def registrar_tratamiento(cita_id):
    if session.get('rol') != 'doctor':
        flash('Acceso restringido a doctores.', 'error')
        return redirect(url_for('index'))

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
def panel_admin_doc():
    if session.get('rol') != 'administrador':
        flash('Acceso denegado. Inicia sesión como administrador.', 'error')
        return redirect(url_for('login_admin'))

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

#Para edición y eliminación de doctores
@app.route('/editar_doctor/<int:id>')
def editar_doctor(id):
    # lógica para editar
    ...

@app.route('/eliminar_doctor/<int:id>', methods=['POST'])
def eliminar_doctor(id):
    if session.get('rol') != 'administrador':
        flash('Acceso denegado. Solo los administradores pueden eliminar doctores.', 'error')
        return redirect(url_for('panel_admin'))

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # 1. Obtener el usuario_id del doctor
        cursor.execute("SELECT usuario_id FROM doctores WHERE id = %s", (id,))
        result = cursor.fetchone()

        if not result:
            flash('❌ Doctor no encontrado.', 'error')
            return redirect(url_for('panel_admin_doc'))

        usuario_id = result[0]

        # 2. Eliminar al usuario (esto eliminará automáticamente al doctor por ON DELETE CASCADE)
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
