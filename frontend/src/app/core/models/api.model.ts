export interface Page<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ListOptions {
  page?: number;
  search?: string;
  ordering?: string;
}

export interface ApiErrorBody {
  error: {
    status: number;
    code: string;
    message: string;
    fields: Record<string, string[]>;
  };
}
