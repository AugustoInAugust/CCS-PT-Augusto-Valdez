import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { Component, computed, inject, signal } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { debounceTime, distinctUntilChanged } from 'rxjs';

import { errorMessage } from '../../../core/errors/api-error';
import { Person } from '../../../core/models/person.model';
import { AuthService } from '../../../core/services/auth.service';
import { UserService } from '../../../core/services/user.service';
import { ConfirmDialogComponent } from '../../../shared/confirm-dialog/confirm-dialog.component';

const PAGE_SIZE = 10;

@Component({
  selector: 'app-people-list',
  imports: [ReactiveFormsModule, RouterLink, ConfirmDialogComponent],
  templateUrl: './people-list.component.html',
})
export class PeopleListComponent {
  private readonly users = inject(UserService);
  private readonly auth = inject(AuthService);

  protected readonly people = signal<Person[]>([]);
  protected readonly total = signal(0);
  protected readonly page = signal(1);
  protected readonly loading = signal(false);
  protected readonly errorText = signal<string | null>(null);
  protected readonly pendingDelete = signal<Person | null>(null);
  protected readonly deleting = signal(false);

  protected readonly isAdmin = this.auth.isAdmin;
  protected readonly totalPages = computed(() => Math.max(1, Math.ceil(this.total() / PAGE_SIZE)));

  protected readonly search = new FormControl('', { nonNullable: true });

  constructor() {
    this.search.valueChanges
      .pipe(debounceTime(300), distinctUntilChanged(), takeUntilDestroyed())
      .subscribe(() => this.goToPage(1));

    this.load();
  }

  protected goToPage(page: number): void {
    if (page < 1 || page > this.totalPages()) {
      return;
    }
    this.page.set(page);
    this.load();
  }

  protected askToDelete(person: Person): void {
    this.pendingDelete.set(person);
  }

  protected cancelDelete(): void {
    this.pendingDelete.set(null);
  }

  protected confirmDelete(): void {
    const person = this.pendingDelete();
    if (!person) {
      return;
    }

    this.deleting.set(true);
    this.errorText.set(null);

    this.users.delete(person.id).subscribe({
      next: () => {
        this.deleting.set(false);
        this.pendingDelete.set(null);
        this.reloadAfterDelete();
      },
      error: (error: unknown) => {
        this.deleting.set(false);
        this.pendingDelete.set(null);
        this.errorText.set(errorMessage(error));
      },
    });
  }

  private reloadAfterDelete(): void {
    const isLastItemOnPage = this.people().length === 1 && this.page() > 1;
    if (isLastItemOnPage) {
      this.page.update((page) => page - 1);
    }
    this.load();
  }

  private load(): void {
    this.loading.set(true);
    this.errorText.set(null);

    this.users
      .list({ page: this.page(), search: this.search.value })
      .subscribe({
        next: (response) => {
          this.people.set(response.results);
          this.total.set(response.count);
          this.loading.set(false);
        },
        error: (error: unknown) => {
          this.errorText.set(errorMessage(error));
          this.loading.set(false);
        },
      });
  }
}
