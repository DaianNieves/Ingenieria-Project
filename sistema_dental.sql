-- Crear la base de datos
CREATE DATABASE Sistema_Dental;
USE Sistema_Dental;

-- Tabla: Administrador
CREATE TABLE Administrador (
    ID_Administrador INT PRIMARY KEY AUTO_INCREMENT,
    Nombre VARCHAR(50),
    Apellido_Pat VARCHAR(50),
    Apellido_Mat VARCHAR(50),
    Telefono VARCHAR(15),
    Direccion VARCHAR(100),
    Correo VARCHAR(100) UNIQUE,
    Contraseña VARCHAR(100)
);

-- Tabla: Pacientes
CREATE TABLE Pacientes (
    ID_Paciente INT PRIMARY KEY AUTO_INCREMENT,
    Nombre VARCHAR(50),
    Apellido_Pat VARCHAR(50),
    Apellido_Mat VARCHAR(50),
    Telefono VARCHAR(15),
    Direccion VARCHAR(100),
    Correo VARCHAR(100) UNIQUE,
    Contraseña VARCHAR(100)
);

-- Tabla: Especialidad
CREATE TABLE Especialidad (
    ID_Especialidad INT PRIMARY KEY AUTO_INCREMENT,
    Nombre_Especialidad VARCHAR(100),
    Descripcion TEXT
);

-- Tabla: Doctores
CREATE TABLE Doctores (
    ID_Doctor INT PRIMARY KEY AUTO_INCREMENT,
    ID_Especialidad INT,
    Nombre VARCHAR(50),
    Apellido_Pat VARCHAR(50),
    Apellido_Mat VARCHAR(50),
    Telefono VARCHAR(15),
    Direccion VARCHAR(100),
    Correo VARCHAR(100) UNIQUE,
    Contraseña VARCHAR(100),
    FOREIGN KEY (ID_Especialidad) REFERENCES Especialidad(ID_Especialidad)
);

-- Tabla: Historial
CREATE TABLE Historial (
    ID_Historial INT PRIMARY KEY AUTO_INCREMENT,
    ID_Paciente INT,
    ID_Doctor INT,
    Problema TEXT,
    Tratamiento TEXT,
    Antecedentes_Medicos TEXT,
    Fecha DATE,
    FOREIGN KEY (ID_Paciente) REFERENCES Pacientes(ID_Paciente),
    FOREIGN KEY (ID_Doctor) REFERENCES Doctores(ID_Doctor)
);

-- Tabla: Citas
CREATE TABLE Citas (
    ID_Cita INT PRIMARY KEY AUTO_INCREMENT,
    ID_Paciente INT,
    ID_Doctor INT,
    Fecha DATE,
    Hora TIME,
    Motivo TEXT,
    Estado ENUM('Pendiente', 'Confirmada', 'Cancelada', 'Atendida'),
    FOREIGN KEY (ID_Paciente) REFERENCES Pacientes(ID_Paciente),
    FOREIGN KEY (ID_Doctor) REFERENCES Doctores(ID_Doctor)
);