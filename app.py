import bcrypt
from flask import Flask, render_template, request, redirect, session, url_for, flash, make_response
from werkzeug.security import check_password_hash
from config import Config
import mysql.connector
import io
from xhtml2pdf import pisa

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

# Módulo Reportes: Seleccionar y ver/descargar reportes en pantalla o PDF.
@app.route('/reportes', methods=['GET', 'POST'])
def seleccionar_reporte():
    if 'rol' not in session:
        flash("Debes iniciar sesión para acceder a los reportes", "error")
        return redirect(url_for('index'))
    if request.method == 'POST':
        tipo = request.form.get('tipo_reporte')
        formato = request.form.get('formato')
        if tipo and formato:
            if formato == 'pantalla':
                return redirect(url_for('ver_reporte', tipo=tipo))
            elif formato == 'pdf':
                return redirect(url_for('descargar_reporte_pdf', tipo=tipo))
    return render_template('Reportes/seleccionar_reporte.html')

@app.route('/reportes/ver/<tipo>')
def ver_reporte(tipo):
    if 'rol' not in session:
        flash("Debes iniciar sesión para ver reportes", "error")
        return redirect(url_for('index'))
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        if tipo == 'citas':
            cursor.execute("""
                SELECT c.fecha, p.nombre AS paciente, p.telefono, p.fecha_nacimiento, c.observaciones
                FROM citas c
                JOIN pacientes p ON c.paciente_id = p.id
                ORDER BY c.fecha DESC
            """)
            datos = cursor.fetchall()
            return render_template('Reportes/reporte_citas.html', citas=datos)
        elif tipo == 'tratamientos':
            cursor.execute("""
                SELECT t.fecha_registro, p.nombre AS paciente, t.diagnostico, t.tratamiento_aplicado, t.observaciones
                FROM tratamientos t
                JOIN citas c ON t.cita_id = c.id
                JOIN pacientes p ON c.paciente_id = p.id
                ORDER BY t.fecha_registro DESC
            """)
            datos = cursor.fetchall()
            return render_template('Reportes/reporte_tratamientos.html', tratamientos=datos)
        else:
            flash("Tipo de reporte no válido", "error")
            return redirect(url_for('seleccionar_reporte'))
    except mysql.connector.Error as e:
        flash(f"Error al cargar el reporte: {e}", "error")
        return redirect(url_for('seleccionar_reporte'))
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

@app.route('/reportes/pdf/<tipo>')
def descargar_reporte_pdf(tipo):
    if 'rol' not in session:
        flash("Debes iniciar sesión para ver reportes", "error")
        return redirect(url_for('index'))
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        if tipo == 'citas':
            cursor.execute("""
                SELECT c.fecha, p.nombre AS paciente, p.telefono, p.fecha_nacimiento, c.observaciones
                FROM citas c
                JOIN pacientes p ON c.paciente_id = p.id
                ORDER BY c.fecha DESC
            """)
            datos = cursor.fetchall()
            rendered = render_template('Reportes/reporte_citas.html', citas=datos)
        elif tipo == 'tratamientos':
            cursor.execute("""
                SELECT t.fecha_registro, p.nombre AS paciente, t.diagnostico, t.tratamiento_aplicado, t.observaciones
                FROM tratamientos t
                JOIN citas c ON t.cita_id = c.id
                JOIN pacientes p ON c.paciente_id = p.id
                ORDER BY t.fecha_registro DESC
            """)
            datos = cursor.fetchall()
            rendered = render_template('Reportes/reporte_tratamientos.html', tratamientos=datos)
        else:
            flash("Tipo de reporte no válido", "error")
            return redirect(url_for('seleccionar_reporte'))
        
        pdf = io.BytesIO()
        pisa_status = pisa.CreatePDF(io.StringIO(rendered), dest=pdf)
        if pisa_status.err:
            flash("Error generando PDF", "error")
            return redirect(url_for('seleccionar_reporte'))
        pdf.seek(0)
        response = make_response(pdf.read())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{tipo}_reporte.pdf"'
        return response
    except mysql.connector.Error as e:
        flash(f"Error al descargar el reporte: {e}", "error")
        return redirect(url_for('seleccionar_reporte'))
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

@app.route('/panel/reportes')
def ver_opcion_reportes():
    if session.get('rol') in ['administrador', 'doctor']:
        return redirect(url_for('seleccionar_reporte'))
    flash('Acceso restringido a usuarios con permisos.', 'error')
    return redirect(url_for('index'))

# Rutas de Login
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
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals() and conn.is_connected():
                conn.close()
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
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals() and conn.is_connected():
                conn.close()
    return render_template('Dentista/login_dentista.html')

# Paneles
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

# Rutas de administración de doctores (solo para administradores)
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
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()
    return render_template('Administrador/panel_admin_doc.html', doctores=doctores)

# Rutas para edición, registro y eliminación de doctores
@app.route('/panel/administrador/doctores/registrar', methods=['GET', 'POST'])
def registrar_doctor():
    if session.get('rol') != 'administrador':
        flash('Acceso denegado. Inicia sesión como administrador.', 'error')
        return redirect(url_for('login_admin'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        contraseña = request.form['contraseña']
        especialidad = request.form['especialidad']
        telefono = request.form['telefono']

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
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals() and conn.is_connected():
                conn.close()

    return render_template('Administrador/registrar_doctor.html')

@app.route('/editar_doctor/<int:id>', methods=['POST'])
def editar_doctor(id):
    if session.get('rol') != 'administrador':
        flash('Acceso denegado. Solo los administradores pueden editar doctores.', 'error')
        return redirect(url_for('panel_admin_doc'))

    nombre = request.form['nombre']
    correo = request.form['correo']
    especialidad = request.form['especialidad']
    telefono = request.form['telefono']

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Obtener el usuario_id correspondiente al doctor
        cursor.execute("SELECT usuario_id FROM doctores WHERE id = %s", (id,))
        result = cursor.fetchone()

        if not result:
            flash('❌ Doctor no encontrado.', 'error')
            return redirect(url_for('panel_admin_doc'))

        usuario_id = result[0]

        # Actualizar usuarios
        cursor.execute("""
            UPDATE usuarios SET nombre = %s, correo = %s WHERE id = %s
        """, (nombre, correo, usuario_id))

        # Actualizar doctores
        cursor.execute("""
            UPDATE doctores SET especialidad = %s, telefono = %s WHERE id = %s
        """, (especialidad, telefono, id))

        conn.commit()
        flash('✅ Doctor actualizado correctamente.', 'success')

    except mysql.connector.Error as e:
        flash(f'❌ Error al actualizar doctor: {e}', 'error')

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals() and conn.is_connected(): conn.close()

    return redirect(url_for('panel_admin_doc'))


@app.route('/eliminar_doctor/<int:id>', methods=['POST'])
def eliminar_doctor(id):
    if session.get('rol') != 'administrador':
        flash('Acceso denegado. Solo los administradores pueden eliminar doctores.', 'error')
        return redirect(url_for('panel_admin'))
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # Obtener el usuario_id del doctor
        cursor.execute("SELECT usuario_id FROM doctores WHERE id = %s", (id,))
        result = cursor.fetchone()
        if not result:
            flash('❌ Doctor no encontrado.', 'error')
            return redirect(url_for('panel_admin_doc'))
        usuario_id = result[0]
        # Eliminar el usuario (se eliminará el doctor por ON DELETE CASCADE)
        cursor.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))
        conn.commit()
        flash('✅ Doctor eliminado correctamente.', 'success')
    except mysql.connector.Error as e:
        flash(f'❌ Error al eliminar doctor: {e}', 'error')
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()
    return redirect(url_for('panel_admin_doc'))

# Rutas para citas y tratamientos
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
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals() and conn.is_connected():
                conn.close()
    return render_template('Dentista/registrar_tratamiento.html', cita_id=cita_id)

@app.route('/citas/registrar', methods=['GET', 'POST'])
def registrar_cita():
    if session.get('rol') != 'doctor':
        flash('Acceso restringido. Solo los doctores pueden registrar citas.', 'error')
        return redirect(url_for('index'))
    if request.method == 'POST':
        paciente_nombre = request.form.get('paciente')
        paciente_telefono = request.form.get('telefono')
        paciente_fecha_nac = request.form.get('fecha_nacimiento')
        fecha = request.form.get('fecha')
        hora = request.form.get('hora')
        observaciones = request.form.get('descripcion')
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM pacientes WHERE nombre = %s AND telefono = %s", (paciente_nombre, paciente_telefono))
            paciente = cursor.fetchone()
            if paciente:
                paciente_id = paciente[0]
            else:
                cursor.execute(
                    "INSERT INTO pacientes (nombre, telefono, fecha_nacimiento) VALUES (%s, %s, %s)",
                    (paciente_nombre, paciente_telefono, paciente_fecha_nac)
                )
                paciente_id = cursor.lastrowid
            cursor.execute("SELECT id FROM doctores WHERE usuario_id = %s", (session['usuario_id'],))
            doctor = cursor.fetchone()
            if not doctor:
                flash("❌ No se encontró el ID del doctor.", "error")
                return redirect(url_for('panel_doctor'))
            doctor_id = doctor[0]
            fecha_completa = f"{fecha} {hora}"
            cursor.execute(
                "INSERT INTO citas (doctor_id, paciente_id, fecha, observaciones) VALUES (%s, %s, %s, %s)",
                (doctor_id, paciente_id, fecha_completa, observaciones)
            )
            conn.commit()
            flash("✅ Cita registrada correctamente.", "success")
            return redirect(url_for('panel_doctor'))
        except mysql.connector.Error as e:
            flash(f"❌ Error al registrar la cita: {e}", "error")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals() and conn.is_connected():
                conn.close()
    return render_template('Dentista/registrar_cita.html')

@app.route('/citas/mis_citas')
def ver_citas():
    if session.get('rol') != 'doctor':
        flash('Acceso restringido. Solo los doctores pueden ver sus citas.', 'error')
        return redirect(url_for('index'))
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT c.id, c.fecha, p.nombre AS paciente, p.telefono, p.fecha_nacimiento, c.observaciones
            FROM citas c
            JOIN pacientes p ON c.paciente_id = p.id
            JOIN doctores d ON c.doctor_id = d.id
            WHERE d.usuario_id = %s
            ORDER BY c.fecha
        """
        cursor.execute(query, (session['usuario_id'],))
        citas = cursor.fetchall()
    except mysql.connector.Error as e:
        flash(f'❌ Error al cargar citas: {e}', 'error')
        citas = []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()
    return render_template('Dentista/mis_citas.html', citas=citas)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
