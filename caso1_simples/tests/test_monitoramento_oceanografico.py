import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from monitoramento_oceanografico import (
    BoiaOceanografica,
    EstacaoCosteira,
    EstacaoMonitoramento,
    EstacaoSubmersa,
    RedeDeMonitoramento,
    SensorCidadaoCientista,
)


def test_boia_coleta_temperatura():
    boia = BoiaOceanografica("Boia-01", -8.05, -34.9, profundidade_ancoragem=200)
    leitura = boia.coletar_leitura()
    assert leitura.grandeza == "Temperatura da superfície"
    assert leitura.unidade == "°C"


def test_encapsulamento_profundidade_invalida_levanta_erro():
    with pytest.raises(ValueError):
        BoiaOceanografica("Boia-X", 0, 0, profundidade_ancoragem=-10)


def test_estacao_submersa_rejeita_profundidade_negativa():
    with pytest.raises(ValueError):
        EstacaoSubmersa("Sub-X", 0, 0, profundidade_operacional=-1)


def test_classmethod_from_config():
    estacao = EstacaoCosteira.from_config(
        {"nome": "Costeira-Teste", "latitude": -8.0, "longitude": -35.0, "altitude": 10}
    )
    assert estacao.nome == "Costeira-Teste"
    assert estacao.altitude == 10


def test_nao_pode_instanciar_classe_abstrata_diretamente():
    with pytest.raises(TypeError):
        EstacaoMonitoramento("X", 0, 0)  # type: ignore[abstract]


def test_polimorfismo_status_funciona_para_qualquer_subclasse():
    estacoes = [
        BoiaOceanografica("B", 0, 0, 100),
        EstacaoCosteira("C", 0, 0, 10),
        EstacaoSubmersa("S", 0, 0, 500),
    ]
    for estacao in estacoes:
        # cada subclasse implementa coletar_leitura() de um jeito, mas
        # status() -- herdado da classe base -- funciona igual para todas.
        assert estacao.tipo in estacao.status()


def test_duck_typing_sensor_cidadao_funciona_na_rede():
    rede = RedeDeMonitoramento("Teste")
    rede.adicionar_estacao(BoiaOceanografica("B", 0, 0, 100))
    rede.adicionar_estacao(SensorCidadaoCientista("Voluntário"))  # não herda de EstacaoMonitoramento

    resultados = rede.coletar_todas()
    assert len(resultados) == 2
    assert any("Sensor Cidadão" in linha for linha in resultados)


def test_dunder_len_e_iter_da_rede():
    rede = RedeDeMonitoramento("Teste")
    rede.adicionar_estacao(BoiaOceanografica("B1", 0, 0, 100))
    rede.adicionar_estacao(BoiaOceanografica("B2", 0, 0, 150))

    assert len(rede) == 2
    assert [e.nome for e in rede] == ["B1", "B2"]


def test_dunder_eq_compara_por_nome():
    b1 = BoiaOceanografica("Boia-01", 0, 0, 100)
    b2 = BoiaOceanografica("Boia-01", 5, 5, 300)
    b3 = BoiaOceanografica("Boia-02", 0, 0, 100)
    assert b1 == b2
    assert b1 != b3
