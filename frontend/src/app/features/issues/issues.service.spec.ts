import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { environment } from '../../../environments/environment';
import { DEFAULT_PAGE_SIZE } from './issue.models';
import { IssuesService } from './issues.service';

describe('IssuesService', () => {
  const apiUrl = `${environment.apiUrl}/issues`;
  let service: IssuesService;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(IssuesService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('lists issues with the page size and no filters', () => {
    service.list({ status: null, priority: null }).subscribe();

    const req = http.expectOne((r) => r.url === apiUrl);
    expect(req.request.method).toBe('GET');
    expect(req.request.params.get('limit')).toBe(String(DEFAULT_PAGE_SIZE));
    expect(req.request.params.has('status')).toBe(false);
    expect(req.request.params.has('priority')).toBe(false);
    expect(req.request.params.has('cursor')).toBe(false);
    req.flush({ items: [], next_cursor: null });
  });

  it('sends filters, cursor and limit as query params', () => {
    service.list({ status: 'open', priority: 'high' }, 'abc', 50).subscribe();

    const req = http.expectOne((r) => r.url === apiUrl);
    expect(req.request.params.get('status')).toBe('open');
    expect(req.request.params.get('priority')).toBe('high');
    expect(req.request.params.get('cursor')).toBe('abc');
    expect(req.request.params.get('limit')).toBe('50');
    req.flush({ items: [], next_cursor: null });
  });

  it('creates an issue', () => {
    const data = { title: 'Bug', description: 'Broken', priority: 'low' } as const;

    service.create(data).subscribe();

    const req = http.expectOne(apiUrl);
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual(data);
    req.flush({});
  });

  it('updates an issue escaping its id', () => {
    service.update('a/b', { status: 'done' }).subscribe();

    const req = http.expectOne(`${apiUrl}/a%2Fb`);
    expect(req.request.method).toBe('PATCH');
    expect(req.request.body).toEqual({ status: 'done' });
    req.flush({});
  });

  it('gets the summary', () => {
    service.summary().subscribe();

    const req = http.expectOne(`${apiUrl}/summary`);
    expect(req.request.method).toBe('GET');
    req.flush({ total: 0, by_status: { open: 0, in_progress: 0, done: 0 } });
  });
});
