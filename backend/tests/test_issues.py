from datetime import UTC, datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient
from google.cloud.firestore import Client

VALID_ISSUE = {'title': 'Broken button', 'description': 'The save button does nothing', 'priority': 'high'}


def create_issue(client: TestClient, headers: dict[str, str], **overrides: str) -> dict[str, Any]:
    response = client.post('/issues', json={**VALID_ISSUE, **overrides}, headers=headers)
    assert response.status_code == 201
    return response.json()


@pytest.mark.parametrize(('method', 'path'), [
    ('get', '/issues'),
    ('post', '/issues'),
    ('patch', '/issues/any-id'),
    ('get', '/issues/summary'),
])
def test_endpoints_require_token(client: TestClient, method: str, path: str):
    response = client.request(method, path, json={})

    assert response.status_code == 401


def test_create_issue(client: TestClient, user: dict[str, str], auth_headers: dict[str, str]):
    response = client.post('/issues', json=VALID_ISSUE, headers=auth_headers)

    assert response.status_code == 201
    issue = response.json()
    assert issue['id']
    assert issue['title'] == VALID_ISSUE['title']
    assert issue['description'] == VALID_ISSUE['description']
    assert issue['priority'] == 'high'
    assert issue['status'] == 'open'
    assert issue['created_by'] == user['username']
    assert issue['created_at'] == issue['updated_at']


def test_created_issue_is_persisted(client: TestClient, auth_headers: dict[str, str]):
    created = create_issue(client, auth_headers)

    issues = client.get('/issues', headers=auth_headers).json()['items']

    assert [issue['id'] for issue in issues] == [created['id']]


def test_create_issue_strips_whitespace(client: TestClient, auth_headers: dict[str, str]):
    issue = create_issue(client, auth_headers, title='  Broken button  ')

    assert issue['title'] == 'Broken button'


@pytest.mark.parametrize('payload', [
    {**VALID_ISSUE, 'title': '   '},
    {**VALID_ISSUE, 'description': ''},
    {**VALID_ISSUE, 'title': 'x' * 201},
    {**VALID_ISSUE, 'priority': 'urgent'},
    {**VALID_ISSUE, 'status': 'done'},
    {'title': 'No description', 'priority': 'low'},
    {'description': 'No title', 'priority': 'low'},
    {'title': 'No priority', 'description': 'Missing priority'},
])
def test_create_issue_invalid_payload(client: TestClient, auth_headers: dict[str, str], payload: dict[str, str]):
    response = client.post('/issues', json=payload, headers=auth_headers)

    assert response.status_code == 422


def test_list_issues_empty(client: TestClient, auth_headers: dict[str, str]):
    response = client.get('/issues', headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {'items': [], 'next_cursor': None}


def test_list_issues_newest_first(client: TestClient, auth_headers: dict[str, str]):
    first = create_issue(client, auth_headers, title='First')
    second = create_issue(client, auth_headers, title='Second')

    issues = client.get('/issues', headers=auth_headers).json()['items']

    assert [issue['id'] for issue in issues] == [second['id'], first['id']]


@pytest.fixture
def mixed_issues(client: TestClient, auth_headers: dict[str, str]) -> dict[str, str]:
    ids = {
        'open_high': create_issue(client, auth_headers, priority='high')['id'],
        'open_low': create_issue(client, auth_headers, priority='low')['id'],
        'done_high': create_issue(client, auth_headers, priority='high')['id'],
        'progress_medium': create_issue(client, auth_headers, priority='medium')['id'],
    }
    client.patch(f"/issues/{ids['done_high']}", json={'status': 'done'}, headers=auth_headers)
    client.patch(f"/issues/{ids['progress_medium']}", json={'status': 'in_progress'}, headers=auth_headers)
    return ids


@pytest.mark.parametrize(('params', 'expected'), [
    ({'status': 'open'}, {'open_high', 'open_low'}),
    ({'status': 'done'}, {'done_high'}),
    ({'status': 'in_progress'}, {'progress_medium'}),
    ({'priority': 'high'}, {'open_high', 'done_high'}),
    ({'priority': 'medium'}, {'progress_medium'}),
    ({'status': 'open', 'priority': 'high'}, {'open_high'}),
    ({'status': 'done', 'priority': 'low'}, set()),
])
def test_list_issues_filters(
    client: TestClient,
    auth_headers: dict[str, str],
    mixed_issues: dict[str, str],
    params: dict[str, str],
    expected: set[str],
):
    response = client.get('/issues', params=params, headers=auth_headers)

    assert response.status_code == 200
    assert {issue['id'] for issue in response.json()['items']} == {mixed_issues[name] for name in expected}


@pytest.mark.parametrize('params', [{'status': 'closed'}, {'priority': 'urgent'}])
def test_list_issues_invalid_filter(client: TestClient, auth_headers: dict[str, str], params: dict[str, str]):
    response = client.get('/issues', params=params, headers=auth_headers)

    assert response.status_code == 422


def fetch_all_pages(client: TestClient, headers: dict[str, str], **params: Any) -> list[list[str]]:
    pages: list[list[str]] = []
    cursor = None
    while True:
        query = {**params, **({'cursor': cursor} if cursor else {})}
        body = client.get('/issues', params=query, headers=headers).json()
        pages.append([issue['id'] for issue in body['items']])
        cursor = body['next_cursor']
        if cursor is None:
            return pages


def test_pagination_walks_every_issue_once_in_order(client: TestClient, auth_headers: dict[str, str]):
    created = [create_issue(client, auth_headers, title=f'Issue {n}')['id'] for n in range(5)]

    pages = fetch_all_pages(client, auth_headers, limit=2)

    assert [len(page) for page in pages] == [2, 2, 1]
    assert [issue_id for page in pages for issue_id in page] == list(reversed(created))


def test_pagination_exact_multiple_has_no_empty_last_page(client: TestClient, auth_headers: dict[str, str]):
    for n in range(4):
        create_issue(client, auth_headers, title=f'Issue {n}')

    pages = fetch_all_pages(client, auth_headers, limit=2)

    assert [len(page) for page in pages] == [2, 2]


def test_pagination_with_filters(client: TestClient, auth_headers: dict[str, str]):
    high = [create_issue(client, auth_headers, priority='high')['id'] for _ in range(3)]
    create_issue(client, auth_headers, priority='low')

    pages = fetch_all_pages(client, auth_headers, limit=2, priority='high')

    assert [issue_id for page in pages for issue_id in page] == list(reversed(high))


def test_pagination_with_identical_created_at(
    client: TestClient, auth_headers: dict[str, str], firestore: Client, user: dict[str, str]
):
    same_time = datetime.now(UTC)
    for issue_id in ['a', 'b', 'c', 'd']:
        firestore.collection('issues').document(issue_id).set({
            **VALID_ISSUE,
            'status': 'open',
            'created_by': user['username'],
            'created_at': same_time,
            'updated_at': same_time,
        })

    pages = fetch_all_pages(client, auth_headers, limit=1)

    assert sorted(issue_id for page in pages for issue_id in page) == ['a', 'b', 'c', 'd']


def test_default_limit(client: TestClient, auth_headers: dict[str, str]):
    for n in range(21):
        create_issue(client, auth_headers, title=f'Issue {n}')

    body = client.get('/issues', headers=auth_headers).json()

    assert len(body['items']) == 20
    assert body['next_cursor'] is not None


@pytest.mark.parametrize('limit', [0, 101, -1])
def test_limit_out_of_range(client: TestClient, auth_headers: dict[str, str], limit: int):
    response = client.get('/issues', params={'limit': limit}, headers=auth_headers)

    assert response.status_code == 422


@pytest.mark.parametrize('cursor', ['', 'a/b', 'a/b/c'])
def test_malformed_cursor(client: TestClient, auth_headers: dict[str, str], cursor: str):
    response = client.get('/issues', params={'cursor': cursor}, headers=auth_headers)

    assert response.status_code == 422


def test_unknown_cursor(client: TestClient, auth_headers: dict[str, str]):
    response = client.get('/issues', params={'cursor': 'does-not-exist'}, headers=auth_headers)

    assert response.status_code == 400


def test_update_status(client: TestClient, auth_headers: dict[str, str]):
    created = create_issue(client, auth_headers)

    response = client.patch(f"/issues/{created['id']}", json={'status': 'in_progress'}, headers=auth_headers)

    assert response.status_code == 200
    issue = response.json()
    assert issue['status'] == 'in_progress'
    assert issue['priority'] == created['priority']
    assert issue['updated_at'] > created['updated_at']


def test_update_priority(client: TestClient, auth_headers: dict[str, str]):
    created = create_issue(client, auth_headers, priority='low')

    response = client.patch(f"/issues/{created['id']}", json={'priority': 'high'}, headers=auth_headers)

    assert response.status_code == 200
    assert response.json()['priority'] == 'high'
    assert response.json()['status'] == 'open'


def test_update_status_and_priority(client: TestClient, auth_headers: dict[str, str]):
    created = create_issue(client, auth_headers)

    response = client.patch(
        f"/issues/{created['id']}", json={'status': 'done', 'priority': 'low'}, headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()['status'] == 'done'
    assert response.json()['priority'] == 'low'


def test_update_is_persisted(client: TestClient, auth_headers: dict[str, str]):
    created = create_issue(client, auth_headers)
    client.patch(f"/issues/{created['id']}", json={'status': 'done'}, headers=auth_headers)

    issues = client.get('/issues', headers=auth_headers).json()['items']

    assert issues[0]['status'] == 'done'


def test_update_unknown_issue(client: TestClient, auth_headers: dict[str, str]):
    response = client.patch('/issues/does-not-exist', json={'status': 'done'}, headers=auth_headers)

    assert response.status_code == 404


@pytest.mark.parametrize('payload', [
    {},
    {'status': 'closed'},
    {'priority': 'urgent'},
    {'title': 'New title'},
])
def test_update_invalid_payload(client: TestClient, auth_headers: dict[str, str], payload: dict[str, str]):
    created = create_issue(client, auth_headers)

    response = client.patch(f"/issues/{created['id']}", json=payload, headers=auth_headers)

    assert response.status_code == 422


def test_summary_empty(client: TestClient, auth_headers: dict[str, str]):
    response = client.get('/issues/summary', headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {'total': 0, 'by_status': {'open': 0, 'in_progress': 0, 'done': 0}}


def test_summary_counts_by_status(client: TestClient, auth_headers: dict[str, str], mixed_issues: dict[str, str]):
    response = client.get('/issues/summary', headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {'total': 4, 'by_status': {'open': 2, 'in_progress': 1, 'done': 1}}
