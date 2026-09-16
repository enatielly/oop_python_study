"""
Caso 1 - POO simples: Rede de Monitoramento Oceanográfico
============================================================

Objetivo didático: demonstrar os quatro pilares da Orientação a Objetos
(encapsulamento, abstração, herança e polimorfismo) e algumas peculiaridades
do Python (dataclasses, dunder methods, @property, @classmethod,
@staticmethod e duck typing) num domínio real de oceanografia -- o mesmo
domínio da minha formação acadêmica.

O cenário: uma rede de estações de monitoramento (boias, estações costeiras,
estações submersas) que coletam leituras ambientais. Cada tipo de estação
coleta uma grandeza diferente, mas todas respondem à mesma interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterator


# ---------------------------------------------------------------------------
# Peculiaridade: @dataclass -- atalho pythônico para uma classe que é,
# essencialmente, um container de dados. Gera __init__, __repr__ e __eq__
# automaticamente a partir dos campos declarados.
# ---------------------------------------------------------------------------
@dataclass
class LeituraSensor:
    grandeza: str
    valor: float
    unidade: str
    coletado_em: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __str__(self) -> str:
        return f"{self.grandeza} = {self.valor:.2f} {self.unidade}"


# ---------------------------------------------------------------------------
# ABSTRAÇÃO: a classe base declara O QUE toda estação faz (a interface),
# sem se comprometer com COMO cada tipo específico faz isso.
# `ABC` + `@abstractmethod` impedem que alguém instancie EstacaoMonitoramento
# diretamente, ou crie uma subclasse sem implementar coletar_leitura().
# ---------------------------------------------------------------------------
class EstacaoMonitoramento(ABC):
    """Classe base abstrata para qualquer estação da rede."""

    def __init__(self, nome: str, latitude: float, longitude: float) -> None:
        self.nome = nome
        self.latitude = latitude
        self.longitude = longitude
        # ENCAPSULAMENTO: atributo "protegido" por convenção (um underscore).
        # Não impede acesso externo, mas sinaliza "isto é implementação
        # interna, não a interface pública da classe".
        self._historico: list[LeituraSensor] = []

    @abstractmethod
    def coletar_leitura(self) -> LeituraSensor:
        """Cada subclasse decide o que e como medir. Contrato obrigatório."""
        raise NotImplementedError

    @property
    @abstractmethod
    def tipo(self) -> str:
        """Também pode ser abstrato: força cada subclasse a se identificar."""
        raise NotImplementedError

    def status(self) -> str:
        """
        Método concreto que já usa POLIMORFISMO: não sabe (nem precisa saber)
        qual subclasse está por trás -- só chama coletar_leitura() e confia
        que cada uma sabe fazer a sua parte.
        """
        leitura = self.coletar_leitura()
        self._historico.append(leitura)
        return f"[{self.tipo}] {self.nome}: {leitura}"

    @property
    def total_leituras(self) -> int:
        """ENCAPSULAMENTO pythônico: exposto como atributo, mas é somente
        leitura -- não existe um `total_leituras.setter`."""
        return len(self._historico)

    @staticmethod
    def metros_para_pes(metros: float) -> float:
        """@staticmethod: função utilitária que pertence à classe por
        contexto, mas não depende de nenhuma instância específica."""
        return metros * 3.28084

    def __repr__(self) -> str:
        # Dunder method: define como o objeto aparece no REPL/debugger.
        return f"{self.__class__.__name__}(nome={self.nome!r})"

    def __eq__(self, other: object) -> bool:
        # Dunder method: permite comparar duas estações com ==.
        if not isinstance(other, EstacaoMonitoramento):
            return NotImplemented
        return self.nome == other.nome


# ---------------------------------------------------------------------------
# HERANÇA: cada subclasse reaproveita __init__, status(), total_leituras
# e metros_para_pes() da classe base, e só implementa o que é específico.
# ---------------------------------------------------------------------------
class BoiaOceanografica(EstacaoMonitoramento):
    """Boia fundeada que mede temperatura da superfície do mar."""

    def __init__(self, nome: str, latitude: float, longitude: float, profundidade_ancoragem: float) -> None:
        super().__init__(nome, latitude, longitude)
        self.profundidade_ancoragem = profundidade_ancoragem  # usa o setter da property abaixo

    @property
    def profundidade_ancoragem(self) -> float:
        return self._profundidade_ancoragem

    @profundidade_ancoragem.setter
    def profundidade_ancoragem(self, valor: float) -> None:
        # ENCAPSULAMENTO com validação: impossível criar uma boia com
        # profundidade de ancoragem negativa, mesmo por engano.
        if valor <= 0:
            raise ValueError("profundidade_ancoragem deve ser positiva")
        self._profundidade_ancoragem = valor

    @property
    def tipo(self) -> str:
        return "Boia Oceanográfica"

    def coletar_leitura(self) -> LeituraSensor:
        # Simulação simples de leitura de temperatura de superfície.
        temperatura = 27.5 - (self.profundidade_ancoragem / 1000)
        return LeituraSensor(grandeza="Temperatura da superfície", valor=temperatura, unidade="°C")


class EstacaoCosteira(EstacaoMonitoramento):
    """Estação fixa em terra que mede velocidade do vento."""

    def __init__(self, nome: str, latitude: float, longitude: float, altitude: float) -> None:
        super().__init__(nome, latitude, longitude)
        self.altitude = altitude

    @classmethod
    def from_config(cls, config: dict) -> "EstacaoCosteira":
        """@classmethod: construtor alternativo a partir de um dicionário de
        configuração -- padrão comum ao carregar estações de um arquivo
        JSON/YAML de configuração da rede."""
        return cls(
            nome=config["nome"],
            latitude=config["latitude"],
            longitude=config["longitude"],
            altitude=config.get("altitude", 0.0),
        )

    @property
    def tipo(self) -> str:
        return "Estação Costeira"

    def coletar_leitura(self) -> LeituraSensor:
        vento = 12.0 + (self.altitude / 100)
        return LeituraSensor(grandeza="Velocidade do vento", valor=vento, unidade="m/s")


class EstacaoSubmersa(EstacaoMonitoramento):
    """Estação de fundo que mede pressão hidrostática."""

    def __init__(self, nome: str, latitude: float, longitude: float, profundidade_operacional: float) -> None:
        super().__init__(nome, latitude, longitude)
        if profundidade_operacional < 0:
            raise ValueError("profundidade_operacional não pode ser negativa")
        self.profundidade_operacional = profundidade_operacional

    @property
    def tipo(self) -> str:
        return "Estação Submersa"

    def coletar_leitura(self) -> LeituraSensor:
        pressao = 1 + (self.profundidade_operacional / 10)  # ~1 atm a cada 10 m
        return LeituraSensor(grandeza="Pressão hidrostática", valor=pressao, unidade="atm")


# ---------------------------------------------------------------------------
# DUCK TYPING: esta classe NÃO herda de EstacaoMonitoramento -- mas tem um
# coletar_leitura() e um atributo `nome` e `tipo`, então funciona
# perfeitamente dentro de RedeDeMonitoramento.coletar_todas(). Em Python,
# o que importa é o objeto SABER FAZER o que é esperado, não a árvore de
# herança dele. "Se anda como pato e grasna como pato, é um pato."
# ---------------------------------------------------------------------------
class SensorCidadaoCientista:
    """Sensor amador, mantido por um voluntário -- fora da rede oficial."""

    def __init__(self, nome: str) -> None:
        self.nome = nome
        self.tipo = "Sensor Cidadão"

    def coletar_leitura(self) -> LeituraSensor:
        return LeituraSensor(grandeza="Temperatura da superfície", valor=26.8, unidade="°C")


class RedeDeMonitoramento:
    """Agrega várias estações (de qualquer tipo) e as trata de forma uniforme."""

    def __init__(self, nome_rede: str) -> None:
        self.nome_rede = nome_rede
        self._estacoes: list = []

    def adicionar_estacao(self, estacao) -> None:
        self._estacoes.append(estacao)

    def __len__(self) -> int:
        # Dunder method: permite usar len(rede).
        return len(self._estacoes)

    def __iter__(self) -> Iterator:
        # Dunder method: permite usar `for estacao in rede:`.
        return iter(self._estacoes)

    def coletar_todas(self) -> list[str]:
        """
        POLIMORFISMO + DUCK TYPING em ação: não importa se o item é uma
        BoiaOceanografica, uma EstacaoSubmersa ou um SensorCidadaoCientista
        que nem herda da hierarquia -- todos respondem a `.coletar_leitura()`
        e `.tipo`, então o loop funciona igual para todos.
        """
        return [estacao.status() if hasattr(estacao, "status") else
                f"[{estacao.tipo}] {estacao.nome}: {estacao.coletar_leitura()}"
                for estacao in self._estacoes]


def demo() -> None:
    rede = RedeDeMonitoramento("Rede PEM-NE (exemplo didático)")

    rede.adicionar_estacao(BoiaOceanografica("Boia-01", -8.05, -34.9, profundidade_ancoragem=200))
    rede.adicionar_estacao(
        EstacaoCosteira.from_config({"nome": "Costeira-Recife", "latitude": -8.06, "longitude": -34.88, "altitude": 15})
    )
    rede.adicionar_estacao(EstacaoSubmersa("Submersa-03", -8.10, -34.95, profundidade_operacional=850))
    rede.adicionar_estacao(SensorCidadaoCientista("Voluntário-Praia-do-Pina"))  # duck typing

    print(f"Rede: {rede.nome_rede} -- {len(rede)} estações\n")
    for linha in rede.coletar_todas():
        print(linha)

    print()
    boia = BoiaOceanografica("Boia-Teste", 0, 0, profundidade_ancoragem=100)
    print(f"200 m equivalem a {EstacaoMonitoramento.metros_para_pes(200):.1f} pés")
    print(f"repr da boia: {boia!r}")
    print(f"Boia-01 == Boia-Teste? {BoiaOceanografica('Boia-01', 0, 0, 10) == boia}")


if __name__ == "__main__":
    demo()
