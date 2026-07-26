import { Session } from '../models/auth.model';

const STORAGE_KEY = 'ccs.session';

export function readSession(): Session | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as Session) : null;
  } catch {
    return null;
  }
}

export function writeSession(session: Session): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
}

export function removeSession(): void {
  localStorage.removeItem(STORAGE_KEY);
}
