import mysql.connector
import bcrypt

db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'sistema_citas',
    'port': 3306
}

# Datos del administrador
nombre = 'Nat'
correo = 'nat.diaz@clinica.com'
password = '1234567891'
rol = 'administrador'

# ✅ Axioma 2: Validar longitud mínima de contraseña
if len(password) < 8:
    print("❌ La contraseña debe tener al menos 8 caracteres.")
    exit()

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # ✅ Axioma 1: Verificar si el correo ya existe
    cursor.execute("SELECT * FROM usuarios WHERE correo = %s", (correo,))
    resultado = cursor.fetchone()

    if resultado:
        print("❌ El correo ya está registrado en el sistema.")
    else:
        # Hashear la contraseña
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Insertar nuevo administrador
        query = """
            INSERT INTO usuarios (nombre, correo, contraseña, rol)
            VALUES (%s, %s, %s, %s)
        """
        values = (nombre, correo, hashed_password, rol)

        cursor.execute(query, values)
        conn.commit()
        print("✅ Administrador registrado correctamente.")

except mysql.connector.Error as err:
    print(f"❌ Error en la base de datos: {err}")
finally:
    if cursor:
        cursor.close()
    if conn and conn.is_connected():
        conn.close()

