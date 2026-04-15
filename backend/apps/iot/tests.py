"""Unit tests for IoT app — MQTT topic parsing."""


def _parse_topic(topic: str):
    # cacao/finca/<finca>/lote/<lote>/<tipo>
    parts = topic.split("/")
    return int(parts[4]), parts[5]


def test_parse_topic_basic():
    lote, tipo = _parse_topic("cacao/finca/1/lote/2/temp_suelo")
    assert lote == 2
    assert tipo == "temp_suelo"


def test_parse_topic_hum_secado():
    lote, tipo = _parse_topic("cacao/finca/3/lote/7/hum_secado")
    assert lote == 7
    assert tipo == "hum_secado"


def test_parse_topic_ph_suelo():
    lote, tipo = _parse_topic("cacao/finca/5/lote/8/ph_suelo")
    assert lote == 8
    assert tipo == "ph_suelo"
