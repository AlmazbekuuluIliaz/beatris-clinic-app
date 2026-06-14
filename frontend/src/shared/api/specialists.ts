import { apiRequest } from './client';

export type Specialist = {
  id: string;
  fullName: string;
  position: string;
  specialization: string;
  experienceYears: number;
  photoUrl?: string;
};

type SpecialistListResponse = {
  items: Specialist[];
};

export function getSpecialists() {
  return apiRequest<SpecialistListResponse>('/specialists').then((response) => response.items);
}
