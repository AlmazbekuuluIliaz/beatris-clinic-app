import { apiRequest } from './client';

export type Product = {
  id: string;
  title: string;
  slug: string;
  description: string;
  price: number;
  imageUrl?: string;
  stock: number;
};

type ProductListResponse = {
  items: Product[];
};

export function getProducts() {
  return apiRequest<ProductListResponse>('/products').then((response) => response.items);
}

export function getProductBySlug(slug: string) {
  return apiRequest<Product>(`/products/${slug}`);
}
