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
        self.nos_instanciados = {}
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
        # 1. Se essa máquina (ou estoque) já existe no chão de fábrica, REAPROVEITA!
        if item in self.nos_instanciados:
            return self.nos_instanciados[item]

        # 2. Caso Base: Matéria-prima bruta (Mina/Estoque)
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
            # Salva no cache pra não criar dois baús do mesmo minério
            self.nos_instanciados[item] = raw_id
            return raw_id

        # 3. Caso de Produção: Cria a máquina UMA ÚNICA VEZ
        dados = self.catalogo[item]
        bancada = dados["bancada"]

        self.contador_instancias += 1
        maquina_id = f"mach_{self.contador_instancias}"
        self.total_maquinas[bancada] += 1

        item_label = item.replace("_", " ").title()
        self.dot.node(
            maquina_id,
            label=f"{bancada}\n(Faz: {item_label})",
            shape="box",
            fillcolor="#FFF3E0",
            color="#F57C00",
        )

        # Registra no cache IMEDIATAMENTE antes de descer pros filhos
        # (isso evita loop infinito caso alguém faça cagada de dependência cíclica)
        self.nos_instanciados[item] = maquina_id

        # Desce a esteira pros insumos normalmente
        for insumo, qtd_insumo in dados["insumos"].items():
            origem_id = self.resolver_item(insumo, qtd_insumo)
            insumo_label = insumo.replace("_", " ").title()

            # Aqui tá a mágica: a aresta sai da máquina existente e chega nessa nova
            self.dot.edge(
                origem_id, maquina_id, label=f" {qtd_insumo}x {insumo_label} "
            )

        return maquina_id

    def compilar_projeto(
        self, demandas, nome_projeto="Reforma da Casa", arquivo_saida="projeto_fabrica"
    ):
        """
        Gera a malha completa para atender uma lista de demandas agregadas.
        demandas: dict com formato {"item_alvo": quantidade_necessaria}
        """
        # 1. Cria o Super-Sink (o objetivo unificado da entrega)
        self.contador_instancias += 1
        master_sink_id = f"project_{self.contador_instancias}"

        self.dot.node(
            master_sink_id,
            label=f"OBJETIVO FINAL\n★ {nome_projeto} ★",
            shape="doubleoctagon",
            fillcolor="#C8E6C9",
            color="#2E7D32",
            penwidth="2.0",
        )

        print(f"\n==========================================")
        print(f" PROJETO: {nome_projeto.upper()}")
        print(f"==========================================")
        print("Demandas cadastradas:")
        for item, qtd in demandas.items():
            print(f"  -> {qtd}x {item.replace('_', ' ').title()}")

        # 2. Resolve cada linha de produto do projeto
        for item, qtd in demandas.items():
            # A recursão desce e monta o miolo (ou reaproveita se já existir)
            maquina_produtora = self.resolver_item(item)
            item_label = item.replace("_", " ").title()

            # Conecta a máquina final direto na entrega do projeto
            self.dot.edge(
                maquina_produtora,
                master_sink_id,
                label=f" Entregar: {qtd}x {item_label} ",
                color="#2E7D32",
                penwidth="1.8",
            )

        # 3. Compila a imagem unificada
        self.dot.render(arquivo_saida, view=True)

        print("\nTotal de máquinas físicas consolidadas no chão de fábrica:")
        for maq, total in sorted(self.total_maquinas.items()):
            print(f"  -> {maq}: {total}x")
        print("==========================================\n")


def main():
    builder = FabricaBuilder(RECEITAS)

    # Lista de compras pra reformar a casa do coveiro:
    materiais_casa = {
        "building_kit_2": 6,
        "furniture_kit_2": 6,
        "sculpture_kit_2": 6,
    }

    builder.compilar_projeto(materiais_casa, nome_projeto="reformar squares")


if __name__ == "__main__":
    main()
