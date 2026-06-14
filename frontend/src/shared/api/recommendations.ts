import { apiRequest } from './client';

export type Recommendation = {
  id: string;
  patientId: string;
  doctorId: string;
  appointmentId?: string | null;
  text: string;
  productIds: string[];
  createdAt: string;
};

export function getMyRecommendations(authToken: string) {
  return apiRequest<Recommendation[]>('/recommendations/my', { authToken });
}
