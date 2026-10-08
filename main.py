from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from schemas import (
    PacienteCreate,
    PacienteUpdate,
    PacienteResponse,
    AvaliacaoCreate,
    AvaliacaoResponse,
    MetaCreate,
    MetaResponse
)

from database import SessionLocal, engine, Base
from models import Paciente, Avaliacao, Meta

from alimentos import (
    buscar_alimento,
    buscar_alimentos,
    buscar_alimento_id
)


Base.metadata.create_all(bind=engine)


app = FastAPI()


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# CÁLCULO DO IMC
# =========================================================

def calcular_imc(peso, altura):

    if peso is None or altura is None:
        return None, "Não calculado"

    altura = altura / 100

    if altura <= 0:
        return None, "Não calculado"

    imc = peso / (altura * altura)

    if imc < 18.5:
        classificacao = "Baixo peso"

    elif imc < 25:
        classificacao = "Peso normal"

    elif imc < 30:
        classificacao = "Sobrepeso"

    elif imc < 35:
        classificacao = "Obesidade grau I"

    elif imc < 40:
        classificacao = "Obesidade grau II"

    else:
        classificacao = "Obesidade grau III"

    return round(imc, 2), classificacao


# =========================================================
# CÁLCULO NUTRICIONAL
# =========================================================

def calcular_nutricao(
    peso: float,
    altura: float,
    idade: int,
    sexo: str,
    nivel_atividade: str,
    objetivo: str
):

    # -----------------------------------------------------
    # ALTURA
    # -----------------------------------------------------

    if altura <= 0:

        return {
            "erro": "Altura inválida"
        }

    # Se vier em metros

    if altura < 3:

        altura_cm = altura * 100

    # Se vier em centímetros

    else:

        altura_cm = altura


    # -----------------------------------------------------
    # TMB - Mifflin-St Jeor
    # -----------------------------------------------------

    sexo_normalizado = sexo.lower().strip()


    if sexo_normalizado == "masculino":

        tmb = (
            (10 * peso)
            + (6.25 * altura_cm)
            - (5 * idade)
            + 5
        )


    elif sexo_normalizado == "feminino":

        tmb = (
            (10 * peso)
            + (6.25 * altura_cm)
            - (5 * idade)
            - 161
        )


    else:

        return {
            "erro": "Sexo inválido",
            "sexo_informado": sexo
        }


    # -----------------------------------------------------
    # FATORES DE ATIVIDADE
    # -----------------------------------------------------

    nivel = nivel_atividade.lower().strip()


    fatores_atividade = {

        "sedentario": 1.2,
        "sedentário": 1.2,

        "pouco_ativo": 1.375,
        "pouco ativo": 1.375,

        "moderadamente_ativo": 1.55,
        "moderadamente ativo": 1.55,

        "intenso": 1.725,

        "muito_ativo": 1.725,
        "muito ativo": 1.725,
        "muito intenso": 1.725,

        "extremamente_ativo": 1.9,
        "extremamente ativo": 1.9
    }


    if nivel not in fatores_atividade:

        return {
            "erro": "Nível de atividade inválido",
            "nivel_informado": nivel_atividade
        }


    fator = fatores_atividade[nivel]


    # -----------------------------------------------------
    # GASTO ENERGÉTICO TOTAL
    # -----------------------------------------------------

    get = tmb * fator


    # -----------------------------------------------------
    # OBJETIVO
    # -----------------------------------------------------

    objetivo_normalizado = objetivo.lower().strip()


    if objetivo_normalizado in [
        "emagrecimento",
        "emagrecer",
        "perder peso"
    ]:

        calorias = get - 500


    elif objetivo_normalizado in [
        "ganho de massa",
        "ganhar massa",
        "hipertrofia"
    ]:

        calorias = get + 300


    else:

        calorias = get


    calorias = round(calorias, 2)


    # -----------------------------------------------------
    # MACRONUTRIENTES
    # -----------------------------------------------------

    # Proteína: 2 g/kg

    proteina = peso * 2


    # Gordura: 25% das calorias

    gordura_calorias = calorias * 0.25

    gordura = gordura_calorias / 9


    # Calorias da proteína

    proteina_calorias = proteina * 4


    # Calorias da gordura

    gordura_calorias = gordura * 9


    # Calorias restantes para carboidratos

    carboidrato_calorias = (
        calorias
        - proteina_calorias
        - gordura_calorias
    )


    carboidrato = carboidrato_calorias / 4


    # -----------------------------------------------------
    # RESULTADO
    # -----------------------------------------------------

    return {

        "peso": peso,

        "altura": round(altura_cm, 2),

        "idade": idade,

        "sexo": sexo,

        "nivel_atividade": nivel_atividade,

        "objetivo": objetivo,

        "tmb": round(tmb, 2),

        "fator_atividade": fator,

        "get": round(get, 2),

        "calorias": calorias,

        "proteina_g": round(proteina, 2),

        "carboidrato_g": round(carboidrato, 2),

        "gordura_g": round(gordura, 2)
    }


# =========================================================
# ALIMENTOS
# =========================================================

@app.get(
    "/alimentos/buscar",
    tags=["Alimentos"]
)
def pesquisar_alimentos(nome: str):

    resultados = buscar_alimentos(nome)

    return {
        "busca": nome,
        "total": len(resultados),
        "alimentos": resultados
    }


@app.get(
    "/alimentos/{alimento_id}",
    tags=["Alimentos"]
)
def pesquisar_alimento_id(alimento_id: int):

    alimento = buscar_alimento_id(alimento_id)

    if alimento is None:

        return {
            "erro": "Alimento não encontrado"
        }

    return alimento


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():

    return {
        "message": "NutriControl AI funcionando 🚀"
    }


# =========================================================
# NUTRIÇÃO DO PACIENTE
# =========================================================

@app.get("/pacientes/{paciente_id}/nutricao")
def calcular_nutricao_paciente(paciente_id: int):

    db = SessionLocal()


    paciente = db.query(Paciente).filter(
        Paciente.id == paciente_id
    ).first()


    if paciente is None:

        db.close()

        return {
            "erro": "Paciente não encontrado"
        }


    resultado = calcular_nutricao(

        peso=paciente.peso,

        altura=paciente.altura,

        idade=paciente.idade,

        sexo=paciente.sexo,

        nivel_atividade=paciente.nivel_atividade,

        objetivo=paciente.objetivo
    )


    db.close()


    return resultado


# =========================================================
# CRIAR PACIENTE
# =========================================================

@app.post(
    "/pacientes",
    response_model=PacienteResponse
)
def criar_paciente(paciente: PacienteCreate):

    db = SessionLocal()


    novo_paciente = Paciente(

        nome=paciente.nome,

        idade=paciente.idade,

        sexo=paciente.sexo,

        telefone=paciente.telefone,

        email=paciente.email,

        peso=paciente.peso,

        altura=paciente.altura,

        objetivo=paciente.objetivo,

        nivel_atividade=paciente.nivel_atividade
    )


    db.add(novo_paciente)

    db.commit()

    db.refresh(novo_paciente)

    db.close()


    return novo_paciente


# =========================================================
# CRIAR AVALIAÇÃO
# =========================================================

@app.post(
    "/avaliacoes",
    response_model=AvaliacaoResponse
)
def criar_avaliacao(avaliacao: AvaliacaoCreate):

    db = SessionLocal()


    paciente = db.query(Paciente).filter(
        Paciente.id == avaliacao.paciente_id
    ).first()


    if paciente is None:

        db.close()

        return {
            "erro": "Paciente não encontrado"
        }


    nova_avaliacao = Avaliacao(

        paciente_id=avaliacao.paciente_id,

        peso=avaliacao.peso,

        altura=avaliacao.altura,

        data=avaliacao.data
    )


    db.add(nova_avaliacao)

    db.commit()

    db.refresh(nova_avaliacao)

    db.close()


    return nova_avaliacao


# =========================================================
# LISTAR PACIENTES
# =========================================================

@app.get("/pacientes")
def listar_pacientes():

    db = SessionLocal()


    pacientes = db.query(Paciente).all()


    resultado = []


    for paciente in pacientes:

        imc, classificacao = calcular_imc(
            paciente.peso,
            paciente.altura
        )


        resultado.append({

            "id": paciente.id,

            "nome": paciente.nome,

            "idade": paciente.idade,

            "sexo": paciente.sexo,

            "telefone": paciente.telefone,

            "email": paciente.email,

            "peso": paciente.peso,

            "altura": paciente.altura,

            "objetivo": paciente.objetivo,

            "nivel_atividade": paciente.nivel_atividade,

            "imc": imc,

            "classificacao_imc": classificacao
        })


    db.close()


    return resultado


# =========================================================
# BUSCAR PACIENTE
# =========================================================

@app.get("/pacientes/{paciente_id}")
def buscar_paciente(paciente_id: int):

    db = SessionLocal()


    paciente = db.query(Paciente).filter(
        Paciente.id == paciente_id
    ).first()


    if paciente is None:

        db.close()

        return {
            "erro": "Paciente não encontrado"
        }


    imc, classificacao = calcular_imc(
        paciente.peso,
        paciente.altura
    )


    resultado = {

        "id": paciente.id,

        "nome": paciente.nome,

        "idade": paciente.idade,

        "sexo": paciente.sexo,

        "telefone": paciente.telefone,

        "email": paciente.email,

        "peso": paciente.peso,

        "altura": paciente.altura,

        "objetivo": paciente.objetivo,

        "nivel_atividade": paciente.nivel_atividade,

        "imc": imc,

        "classificacao_imc": classificacao
    }


    db.close()


    return resultado


# =========================================================
# ATUALIZAR PACIENTE
# =========================================================

@app.put(
    "/pacientes/{paciente_id}",
    response_model=PacienteResponse
)
def atualizar_paciente(
    paciente_id: int,
    paciente_atualizado: PacienteUpdate
):

    db = SessionLocal()


    paciente = db.query(Paciente).filter(
        Paciente.id == paciente_id
    ).first()


    if paciente is None:

        db.close()

        return {
            "erro": "Paciente não encontrado"
        }


    dados = paciente_atualizado.model_dump(
        exclude_unset=True
    )


    for campo, valor in dados.items():

        setattr(
            paciente,
            campo,
            valor
        )


    db.commit()

    db.refresh(paciente)

    db.close()


    return paciente


# =========================================================
# EXCLUIR PACIENTE
# =========================================================

@app.delete("/pacientes/{paciente_id}")
def excluir_paciente(paciente_id: int):

    db = SessionLocal()


    paciente = db.query(Paciente).filter(
        Paciente.id == paciente_id
    ).first()


    if paciente is None:

        db.close()

        return {
            "erro": "Paciente não encontrado"
        }


    db.delete(paciente)

    db.commit()

    db.close()


    return {

        "message": "Paciente excluído com sucesso",

        "id": paciente_id
    }


# =========================================================
# EDITAR PACIENTE - PATCH
# =========================================================

@app.patch(
    "/pacientes/{paciente_id}",
    response_model=PacienteResponse
)
def editar_campo_paciente(
    paciente_id: int,
    dados: PacienteUpdate
):

    db = SessionLocal()


    paciente = db.query(Paciente).filter(
        Paciente.id == paciente_id
    ).first()


    if paciente is None:

        db.close()

        return {
            "erro": "Paciente não encontrado"
        }


    dados_alterados = dados.model_dump(
        exclude_unset=True
    )


    for campo, valor in dados_alterados.items():

        setattr(
            paciente,
            campo,
            valor
        )


    db.commit()

    db.refresh(paciente)

    db.close()


    return paciente


# =========================================================
# LISTAR AVALIAÇÕES
# =========================================================

@app.get("/avaliacoes/paciente/{paciente_id}")
def listar_avaliacoes(paciente_id: int):

    db = SessionLocal()


    paciente = db.query(Paciente).filter(
        Paciente.id == paciente_id
    ).first()


    if paciente is None:

        db.close()

        return {
            "erro": "Paciente não encontrado"
        }


    avaliacoes = db.query(Avaliacao).filter(
        Avaliacao.paciente_id == paciente_id
    ).all()


    resultado = []


    for avaliacao in avaliacoes:

        imc, classificacao = calcular_imc(

            avaliacao.peso,

            avaliacao.altura
        )


        resultado.append({

            "id": avaliacao.id,

            "paciente_id": avaliacao.paciente_id,

            "peso": avaliacao.peso,

            "altura": avaliacao.altura,

            "data": avaliacao.data,

            "imc": imc,

            "classificacao": classificacao
        })


    db.close()


    return resultado


# =========================================================
# EVOLUÇÃO
# =========================================================

@app.get("/avaliacoes/evolucao/{paciente_id}")
def evolucao_paciente(paciente_id: int):

    db = SessionLocal()


    paciente = db.query(Paciente).filter(
        Paciente.id == paciente_id
    ).first()


    if paciente is None:

        db.close()

        return {
            "erro": "Paciente não encontrado"
        }


    avaliacoes = db.query(Avaliacao).filter(
        Avaliacao.paciente_id == paciente_id
    ).order_by(
        Avaliacao.data.asc()
    ).all()


    if len(avaliacoes) == 0:

        db.close()

        return {
            "erro": "Paciente não possui avaliações"
        }


    primeira = avaliacoes[0]

    ultima = avaliacoes[-1]


    imc_inicial, classificacao_inicial = calcular_imc(

        primeira.peso,

        primeira.altura
    )


    imc_atual, classificacao_atual = calcular_imc(

        ultima.peso,

        ultima.altura
    )


    diferenca_peso = round(

        ultima.peso - primeira.peso,

        2
    )


    diferenca_imc = round(

        imc_atual - imc_inicial,

        2
    )


    db.close()


    return {

        "paciente_id": paciente.id,

        "paciente": paciente.nome,

        "primeira_avaliacao": {

            "data": primeira.data,

            "peso": primeira.peso,

            "imc": imc_inicial,

            "classificacao": classificacao_inicial
        },

        "avaliacao_atual": {

            "data": ultima.data,

            "peso": ultima.peso,

            "imc": imc_atual,

            "classificacao": classificacao_atual
        },

        "evolucao": {

            "diferenca_peso": diferenca_peso,

            "diferenca_imc": diferenca_imc
        }
    }


# =========================================================
# HISTÓRICO
# =========================================================

@app.get("/avaliacoes/historico/{paciente_id}")
def historico_avaliacoes(paciente_id: int):

    db = SessionLocal()


    paciente = db.query(Paciente).filter(
        Paciente.id == paciente_id
    ).first()


    if paciente is None:

        db.close()

        return {
            "erro": "Paciente não encontrado"
        }


    avaliacoes = db.query(Avaliacao).filter(
        Avaliacao.paciente_id == paciente_id
    ).order_by(
        Avaliacao.data.asc()
    ).all()


    if len(avaliacoes) == 0:

        db.close()

        return {
            "erro": "Paciente não possui avaliações"
        }


    historico = []


    for avaliacao in avaliacoes:

        imc, classificacao = calcular_imc(

            avaliacao.peso,

            avaliacao.altura
        )


        historico.append({

            "id": avaliacao.id,

            "data": avaliacao.data,

            "peso": avaliacao.peso,

            "altura": avaliacao.altura,

            "imc": imc,

            "classificacao": classificacao
        })


    db.close()


    return {

        "paciente_id": paciente.id,

        "paciente": paciente.nome,

        "total_avaliacoes": len(historico),

        "historico": historico
    }


# =========================================================
# PROGRESSO DAS AVALIAÇÕES
# =========================================================

@app.get("/avaliacoes/progresso/{paciente_id}")
def progresso_paciente(paciente_id: int):

    db = SessionLocal()


    paciente = db.query(Paciente).filter(
        Paciente.id == paciente_id
    ).first()


    if paciente is None:

        db.close()

        return {
            "erro": "Paciente não encontrado"
        }


    avaliacoes = db.query(Avaliacao).filter(
        Avaliacao.paciente_id == paciente_id
    ).order_by(
        Avaliacao.data.asc()
    ).all()


    if len(avaliacoes) < 2:

        db.close()

        return {
            "erro": "É necessário ter pelo menos 2 avaliações"
        }


    progresso = []


    for i in range(1, len(avaliacoes)):

        anterior = avaliacoes[i - 1]

        atual = avaliacoes[i]


        imc_anterior, classificacao_anterior = calcular_imc(

            anterior.peso,

            anterior.altura
        )


        imc_atual, classificacao_atual = calcular_imc(

            atual.peso,

            atual.altura
        )


        diferenca_peso = round(

            atual.peso - anterior.peso,

            2
        )


        diferenca_imc = round(

            imc_atual - imc_anterior,

            2
        )


        progresso.append({

            "avaliacao_anterior": {

                "id": anterior.id,

                "data": anterior.data,

                "peso": anterior.peso,

                "imc": imc_anterior,

                "classificacao": classificacao_anterior
            },

            "avaliacao_atual": {

                "id": atual.id,

                "data": atual.data,

                "peso": atual.peso,

                "imc": imc_atual,

                "classificacao": classificacao_atual
            },

            "evolucao": {

                "diferenca_peso": diferenca_peso,

                "diferenca_imc": diferenca_imc
            }
        })


    db.close()


    return {

        "paciente_id": paciente.id,

        "paciente": paciente.nome,

        "total_avaliacoes": len(avaliacoes),

        "progresso": progresso
    }


# =========================================================
# CRIAR META
# =========================================================

@app.post(
    "/metas",
    response_model=MetaResponse
)
def criar_meta(meta: MetaCreate):

    db = SessionLocal()


    paciente = db.query(Paciente).filter(
        Paciente.id == meta.paciente_id
    ).first()


    if paciente is None:

        db.close()

        return {
            "erro": "Paciente não encontrado"
        }


    nova_meta = Meta(

        paciente_id=meta.paciente_id,

        peso_meta=meta.peso_meta,

        objetivo=meta.objetivo,

        data=meta.data
    )


    db.add(nova_meta)

    db.commit()

    db.refresh(nova_meta)

    db.close()


    return nova_meta


# =========================================================
# LISTAR METAS
# =========================================================

@app.get("/metas/paciente/{paciente_id}")
def listar_metas(paciente_id: int):

    db = SessionLocal()


    paciente = db.query(Paciente).filter(
        Paciente.id == paciente_id
    ).first()


    if paciente is None:

        db.close()

        return {
            "erro": "Paciente não encontrado"
        }


    metas = db.query(Meta).filter(
        Meta.paciente_id == paciente_id
    ).all()


    db.close()


    return metas


# =========================================================
# PROGRESSO DA META
# =========================================================

@app.get("/metas/progresso/{paciente_id}")
def progresso_meta(paciente_id: int):

    db = SessionLocal()


    paciente = db.query(Paciente).filter(
        Paciente.id == paciente_id
    ).first()


    if paciente is None:

        db.close()

        return {
            "erro": "Paciente não encontrado"
        }


    # Pega a meta mais recente

    meta = db.query(Meta).filter(
        Meta.paciente_id == paciente_id
    ).order_by(
        Meta.data.desc()
    ).first()


    if meta is None:

        db.close()

        return {
            "erro": "Paciente não possui meta cadastrada"
        }


    # Pega a avaliação mais recente

    avaliacao_atual = db.query(Avaliacao).filter(
        Avaliacao.paciente_id == paciente_id
    ).order_by(
        Avaliacao.data.desc()
    ).first()


    if avaliacao_atual is None:

        db.close()

        return {
            "erro": "Paciente não possui avaliações"
        }


    peso_atual = avaliacao_atual.peso

    peso_meta = meta.peso_meta


    # Pega a primeira avaliação

    avaliacao_inicial = db.query(Avaliacao).filter(
        Avaliacao.paciente_id == paciente_id
    ).order_by(
        Avaliacao.data.asc()
    ).first()


    peso_inicial = avaliacao_inicial.peso


    # -----------------------------------------------------
    # CÁLCULO DO PROGRESSO
    # -----------------------------------------------------

    total_a_perder = peso_inicial - peso_meta

    ja_perdeu = peso_inicial - peso_atual


    if total_a_perder <= 0:

        progresso = 100

    else:

        progresso = (
            ja_perdeu / total_a_perder
        ) * 100


    progresso = round(

        max(
            0,
            min(progresso, 100)
        ),

        2
    )


    falta = round(

        peso_atual - peso_meta,

        2
    )


    db.close()


    return {

        "paciente_id": paciente.id,

        "paciente": paciente.nome,

        "objetivo": meta.objetivo,

        "peso_inicial": peso_inicial,

        "peso_atual": peso_atual,

        "peso_meta": peso_meta,

        "falta": falta,

        "progresso_percentual": progresso
    }
