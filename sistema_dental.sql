-- Base de datos del sistema de clínica médica
CREATE DATABASE IF NOT EXISTS sistema_citas;
USE sistema_citas;

-- Tabla de usuarios (incluye administradores y doctores)
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) NOT NULL UNIQUE,
    contraseña VARCHAR(255) NOT NULL,
    rol ENUM('administrador', 'doctor') NOT NULL,
    activo BOOLEAN DEFAULT TRUE
);

-- Tabla de doctores con vínculo a usuarios
CREATE TABLE IF NOT EXISTS doctores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    especialidad VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Tabla de pacientes
CREATE TABLE IF NOT EXISTS pacientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    fecha_nacimiento DATE
);

-- Tabla de citas
CREATE TABLE IF NOT EXISTS citas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    doctor_id INT NOT NULL,
    paciente_id INT NOT NULL,
    fecha DATETIME NOT NULL,
    estado ENUM('pendiente', 'completada', 'cancelada') DEFAULT 'pendiente',
    observaciones TEXT,
    FOREIGN KEY (doctor_id) REFERENCES doctores(id),
    FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
);

-- Tabla de tratamientos
CREATE TABLE IF NOT EXISTS tratamientos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cita_id INT NOT NULL,
    diagnostico TEXT NOT NULL,
    tratamiento_aplicado TEXT NOT NULL,
    observaciones TEXT,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cita_id) REFERENCES citas(id) ON DELETE CASCADE
);
