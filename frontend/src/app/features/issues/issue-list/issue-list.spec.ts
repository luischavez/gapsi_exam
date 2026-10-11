import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of, throwError } from 'rxjs';

import { Issue, IssueFilters, IssuePage, IssueSummary } from '../issue.models';
import { IssuesService } from '../issues.service';
import { IssueList } from './issue-list';

function makeIssue(overrides: Partial<Issue> = {}): Issue {
  return {
    id: '1',
    title: 'Broken button',
    description: 'Nothing happens',
    priority: 'high',
    status: 'open',
    created_by: 'user1',
    created_at: '2026-10-10T10:00:00Z',
    updated_at: '2026-10-10T10:00:00Z',
    ...overrides,
  };
}

const SUMMARY: IssueSummary = { total: 3, by_status: { open: 1, in_progress: 1, done: 1 } };

describe('IssueList', () => {
  let fixture: ComponentFixture<IssueList>;
  let element: HTMLElement;
  let service: {
    list: ReturnType<typeof vi.fn>;
    update: ReturnType<typeof vi.fn>;
    summary: ReturnType<typeof vi.fn>;
  };

  async function render(firstPage: IssuePage): Promise<void> {
    service.list.mockReturnValueOnce(of(firstPage));
    fixture = TestBed.createComponent(IssueList);
    element = fixture.nativeElement;
    await fixture.whenStable();
  }

  function titles(): string[] {
    return Array.from(element.querySelectorAll('.issue h2')).map((h2) => h2.textContent!.trim());
  }

  function selectOption(select: HTMLSelectElement, index: number): void {
    select.selectedIndex = index;
    select.dispatchEvent(new Event('change'));
  }

  function lastListFilters(): IssueFilters {
    return service.list.mock.lastCall![0];
  }

  beforeEach(() => {
    service = {
      list: vi.fn(),
      update: vi.fn(),
      summary: vi.fn().mockReturnValue(of(SUMMARY)),
    };
    TestBed.configureTestingModule({
      imports: [IssueList],
      providers: [provideRouter([]), { provide: IssuesService, useValue: service }],
    });
  });

  it('loads the first page and the summary', async () => {
    await render({ items: [makeIssue({ title: 'First' })], next_cursor: null });

    expect(titles()).toEqual(['First']);
    expect(element.querySelector('app-issue-summary')?.textContent).toContain('3');
    expect(service.list).toHaveBeenCalledWith({ status: null, priority: null }, null, 20);
    expect(element.querySelector('.load-more')).toBeNull();
  });

  it('shows a message when there are no issues', async () => {
    await render({ items: [], next_cursor: null });

    expect(element.querySelector('.empty')?.textContent).toContain('No issues found');
  });

  it('appends the next page when loading more', async () => {
    await render({ items: [makeIssue({ id: '1', title: 'First' })], next_cursor: '1' });
    service.list.mockReturnValueOnce(
      of({ items: [makeIssue({ id: '2', title: 'Second' })], next_cursor: null }),
    );

    element.querySelector<HTMLButtonElement>('.load-more')!.click();
    await fixture.whenStable();

    expect(service.list).toHaveBeenLastCalledWith({ status: null, priority: null }, '1', 20);
    expect(titles()).toEqual(['First', 'Second']);
    expect(element.querySelector('.load-more')).toBeNull();
  });

  it('reloads from the first page when a filter changes', async () => {
    await render({ items: [makeIssue({ title: 'Any' })], next_cursor: '1' });
    service.list.mockReturnValueOnce(of({ items: [makeIssue({ title: 'Done one' })], next_cursor: null }));

    selectOption(element.querySelector<HTMLSelectElement>('.filters select[formControlName="status"]')!, 3);
    await fixture.whenStable();

    expect(lastListFilters()).toEqual({ status: 'done', priority: null });
    expect(service.list.mock.lastCall![1]).toBeNull();
    expect(titles()).toEqual(['Done one']);
  });

  it('reloads from the first page with the selected page size', async () => {
    await render({ items: [makeIssue({ title: 'Any' })], next_cursor: '1' });
    service.list.mockReturnValueOnce(of({ items: [makeIssue({ title: 'Fresh' })], next_cursor: null }));

    selectOption(element.querySelector<HTMLSelectElement>('.page-size select')!, 2);
    await fixture.whenStable();

    expect(service.list).toHaveBeenLastCalledWith({ status: null, priority: null }, null, 50);
    expect(titles()).toEqual(['Fresh']);
  });

  it('keeps the page size when loading more and when clearing filters', async () => {
    await render({ items: [makeIssue({ id: '1' })], next_cursor: null });
    service.list.mockReturnValue(of({ items: [makeIssue({ id: '1' })], next_cursor: '1' }));
    selectOption(element.querySelector<HTMLSelectElement>('.page-size select')!, 0);
    await fixture.whenStable();

    element.querySelector<HTMLButtonElement>('.load-more')!.click();
    await fixture.whenStable();
    expect(service.list).toHaveBeenLastCalledWith({ status: null, priority: null }, '1', 10);

    element.querySelector<HTMLButtonElement>('.filters .link')!.click();
    await fixture.whenStable();
    expect(service.list).toHaveBeenLastCalledWith({ status: null, priority: null }, null, 10);
  });

  it('updates the status of an issue and refreshes the summary', async () => {
    await render({ items: [makeIssue()], next_cursor: null });
    service.update.mockReturnValue(of(makeIssue({ status: 'done' })));

    selectOption(element.querySelector<HTMLSelectElement>('.issue-controls select')!, 2);
    await fixture.whenStable();

    expect(service.update).toHaveBeenCalledWith('1', { status: 'done' });
    expect(service.summary).toHaveBeenCalledTimes(2);
  });

  it('removes an updated issue that no longer matches the filter', async () => {
    await render({ items: [], next_cursor: null });
    service.list.mockReturnValueOnce(of({ items: [makeIssue()], next_cursor: null }));
    selectOption(element.querySelector<HTMLSelectElement>('.filters select[formControlName="status"]')!, 1);
    await fixture.whenStable();
    service.update.mockReturnValue(of(makeIssue({ status: 'done' })));

    selectOption(element.querySelector<HTMLSelectElement>('.issue-controls select')!, 2);
    await fixture.whenStable();

    expect(titles()).toEqual([]);
  });

  it('reverts the select and shows an error when the update fails', async () => {
    await render({ items: [makeIssue()], next_cursor: null });
    service.update.mockReturnValue(throwError(() => new Error('boom')));
    const select = element.querySelector<HTMLSelectElement>('.issue-controls select')!;

    selectOption(select, 2);
    await fixture.whenStable();

    expect(select.value).toBe('open');
    expect(element.querySelector('.error')?.textContent).toContain('Could not update the issue');
  });
});
