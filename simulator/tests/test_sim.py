"""Unit tests for CacaoTrace simulator."""
from main import FINCAS, Sim


def test_sim_generates_base_readings():
    s = Sim(1, 1, "trinitario", False)
    tipos = [r[0] for r in s.readings()]
    # Non-fermenting lote: 3 base readings only.
    assert tipos == ["temp_suelo", "hum_suelo", "ph_suelo"]


def test_sim_fermenting_has_ferm_and_drying():
    s = Sim(1, 1, "trinitario", True)
    tipos = [r[0] for r in s.readings()]
    assert "temp_ferm" in tipos
    assert "hum_secado" in tipos
    assert len(tipos) == 5


def test_fincas_count_8_lotes():
    total = sum(len(lotes) for _, lotes in FINCAS)
    assert total == 8
    assert len(FINCAS) == 5


def test_advance_increments_ferm_day():
    s = Sim(1, 1, "trinitario", True)
    for _ in range(400):
        s.advance()
    assert s.ferm_day >= 1


def test_readings_have_unidad():
    s = Sim(1, 1, "trinitario", True)
    for tipo, valor, unidad in s.readings():
        assert isinstance(valor, float)
        assert isinstance(unidad, str)


def test_temp_ferm_in_reasonable_range():
    s = Sim(1, 1, "trinitario", True)
    s.ferm_day = 3  # peak
    readings = dict((t, v) for t, v, _ in s.readings())
    assert 40 <= readings["temp_ferm"] <= 55
