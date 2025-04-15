-- Base de datos del sistema de clínica médica
CREATE DATABASE IF NOT EXISTS sistema_citas;
USE sistema_citas;

-- Tabla de usuarios
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) NOT NULL UNIQUE,
    contraseña VARCHAR(255) NOT NULL,
    rol ENUM('administrador', 'doctor') NOT NULL
);

-- Tabla de doctores
CREATE TABLE doctores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    especialidad VARCHAR(100),
    telefono VARCHAR(20),
    fecha_registro DATETIME,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Tabla de pacientes (con relación directa a un doctor)
CREATE TABLE pacientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    fecha_nacimiento DATE,
    doctor_id INT,
    FOREIGN KEY (doctor_id) REFERENCES doctores(id) ON DELETE SET NULL
);

-- Relación muchos a muchos entre doctores y pacientes
CREATE TABLE doctor_paciente (
    doctor_id INT NOT NULL,
    paciente_id INT NOT NULL,
    PRIMARY KEY (doctor_id, paciente_id),
    FOREIGN KEY (doctor_id) REFERENCES doctores(id) ON DELETE CASCADE,
    FOREIGN KEY (paciente_id) REFERENCES pacientes(id) ON DELETE CASCADE
);

-- Citas sin campo 'estado'
CREATE TABLE citas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    doctor_id INT NOT NULL,
    paciente_id INT NOT NULL,
    fecha DATETIME NOT NULL,
    observaciones TEXT,
    FOREIGN KEY (doctor_id) REFERENCES doctores(id) ON DELETE CASCADE,
    FOREIGN KEY (paciente_id) REFERENCES pacientes(id) ON DELETE CASCADE
);

-- Tratamientos relacionados con citas
CREATE TABLE tratamientos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cita_id INT NOT NULL,
    diagnostico VARCHAR(100),
    tratamiento_aplicado VARCHAR(100),
    observaciones TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cita_id) REFERENCES citas(id) ON DELETE CASCADE
);

SELECT * FROM pacientes WHERE doctor_id = 2;


