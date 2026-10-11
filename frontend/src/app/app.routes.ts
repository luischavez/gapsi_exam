import { Routes } from '@angular/router';
import { authGuard, guestGuard } from './core/auth/auth.guard';

export const routes: Routes = [
  {
    path: 'login',
    canActivate: [guestGuard],
    loadComponent: () => import('./features/login/login').then(m => m.Login),
  },
  {
    path: '',
    canActivate: [authGuard],
    loadComponent: () => import('./layout/shell/shell').then(m => m.Shell),
    children: [
      {
        path: 'issues',
        loadChildren: () => import('./features/issues/issues.routes').then(m => m.ISSUES_ROUTES),
      },
      { path: '', pathMatch: 'full', redirectTo: 'issues' },
    ],
  },
  { path: '**', redirectTo: '' },
];
