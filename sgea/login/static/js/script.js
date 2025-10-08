document.addEventListener("DOMContentLoaded", function () {
    const tipoSelect = document.getElementById("tipo");
    const campoSenha = document.getElementById("campoSenhaAcesso");

    function mostrarCampoSenha() {
        const tipo = tipoSelect.value;
        if (tipo == "professor"){
            campoSenha.style.display = tipo === "professor" ? "flex" : "none";
        }
        if (tipo == "organizador") {
            campoSenha.style.display = tipo === "organizador" ? "flex" : "none";
        }
        if (tipo == "estudante") {
            campoSenha.style.display = "none";
        }
    }

    if (tipoSelect) {
        tipoSelect.addEventListener("change", mostrarCampoSenha);
    }
});
