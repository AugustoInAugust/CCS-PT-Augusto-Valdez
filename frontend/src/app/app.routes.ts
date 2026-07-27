import { Routes } from '@angular/router';

import { authGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  {
    path: 'login',
    loadComponent: () =>
      import('./components/login/login.component').then((m) => m.LoginComponent),
  },
  {
    path: 'people',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./components/people/people-list/people-list.component').then(
        (m) => m.PeopleListComponent,
      ),
  },
  {
    path: 'people/:id',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./components/people/user-details/user-details.component').then(
        (m) => m.UserDetailsComponent,
      ),
  },
  { path: '', pathMatch: 'full', redirectTo: 'people' },
  { path: '**', redirectTo: 'people' },
];
