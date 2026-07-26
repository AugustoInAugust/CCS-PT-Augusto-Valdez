export type Role = 'ADMIN' | 'USER';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  person_id: number;
  username: string;
  role: Role;
}

export interface RefreshResponse {
  access: string;
  refresh?: string;
}

export interface Session {
  access: string;
  refresh: string;
  personId: number;
  username: string;
  role: Role;
}
