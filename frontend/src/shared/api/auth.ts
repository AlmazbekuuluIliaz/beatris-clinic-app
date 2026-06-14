import { apiRequest } from './client';

export type AuthUser = {
  id: string;
  fullName: string;
  phone?: string;
  email: string;
  role: 'patient' | 'doctor' | 'admin';
};

export type LoginPayload = {
  email: string;
  password: string;
};

export type AuthResponse = {
  accessToken: string;
  user: AuthUser;
};

export function login(payload: LoginPayload) {
  return apiRequest<AuthResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function getCurrentUser(authToken: string) {
  return apiRequest<AuthUser>('/auth/me', { authToken });
}
