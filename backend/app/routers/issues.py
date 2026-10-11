from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi import status as http_status

from app.dependencies import CurrentUser, FirestoreDB, get_current_user
from app.schemas.issue import Issue, IssueCreate, IssuePage, IssuePriority, IssueStatus, IssueSummary, IssueUpdate
from app.services import issues as issues_service

router = APIRouter(prefix='/issues', tags=['issues'], dependencies=[Depends(get_current_user)])


@router.get('/summary')
async def get_summary(db: FirestoreDB) -> IssueSummary:
    """
    Get the issues summary details
    :param db: database
    :return: summary
    """
    return await issues_service.get_summary(db)


@router.get('')
async def list_issues(
    db: FirestoreDB,
    status: IssueStatus | None = None,
    priority: IssuePriority | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    # firestore ids can't be empty or contain '/'
    cursor: Annotated[str | None, Query(min_length=1, pattern=r'^[^/]+$')] = None,
) -> IssuePage:
    """
    Get a paginated response of issues limited by the limit parameter
    :param db: database
    :param status: status to filter
    :param priority: priority to filter
    :param limit: limit of issues
    :param cursor: cursor for fetching next pages
    :return: paginated response
    """
    try:
        return await issues_service.list_issues(db, status=status, priority=priority, limit=limit, cursor=cursor)
    except issues_service.InvalidCursorError:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail='Invalid cursor')


@router.post('', status_code=http_status.HTTP_201_CREATED)
async def create_issue(data: IssueCreate, user: CurrentUser, db: FirestoreDB) -> Issue:
    """
    Create a new issue
    :param data: issue data
    :param user: user that is creating the issue
    :param db: database
    :return: created issue
    """
    return await issues_service.create_issue(db, data, user.username)


@router.patch('/{issue_id}')
async def update_issue(issue_id: str, data: IssueUpdate, db: FirestoreDB) -> Issue:
    """
    Updates an issue by id
    :param issue_id: issue id
    :param data: issue data to update
    :param db: database
    :return: updated issue
    """
    issue = await issues_service.update_issue(db, issue_id, data)
    if issue is None:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail='Issue not found')
    return issue
