import mysql.connector
import bcrypt

db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'sistema_citas',
    'port': 3306
}

# Datos del dentista
nombre = 'Daian'
correo = 'Daian@ejemplo.com'
password = '1234567891'
rol = 'doctor'
especialidad = 'Ortodoncia'
telefono = '5547891230'

# Hashear la contraseña
hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Insertar en la tabla usuarios
    insert_usuario = """
        INSERT INTO usuarios (nombre, correo, contraseña, rol)
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(insert_usuario, (nombre, correo, hashed_password, rol))
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
