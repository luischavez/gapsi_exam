import { DatePipe } from '@angular/common';
import { Component, DestroyRef, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { merge, Subscription } from 'rxjs';

import { IssueSummaryPanel } from '../issue-summary/issue-summary';
import {
  DEFAULT_PAGE_SIZE,
  Issue,
  IssueFilters,
  IssuePriority,
  IssueStatus,
  IssueSummary,
  IssueUpdate,
  isIssuePriority,
  isIssueStatus,
  PAGE_SIZES,
  PRIORITIES,
  PRIORITY_LABELS,
  STATUS_LABELS,
  STATUSES,
} from '../issue.models';
import { IssuesService } from '../issues.service';

@Component({
  imports: [DatePipe, IssueSummaryPanel, ReactiveFormsModule, RouterLink],
  selector: 'app-issue-list',
  styleUrl: './issue-list.scss',
  templateUrl: './issue-list.html',
})
export class IssueList {
  private readonly issuesService = inject(IssuesService);
  private readonly destroyRef = inject(DestroyRef);
  private pageRequest?: Subscription;

  protected readonly filters = new FormGroup({
    status: new FormControl<IssueStatus | null>(null),
    priority: new FormControl<IssuePriority | null>(null),
  });
  protected readonly pageSize = new FormControl(DEFAULT_PAGE_SIZE, { nonNullable: true });

  protected readonly issues = signal<Issue[]>([]);
  protected readonly nextCursor = signal<string | null>(null);
  protected readonly summary = signal<IssueSummary | null>(null);
  protected readonly loading = signal(false);
  protected readonly error = signal<string | null>(null);

  protected readonly statuses = STATUSES;
  protected readonly priorities = PRIORITIES;
  protected readonly pageSizes = PAGE_SIZES;
  protected readonly statusLabels = STATUS_LABELS;
  protected readonly priorityLabels = PRIORITY_LABELS;

  constructor() {
    merge(this.filters.valueChanges, this.pageSize.valueChanges)
      .pipe(takeUntilDestroyed())
      .subscribe(() => this.reload());
    this.reload();
    this.loadSummary();
  }

  protected loadMore(): void {
    const cursor = this.nextCursor();
    if (cursor) {
      this.fetchPage(cursor);
    }
  }

  protected clearFilters(): void {
    this.filters.setValue({ status: null, priority: null });
  }

  protected changeStatus(issue: Issue, select: HTMLSelectElement): void {
    if (isIssueStatus(select.value)) {
      this.update(issue, { status: select.value }, () => (select.value = issue.status));
    }
  }

  protected changePriority(issue: Issue, select: HTMLSelectElement): void {
    if (isIssuePriority(select.value)) {
      this.update(issue, { priority: select.value }, () => (select.value = issue.priority));
    }
  }

  private reload(): void {
    // drop the request for the old filters, otherwise a slow response could get mixed into the new list
    this.pageRequest?.unsubscribe();
    this.issues.set([]);
    this.nextCursor.set(null);
    this.fetchPage(null);
  }

  private fetchPage(cursor: string | null): void {
    this.loading.set(true);
    this.error.set(null);
    this.pageRequest = this.issuesService
      .list(this.currentFilters(), cursor, this.pageSize.value)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (page) => {
          this.issues.update((current) => [...current, ...page.items]);
          this.nextCursor.set(page.next_cursor);
          this.loading.set(false);
        },
        error: () => {
          this.error.set('Could not load the issues, try again later');
          this.loading.set(false);
        },
      });
  }

  private loadSummary(): void {
    this.issuesService
      .summary()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (summary) => this.summary.set(summary),
        error: () => this.summary.set(null),
      });
  }

  private update(issue: Issue, changes: IssueUpdate, revert: () => void): void {
    this.error.set(null);
    this.issuesService
      .update(issue.id, changes)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (updated) => {
          // with a filter on, an issue that no longer matches it shouldn't stay on screen
          this.issues.update((current) =>
            this.matchesFilters(updated)
              ? current.map((item) => (item.id === updated.id ? updated : item))
              : current.filter((item) => item.id !== updated.id),
          );
          this.loadSummary();
        },
        error: () => {
          revert();
          this.error.set('Could not update the issue, try again later');
        },
      });
  }

  private currentFilters(): IssueFilters {
    return this.filters.getRawValue();
  }

  private matchesFilters(issue: Issue): boolean {
    const { status, priority } = this.currentFilters();
    return (!status || issue.status === status) && (!priority || issue.priority === priority);
  }
}
