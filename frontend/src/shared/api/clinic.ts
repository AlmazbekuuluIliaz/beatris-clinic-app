import { apiRequest } from './client';

export type ClinicInfo = {
  id: string;
  name: string;
  description: string;
  address: string;
  phone: string;
  workingHours: string;
};

export function getClinicInfo() {
  return apiRequest<ClinicInfo>('/clinic-info');
}
