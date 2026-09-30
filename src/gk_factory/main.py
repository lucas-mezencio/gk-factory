from collections import Counter
from graphviz import Digraph

# 1. Catálogo Agnóstico de Receitas
# Se o item NÃO estiver aqui, o algoritmo assume que é matéria-prima pura (mina/estoque).
RECEITAS = {
    "furniture_kit_2": {
        "bancada": "Assembly Bench III",
        "qtd_saida": 1,
        "insumos": {"wooden_kit_2": 1, "iron_kit_2": 1},
    },
    "wooden_kit_2": {
        "bancada": "Assembly Bench II",
        "extensao": "Drill Press",
        "qtd_saida": 1,
        "insumos": {"special_wood": 1},
    },
    "iron_kit_2": {
        "bancada": "Smithy II",
        "extensao": "Bellows",
        "qtd_saida": 1,
        "insumos": {"iron_ingot": 1, "clay_molds": 2},
    },
    "iron_ingot": {
        "bancada": "Smithy",
        "qtd_saida": 1,
        "insumos": {"iron_ore": 1, "coal": 1},
    },
    "clay_molds": {
        "bancada": "Smithy II",
        "qtd_saida": 1,
        "insumos": {"clay": 2, "coal": 1},
    },
    "building_kit_2": {
        "bancada": "Assembly Bench III",
        "qtd_saida": 1,
        "insumos": {"wooden_kit_2": 1, "marble_kit": 1},
    },
    "marble_kit": {
        "bancada": "Assembly Bench II",
        "qtd_saida": 1,
        "insumos": {"marble": 2},
    },
    "sculpture_kit_2": {
        "bancada": "Assembly Bench III",
        "qtd_saida": 1,
        "insumos": {"marble": 4},
    },
}


class FabricaBuilder:
    def __init__(self, catalogo):
        self.catalogo = catalogo
        self.contador_instancias = 0
        self.total_maquinas = Counter()
        self.dot = Digraph(
            name="LinhaProducao",
            format="png",
            graph_attr={"rankdir": "LR", "nodesep": "0.6", "ranksep": "1.0"},
            node_attr={
                "fontname": "Helvetica",
                "fontsize": "10",
                "style": "filled, rounded",
            },
            edge_attr={"fontname": "Helvetica", "fontsize": "9", "color": "#455A64"},
        )

    def resolver_item(self, item, qtd_desejada=1):
        """
        Gera recursivamente as máquinas e esteiras necessárias para produzir 'item'.
        Retorna o node_id que cuspiu o item pronto.
        """
        # Caso Base: Não tem receita cadastrada -> É recurso bruto (Mina/Estoque)
        if item not in self.catalogo:
            self.contador_instancias += 1
            raw_id = f"raw_{self.contador_instancias}"
            nome_amigavel = item.replace("_", " ").title()

            self.dot.node(
                raw_id,
                label=f"Estoque\n[{nome_amigavel}]",
                shape="folder",
                fillcolor="#E1F5FE",
                color="#0288D1",
            )
            return raw_id

        # Caso Recursivo: Tem receita -> Instancia uma máquina física dedicada
        dados = self.catalogo[item]
        bancada = dados["bancada"]

        self.contador_instancias += 1
        maquina_id = f"mach_{self.contador_instancias}"
        self.total_maquinas[bancada] += 1

        item_label = item.replace("_", " ").title()
        self.dot.node(
            maquina_id,
            label=f"{bancada}\n(Fazendo: {item_label})",
            shape="box",
            fillcolor="#FFF3E0",
            color="#F57C00",
        )

        # Desce a árvore para cada insumo necessário
        for insumo, qtd_insumo in dados["insumos"].items():
            origem_id = self.resolver_item(insumo, qtd_insumo)
            insumo_label = insumo.replace("_", " ").title()

            # Conecta a esteira da máquina fornecedora para esta máquina
            self.dot.edge(
                origem_id, maquina_id, label=f" {qtd_insumo}x {insumo_label} "
            )

        return maquina_id

    def compilar(self, item_alvo, arquivo_saida="linha_montagem"):
        # Resolve a cascata a partir do item raiz
        no_raiz = self.resolver_item(item_alvo)

        # Adiciona um nó de saída final (o baú onde cai o produto pronto)
        self.contador_instancias += 1
        sink_id = f"sink_{self.contador_instancias}"
        alvo_label = item_alvo.replace("_", " ").title()

        self.dot.node(
            sink_id,
            label=f"Saída Final\n[{alvo_label}]",
            shape="cylinder",
            fillcolor="#E8F5E9",
            color="#388E3C",
        )
        self.dot.edge(no_raiz, sink_id, label=f" Pronto: {alvo_label} ")

        # Renderiza a imagem
        self.dot.render(arquivo_saida, view=True)

        # Relatório de contabilidade de obras de fábrica
        print(f"\n==========================================")
        print(f" LINHA DE MONTAGEM: {alvo_label.upper()}")
        print(f"==========================================")
        print("Total de máquinas físicas que você precisa construir:")
        for maq, total in sorted(self.total_maquinas.items()):
            print(f"  -> {maq}: {total}x")
        print("==========================================\n")


def main():
    builder = FabricaBuilder(RECEITAS)

    # Testa trocar por "iron_kit_1" ou "reinforced_kit"
    builder.compilar("reinforced_kit")


if __name__ == "__main__":
    main()
