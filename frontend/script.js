 async function carregarPacientes() {

    try {

        const resposta = await fetch(
            "http://127.0.0.1:8000/pacientes"
        );

        if (!resposta.ok) {
            throw new Error("Erro ao buscar pacientes");
        }

        const pacientes = await resposta.json();

        const lista = document.getElementById(
            "lista-pacientes"
        );

        lista.innerHTML = "";

        for (const paciente of pacientes) {

            let calorias = "Calculando...";

            try {

                const respostaNutricao = await fetch(
                    `http://127.0.0.1:8000/pacientes/${paciente.id}/nutricao`
                );

                if (respostaNutricao.ok) {

                    const dadosNutricao =
                        await respostaNutricao.json();

                    if (!dadosNutricao.erro) {

                        calorias =
                            `${dadosNutricao.calorias} kcal/dia`;
                    }
                }

            } catch (erro) {

                console.error(
                    `Erro ao calcular calorias do paciente ${paciente.id}:`,
                    erro
                );

                calorias = "Não disponível";
            }

            const item = document.createElement("div");

            item.className = "card-paciente";

            item.innerHTML = `
                <h3>${paciente.nome}</h3>

                <p>
                    <strong>Idade:</strong>
                    ${paciente.idade} anos
                </p>

                <p>
                    <strong>Sexo:</strong>
                    ${paciente.sexo}
                </p>

                <p>
                    <strong>Peso:</strong>
                    ${paciente.peso} kg
                </p>

                <p>
                    <strong>Altura:</strong>
                    ${paciente.altura} cm
                </p>

                <p>
                    <strong>Objetivo:</strong>
                    ${paciente.objetivo}
                </p>

                <p>
                    <strong>Nível de atividade:</strong>
                    ${paciente.nivel_atividade}
                </p>

                <p>
                    <strong>IMC:</strong>
                    ${paciente.imc}
                </p>

                <p>
                    <strong>Classificação:</strong>
                    ${paciente.classificacao_imc}
                </p>

                <p>
                    <strong>Calorias:</strong>
                    ${calorias}
                </p>

                <button onclick="editarPaciente(${paciente.id})">
                    Editar
                </button>

                <button onclick="excluirPaciente(${paciente.id})">
                    Excluir
                </button>

                <button onclick="calcularNutricao(${paciente.id})">
                    Calcular nutrição
                </button>
            `;

            lista.appendChild(item);
        }

    } catch (erro) {

        console.error(
            "Erro ao carregar pacientes:",
            erro
        );

        alert("Erro ao carregar pacientes.");
    }

}


async function excluirPaciente(id) {

    // resto do código...
}


async function editarPaciente(id) {

    const nome = prompt("Nome do paciente:");
    const idade = prompt("Idade:");
    const telefone = prompt("Telefone:");
    const email = prompt("E-mail:");
    const peso = prompt("Peso (kg):");
    const altura = prompt("Altura (cm):");
    const objetivo = prompt("Objetivo:");
    const sexo = prompt("Sexo:");
    const nivel_atividade = prompt(
        "Nível de atividade:"
    );

    if (!nome || !idade || !peso || !altura) {
        alert("Preencha os dados obrigatórios.");
        return;
    }

    try {

        const resposta = await fetch(
            `http://127.0.0.1:8000/pacientes/${id}`,
            {
                method: "PUT",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    nome: nome,

                    idade: Number(idade),

                    telefone: telefone,

                    email: email,

                    peso: Number(peso),

                    altura: Number(altura),

                    objetivo: objetivo,

                    sexo: sexo,

                    nivel_atividade: nivel_atividade
                })
            }
        );

        if (resposta.ok) {

            alert(
                "Paciente atualizado com sucesso!"
            );

            carregarPacientes();

        } else {

            const erro = await resposta.json();

            console.error(erro);

            alert(
                "Erro ao atualizar paciente."
            );
        }

    } catch (erro) {

        console.error(
            "Erro ao atualizar:",
            erro
        );

        alert(
            "Erro ao conectar com a API."
        );
    }
}


async function calcularNutricao(pacienteId) {

    try {

        const resposta = await fetch(
            `http://127.0.0.1:8000/pacientes/${pacienteId}/nutricao`
        );

        const dados = await resposta.json();

        console.log(
            "Resultado da nutrição:",
            dados
        );

        if (dados.erro) {

            alert(dados.erro);

            return;
        }

        alert(
            `Resultado nutricional

TMB: ${dados.tmb} kcal

GET: ${dados.get} kcal

Calorias do objetivo: ${dados.calorias} kcal

Proteína: ${dados.proteina_g} g

Carboidrato: ${dados.carboidrato_g} g

Gordura: ${dados.gordura_g} g`
        );

    } catch (erro) {

        console.error(
            "Erro ao calcular nutrição:",
            erro
        );

        alert(
            "Erro ao conectar com a API"
        );
    }
}


function limparPacientes() {

    const lista = document.getElementById(
        "lista-pacientes"
    );

    lista.innerHTML = "";
}


async function adicionarPaciente(event) {

    event.preventDefault();

    const paciente = {

        nome: document.getElementById("nome").value,

        idade: Number(
            document.getElementById("idade").value
        ),

        telefone: document.getElementById("telefone").value,

        email: document.getElementById("email").value,

        peso: Number(
            document.getElementById("peso").value
        ),

        altura: Number(
            document.getElementById("altura").value
        ),

        objetivo: document.getElementById("objetivo").value,

        sexo: document.getElementById("sexo").value,

        nivel_atividade: document.getElementById("nivel_atividade").value
    };

    try {

        const resposta = await fetch(
            "http://127.0.0.1:8000/pacientes",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(paciente)
            }
        );

        if (!resposta.ok) {

            const erro = await resposta.text();

            console.error(
                "Erro ao cadastrar:",
                erro
            );

            alert("Erro ao adicionar paciente.");

            return;
        }

        const dados = await resposta.json();

        console.log(
            "Paciente cadastrado:",
            dados
        );

        alert(
            "Paciente adicionado com sucesso!"
        );

        document
            .getElementById("form-paciente")
            .reset();

        carregarPacientes();

    } catch (erro) {

        console.error(
            "Erro ao adicionar paciente:",
            erro
        );

        alert(
            "Erro ao conectar com a API."
        );
    }
}


document
    .getElementById("form-paciente")
    .addEventListener(
        "submit",
        adicionarPaciente
    );


javascript
async function buscarAlimentos() {

    const nome = document
        .getElementById("busca-alimento")
        .value
        .trim();

    if (!nome) {
        alert("Digite o nome do alimento.");
        return;
    }

    try {

        const resposta = await fetch(
            `http://127.0.0.1:8000/alimentos/buscar?nome=${encodeURIComponent(nome)}`
        );

        if (!resposta.ok) {
            throw new Error("Erro ao buscar alimentos");
        }

        const dados = await resposta.json();

        const lista = document.getElementById(
            "lista-alimentos"
        );

        lista.innerHTML = "";

        if (
            !dados.alimentos ||
            dados.alimentos.length === 0
        ) {

            lista.innerHTML =
                "<p>Nenhum alimento encontrado.</p>";

            return;
        }

        dados.alimentos.forEach((alimento, index) => {

            const item = document.createElement("div");

            item.className = "card-alimento";

            item.innerHTML = `
                <h3>${alimento.nome}</h3>

                <p>
                    <strong>Valores por 100 g</strong>
                </p>

                <label>
                    Quantidade:
                    <input
                        type="number"
                        id="quantidade-${index}"
                        value="100"
                        min="1"
                        step="1"
                        oninput="calcularAlimento(${index}, ${alimento.energia}, ${alimento.proteina}, ${alimento.carboidratos}, ${alimento.lipideos}, ${alimento.fibra})"
                    >
                    g
                </label>

                <div id="resultado-alimento-${index}">

                    <p>
                        <strong>Energia:</strong>
                        <span>${alimento.energia}</span> kcal
                    </p>

                    <p>
                        <strong>Proteína:</strong>
                        <span>${alimento.proteina}</span> g
                    </p>

                    <p>
                        <strong>Carboidratos:</strong>
                        <span>${alimento.carboidratos}</span> g
                    </p>

                    <p>
                        <strong>Gorduras:</strong>
                        <span>${alimento.lipideos}</span> g
                    </p>

                    <p>
                        <strong>Fibras:</strong>
                        <span>${alimento.fibra}</span> g
                    </p>

                </div>

                <hr>
            `;

            lista.appendChild(item);
        });

    } catch (erro) {

        console.error(
            "Erro ao buscar alimentos:",
            erro
        );

        alert("Erro ao conectar com a API.");
    }
}


function calcularAlimento(
    index,
    energia100,
    proteina100,
    carboidratos100,
    gorduras100,
    fibras100
) {

    const quantidade = Number(
        document.getElementById(`quantidade-${index}`).value
    );

    if (!quantidade || quantidade <= 0) {
        return;
    }

    const fator = quantidade / 100;

    const energia = energia100 * fator;
    const proteina = proteina100 * fator;
    const carboidratos = carboidratos100 * fator;
    const gorduras = gorduras100 * fator;
    const fibras = fibras100 * fator;

    const resultado = document.getElementById(
        `resultado-alimento-${index}`
    );

    resultado.innerHTML = `

        <p>
            <strong>Energia:</strong>
            ${energia.toFixed(2)} kcal
        </p>

        <p>
            <strong>Proteína:</strong>
            ${proteina.toFixed(2)} g
        </p>

        <p>
            <strong>Carboidratos:</strong>
            ${carboidratos.toFixed(2)} g
        </p>

        <p>
            <strong>Gorduras:</strong>
            ${gorduras.toFixed(2)} g
        </p>

        <p>
            <strong>Fibras:</strong>
            ${fibras.toFixed(2)} g
        </p>

    `;

 

}


function limparAlimentos() {
    // Limpa o campo de pesquisa
    document.getElementById("busca-alimento").value = "";

    // Limpa os resultados da pesquisa
    document.getElementById("lista-alimentos").innerHTML = "";
}


// Carrega os pacientes quando a página abre

carregarPacientes();