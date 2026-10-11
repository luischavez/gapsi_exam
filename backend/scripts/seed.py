import asyncio
import random
from datetime import UTC, datetime, timedelta

from app.database import get_db
from app.internal.security import hash_password
from app.schemas.issue import IssuePriority, IssueStatus

USERS = [
    {'username': 'user1', 'password': 'demo_user1pass'},
    {'username': 'user2', 'password': 'demo_user2pass'},
]

ISSUES_COUNT = 50

BASE_ISSUE = {
    'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore.',
}


def build_issues() -> list[dict]:
    return [
        {
            **BASE_ISSUE,
            # fixed ids so running the seed again overwrites them instead of creating duplicates
            'id': f'seed-{number}',
            'title': f'Test issue {number}',
            'priority': random.choice(list(IssuePriority)),
            'status': random.choice(list(IssueStatus)),
            'created_by': random.choice(USERS)['username'],
        }
        for number in range(1, ISSUES_COUNT + 1)
    ]


async def main() -> None:
    db = get_db()
    for user in USERS:
        await db.collection('users').document(user['username']).set({
            'password_hash': hash_password(user['password']),
        })
        print(f"user {user['username']} added to the db")

    issues = build_issues()
    batch = db.batch()
    now = datetime.now(UTC)
    for index, issue in enumerate(issues):
        # one issue per hour for sorting purposes
        created_at = now - timedelta(hours=len(issues) - index)
        batch.set(db.collection('issues').document(issue['id']), {
            'title': issue['title'],
            'description': issue['description'],
            'priority': issue['priority'].value,
            'status': issue['status'].value,
            'created_by': issue['created_by'],
            'created_at': created_at,
            'updated_at': created_at,
        })
    await batch.commit()
    print(f'{len(issues)} issues added to the db')


if __name__ == '__main__':
    asyncio.run(main())
