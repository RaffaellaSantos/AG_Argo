import numpy as np

NUM_INDIVIDUOS = 100
MARGEM_ERRO = 50
NUM_CONTAINERS = 24
NUM_GERACOES = 401

NUM_CARRERISTAS = 3
CAPACIDADE_MAX = 2

PESO_CONTAINER = 57.0

VAZIO = 0
AZUL = 1      #leve
VERMELHO = 2  #dobro do peso 

TIPO_CONTAINER = {"vermelho": 2 * PESO_CONTAINER, "azul": PESO_CONTAINER}

#DIMENSÕES DO BARCO
LARGURA_BARCO = 17.0
COMP_BARCO = 60.0
CENTRO_BARCO = 8.5

PIER_NODE = "jambeiro"

DEMANDA_CAMPUS = {
    AZUL: [
        "Quadra",
        "Sala A4",
        "Urutau",
        "Baja",
        "Ocean",
        "Hub",
    ],
    VERMELHO: [
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
            [VERMELHO, VAZIO, VERMELHO, VAZIO],
            [VERMELHO, VERMELHO, VERMELHO, AZUL],
            [VERMELHO, VERMELHO, AZUL, VERMELHO],
            [VAZIO, VAZIO, VAZIO, VERMELHO],
        ],
        [  # Segundo andar
            [VAZIO, VAZIO, AZUL, VAZIO],
            [VERMELHO, VERMELHO, AZUL, AZUL],
            [AZUL, AZUL, AZUL, AZUL],
            [VAZIO, VAZIO, VAZIO, AZUL],
        ],
        [  # Terceiro andar
            [VAZIO, VAZIO, VAZIO, VAZIO],
            [VAZIO, VERMELHO, AZUL, VAZIO],
            [VAZIO, VAZIO, AZUL, VAZIO],
            [VAZIO, VAZIO, VAZIO, VAZIO],
        ],
    ]
)
