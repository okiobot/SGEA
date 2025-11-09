document.addEventListener("DOMContentLoaded", function () {

    /* Tipo de usuário */
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
    
    
    /* Detalhes de eventos */
    const botoesDetalhes = document.querySelectorAll(".botao-detalhe");
    const modais = document.querySelectorAll(".evento-modal");

    botoesDetalhes.forEach(botao => {
        botao.addEventListener("click", () => {
            const eventoId = botao.getAttribute("data-evento-id");
            const modal = document.getElementById(`modal-${eventoId}`);
            modal.style.display = "flex";
        });
    });

    modais.forEach(modal => {
        const fechar = modal.querySelector(".fechar-modal");
        fechar.addEventListener("click", () => {
            modal.style.display = "none";
        });

        // fecha se clicar fora tbm
        modal.addEventListener("click", e => {
            if (e.target === modal) {
                modal.style.display = "none";
            }
        });
    });
});


