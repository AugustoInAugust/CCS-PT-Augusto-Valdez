import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

import { errorMessage, fieldErrors } from '../../../core/errors/api-error';
import { Person } from '../../../core/models/person.model';
import { AuthService } from '../../../core/services/auth.service';
import { UserService } from '../../../core/services/user.service';

type FieldName = 'first_name' | 'last_name' | 'email' | 'phone' | 'country' | 'birth_date';

@Component({
  selector: 'app-user-details',
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './user-details.component.html',
})
export class UserDetailsComponent {
  private readonly users = inject(UserService);
  private readonly auth = inject(AuthService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly fb = inject(FormBuilder);

  private readonly personId = Number(this.route.snapshot.paramMap.get('id'));

  protected readonly person = signal<Person | null>(null);
  protected readonly loading = signal(true);
  protected readonly saving = signal(false);
  protected readonly errorText = signal<string | null>(null);
  protected readonly savedText = signal<string | null>(null);
  protected readonly serverErrors = signal<Record<string, string[]>>({});

  protected readonly isAdmin = this.auth.isAdmin;

  protected readonly form = this.fb.nonNullable.group({
    first_name: ['', [Validators.required, Validators.maxLength(100)]],
    last_name: ['', [Validators.required, Validators.maxLength(100)]],
    email: ['', [Validators.required, Validators.email]],
    phone: ['', [Validators.required, Validators.maxLength(30)]],
    country: ['', [Validators.required, Validators.maxLength(100)]],
    birth_date: ['', Validators.required],
  });

  constructor() {
    this.load();
  }

  public save(): void {
    if (this.form.invalid || this.saving()) {
      this.form.markAllAsTouched();
      return;
    }

    this.saving.set(true);
    this.errorText.set(null);
    this.savedText.set(null);
    this.serverErrors.set({});

    this.users.update(this.personId, this.form.getRawValue()).subscribe({
      next: (updated) => {
        this.person.set(updated);
        this.savedText.set('Changes saved.');
        this.saving.set(false);
      },
      error: (error: unknown) => {
        this.errorText.set(errorMessage(error));
        this.serverErrors.set(fieldErrors(error));
        this.saving.set(false);
      },
    });
  }

  protected back(): void {
    this.router.navigate(['/people']);
  }

  protected invalid(field: FieldName): boolean {
    const control = this.form.controls[field];
    return control.invalid && control.touched;
  }

  protected serverError(field: FieldName): string | null {
    return this.serverErrors()[field]?.[0] ?? null;
  }

  private load(): void {
    if (!Number.isInteger(this.personId)) {
      this.errorText.set('Invalid user id.');
      this.loading.set(false);
      return;
    }

    this.users.getById(this.personId).subscribe({
      next: (person) => {
        this.person.set(person);
        this.form.patchValue(person);

        if (!this.isAdmin()) {
          this.form.disable();
        }

        this.loading.set(false);
      },
      error: (error: unknown) => {
        this.errorText.set(errorMessage(error));
        this.loading.set(false);
      },
    });
  }
}
