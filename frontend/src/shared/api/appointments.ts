import { apiRequest } from './client';

export type AppointmentPayload = {
  serviceId: string;
  specialistId: string;
  date: string;
  time: string;
  patientName: string;
  patientPhone: string;
  comment?: string;
};

export function createAppointment(payload: AppointmentPayload, authToken?: string) {
  return apiRequest('/appointments', {
    method: 'POST',
    authToken,
    body: JSON.stringify(payload),
  });
}
