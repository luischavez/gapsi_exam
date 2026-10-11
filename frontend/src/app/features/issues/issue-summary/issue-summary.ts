import { Component, input } from '@angular/core';

import { IssueSummary, STATUS_LABELS, STATUSES } from '../issue.models';

@Component({
  imports: [],
  selector: 'app-issue-summary',
  styleUrl: './issue-summary.scss',
  templateUrl: './issue-summary.html',
})
export class IssueSummaryPanel {
  readonly summary = input.required<IssueSummary>();

  protected readonly statuses = STATUSES;
  protected readonly statusLabels = STATUS_LABELS;
}
