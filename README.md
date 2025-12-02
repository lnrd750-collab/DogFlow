
# DogFlow — Buffet Checklist (Terminal)

Buffet_Checklist é uma aplicação terminal em Python para gerenciar checklists operacionais de um balcão/fast-food (ex.: hot-dog), controlar insumos, criar fichas técnicas e calcular custos e preços de venda. A interface é simples, baseada em menus de terminal com caixas e cores ANSI.

Observação: o arquivo principal implementado neste repositório é `Buffet_checklist.py`.

## Principais funcionalidades

- Modelos de checklist (templates) com itens padrão (Abertura, Operação, Fechamento, POPs, etc.).
- Criar/carregar checklists diários por template e marcar/desmarcar itens com timestamp.
- Visualizar progresso por checklist e finalizar o turno com resumo (aprovado/pendente).
- Gerenciar templates: listar, criar, apagar e restaurar modelos recomendados (reset).
- Cadastrar insumos (nome, unidade, custo unitário) e listar insumos.
- Criar/editar fichas técnicas (produto final) usando insumos cadastrados.
- Calcular custo total de fichas e definir preço por margem ou valor direto.
- Relatórios simples: progresso do dia e histórico de percentuais por data.
- Armazenamento local usando TinyDB (`buffet_db.json`).

## Requisitos

- Python 3.7+
- tinydb

Instalação do TinyDB:
```
pip install tinydb
```

Observações sobre cores:
- O script usa sequências ANSI para colorir a saída. Em terminais Windows mais antigos pode ser preciso habilitar sequências ANSI ou usar um wrapper como `colorama`. O script não depende de `colorama` por padrão.

## Como usar

1. Clone ou baixe o repositório.
2. Instale as dependências (somente tinydb).
3. Execute:
```
python Buffet_checklist.py
```

Ao iniciar, o menu principal apresenta opções numeradas:

- 1 — Iniciar checklist do dia: cria ou carrega o checklist do dia baseado em um template.
- 2 — Marcar/Desmarcar item: alterna o estado de um item (feito / não feito) e grava timestamp.
- 3 — Ver checklists de hoje: exibe todos os checklists iniciados no dia com progresso e timestamps.
- 4 — Finalizar checklist (resumo do turno): mostra resumo e marca como APROVADO se 100% concluído.
- 5 — Gerenciar modelos de checklist: submenu para listar, criar, apagar e restaurar templates.
- 6 — Gestão de custos e fichas técnicas: submenu para cadastrar insumos, criar fichas, definir preço e ver relatórios.
- 7 — Relatórios de execução: progresso de hoje e histórico.
- 0 — Sair.

Dentro de "Gestão de custos":
- Cadastrar insumo: nome, unidade e custo por unidade.
- Listar insumos: mostra insumos ordenados por nome.
- Criar/Editar ficha técnica: monte um produto final a partir de insumos cadastrados e registre quantidades.
- Listar fichas técnicas: mostra custo e ingredientes.
- Definir preço: por valor direto ou definindo margem desejada.
- Relatório custos & margens: visão rápida de custo, preço e margem.

## Dados e persistência

- Banco local: `buffet_db.json` (TinyDB). Tabelas internas:
  - `templates` — modelos de checklist.
  - `checklists` — registros diários por template e itens com timestamps.
  - `insumos` — insumos base (nome, unidade, custo_unit).
  - `fichas` — fichas técnicas (produto, ingredientes, custo, preço).

- Ao iniciar o programa, se não houver templates, os modelos padrão (DEFAULT_TEMPLATES) são carregados automaticamente.

- Para restaurar os modelos recomendados manualmente: Gerenciar modelos → Restaurar modelos recomendados (atenção: apaga modelos atuais, não apaga histórico de checklists).

## Estrutura básica das entidades

- Template:
  - nome: str
  - itens: [str]

- Checklist:
  - data: "YYYY-MM-DD"
  - template: nome do template
  - itens: [{ "nome": str, "done": bool, "timestamp": ISO-8601 | None }]

- Insumo:
  - nome: str
  - unidade: str (ex.: un, kg, g, ml)
  - custo_unit: float

- Ficha técnica:
  - nome_prod: str
  - ingredientes: [{ nome, unidade, qtd, custo_unit }]
  - custo: float (calculado)
  - preco: float | None

## Boas práticas e dicas

- Cadastre os insumos antes de criar fichas técnicas — o editor de ficha busca os insumos por nome.
- Use unidades consistentes: a quantidade informada na ficha deve corresponder à unidade do insumo.
- Faça backups periódicos de `buffet_db.json` se for usado em produção.
- Para habilitar melhor suporte a cores no Windows, considere instalar e inicializar `colorama` no início do script:
  ```
  pip install colorama
  ```
  e, no código:
  ```py
  from colorama import init
  init()
  ```
  (isso não está incluído por padrão)

## Possíveis melhorias (próximos passos)

- Exportar relatórios para CSV/Excel.
- Autenticação/usuários para registrar responsáveis pelos itens.
- Sincronização/backup remoto (por exemplo GitHub/GCS).
- Interface gráfica ou web (para uso em tablets/telefones).
- Testes automatizados e validação de entradas mais robusta.

## Licença

Sem licença explícita no repositório. Se desejar, adicione um arquivo LICENSE com a licença escolhida (por exemplo MIT).

## Contato / Contribuição

Sinta-se à vontade para abrir issues, propor correções ou melhorias. Para contribuir:
- Crie uma branch, ajuste o código / documentação e abra um PR descrevendo as alterações.

