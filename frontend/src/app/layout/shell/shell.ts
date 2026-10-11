import { Component, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { RouterLink, RouterOutlet } from '@angular/router';
import { catchError, of } from 'rxjs';

import { AuthService } from '../../core/auth/auth.service';

@Component({
  imports: [RouterLink, RouterOutlet],
  selector: 'app-shell',
  styleUrl: './shell.scss',
  templateUrl: './shell.html',
})
export class Shell {
  private readonly auth = inject(AuthService);

  // a 401 is already handled by the interceptor, this just keeps the header from breaking
  protected readonly user = toSignal(this.auth.getCurrentUser().pipe(catchError(() => of(null))));

  protected logout(): void {
    this.auth.logout();
  }
}
