import numpy as np

NUM_INDIVIDUOS = 100
MARGEM_ERRO = 50
NUM_CONTAINERS = 24
NUM_GERACOES = 400

NUM_CARRERISTAS = 3
CAPACIDADE_MAX = 2
VELOCIDADE_CARRERISTA_CM_S = 150.0  # 1,5 m/s

PESO_CONTAINER = 57.0
LARGURA_CONTAINER_CM = 4
VELOCIDADE_GARRA_CM_S = 50

VAZIO = 0
AMARELO = 1  # leve
ROSA = 2  # dobro do peso

TIPO_CONTAINER = {"rosa": ROSA * PESO_CONTAINER, "amarelo": PESO_CONTAINER}

# DIMENSÕES DO BARCO
LARGURA_BARCO = 18.0
COMP_BARCO = 60.0


PIER_NODE = "jambeiro"

DEMANDA_CAMPUS = {
    AMARELO: [
        "Quadra",
        "Sala A4",
        "Urutau",
        "Baja",
        "Ocean",
        "Hub",
    ],
    ROSA: [
        "Urutau",
        "Baja",
        "Ocean",
        "Hub",
        "Sala A18",
        "Sala C18",
        "Callidus",
        "Escadaria biblioteca",
        "Escadaria entrada",
        "FemtonLab",
    ],
}

BARCO_INICIAL = np.array(
    [
        [  # Primeiro andar
            [ROSA, VAZIO, ROSA, VAZIO],
            [ROSA, ROSA, ROSA, AMARELO],
            [ROSA, ROSA, AMARELO, ROSA],
            [VAZIO, VAZIO, VAZIO, ROSA],
        ],
        [  # Segundo andar
            [VAZIO, VAZIO, AMARELO, VAZIO],
            [ROSA, ROSA, AMARELO, AMARELO],
            [AMARELO, AMARELO, AMARELO, AMARELO],
            [VAZIO, VAZIO, VAZIO, AMARELO],
        ],
        [  # Terceiro andar
            [VAZIO, VAZIO, VAZIO, VAZIO],
            [VAZIO, ROSA, AMARELO, VAZIO],
            [VAZIO, VAZIO, AMARELO, VAZIO],
            [VAZIO, VAZIO, VAZIO, VAZIO],
        ],
    ]
)
