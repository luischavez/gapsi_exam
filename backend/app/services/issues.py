import asyncio
from datetime import UTC, datetime

from google.api_core.exceptions import NotFound
from google.cloud.firestore import AsyncClient, DocumentSnapshot, Query
from google.cloud.firestore_v1.base_query import FieldFilter
from google.cloud.firestore_v1.field_path import FieldPath

from app.schemas.issue import Issue, IssueCreate, IssuePage, IssuePriority, IssueStatus, IssueSummary, IssueUpdate

COLLECTION = 'issues'


def _to_issue(doc: DocumentSnapshot) -> Issue:
    return Issue(id=doc.id, **doc.to_dict())


class InvalidCursorError(Exception):
    pass


async def list_issues(
    db: AsyncClient,
    status: IssueStatus | None = None,
    priority: IssuePriority | None = None,
    limit: int = 20,
    cursor: str | None = None,
) -> IssuePage:
    collection = db.collection(COLLECTION)
    query = collection
    if status is not None:
        query = query.where(filter=FieldFilter('status', '==', status.value))
    if priority is not None:
        query = query.where(filter=FieldFilter('priority', '==', priority.value))
    query = query.order_by('created_at', direction=Query.DESCENDING)
    # tie-breaker, without it issues with the same created_at could repeat or get lost between pages
    query = query.order_by(FieldPath.document_id(), direction=Query.DESCENDING)

    if cursor is not None:
        last = await collection.document(cursor).get()
        if not last.exists:
            raise InvalidCursorError(cursor)
        query = query.start_after(last)

    # one extra doc tells us if there's a next page, so we never return a cursor to an empty one
    docs = [doc async for doc in query.limit(limit + 1).stream()]
    has_more = len(docs) > limit
    docs = docs[:limit]

    return IssuePage(
        items=[_to_issue(doc) for doc in docs],
        next_cursor=docs[-1].id if has_more else None,
    )


async def create_issue(db: AsyncClient, data: IssueCreate, username: str) -> Issue:
    now = datetime.now(UTC)
    ref = db.collection(COLLECTION).document()
    fields = {
        **data.model_dump(mode='json'),
        'status': IssueStatus.OPEN.value,
        'created_by': username,
        'created_at': now,
        'updated_at': now,
    }
    await ref.set(fields)

    return Issue(id=ref.id, **fields)


async def update_issue(db: AsyncClient, issue_id: str, data: IssueUpdate) -> Issue | None:
    ref = db.collection(COLLECTION).document(issue_id)
    changes = {
        **data.model_dump(mode='json', exclude_none=True),
        'updated_at': datetime.now(UTC),
    }
    # update() raises NotFound for missing docs, so there's no need to read it first
    try:
        await ref.update(changes)
    except NotFound:
        return None

    return _to_issue(await ref.get())


async def _count_by_status(db: AsyncClient, status: IssueStatus) -> int:
    query = db.collection(COLLECTION).where(filter=FieldFilter('status', '==', status.value))
    # aggregation query, the count is done by Firestore without downloading the docs
    result = await query.count().get()
    return int(result[0][0].value)


async def get_summary(db: AsyncClient) -> IssueSummary:
    statuses = list(IssueStatus)
    counts = await asyncio.gather(*(_count_by_status(db, status) for status in statuses))
    by_status = dict(zip(statuses, counts))

    return IssueSummary(total=sum(counts), by_status=by_status)
