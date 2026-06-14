import { apiRequest } from './client';
import type { Product } from './products';

export type WishlistItem = {
  id: string;
  product: Product;
  createdAt?: string | null;
};

export function getWishlist(authToken: string) {
  return apiRequest<WishlistItem[]>('/wishlist', { authToken });
}
