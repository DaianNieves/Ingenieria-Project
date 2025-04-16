import mysql.connector
import bcrypt
from config import db_config

# Función para conectar a la base de datos
def get_connection():
    return mysql.connector.connect(**db_config)

# Función para registrar un dentista
def registrar_dentista(nombre, correo, password, especialidad, telefono):
    try:
        # Hashear la contraseña
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Conectar a la base de datos
        conn = get_connection()
        cursor = conn.cursor()

        # Insertar en la tabla usuarios
        insert_usuario = """
            INSERT INTO usuarios (nombre, correo, contraseña, rol)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_usuario, (nombre, correo, hashed_password, 'doctor'))
        usuario_id = cursor.lastrowid

        # Insertar en la tabla doctores con usuario_id
        insert_doctor = """
            INSERT INTO doctores (usuario_id, especialidad, telefono)
            VALUES (%s, %s, %s)
        """
        cursor.execute(insert_doctor, (usuario_id, especialidad, telefono))

        conn.commit()
        print("✅ Dentista registrado correctamente.")

    except mysql.connector.Error as err:
        print(f"❌ Error en la base de datos: {err}")
    
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

# Datos del dentista
nombre = 'Daian'
correo = 'Daian@ejemplo.com'
password = '1234567891'
especialidad = 'Ortodoncia'
telefono = '5547891230'

# Llamada a la función para registrar el dentista
registrar_dentista(nombre, correo, password, especialidad, telefono)