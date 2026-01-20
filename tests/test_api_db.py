import pytest


class DummyConn:
    def __init__(self, rows):
        self._rows = rows

    def execute(self, q, params=None):
        class R:
            def __init__(self, rows):
                self._rows = rows

            def fetchall(self):
                return self._rows

        return R(self._rows)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class DummyEngine:
    def __init__(self, rows):
        self._rows = rows

    def connect(self):
        return DummyConn(self._rows)


def test_top_products_and_visual_content(monkeypatch):
    # Provide deterministic rows for top-products and visual-content
    top_rows = [('product_display', 5)]
    vis_rows = [(1, 'data/raw/images/chan_1_12345.jpg', 'product_display', 0.98)]

    # Monkeypatch engine in api.main
    import api.main as main

    main.engine = DummyEngine(top_rows)
    from fastapi.testclient import TestClient

    client = TestClient(main.app)
    r = client.get('/top-products')
    assert r.status_code == 200
    assert r.json()[0]['label'] == 'product_display'

    # patch engine for visual content call
    main.engine = DummyEngine(vis_rows)
    r2 = client.get('/visual-content')
    assert r2.status_code == 200
    assert r2.json()[0]['label'] == 'product_display'
