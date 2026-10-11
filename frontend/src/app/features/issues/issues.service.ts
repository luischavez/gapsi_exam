import { HttpClient, HttpParams } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import {
  DEFAULT_PAGE_SIZE,
  Issue,
  IssueCreate,
  IssueFilters,
  IssuePage,
  IssueSummary,
  IssueUpdate,
} from './issue.models';

@Injectable({ providedIn: 'root' })
export class IssuesService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/issues`;

  list(
    filters: IssueFilters,
    cursor: string | null = null,
    limit: number = DEFAULT_PAGE_SIZE,
  ): Observable<IssuePage> {
    let params = new HttpParams().set('limit', limit);
    if (filters.status) {
      params = params.set('status', filters.status);
    }
    if (filters.priority) {
      params = params.set('priority', filters.priority);
    }
    if (cursor) {
      params = params.set('cursor', cursor);
    }
    return this.http.get<IssuePage>(this.apiUrl, { params });
  }

  create(data: IssueCreate): Observable<Issue> {
    return this.http.post<Issue>(this.apiUrl, data);
  }

  update(id: string, changes: IssueUpdate): Observable<Issue> {
    return this.http.patch<Issue>(`${this.apiUrl}/${encodeURIComponent(id)}`, changes);
  }

  summary(): Observable<IssueSummary> {
    return this.http.get<IssueSummary>(`${this.apiUrl}/summary`);
  }
}
