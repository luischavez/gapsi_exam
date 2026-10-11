import { HttpErrorResponse } from '@angular/common/http';
import { Component, DestroyRef, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

import { IssuePriority, PRIORITIES, PRIORITY_LABELS } from '../issue.models';
import { IssuesService } from '../issues.service';

// same limits the API enforces, so the user sees the error before sending the form
export const TITLE_MAX_LENGTH = 200;
export const DESCRIPTION_MAX_LENGTH = 5000;
const NOT_BLANK = /\S/;

@Component({
  imports: [ReactiveFormsModule, RouterLink],
  selector: 'app-issue-form',
  styleUrl: './issue-form.scss',
  templateUrl: './issue-form.html',
})
export class IssueForm {
  private readonly issuesService = inject(IssuesService);
  private readonly router = inject(Router);
  private readonly destroyRef = inject(DestroyRef);
  private readonly fb = inject(NonNullableFormBuilder);

  protected readonly form = this.fb.group({
    title: [
      '',
      [Validators.required, Validators.pattern(NOT_BLANK), Validators.maxLength(TITLE_MAX_LENGTH)],
    ],
    description: [
      '',
      [
        Validators.required,
        Validators.pattern(NOT_BLANK),
        Validators.maxLength(DESCRIPTION_MAX_LENGTH),
      ],
    ],
    priority: this.fb.control<IssuePriority>('medium', Validators.required),
  });
  protected readonly saving = signal(false);
  protected readonly error = signal<string | null>(null);

  protected readonly priorities = PRIORITIES;
  protected readonly priorityLabels = PRIORITY_LABELS;
  protected readonly titleMaxLength = TITLE_MAX_LENGTH;
  protected readonly descriptionMaxLength = DESCRIPTION_MAX_LENGTH;

  protected submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.saving.set(true);
    this.error.set(null);
    this.issuesService
      .create(this.form.getRawValue())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => void this.router.navigateByUrl('/issues'),
        error: (err: HttpErrorResponse) => {
          this.error.set(
            err.status === 422
              ? 'Some fields are not valid, check them and try again'
              : 'Could not create the issue, try again later',
          );
          this.saving.set(false);
        },
      });
  }
}
