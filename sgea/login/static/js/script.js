document.addEventListener("DOMContentLoaded", function () {
    const tipoSelect = document.getElementById("tipo");
    const campoSenha = document.getElementById("campoSenhaProfessor");

    function mostrarCampoSenha() {
        const tipo = tipoSelect.value;
        campoSenha.style.display = tipo === "professor" ? "flex" : "none";
    }

    if (tipoSelect) {
        tipoSelect.addEventListener("change", mostrarCampoSenha);
    }
});