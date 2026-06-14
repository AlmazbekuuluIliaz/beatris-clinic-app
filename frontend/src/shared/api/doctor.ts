import { apiRequest } from './client';

export function getDoctorSchedule(authToken: string) {
  return apiRequest('/doctor/schedule', { authToken });
}
