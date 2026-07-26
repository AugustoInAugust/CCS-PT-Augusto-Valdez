import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { ListOptions, Page } from '../models/api.model';
import { Person, PersonPayload } from '../models/person.model';

@Injectable({ providedIn: 'root' })
export class UserService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/users/`;

  public list(options: ListOptions = {}): Observable<Page<Person>> {
    let params = new HttpParams();

    if (options.page) {
      params = params.set('page', options.page);
    }
    if (options.search) {
      params = params.set('search', options.search);
    }
    if (options.ordering) {
      params = params.set('ordering', options.ordering);
    }

    return this.http.get<Page<Person>>(this.baseUrl, { params });
  }

  public getById(id: number): Observable<Person> {
    return this.http.get<Person>(`${this.baseUrl}${id}/`);
  }

  public create(payload: PersonPayload): Observable<Person> {
    return this.http.post<Person>(this.baseUrl, payload);
  }

  public update(id: number, payload: PersonPayload): Observable<Person> {
    return this.http.put<Person>(`${this.baseUrl}${id}/`, payload);
  }

  public delete(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}${id}/`);
  }
}
