"""API tests for vote endpoints."""


def test_post_vote_requires_auth(client):
    res = client.post(
        "/vote",
        json={"section_type": "news", "item_id": "x", "vote_type": "up"},
    )
    assert res.status_code == 401


def test_post_vote_success(client, auth_headers):
    _, headers = auth_headers
    res = client.post(
        "/vote",
        headers=headers,
        json={"section_type": "price", "item_id": "BTC|100", "vote_type": "up"},
    )
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
    assert res.json()["action"] in ("created", "updated")


def test_post_vote_twice_same_item_updates(client, auth_headers):
    _, headers = auth_headers
    body = {"section_type": "ai", "item_id": "daily-insight", "vote_type": "up"}
    r1 = client.post("/vote", headers=headers, json=body)
    r2 = client.post("/vote", headers=headers, json={**body, "vote_type": "down"})
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r2.json()["action"] == "updated"


def test_delete_vote_success(client, auth_headers):
    _, headers = auth_headers
    body = {"section_type": "meme", "item_id": "meme-1", "vote_type": "up"}
    client.post("/vote", headers=headers, json=body)
    res = client.request("DELETE", "/vote", headers=headers, json={"section_type": "meme", "item_id": "meme-1"})
    assert res.status_code == 200
    assert res.json()["action"] == "cancelled"


def test_delete_vote_nonexistent_returns_404(client, auth_headers):
    _, headers = auth_headers
    res = client.request(
        "DELETE",
        "/vote",
        headers=headers,
        json={"section_type": "news", "item_id": "no-such-id"},
    )
    assert res.status_code == 404
