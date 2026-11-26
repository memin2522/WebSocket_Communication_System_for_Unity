def test_health(http):
    r = http.get("/health")
    assert r.status_code == 200
    assert r.get_data(as_text=True) == "OK"


def test_pagina_principal_usa_titulo_configurable(http):
    r = http.get("/")
    assert r.status_code == 200
    assert "WebSocket Communication System" in r.get_data(as_text=True)


def test_answer_post_y_get_consume_la_respuesta(http):
    assert http.post("/answer", json={"answer": "42"}).get_json() == {"answer": "42"}
    assert http.get("/answer").get_json() == {"answer": "42"}
    assert http.get("/answer").status_code == 400


def test_question_comportamiento_original_conservado(http):
    # Comportamiento original: POST /question rechaza si no hay pregunta previa,
    # por lo que GET /question siempre responde 400. Ver docs/comportamientos-conocidos.md.
    assert http.post("/question", json={"question": "q"}).status_code == 400
    assert http.get("/question").status_code == 400


def test_openapi_disponible(http):
    assert http.get("/openapi.json").status_code == 200
