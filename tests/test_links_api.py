# from .conftest import client
import pytest
from datetime import datetime, timedelta, timezone


@pytest.mark.asyncio(loop_scope="session")
async def test_create_link(ac):
    response = await ac.post("/links/shorten", json={
        "orig_url": "http://google.com",
    })
    assert response.status_code == 200


@pytest.mark.asyncio(loop_scope="session")
async def test_create_link_wrong_url(ac):
    response = await ac.post("/links/shorten", json={
        "orig_url": "wrong_url",
    })
    assert response.status_code == 400
    data = response.json()
    assert data['detail']['error'] == "Wrong URL"


@pytest.mark.asyncio(loop_scope="session")
async def test_create_link_with_custom_code(ac):
    response = await ac.post("/links/shorten", json={
        "orig_url": "http://google.com",
        "custom_alias": "12345678",
    })
    assert response.status_code == 200
    data = response.json()
    assert data['data'] == "12345678"


@pytest.mark.asyncio(loop_scope="session")
async def test_create_link_wrong_code(ac):
    response = await ac.post("/links/shorten", json={
        "orig_url": "http://google.com",
        "custom_alias": "too_big_code",
    })
    assert response.status_code == 400
    data = response.json()
    assert data['detail']['error'] == "Short code must be 8 symbols"


@pytest.mark.asyncio(loop_scope="session")
async def test_create_link_with_already_existed_custom_code(ac):
    response = await ac.post("/links/shorten", json={
        "orig_url": "http://google.com",
        "custom_alias": "12345678",
    })
    assert response.status_code == 400
    data = response.json()
    assert data['detail']['error'] == "There is already link with code: 12345678"


@pytest.mark.asyncio(loop_scope="session")
async def test_create_link_with_exp_date(ac):
    response = await ac.post("/links/shorten", json={
        "orig_url": "http://google.com",
        "custom_alias": "qwertyui",
        "expires_at": "2999-03-15T14:30:00Z",
    })
    assert response.status_code == 200
    data = response.json()
    assert data['data'] == "qwertyui"


@pytest.mark.asyncio(loop_scope="session")
async def test_create_link_wrong_exp_date(ac):
    response = await ac.post("/links/shorten", json={
        "orig_url": "http://google.com",
        "expires_at": "1970-03-15T14:30:00Z",
    })
    assert response.status_code == 400
    data = response.json()
    assert data['detail']['error'] == "Incorrect expiration date"


@pytest.mark.asyncio(loop_scope="session")
async def test_get_link(ac):
    response = await ac.get("/links/12345678")
    assert response.status_code == 307  # Redirect


@pytest.mark.asyncio(loop_scope="session")
async def test_get_unexisted_link(ac):
    response = await ac.get("/links/11111111")
    assert response.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_get_wrong_link(ac):
    response = await ac.get("/links/1")
    assert response.status_code == 400
    data = response.json()
    assert data['detail']['error'] == "Incorrect short code, it must have 8 symbols"


@pytest.mark.asyncio(loop_scope="session")
async def test_search_code(ac):
    response = await ac.post("/links/shorten", json={
        "orig_url": "http://test_url.com",
    })
    assert response.status_code == 200
    data = response.json()
    code = data['data']

    response = await ac.get('/links/search?original_url=http://test_url.com')
    assert response.status_code == 200
    data = response.json()
    assert data['data'] == [code]


@pytest.mark.asyncio(loop_scope="session")
async def test_search_unexisted_url(ac):
    response = await ac.get('/links/search?original_url=http://noexst.com')
    assert response.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_code(ac_logined):
    response = await ac_logined.post("/links/shorten", json={
        "orig_url": "http://google.com",
        "custom_alias": "11223344",
    })
    assert response.status_code == 200

    response = await ac_logined.delete('/links/11223344')
    assert response.status_code == 200


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_code_wrong_code(ac_logined):
    response = await ac_logined.delete('/links/too_big_code')
    assert response.status_code == 400
    data = response.json()
    assert data['detail']['error'] == "Incorrect short code, it must have 8 symbols"


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_unexisted_code(ac_logined):
    response = await ac_logined.delete('/links/11223344')
    assert response.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_put_code(ac_logined):
    response = await ac_logined.post("/links/shorten", json={
        "orig_url": "http://google.com",
        "custom_alias": "11223344",
    })
    assert response.status_code == 200

    response = await ac_logined.put("/links/11223344", json={
        "custom_alias": "11112222",
        "expires_at": "2999-03-15T14:30:00Z",
    })
    assert response.status_code == 200

    response = await ac_logined.get("/links/11112222")
    assert response.status_code == 307  # Redirect


@pytest.mark.asyncio(loop_scope="session")
async def test_put_generated_code(ac_logined):
    response = await ac_logined.post("/links/shorten", json={
        "orig_url": "http://google.com",
        "custom_alias": "11223344",
    })
    assert response.status_code == 200

    response = await ac_logined.put("/links/11223344", json={})
    assert response.status_code == 200
    data = response.json()

    response = await ac_logined.get(f"/links/{data['data']}")
    assert response.status_code == 307  # Redirect


@pytest.mark.asyncio(loop_scope="session")
async def test_put_already_taken_code(ac_logined):
    response = await ac_logined.put("/links/11223344", json={
        "custom_alias": "11112222",
        "expires_at": "2999-03-15T14:30:00Z",
    })
    assert response.status_code == 400
    data = response.json()
    assert data['detail']['error'] == "There is already link with code: 11112222"


@pytest.mark.asyncio(loop_scope="session")
async def test_put_unexisted_code(ac_logined):
    response = await ac_logined.put("/links/11223344", json={})
    assert response.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_put_wrong_code(ac_logined):
    response = await ac_logined.put("/links/too_big_code", json={})
    assert response.status_code == 400
    data = response.json()
    assert data['detail']['error'] == "Incorrect short code, it must have 8 symbols"


@pytest.mark.asyncio(loop_scope="session")
async def test_put_wrong_input_code(ac_logined):
    response = await ac_logined.put("/links/11223344", json={
        "custom_alias": "too_big_code",
        "expires_at": "2999-03-15T14:30:00Z",
    })
    assert response.status_code == 400
    data = response.json()
    assert data['detail']['error'] == "Incorrect short code, it must have 8 symbols"


@pytest.mark.asyncio(loop_scope="session")
async def test_get_stats(ac_logined_redis):
    response = await ac_logined_redis.post("/links/shorten", json={
        "orig_url": "http://google.com",
        "custom_alias": "get_stat",
    })
    assert response.status_code == 200

    response = await ac_logined_redis.get("/links/get_stat")
    response = await ac_logined_redis.get("/links/get_stat")
    assert response.status_code == 307

    response = await ac_logined_redis.get("/links/get_stat/stats")
    assert response.status_code == 200
    data = response.json()['data']
    assert data['counter'] == 2
    assert datetime.now() - datetime.fromisoformat(data['creation_time']) < timedelta(seconds=1)
    assert datetime.now(timezone.utc) - datetime.fromisoformat(data['last_use_time'], ) < timedelta(seconds=1)
    assert data['original_url'] == "http://google.com"


@pytest.mark.asyncio(loop_scope="session")
async def test_get_stats_unexisted(ac_logined):
    response = await ac_logined.get("/links/noexistd")
    assert response.status_code == 404
