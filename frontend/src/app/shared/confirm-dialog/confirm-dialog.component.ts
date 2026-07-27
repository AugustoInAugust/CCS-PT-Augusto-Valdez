import { Component, input, output } from '@angular/core';

@Component({
  selector: 'app-confirm-dialog',
  templateUrl: './confirm-dialog.component.html',
  host: {
    '(document:keydown.escape)': 'onCancel()',
  },
})
export class ConfirmDialogComponent {
  public readonly title = input.required<string>();
  public readonly message = input.required<string>();
  public readonly confirmLabel = input('Confirm');
  public readonly cancelLabel = input('Cancel');
  public readonly busy = input(false);
  public readonly danger = input(false);

  public readonly confirmed = output<void>();
  public readonly cancelled = output<void>();

  protected onCancel(): void {
    if (!this.busy()) {
      this.cancelled.emit();
    }
  }
}
