import { HttpErrorResponse } from '@angular/common/http';

import { ApiErrorBody } from '../models/api.model';

const NETWORK_ERROR = 'The server is unreachable. Check that the API is running.';
const UNEXPECTED_ERROR = 'Something went wrong. Please try again.';

function asApiErrorBody(error: unknown): ApiErrorBody | null {
  if (!(error instanceof HttpErrorResponse)) {
    return null;
  }

  const body = error.error as Partial<ApiErrorBody> | null;
  return body && typeof body === 'object' && body.error ? (body as ApiErrorBody) : null;
}

export function errorMessage(error: unknown): string {
  if (error instanceof HttpErrorResponse && error.status === 0) {
    return NETWORK_ERROR;
  }

  return asApiErrorBody(error)?.error.message ?? UNEXPECTED_ERROR;
}

export function fieldErrors(error: unknown): Record<string, string[]> {
  return asApiErrorBody(error)?.error.fields ?? {};
}
