import { HttpErrorResponse } from '@angular/common/http';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter, Router } from '@angular/router';
import { of, throwError } from 'rxjs';

import { IssuesService } from '../issues.service';
import { IssueForm } from './issue-form';

describe('IssueForm', () => {
  let fixture: ComponentFixture<IssueForm>;
  let element: HTMLElement;
  let create: ReturnType<typeof vi.fn>;
  let navigate: ReturnType<typeof vi.spyOn>;

  function type(selector: string, value: string): void {
    const field = element.querySelector<HTMLInputElement | HTMLTextAreaElement>(selector)!;
    field.value = value;
    field.dispatchEvent(new Event('input'));
  }

  async function submit(): Promise<void> {
    element.querySelector('form')!.dispatchEvent(new Event('submit'));
    await fixture.whenStable();
  }

  beforeEach(async () => {
    create = vi.fn();
    TestBed.configureTestingModule({
      imports: [IssueForm],
      providers: [provideRouter([]), { provide: IssuesService, useValue: { create } }],
    });
    navigate = vi.spyOn(TestBed.inject(Router), 'navigateByUrl').mockResolvedValue(true);
    fixture = TestBed.createComponent(IssueForm);
    element = fixture.nativeElement;
    await fixture.whenStable();
  });

  it('does not submit an empty form and shows the errors', async () => {
    await submit();

    expect(create).not.toHaveBeenCalled();
    expect(element.textContent).toContain('Title is required');
    expect(element.textContent).toContain('Description is required');
  });

  it('does not accept a title made only of spaces', async () => {
    type('input[formControlName="title"]', '   ');
    type('textarea[formControlName="description"]', 'Something');

    await submit();

    expect(create).not.toHaveBeenCalled();
    expect(element.textContent).toContain('Title is required');
  });

  it('creates the issue and goes back to the list', async () => {
    create.mockReturnValue(of({}));
    type('input[formControlName="title"]', 'Broken button');
    type('textarea[formControlName="description"]', 'Nothing happens');
    const priority = element.querySelector<HTMLSelectElement>('select[formControlName="priority"]')!;
    priority.selectedIndex = 0;
    priority.dispatchEvent(new Event('change'));

    await submit();

    expect(create).toHaveBeenCalledWith({
      title: 'Broken button',
      description: 'Nothing happens',
      priority: 'high',
    });
    expect(navigate).toHaveBeenCalledWith('/issues');
  });

  it('shows a message when the API rejects the data', async () => {
    create.mockReturnValue(throwError(() => new HttpErrorResponse({ status: 422 })));
    type('input[formControlName="title"]', 'Broken button');
    type('textarea[formControlName="description"]', 'Nothing happens');

    await submit();

    expect(navigate).not.toHaveBeenCalled();
    expect(element.querySelector('.error')?.textContent).toContain('Some fields are not valid');
    expect(element.querySelector<HTMLButtonElement>('button[type="submit"]')!.disabled).toBe(false);
  });
});
