from tinydb import TinyDB, Query
from datetime import datetime, date
import os
import sys
import textwrap

# ------------------------- CORES ANSI E LOGO ------------------------- #
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"

DOGFLOW_LOGO = r"""
 ____             _____ _                 
|  _ \  ___   ___|  ___| | _____      __ 
| | | |/ _ \ / _ \ |_  | |/ _ \ \ /\ / / 
| |_| | (_) |  __/  _| | | (_) \ V  V /  
|____/ \___/ \___|_|   |_|\___/ \_/\_/   

"""

DB_PATH = "buffet_db.json"
db = TinyDB(DB_PATH)

# Tabelas do banco
tpl_table = db.table("templates")      # modelos de checklist (itens padrão)
chk_table = db.table("checklists")     # checklists do dia/turno
insumos_table = db.table("insumos")    # insumos (matérias-primas)
fichas_table = db.table("fichas")      # fichas técnicas (produtos)


def money(v: float) -> str:
    """Formata valores monetários em R$."""
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def find_insumo(nome: str):
    """Busca um insumo cadastrado pelo nome."""
    Q = Query()
    return insumos_table.get(Q.nome == nome.strip())


def custo_da_ficha(ficha: dict) -> float:
    """Calcula o custo total de uma ficha técnica."""
    total = 0.0
    for item in ficha["ingredientes"]:
        total += item["qtd"] * item["custo_unit"]
    return round(total, 2)


# ------------------------- UI BONITA (CAIXAS) ------------------------- #
def clear():
    """Limpa a tela e mostra o cabeçalho do sistema."""
    os.system("cls" if os.name == "nt" else "clear")
    # Logo colorido
    print(RED + DOGFLOW_LOGO + RESET)
    print(YELLOW + BOLD + "      DOGFLOW – Sistema de Gestão Operacional\n" + RESET)

def boxed(title: str, body: str = "", width: int = 72) -> str:
    """Desenha uma caixa com título e corpo opcional (agora com cores)."""
    title = f" {title.strip()} "
    top = BLUE + "╔" + "═" * (width - 2) + "╗" + RESET
    mid = "║" + BOLD + CYAN + title.center(width - 2, "═") + RESET + "║"
    empty = "║" + " " * (width - 2) + "║"
    lines = [top, mid, empty]

    if body:
        for line in body.splitlines():
            for wrapped in textwrap.wrap(line, width=width - 4, replace_whitespace=False):
                lines.append("║ " + wrapped.ljust(width - 4) + " ║")
    lines.append(empty)
    bottom = BLUE + "╚" + "═" * (width - 2) + "╝" + RESET
    lines.append(bottom)
    return "\n".join(lines)


def menu_box(options, title="MENU PRINCIPAL"):
    """Mostra um menu com as opções coloridas."""
    body = []
    for key, label in options:
        body.append(f"{YELLOW}[{key}]{RESET} {label}")
    print(boxed(title, "\n".join(body)))


def pause(msg="\nPressione Enter para continuar..."):
    input(msg)


# ------------------------- DADOS & MODELOS ------------------------- #
DEFAULT_TEMPLATES = [
    {
        "nome": "Abertura – Hot Dog",
        "itens": [
            "Higienização pessoal: lavar mãos, unhas curtas, avental/luvas (POP Higiene Pessoal)",
            "Checagem de gás e exaustão; teste de vazamento com espuma (segurança)",
            "Ligar chapa e banho-maria; pré-aquecer até temperatura operacional",
            "Sanitizar bancadas, pinças, espátulas, facas e tábua (diluição correta do sanitizante)",
            "Conferir validades: pães, salsichas, molhos, bebidas (FIFO/PEPS)",
            "Mise en place: pães cortados, caixas GN com molhos tampadas",
            "Descongelar pães/insumos conforme previsão de vendas (registro de tempo/temperatura)",
            "Checar estoque mínimo do turno (pães, salsichas, guardanapos, embalagens, copos)",
            "Abrir caixa: conferir troco inicial e registrar valor",
            "Briefing rápido da equipe: metas do dia + POPs críticos",
        ],
    },
    {
        "nome": "Operação – Produção & Qualidade",
        "itens": [
            "Controle de temperatura: chapa ≥ 170°C; banho-maria 60–70°C (HACCP PCC)",
            "Cozimento/regeneração de salsichas por batelada; descartar após 2h no aquecimento",
            "Reposição de molhos com etiqueta (data/hora) e tampa; não misturar antigo com novo",
            "Limpeza rápida a cada 30 min: bancadas, alça de geladeira, puxadores e POS",
            "Medição de temperatura de alimentos prontos (≥ 65°C) com termômetro higienizado",
            "Reposição de pães conforme demanda; evitar sobras ao final do turno",
            "Separação de áreas/utensílios crus x prontos (evitar contaminação cruzada)",
            "Registro de vendas fora do sistema (contingência) — lançar no fim do turno",
            "Coleta de feedback dos clientes (anotar itens mais pedidos e reclamações)",
            "Verificar validade/aparência dos perecíveis a cada 2h; descartar suspeitos",
        ],
    },
    {
        "nome": "Operação – Delivery/Embalagem",
        "itens": [
            "Checar integridade das embalagens, selos e sacolas (sem odor/umidade)",
            "Padronizar montagem (peso do hot dog, sequência de ingredientes, foto-modelo)",
            "Separar pedidos múltiplos por cliente; conferência dupla (itens/bebidas/molhos)",
            "Etiquetar pedido com hora de saída, nome do cliente e observações",
            "Despacho: motorista/entregador registrado; manter alimento protegido do calor externo",
        ],
    },
    {
        "nome": "Fechamento – Limpeza & Caixa",
        "itens": [
            "Desligar chapa/gás e fechar registro; aguardar resfriar para limpeza",
            "Descartar restos conforme POP de resíduos (orgânico/reciclável/óleo)",
            "Lavar e sanitizar utensílios, GN, bancadas, coifa e piso (checklist de pontos críticos)",
            "Conferência de caixa: total do sistema x dinheiro/PIX/cartão; lançar sangria",
            "Atualizar estoque mínimo para o dia seguinte; registrar faltas e perdas",
            "Guardar insumos etiquetados (PEPS), tampados e refrigerados",
            "Checklist final da loja (portas, luzes, gás, lixo externo, documentos)",
        ],
    },
    {
        "nome": "POP – Preparação de Molhos",
        "itens": [
            "Higienizar utensílios e recipientes; conferir validade dos ingredientes",
            "Preparar receita padrão (gramas/ml) — fidelidade à ficha técnica",
            "Envasar em bisnagas/recipientes sanitizados; etiquetar com data/hora e validade",
            "Armazenar refrigerado; controlar primeira saída (PEPS)",
            "Registrar lote do molho em planilha para rastreio",
        ],
    },
    {
        "nome": "POP – Higienização de Equipamentos",
        "itens": [
            "Chapa: raspar resíduos após resfriar; aplicar desengordurante; enxaguar e secar",
            "Banho-maria: esvaziar, remover incrustações e sanitizar; enxaguar",
            "Coifa/filtros: desengordurar, lavar, secar; agendar limpeza profunda semanal",
            "Geladeira/freezer: limpeza de prateleiras; checar borrachas e drenagem",
            "Registrar execução (data/hora/responsável) em planilha ou caderno",
            "Descartar resíduos conforme POP de resíduos (orgânico/reciclável/óleo)",
        ],
    },
]


def restaurar_modelos_recomendados():
    tpl_table.truncate()
    tpl_table.insert_multiple(DEFAULT_TEMPLATES)


def atalho_restaurar_modelos():
    clear()
    print(
        boxed(
            "Atenção",
            "Isso APAGA todos os modelos atuais e carrega os modelos recomendados.\n"
            "Os checklists já criados (histórico) não serão apagados.",
        )
    )
    conf = input("Digite 'SIM' para confirmar: ").strip().upper()
    if conf == "SIM":
        restaurar_modelos_recomendados()
        print("\nModelos restaurados com sucesso!")
    else:
        print("\nOperação cancelada.")
    pause()


def ensure_default_templates():
    if len(tpl_table) == 0:
        tpl_table.insert_multiple(DEFAULT_TEMPLATES)


def today_str() -> str:
    return date.today().isoformat()


def get_or_create_checklist(dia: str, nome_template: str) -> dict:
    QueryChk = Query()
    found = chk_table.get((QueryChk.data == dia) & (QueryChk.template == nome_template))
    if found:
        return found

    tpl = Query()
    modelo = tpl_table.get(tpl.nome == nome_template)
    if not modelo:
        raise ValueError(f"Template '{nome_template}' não existe.")

    itens = [{"nome": n, "done": False, "timestamp": None} for n in modelo["itens"]]
    cid = chk_table.insert({"data": dia, "template": nome_template, "itens": itens})
    return chk_table.get(doc_id=cid)


def list_templates_names():
    return [tpl["nome"] for tpl in tpl_table.all()]


def checklist_progress(reg):
    itens = reg["itens"]
    done = sum(1 for i in itens if i["done"])
    total = len(itens) if itens else 1
    return done, total, int(done * 100 / total)


# ------------------------- FUNÇÕES DE NEGÓCIO ------------------------- #
def iniciar_checklist():
    clear()
    nomes = list_templates_names()
    if not nomes:
        print(boxed("Aviso", "Nenhum modelo cadastrado."))
        return pause()

    body = "Escolha um modelo para iniciar o checklist de HOJE:\n"
    for i, n in enumerate(nomes, start=1):
        body += f"{i}. {n}\n"
    print(boxed("Iniciar Checklist", body))

    try:
        idx = int(input("Número do modelo: ")) - 1
        nome_template = nomes[idx]
    except Exception:
        print(RED + "Opção inválida." + RESET)
        return pause()

    reg = get_or_create_checklist(today_str(), nome_template)
    done, total, pct = checklist_progress(reg)
    print(
        boxed(
            "Checklist criado/carregado",
            f"Data: {reg['data']}\nModelo: {reg['template']}\nProgresso: {done}/{total} ({pct}%)",
        )
    )
    pause()


def marcar_item():
    clear()
    nomes = list_templates_names()
    if not nomes:
        print(boxed("Aviso", "Nenhum template cadastrado."))
        return pause()

    body = "Selecione o checklist do dia para MARCAR itens:\n"
    for i, n in enumerate(nomes, start=1):
        body += f"{i}. {n}\n"
    print(boxed("Marcar Item", body))

    try:
        idx = int(input("Número do modelo: ")) - 1
        nome_template = nomes[idx]
    except Exception:
        print(RED + "Opção inválida." + RESET)
        return pause()

    reg = get_or_create_checklist(today_str(), nome_template)
    itens = reg["itens"]

    # listar itens
    body_lines = []
    for i, it in enumerate(itens, start=1):
        mark = "✔" if it["done"] else "□"
        body_lines.append(f"{i:02d}. {mark} {it['nome']}")
    print(boxed(f"Checklist {reg['template']} – {reg['data']}", "\n".join(body_lines)))

    try:
        choice = int(input("Qual item deseja alternar (0 para voltar)? "))
    except Exception:
        return
    if choice == 0:
        return

    pos = choice - 1
    if 0 <= pos < len(itens):
        itens[pos]["done"] = not itens[pos]["done"]
        itens[pos]["timestamp"] = (
            datetime.now().isoformat(timespec="seconds") if itens[pos]["done"] else None
        )
        chk_table.update({"itens": itens}, doc_ids=[reg.doc_id])
        print("\nItem atualizado!")
    else:
        print("\nÍndice inválido.")
    pause()


def ver_checklist():
    clear()
    registros = sorted(chk_table.search(Query().data == today_str()), key=lambda r: r["template"])
    if not registros:
        print(boxed("Hoje", "Nenhum checklist iniciado."))
        return pause()

    for reg in registros:
        done, total, pct = checklist_progress(reg)
        head = f"{reg['template']} – {reg['data']}  |  Progresso: {done}/{total} ({pct}%)"
        linhas = []
        for i, it in enumerate(reg["itens"], start=1):
            mark = "✔" if it["done"] else "□"
            ts = f" [{it['timestamp']}]" if it["timestamp"] else ""
            linhas.append(f"{i:02d}. {mark} {it['nome']}{ts}")
        print(boxed(head, "\n".join(linhas)))
    pause()


def finalizar_checklist():
    clear()
    nomes = list_templates_names()
    if not nomes:
        print(boxed("Aviso", "Nenhum template cadastrado."))
        return pause()

    body = "Selecione o checklist para FECHAR:\n"
    for i, n in enumerate(nomes, start=1):
        body += f"{i}. {n}\n"
    print(boxed("Finalizar Checklist", body))

    try:
        idx = int(input("Número do modelo: ")) - 1
        nome_template = nomes[idx]
    except Exception:
        print(RED + "Opção inválida." + RESET)
        return pause()

    reg = get_or_create_checklist(today_str(), nome_template)
    done, total, pct = checklist_progress(reg)
    status = "APROVADO" if pct == 100 else "PENDENTE"
    resumo = (
        f"Modelo: {reg['template']}\n"
        f"Data: {reg['data']}\n"
        f"Concluídos: {done}/{total}\n"
        f"Percentual: {pct}%\n"
        f"Status: {status}"
    )
    print(boxed("Resumo do Turno", resumo))
    pause()


# ------------------------- GERENCIAR MODELOS ------------------------- #
def listar_modelos():
    clear()
    if len(tpl_table) == 0:
        print(boxed("Modelos", "Nenhum modelo cadastrado."))
        return pause()

    for tpl in tpl_table.all():
        body = "\n".join([f"- {i}" for i in tpl["itens"]])
        print(boxed(f"Modelo: {tpl['nome']}", body))
    pause()


def criar_modelo():
    clear()
    nome = input("Nome do novo modelo (ex.: Limpeza Semanal): ").strip()
    if not nome:
        print("Nome inválido.")
        return pause()

    itens = []
    print("\nDigite os itens (vazio para encerrar):")
    while True:
        it = input("  - ")
        if not it.strip():
            break
        itens.append(it.strip())

    if not itens:
        print("Modelo precisa ter ao menos um item.")
        return pause()

    tpl_table.insert({"nome": nome, "itens": itens})
    print(GREEN + "Modelo criado com sucesso!" + RESET)
    pause()


def apagar_modelo():
    clear()
    nomes = list_templates_names()
    if not nomes:
        print(boxed("Modelos", "Nenhum modelo para apagar."))
        return pause()

    for i, n in enumerate(nomes, start=1):
        print(f"{i}. {n}")

    try:
        idx = int(input("\nNúmero do modelo para apagar: ")) - 1
        alvo = nomes[idx]
    except Exception:
        print(RED + "Opção inválida." + RESET)
        return pause()

    tpl_table.remove(Query().nome == alvo)
    print("\nModelo removido.")
    pause()


def gerenciar_modelos():
    while True:
        clear()
        menu_box(
            [
                ("1", "Listar modelos"),
                ("2", "Criar modelo"),
                ("3", "Apagar modelo"),
                ("4", "Restaurar modelos recomendados"),
                ("0", "Voltar"),
            ],
            title="GERENCIAR MODELOS",
        )
        op = input("Escolha: ").strip()
        if op == "1":
            listar_modelos()
        elif op == "2":
            criar_modelo()
        elif op == "3":
            apagar_modelo()
        elif op == "4":
            atalho_restaurar_modelos()
        elif op == "0":
            break
        else:
            print(RED + "Opção inválida." + RESET)
            pause()


# ------------------------- GESTÃO DE INSUMOS ------------------------- #
def cadastrar_insumo():
    clear()
    print(
        boxed(
            "Cadastrar Insumo",
            "Informe dados do insumo base para custo.\n"
            "Ex.: 'Pão 50g', unidade = 'un', custo_unit = preço por unidade.",
        )
    )
    nome = input("Nome do insumo: ").strip()
    if not nome:
        return
    unidade = input("Unidade (ex.: un, kg, L, g, ml): ").strip() or "un"
    try:
        custo_unit = float(input("Custo por unidade base (ex.: 1.20): ").replace(",", "."))
    except Exception:
        print("Valor inválido.")
        return pause()

    existente = find_insumo(nome)
    if existente:
        insumos_table.update(
            {"unidade": unidade, "custo_unit": custo_unit},
            doc_ids=[existente.doc_id],
        )
        msg = "Insumo atualizado."
    else:
        insumos_table.insert({"nome": nome, "unidade": unidade, "custo_unit": custo_unit})
        msg = "Insumo cadastrado."
    print("\n" + msg)
    pause()


def listar_insumos():
    clear()
    itens = sorted(insumos_table.all(), key=lambda x: x["nome"].lower())
    if not itens:
        print(boxed("Insumos", "Nenhum insumo cadastrado."))
        return pause()

    linhas = [
        f"- {i['nome']}  ({i['unidade']})  |  custo: {money(i['custo_unit'])}" for i in itens
    ]
    print(boxed("Insumos Cadastrados", "\n".join(linhas)))
    pause()


# ------------------------- FICHA TÉCNICA ------------------------- #
def criar_ou_editar_ficha():
    clear()
    print(
        boxed(
            "Ficha Técnica",
            "Dê um nome ao produto final (ex.: Hot Dog Simples) e adicione os insumos com quantidades.\n"
            "A quantidade deve estar na mesma unidade de custo do insumo (ex.: pão 'un'=1, molho 'g'=30).",
        )
    )
    nome_prod = input("Nome do produto final: ").strip()
    if not nome_prod:
        return

    ingredientes = []
    while True:
        print("\nDigite o NOME do insumo (vazio para terminar).")
        nome_ins = input("  Insumo: ").strip()
        if not nome_ins:
            break
        ins = find_insumo(nome_ins)
        if not ins:
            print("   → Insumo não encontrado. Cadastre primeiro em 'Cadastrar Insumo'.")
            continue
        try:
            qtd = float(input(f"  Quantidade usada ({ins['unidade']}): ").replace(",", "."))
        except Exception:
            print("   → Quantidade inválida.")
            continue
        ingredientes.append(
            {
                "nome": ins["nome"],
                "unidade": ins["unidade"],
                "qtd": qtd,
                "custo_unit": ins["custo_unit"],
            }
        )

    if not ingredientes:
        print("\nNenhum ingrediente informado.")
        return pause()

    custo = custo_da_ficha({"ingredientes": ingredientes})
    preco_venda = input(
        f"Preço de venda sugerido (enter para definir depois) | Custo: {money(custo)} : "
    ).strip()
    preco = float(preco_venda.replace(",", ".")) if preco_venda else None

    # salva/atualiza
    Q = Query()
    found = fichas_table.get(Q.nome_prod == nome_prod)
    payload = {
        "nome_prod": nome_prod,
        "ingredientes": ingredientes,
        "custo": custo,
        "preco": preco,
    }
    if found:
        fichas_table.update(payload, doc_ids=[found.doc_id])
    else:
        fichas_table.insert(payload)

    print(
        boxed(
            "Ficha salva",
            f"Produto: {nome_prod}\nCusto: {money(custo)}\n"
            f"Preço: {(money(preco) if preco else '—')}",
        )
    )
    pause()


def listar_fichas():
    clear()
    fichas = sorted(fichas_table.all(), key=lambda x: x["nome_prod"].lower())
    if not fichas:
        print(boxed("Fichas Técnicas", "Nenhuma ficha cadastrada."))
        return pause()

    for f in fichas:
        custo = f.get("custo") or custo_da_ficha(f)
        preco = f.get("preco")
        body = [
            f"Custo total: {money(custo)}",
            f"Preço de venda: {money(preco) if preco else '—'}",
            "",
            "INGREDIENTES:",
        ]
        for it in f["ingredientes"]:
            body.append(
                f"- {it['nome']}  {it['qtd']} {it['unidade']}  "
                f"(custo unit: {money(it['custo_unit'])})"
            )
        print(boxed(f"Produto: {f['nome_prod']}", "\n".join(body)))
    pause()


def definir_preco():
    clear()
    fichas = sorted(fichas_table.all(), key=lambda x: x["nome_prod"].lower())
    if not fichas:
        print(boxed("Preço de Venda", "Cadastre uma ficha antes."))
        return pause()

    for i, f in enumerate(fichas, start=1):
        print(f"{i}. {f['nome_prod']}")

    try:
        idx = int(input("\nSelecione o produto: ")) - 1
        f = fichas[idx]
    except Exception:
        print("Entrada inválida.")
        return pause()

    custo = f.get("custo") or custo_da_ficha(f)
    print(f"Custo atual calculado: {money(custo)}")
    modo = input("Definir por (1) preço direto ou (2) margem desejada % ? ").strip()
    if modo == "2":
        try:
            margem = float(input("Margem desejada (%): ").replace(",", "."))
        except Exception:
            print("Inválido.")
            return pause()
        preco = round(custo / (1 - margem / 100), 2)
    else:
        try:
            preco = float(input("Preço de venda: ").replace(",", "."))
        except Exception:
            print("Inválido.")
            return pause()

    fichas_table.update({"preco": preco, "custo": custo}, doc_ids=[f.doc_id])
    print("\nPreço atualizado:", money(preco))
    pause()


def relatorio_custos_margens():
    clear()
    fichas = sorted(fichas_table.all(), key=lambda x: x["nome_prod"].lower())
    if not fichas:
        print(boxed("Relatório de Custos", "Nenhuma ficha cadastrada."))
        return pause()

    linhas = []
    for f in fichas:
        custo = f.get("custo") or custo_da_ficha(f)
        preco = f.get("preco") or 0.0
        margem = 0 if not preco else round((preco - custo) / preco * 100, 2)
        linhas.append(
            f"{f['nome_prod']:<24} | Custo: {money(custo):>10} | "
            f"Preço: {money(preco):>10} | Margem: {margem:>6.2f}%"
        )
    print(boxed("Custos & Margens (unitário)", "\n".join(linhas)))
    pause()


def gestao_custos():
    while True:
        clear()
        menu_box(
            [
                ("1", "Cadastrar insumo"),
                ("2", "Listar insumos"),
                ("3", "Criar/Editar ficha técnica"),
                ("4", "Listar fichas técnicas"),
                ("5", "Definir preço de venda"),
                ("6", "Relatório custos & margens"),
                ("0", "Voltar"),
            ],
            title="GESTÃO DE CUSTOS",
        )
        op = input("Escolha: ").strip()
        if op == "1":
            cadastrar_insumo()
        elif op == "2":
            listar_insumos()
        elif op == "3":
            criar_ou_editar_ficha()
        elif op == "4":
            listar_fichas()
        elif op == "5":
            definir_preco()
        elif op == "6":
            relatorio_custos_margens()
        elif op == "0":
            break
        else:
            print("Opção inválida.")
            pause()


# ------------------------- RELATÓRIOS SIMPLES ------------------------- #
def relatorios():
    clear()
    print(
        boxed(
            "Relatórios",
            "1) Progresso de hoje por checklist\n"
            "2) Histórico de percentuais por data (todos os modelos)\n"
            "0) Voltar",
        )
    )
    op = input("Escolha: ").strip()
    if op == "1":
        ver_checklist()
    elif op == "2":
        clear()
        linhas = []
        for reg in sorted(
            chk_table.all(), key=lambda r: (r["data"], r["template"])
        ):
            done, total, pct = checklist_progress(reg)
            linhas.append(
                f"{reg['data']} | {reg['template']:<30} | {done:02d}/{total:02d} => {pct:3d}%"
            )
        print(
            boxed(
                "Histórico (todos os dias)",
                "\n".join(linhas) if linhas else "Sem dados.",
            )
        )
        pause()
    else:
        return


# ------------------------- APLICAÇÃO ------------------------- #
def main():
    ensure_default_templates()
    while True:
        clear()
        menu_box(
            [
                ("1", "Iniciar checklist do dia"),
                ("2", "Marcar/Desmarcar item"),
                ("3", "Ver checklists de hoje"),
                ("4", "Finalizar checklist (resumo do turno)"),
                ("5", "Gerenciar modelos de checklist"),
                ("6", "Gestão de custos e fichas técnicas"),
                ("7", "Relatórios de execução"),
                ("0", "Sair"),
            ],
            title="BUFFET CHECKLIST – SISTEMA DE TERMINAL",
        )
        op = input("Escolha uma opção: ").strip()
        if op == "1":
            iniciar_checklist()
        elif op == "2":
            marcar_item()
        elif op == "3":
            ver_checklist()
        elif op == "4":
            finalizar_checklist()
        elif op == "5":
            gerenciar_modelos()
        elif op == "6":
            gestao_custos()
        elif op == "7":
            relatorios()
        elif op == "0":
            clear()
            print(boxed("Até logo!", "Sucesso no buffet e no projeto!"))
            sys.exit(0)
        else:
            print(RED + "Opção inválida." + RESET)
            pause()


if __name__ == "__main__":
    main()