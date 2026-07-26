import { HttpClient } from '@angular/common/http';
import { Injectable, computed, inject, signal } from '@angular/core';
import { Observable, catchError, finalize, of, shareReplay, tap } from 'rxjs';

import { environment } from '../../../environments/environment';
import { LoginRequest, LoginResponse, RefreshResponse, Session } from '../models/auth.model';
import { readSession, removeSession, writeSession } from '../storage/session.storage';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly session = signal<Session | null>(readSession());

  private refreshInFlight: Observable<RefreshResponse> | null = null;

  public readonly isAuthenticated = computed(() => this.session() !== null);
  public readonly isAdmin = computed(() => this.session()?.role === 'ADMIN');
  public readonly username = computed(() => this.session()?.username ?? '');
  public readonly personId = computed(() => this.session()?.personId ?? null);

  public accessToken(): string | null {
    return this.session()?.access ?? null;
  }

  public refreshToken(): string | null {
    return this.session()?.refresh ?? null;
  }

  public login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.http
      .post<LoginResponse>(`${environment.apiUrl}/login/`, credentials)
      .pipe(tap((response) => this.startSession(response)));
  }

  public refresh(): Observable<RefreshResponse> {
    if (this.refreshInFlight) {
      return this.refreshInFlight;
    }

    this.refreshInFlight = this.http
      .post<RefreshResponse>(`${environment.apiUrl}/token/refresh/`, {
        refresh: this.refreshToken(),
      })
      .pipe(
        tap((response) => this.applyTokens(response)),
        finalize(() => (this.refreshInFlight = null)),
        shareReplay(1),
      );

    return this.refreshInFlight;
  }

  public logout(): Observable<unknown> {
    const refresh = this.refreshToken();
    this.clearSession();

    if (!refresh) {
      return of(null);
    }

    return this.http
      .post(`${environment.apiUrl}/logout/`, { refresh })
      .pipe(catchError(() => of(null)));
  }

  public clearSession(): void {
    this.session.set(null);
    removeSession();
  }

  private startSession(response: LoginResponse): void {
    this.persist({
      access: response.access,
      refresh: response.refresh,
      personId: response.person_id,
      username: response.username,
      role: response.role,
    });
  }

  private applyTokens(response: RefreshResponse): void {
    const current = this.session();
    if (!current) {
      return;
    }

    this.persist({
      ...current,
      access: response.access,
      refresh: response.refresh ?? current.refresh,
    });
  }

  private persist(session: Session): void {
    this.session.set(session);
    writeSession(session);
  }
}
