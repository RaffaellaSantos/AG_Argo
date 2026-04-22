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
        "no_6": ("Corredor Daetec 1", "Entrada", 600), # medido MAPS
        "no_7": ("Entrada", "Escadaria entrada", 9900), # medido MAPS
        "no_8": ("Entrada", "Hub", 22500), # medido MAPS
        "no_9": ("Entrada", "Escadaria biblioteca", 1500), # medido MAPS
        "no_10": ("Entrada", "Callidus", 26900), # medido MAPS
        "no_11": ("Entrada", "Corredor Bloco B-C-1.1", 460), # medido MAPS
        "no_12": ("Escadaria entrada", "Hub", 22000), # medido MAPS
        "no_13": ("Escadaria entrada", "Escadaria biblioteca", 10400), # medido MAPS
        "no_14": ("Hub", "Callidus", 11500), # medido MAPS
        "no_15": ("Callidus", "FemtonLab", 7300), # medido MAPS
        "no_16": ("Callidus", "Corredor Bloco D-1.3", 10300), # medido MAPS
        "no_17": ("Callidus", "Quadra", 12100), # medido MAPS
        "no_18": ("FemtonLab", "Quadra", 17000), # medido MAPS
        "no_19": ("Corredor Bloco D-1.3", "Entrada lado da Quadra", 7800), # medido MAPS
        "no_20": ("Corredor Bloco D-1.3", "Entrada lado do Campo", 9200), # medido MAPS
        "no_21": ("FemtonLab", "Entrada lado da Quadra", 12400), # medido MAPS
        "no_22": ("FemtonLab", "Entrada lado do Campo", 4700), # medido MAPS
        "no_23": ("FemtonLab", "Urutau", 12700), # medido MAPS
        "no_24": ("FemtonLab", "Corredor STEM-RU", 16800), # medido MAPS
        "no_25": ("FemtonLab", "Corredor STEM-OCEAN", 20100), # medido MAPS
        "no_26": ("Urutau", "Entrada lado da Quadra", 3300), # medido MAPS
        "no_27": ("Ocean", "Corredor STEM-OCEAN", 8900), # medido MAPS
        "no_28": ("Ocean", "Corredor STEM-RU", 6100), # medido MAPS
        "no_29": ("Ocean", "Quadra", 6200), # medido MAPS
        "no_30": ("Ocean", "Baja", 1600), # medido MAPS
        "no_31": ("Ocean", "Escadaria biblioteca", 9200), # medido MAPS
        "no_32": ("Ocean", "Corredor Bloco D-1.3", 9400), # medido MAPS
        "no_33": ("Baja", "Escadaria biblioteca", 9300), # medido MAPS
        "no_34": ("Baja", "Corredor STEM-OCEAN", 4200), # medido MAPS
        "no_35": ("Baja", "Corredor STEM-RU", 5700), # medido MAPS
        "no_36": ("Baja", "Entrada lado da Quadra", 8800), # medido MAPS
        "no_37": ("Baja", "Entrada lado do Campo", 14800), # medido MAPS
        "no_38": ("Baja", "Corredor Bloco D-1.3", 9200), # medido MAPS
        "no_39": ("Quadra", "Entrada lado da Quadra", 3200), # medido MAPS
        "no_40": ("Quadra", "Entrada lado do Campo", 10600), # medido MAPS
        "no_41": ("Quadra", "Corredor Bloco D-1.3", 4900), # medido MAPS
        "no_42": ("Quadra", "Corredor STEM-RU", 7400), # medido MAPS
        "no_43": ("Quadra", "Corredor STEM-OCEAN", 8400), # medido MAPS
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