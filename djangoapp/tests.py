import json

import pytest


test_url_1 = 'https://semantive.com/'
test_url_2 = 'https://semantive.com/contact/'


@pytest.mark.django_db
def test_app(client):
    # bad task request - no url arg
    resp = client.post('/task/', content_type='application/json')
    assert resp.status_code == 400
    assert 'error_msg' in json.loads(resp.content)

    # bad task request - bad url arg
    resp = client.post('/task/', content_type='application/json', url='http://badurl!!!')
    assert resp.status_code == 400
    assert 'error_msg' in json.loads(resp.content)

    # first page + status checking
    resp = client.post('/task/', content_type='application/json', data={'url': test_url_1})
    assert resp.status_code == 200
    assert json.loads(resp.content) == {'task_id': 1, 'url': test_url_1}

    resp = client.get('/task/1/status/')
    assert resp.status_code == 200
    assert json.loads(resp.content) == {'task_id': 1, 'url': test_url_1, 'text_ready': True, 'images_ready': True}

    # second page + status checking
    resp = client.post('/task/', content_type='application/json', data={'url': test_url_2})
    assert resp.status_code == 200
    assert json.loads(resp.content) == {'task_id': 2, 'url': test_url_2}

    resp = client.get('/task/2/status/')
    assert resp.status_code == 200
    assert json.loads(resp.content) == {'task_id': 2, 'url': test_url_2, 'text_ready': True, 'images_ready': True}

    # update first page + status checking
    resp = client.post('/task/', content_type='application/json', data={'url': test_url_1})
    assert resp.status_code == 200
    assert json.loads(resp.content) == {'task_id': 1, 'url': test_url_1}

    resp = client.get('/task/1/status/')
    assert resp.status_code == 200
    assert json.loads(resp.content) == {'task_id': 1, 'url': test_url_1, 'text_ready': True, 'images_ready': True}

    # get first page text
    resp = client.get('/task/1/text/')
    assert resp.status_code == 200
    assert json.loads(resp.content)['task_id'] == 1
    assert json.loads(resp.content)['url'] == test_url_1
    assert 'semantive' in json.loads(resp.content)['text']

    # get first page images list and images
    resp = client.get('/task/1/images/')
    assert resp.status_code == 200
    assert json.loads(resp.content)['task_id'] == 1
    assert json.loads(resp.content)['url'] == test_url_1
    images_urls = json.loads(resp.content)['images_urls']
    assert isinstance(images_urls, list)
    for img_url in images_urls:
        resp = client.get(img_url)
        assert resp.status_code == 200








