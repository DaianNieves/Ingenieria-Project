// Abrir el modal y cargar los datos del doctor
function openEditModal(id, nombre, correo, especialidad, telefono) {
    // Llenar los campos del formulario
    document.getElementById("doctorId").value = id;
    document.getElementById("nombre").value = nombre;
    document.getElementById("correo").value = correo;
    document.getElementById("especialidad").value = especialidad;
    document.getElementById("telefono").value = telefono;

    // Establecer la ruta del formulario (con el id del doctor)
    document.getElementById("editDoctorForm").action = `/editar_doctor/${id}`;

    // Mostrar el modal
    document.getElementById("editDoctorModal").style.display = "block";
}

// Cerrar el modal
function closeEditModal() {
    document.getElementById("editDoctorModal").style.display = "none";
}

// Cerrar el modal si se hace clic fuera de él
window.onclick = function(event) {
    const modal = document.getElementById("editDoctorModal");
    if (event.target === modal) {
        closeEditModal();
    }
}
