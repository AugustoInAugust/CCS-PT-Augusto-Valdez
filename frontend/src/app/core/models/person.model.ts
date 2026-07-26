export interface Person {
  id: number;
  first_name: string;
  last_name: string;
  full_name: string;
  email: string;
  phone: string;
  country: string;
  birth_date: string;
}

export type PersonPayload = Omit<Person, 'id' | 'full_name'>;
