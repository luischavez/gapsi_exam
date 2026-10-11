import { Routes } from '@angular/router';

export const ISSUES_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('./issue-list/issue-list').then((m) => m.IssueList),
  },
  {
    path: 'new',
    loadComponent: () => import('./issue-form/issue-form').then((m) => m.IssueForm),
  },
];
