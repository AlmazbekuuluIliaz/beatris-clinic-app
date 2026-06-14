import { apiRequest } from './client';

export type Service = {
  id: string;
  title: string;
  slug: string;
  description: string;
  price: number;
  durationMinutes: number;
  imageUrl?: string;
};

export type ServiceCategory = {
  id: string;
  title: string;
  slug: string;
  description?: string | null;
  image?: string | null;
  imageUrl?: string | null;
};

export function getServiceCategories() {
  return apiRequest<ServiceCategory[]>('/service-categories');
}

export function getServices() {
  return apiRequest<Service[]>('/services');
}

export function getServiceBySlug(slug: string) {
  return apiRequest<Service>(`/services/${slug}`);
}
