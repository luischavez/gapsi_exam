export type IssuePriority = 'high' | 'medium' | 'low';
export type IssueStatus = 'open' | 'in_progress' | 'done';

export interface Issue {
  id: string;
  title: string;
  description: string;
  priority: IssuePriority;
  status: IssueStatus;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface IssuePage {
  items: Issue[];
  next_cursor: string | null;
}

export interface IssueSummary {
  total: number;
  by_status: Record<IssueStatus, number>;
}

export interface IssueCreate {
  title: string;
  description: string;
  priority: IssuePriority;
}

export type IssueUpdate = Partial<Pick<Issue, 'status' | 'priority'>>;

export interface IssueFilters {
  status: IssueStatus | null;
  priority: IssuePriority | null;
}

// the API rejects anything above 100
export const PAGE_SIZES: readonly number[] = [10, 20, 50, 100];
export const DEFAULT_PAGE_SIZE = 20;

export const PRIORITIES: readonly IssuePriority[] = ['high', 'medium', 'low'];
export const STATUSES: readonly IssueStatus[] = ['open', 'in_progress', 'done'];

export const PRIORITY_LABELS: Record<IssuePriority, string> = {
  high: 'High',
  medium: 'Medium',
  low: 'Low',
};

export const STATUS_LABELS: Record<IssueStatus, string> = {
  open: 'Open',
  in_progress: 'In progress',
  done: 'Done',
};

export function isIssuePriority(value: string): value is IssuePriority {
  return (PRIORITIES as readonly string[]).includes(value);
}

export function isIssueStatus(value: string): value is IssueStatus {
  return (STATUSES as readonly string[]).includes(value);
}
