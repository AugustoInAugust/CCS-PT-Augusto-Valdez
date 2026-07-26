import { HttpErrorResponse, HttpInterceptorFn, HttpRequest } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, switchMap, throwError } from 'rxjs';

import { AuthService } from '../services/auth.service';

const PUBLIC_PATHS = ['/login/', '/token/refresh/', '/logout/'];

function isPublic(url: string): boolean {
  return PUBLIC_PATHS.some((path) => url.includes(path));
}

function withBearer<T>(request: HttpRequest<T>, token: string): HttpRequest<T> {
  return request.clone({ setHeaders: { Authorization: `Bearer ${token}` } });
}

export const authInterceptor: HttpInterceptorFn = (request, next) => {
  const auth = inject(AuthService);
  const router = inject(Router);

  const token = auth.accessToken();
  const skip = isPublic(request.url);
  const outgoing = token && !skip ? withBearer(request, token) : request;

  return next(outgoing).pipe(
    catchError((error: HttpErrorResponse) => {
      const canRetry = error.status === 401 && !skip && auth.refreshToken() !== null;

      if (!canRetry) {
        return throwError(() => error);
      }

      return auth.refresh().pipe(
        switchMap((response) => next(withBearer(request, response.access))),
        catchError((refreshError) => {
          auth.clearSession();
          router.navigate(['/login']);
          return throwError(() => refreshError);
        }),
      );
    }),
  );
};
