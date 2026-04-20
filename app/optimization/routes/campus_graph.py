import networkx as nx

def create_campus_graph():
    """Cria o grafo dos locais de entrega"""

    G = nx.Graph()

    destinos = {
        "Urutau": {"carga": "misto"},
        "Baja": {"carga": "misto"},
        "Ocean": {"carga": "misto"},
        "Hub": {"carga": "misto"},
        "Sala A18": {"carga": "vermelho"},
        "Sala C18": {"carga": "vermelho"},
        "Callidus": {"carga": "vermelho"},
        "Escadaria biblioteca": {"carga": "vermelho"},
        "Escadaria entrada": {"carga": "vermelho"},
        "FemtonLab": {"carga": "vermelho"},
        "Quadra": {"carga": "azul"},
        "Sala A4": {"carga": "azul"},
    }

    rotas_intermediarias = [
        "jambeiro",
        "jambeiro Saída 1",
        "Corredor Bloco A-B-1.1",
        "Corredor Bloco A-B-1.2",
        "Corredor Bloco A-B-1.3",
        "Corredor Bloco A-B-1.4",
        "Corredor Daetec 1",
        "Corredor B-1.1",
        "Corredor B-1.2",
        "jambeiro Saída 2",
        "Cruza Bloco B->A",
        "Corredor Transicao B->C",
        "Corredor Bloco B-C-1.1",
        "Corredor Bloco B-C-1.2",
        "Corredor Bloco B-C-1.3",
        "Corredor Bloco B-C-1.4",
        "Corredor Bloco C-1.1",
        "Corredor Bloco C-1.2",
        "Corredor Bloco C-1.3",
        "Corredor Bloco C-1.4",
        "Corredor Bloco D-1.1",
        "Corredor Bloco D-1.2",
        "Corredor Bloco D-1.3",
        "Entrada",
        "Entrada lado da Quadra",
        "Entrada lado do Campo",
        "Corredor STEM-RU",
        "Corredor STEM-OCEAN",
    ]

    conexoes = {
        "no_1": ("jambeiro", "jambeiro Saída 1", 464),
        "no_2": ("jambeiro Saída 1", "Corredor Bloco A-B-1.2", 992),
        "no_3": ("Corredor Bloco A-B-1.2", "Corredor Bloco A-B-1.1", 187),
        "no_4": ("Corredor Bloco A-B-1.1", "Sala A4", 2890),
        "no_5": ("Corredor Bloco A-B-1.1", "Corredor Daetec 1", 1487),
        "no_6": ("Corredor Daetec 1", "Entrada", 600), # Não medido
        "no_7": ("Entrada", "Escadaria entrada", 28000), # Não medido
        "no_8": ("Entrada", "Hub", 30000), # Não medido
        "no_9": ("Entrada", "Escadaria biblioteca", 10000), # Não medido
        "no_10": ("Entrada", "Callidus", 20000), # Não medido
        "no_11": ("Entrada", "Corredor Bloco B-C-1.1", 460), # Não medido
        "no_12": ("Escadaria entrada", "Hub", 35000), # Não medido
        "no_13": ("Escadaria entrada", "Escadaria biblioteca", 40000), # Não medido
        "no_14": ("Hub", "Callidus", 17000), # Não medido
        "no_15": ("Callidus", "FemtonLab", 6000), # Não medido
        "no_16": ("Callidus", "Corredor Bloco D-1.3", 9000), # Não medido
        "no_17": ("Callidus", "Quadra", 10000), # Não medido
        "no_18": ("FemtonLab", "Quadra", 16000), # Não medido
        "no_19": ("Corredor Bloco D-1.3", "Entrada lado da Quadra", 2000), # Não medido
        "no_20": ("Corredor Bloco D-1.3", "Entrada lado do Campo", 9000), # Não medido
        "no_21": ("FemtonLab", "Entrada lado da Quadra", 6000), # Não medido
        "no_22": ("FemtonLab", "Entrada lado do Campo", 8000), # Não medido
        "no_23": ("FemtonLab", "Urutau", 10000), # Não medido
        "no_24": ("FemtonLab", "Corredor STEM-RU", 100000), # Não medido
        "no_25": ("FemtonLab", "Corredor STEM-OCEAN", 105000), # Não medido
        "no_26": ("Urutau", "Entrada lado da Quadra", 3000), # Não medido
        "no_27": ("Ocean", "Corredor STEM-OCEAN", 2000), # Não medido
        "no_28": ("Ocean", "Corredor STEM-RU", 3000), # Não medido
        "no_29": ("Ocean", "Quadra", 5000), # Não medido
        "no_30": ("Ocean", "Baja", 1000), # Não medido
        "no_31": ("Ocean", "Escadaria biblioteca", 9000), # Não medido
        "no_32": ("Ocean", "Corredor Bloco D-1.3", 5500), # Não medido
        "no_33": ("Baja", "Escadaria biblioteca", 9010), # Não medido
        "no_34": ("Baja", "Corredor STEM-OCEAN", 2200), # Não medido
        "no_35": ("Baja", "Corredor STEM-RU", 3300), # Não medido
        "no_36": ("Baja", "Entrada lado da Quadra", 4400), # Não medido
        "no_37": ("Baja", "Entrada lado do Campo", 5500), # Não medido
        "no_38": ("Baja", "Corredor Bloco D-1.3", 2200), # Não medido
        "no_39": ("Quadra", "Entrada lado da Quadra", 4000), # Não medido
        "no_40": ("Quadra", "Entrada lado do Campo", 10000), # Não medido
        "no_41": ("Quadra", "Corredor Bloco D-1.3", 800), # Não medido
        "no_42": ("Quadra", "Corredor STEM-RU", 1000), # Não medido
        "no_43": ("Quadra", "Corredor STEM-OCEAN", 1200), # Não medido
        "no_44": ("Corredor Bloco D-1.3", "Corredor Bloco D-1.1", 1500), # Não medido
        "no_45": ("Corredor Bloco D-1.3", "Corredor Bloco D-1.2", 1500), # Não medido
        "no_46": ("Corredor Bloco D-1.2", "Corredor Bloco C-1.2", 3500),
        "no_47": ("Corredor Bloco C-1.2", "Corredor Bloco C-1.1", 2332),
        "no_48": ("Corredor Bloco C-1.2", "Sala C18", 2000),
        "no_49": ("Corredor Bloco C-1.2", "Corredor Bloco C-1.3", 1887),
        "no_50": ("Corredor Bloco C-1.3", "Corredor Bloco C-1.4", 3500),
        "no_51": ("Corredor Bloco C-1.4", "Corredor Bloco B-C-1.1", 550), # Não medido
        "no_52": ("Corredor Bloco C-1.4", "Corredor Bloco B-C-1.2", 750), # Não medido
        "no_53": ("Corredor Bloco B-C-1.2", "Corredor Transicao B->C", 820),
        "no_54": ("Corredor Bloco B-C-1.2", "Corredor Bloco B-C-1.3", 200), # Não medido
        "no_55": ("Corredor Bloco B-C-1.3", "Corredor Bloco C-1.1", 3400),
        "no_56": ("Corredor Bloco B-C-1.3", "Corredor Bloco B-C-1.4", 1500), # Não medido
        "no_57": ("Corredor Bloco B-C-1.4", "Corredor Bloco D-1.3", 1500), # Não medido
        "no_58": ("Corredor Bloco D-1.1", "Corredor Bloco A-B-1.4", 2888),
        "no_59": ("Corredor Bloco A-B-1.4", "Corredor Bloco A-B-1.3", 2306),
        "no_60": ("Corredor Bloco A-B-1.4", "Sala A18", 1500),
        "no_61": ("Corredor Bloco A-B-1.3", "Corredor Bloco A-B-1.2", 2236),
        "no_62": ("Corredor Daetec 1", "Corredor B-1.1", 1987),
        "no_63": ("Corredor B-1.1", "Cruza Bloco B->A", 1487),
        "no_64": ("Cruza Bloco B->A", "jambeiro Saída 2", 1348),
        "no_65": ("Corredor B-1.1", "Corredor B-1.2", 1487),
        "no_66": ("Corredor B-1.2", "Corredor Transicao B->C", 1500),
        "no_67": ("Corredor Bloco A-B-1.3", "Sala A18", 1500),
    }

    G.add_nodes_from(destinos.keys())
    G.add_nodes_from(rotas_intermediarias)

    nx.set_node_attributes(G, destinos)

    for u, v, w in conexoes.values():
        G.add_edge(u, v, weight=w)

    return G

def get_travel_matrix(G):
    """Converte o grafo em uma matriz de tempos/distâncias para o roteamento"""

    nodes = list(G.nodes())
    matriz = nx.floyd_warshall_numpy(G, weight='weight')
    return matriz, nodes