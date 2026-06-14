import { apiRequest } from './client';
import type { Product } from './products';

export type CartItem = {
  id: string;
  product: Product;
  quantity: number;
  price: number;
  subtotal: number;
};

export type Cart = {
  items: CartItem[];
  totalPrice: number;
};

export function getCart(authToken: string) {
  return apiRequest<Cart>('/cart', { authToken });
}

export function updateCartItem(itemId: string, quantity: number, authToken: string) {
  return apiRequest<Cart>(`/cart/items/${itemId}`, {
    method: 'PATCH',
    authToken,
    body: JSON.stringify({ quantity }),
  });
}

export function deleteCartItem(itemId: string, authToken: string) {
  return apiRequest<void>(`/cart/items/${itemId}`, {
    method: 'DELETE',
    authToken,
  });
}
