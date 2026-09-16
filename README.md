# Orientação a Objetos em Python — Estudos de Caso

![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)

Repositório de estudo, criado para consolidar e demonstrar na prática os
quatro pilares da Orientação a Objetos (encapsulamento, abstração, herança e
polimorfismo) em Python, junto com peculiaridades da linguagem (duck typing,
dunder methods, `@property`, `@classmethod`/`@staticmethod`, `@dataclass`).

Dois casos práticos, do mais simples ao mais próximo de um cenário real:

- **Caso 1** aplica os pilares num domínio puro de POO, sem dependências externas.
- **Caso 2** usa os mesmos princípios (abstração, composição, polimorfismo),
  só que aplicados a um pipeline real de Machine Learning — e conecta
  diretamente ao Caso 1, usando os mesmos tipos de leitura que a rede de
  monitoramento coleta (vento, temperatura de superfície, pressão) para
  treinar um classificador.

## Sumário

- [Estrutura do repositório](#estrutura-do-repositório)
- [Caso 1 — Rede de Monitoramento Oceanográfico](#caso-1--rede-de-monitoramento-oceanográfico)
- [Caso 2 — Risco de Mar Agitado e Ressaca](#caso-2--risco-de-mar-agitado-e-ressaca)
- [Referência usada para revisar os artefatos](#referência-usada-para-revisar-os-artefatos)
- [Autoria](#autoria)

## Estrutura do repositório

| Pasta | Conteúdo |
|---|---|
| [`caso1_simples/`](./caso1_simples) | Rede de monitoramento oceanográfico — POO pura, sem dependências externas. |
| [`caso2_risco_maritimo/`](./caso2_risco_maritimo) | Classificação de risco de mar agitado/ressaca — POO aplicada a um pipeline de Machine Learning (pandas/scikit-learn/XGBoost). |
| [`assets/`](./assets) | Mapa mental dos quatro pilares (imagem + fonte do sketch). |
| [`blog/`](./blog) | Rascunho de um post explicando o Caso 1 em mais detalhe (ainda não publicado). |

## Caso 1 — Rede de Monitoramento Oceanográfico

Domínio escolhido de propósito: é a minha área de formação (Oceanografia),
então o exemplo é meu, não um "Animal/Cachorro" genérico de tutorial.

Uma `EstacaoMonitoramento` abstrata define o contrato (`coletar_leitura()`),
e três subclasses (`BoiaOceanografica`, `EstacaoCosteira`, `EstacaoSubmersa`)
implementam esse contrato cada uma à sua maneira. Uma quarta classe,
`SensorCidadaoCientista`, nem herda da hierarquia — e ainda assim funciona
dentro da rede, por **duck typing**.

Conceitos demonstrados: classe abstrata (`ABC`/`@abstractmethod`),
`@property` com validação, `@classmethod` como construtor alternativo,
`@staticmethod`, `@dataclass`, dunder methods (`__repr__`, `__eq__`,
`__len__`, `__iter__`), polimorfismo e duck typing.

```bash
cd caso1_simples
pip install -r requirements.txt
python src/monitoramento_oceanografico.py   # demo
python -m pytest tests/ -v                  # 9 testes
```

## Caso 2 — Risco de Mar Agitado e Ressaca

Continuação natural do Caso 1: em vez de simular a coleta de leituras, este
caso usa leituras (sintéticas, mas fisicamente plausíveis) dos mesmos tipos
de grandeza que `BoiaOceanografica`, `EstacaoCosteira` e `EstacaoSubmersa`
medem — vento, temperatura de superfície, pressão — somadas a variáveis
oceanográficas adicionais (altura de onda, amplitude de maré), para treinar
um classificador binário: a condição do mar está segura ou perigosa para
banhistas e pequenas embarcações?

O foco não é o modelo de Machine Learning em si (o dataset é sintético e
gerado com seed fixa), e sim a arquitetura por trás dele: uma classe
abstrata `ModeloClassificacao` define o contrato
(`treinar()`/`prever()`/`prever_proba()`), e três subclasses
(`ModeloXGBoost`, `ModeloRandomForest`, `ModeloRegressaoLogistica`)
implementam esse contrato usando três bibliotecas diferentes por baixo. Um
`ComparadorModelos` treina e avalia qualquer lista desses modelos com o
mesmo código — adicionar um quarto modelo não muda uma linha da classe de
comparação.

Arquitetura:

- `CarregadorDados` — encapsula de onde vêm os dados (hoje, um CSV; poderia
  ser outra fonte sem afetar o resto do pipeline).
- `PreProcessador` — **composição** em vez de herança: "tem um"
  `ColumnTransformer` do scikit-learn por dentro, não herda dele.
- `ModeloClassificacao` (ABC) + `ModeloXGBoost` / `ModeloRandomForest` /
  `ModeloRegressaoLogistica` — **abstração e polimorfismo** sobre três
  bibliotecas diferentes.
- `ComparadorModelos` — consome a hierarquia de modelos de forma
  polimórfica.

Conceitos demonstrados: classe abstrata (`ABC`/`@abstractmethod`),
composição ("tem um" `ColumnTransformer`), `@dataclass` como value object
(`ResultadoAvaliacao`), polimorfismo aplicado a bibliotecas de ML reais
(XGBoost, scikit-learn).

**Sobre o dataset:** o CSV não é versionado no repositório — só o script
que o gera (`data/gerar_dataset.py`). Isso é intencional, não uma omissão:
o script usa `numpy.random.default_rng(seed=42)`, e a versão do numpy é
**fixada** (`==`, não `>=`) em `requirements.txt` justamente para que o
CSV gerado seja idêntico, byte a byte, em qualquer máquina — reprodutibilidade
sem precisar distribuir dado nenhum.

```bash
cd caso2_risco_maritimo
pip install -r requirements.txt
python data/gerar_dataset.py                # gera o dataset sintético (reprodutível)
python src/pipeline.py                      # roda o pipeline completo
python -m pytest tests/ -v                  # 7 testes
```

## Referência usada para revisar os artefatos

*Learning Python: Powerful Object-Oriented Programming* (6ª ed., 2025), de
Mark Lutz e David Ascher (O'Reilly) — especificamente a **Parte VI, "Classes
and OOP"** (p. 649–874), usada para conferir cada conceito aplicado nos dois
casos deste repositório.

### Os quatro pilares

| Pilar | Capítulo do livro |
|---|---|
| Abstração | Cap. 26 — *OOP: The Big Picture*, seção *Attribute Inheritance Search* (p. 651), e Cap. 29 — *Class Coding Details*, seção *Abstract Superclasses* (p. 722) |
| Encapsulamento | Cap. 28 — *A More Realistic Example*, seção *Coding Methods* (p. 684) |
| Herança | Cap. 26 — *OOP: The Big Picture* (p. 651), e Cap. 29 — *Class Coding Details*, seção *Inheritance* (p. 718) |
| Polimorfismo | Cap. 31 — *Designing with Classes*, seção *Polymorphism Means Interfaces, Not Call Signatures* (p. 780) |

### Outros conceitos usados nos cases

| Conceito no case | Capítulo do livro |
|---|---|
| Sintaxe básica de classe, atributos, métodos | Cap. 27 — *Class Coding Basics* (p. 661) |
| Composição (`RedeDeMonitoramento` *tem várias* estações, `PreProcessador` *tem um* `ColumnTransformer` — nenhum herda) | Cap. 28 — *A More Realistic Example*, seção *Other Ways to Combine Classes: Composites* (p. 695) |
| Dunder methods / operator overloading (`__repr__`, `__eq__`, `__len__`, `__iter__`) | Cap. 30 — *Operator Overloading* (p. 739) |
| Composição vs. herança (*Is-a* × *Has-a* × *Like-a*/delegação) | Cap. 31 — *Designing with Classes* (p. 779–796) |
| `@property`, `@classmethod`, `@staticmethod`, decorators | Cap. 32 — *Class Odds and Ends*, seções *Properties* (p. 834) e *Static and Class Methods* (p. 837) |

## Autoria

Enatielly Goes — [linkedin.com/in/enatielly-goes](https://www.linkedin.com/in/enatielly-goes/)
