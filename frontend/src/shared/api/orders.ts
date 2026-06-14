import { apiRequest } from './client';

export type OrderStatus = 'created' | 'paid' | 'processing' | 'delivered' | 'cancelled';
export type PaymentStatus = 'pending' | 'paid' | 'failed' | 'refunded';

export type OrderProduct = {
  id: string;
  slug: string;
  title: string;
  brand?: string | null;
  imageUrl?: string | null;
  price?: number;
};

export type OrderItem = {
  product: OrderProduct;
  quantity: number;
  price: number;
  subtotal: number;
};

export type Order = {
  id: string;
  userId?: string | null;
  items: OrderItem[];
  totalPrice: number;
  paymentStatus: PaymentStatus;
  orderStatus: OrderStatus;
  deliveryAddress?: string | null;
  recipientName?: string | null;
  recipientPhone?: string | null;
  createdAt?: string | null;
};

export function getMyOrders(authToken: string) {
  return apiRequest<Order[]>('/orders/my', { authToken });
}
