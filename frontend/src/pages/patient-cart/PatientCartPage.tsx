import {
  CalendarDays,
  ChevronRight,
  ClipboardList,
  Heart,
  Home,
  LogOut,
  Minus,
  Plus,
  ShieldCheck,
  ShoppingBag,
  ShoppingCart,
  Trash2,
  Truck,
  UserRound,
} from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import { ApiError } from '@/shared/api/client';
import { deleteCartItem, getCart, updateCartItem, type CartItem } from '@/shared/api/cart';
import { Button } from '@/shared/ui/Button';

import './PatientCartPage.css';

type CartViewItem = CartItem & {
  image: string;
};

type ViewState = 'loading' | 'success' | 'empty' | 'error' | 'unauthorized';

const navItems = [
  { label: 'Профиль', to: '/account', icon: <UserRound /> },
  { label: 'Мои записи', to: '/account/appointments', icon: <CalendarDays /> },
  { label: 'Рекомендации врача', to: '/account/recommendations', icon: <ClipboardList /> },
  { label: 'Мои заказы', to: '/account/orders', icon: <ShoppingBag /> },
  { label: 'Избранное', to: '/account/wishlist', icon: <Heart /> },
  { label: 'Корзина', to: '/account/cart', icon: <ShoppingCart />, badge: '2', active: true },
];

const demoItems: CartViewItem[] = [
  {
    id: 'cart-1',
    quantity: 1,
    price: 16900,
    subtotal: 16900,
    image: 'https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?auto=format&fit=crop&w=420&q=85',
    product: {
      id: 'c-e-ferulic',
      slug: 'c-e-ferulic',
      title: 'SkinCeuticals C E Ferulic',
      description: 'Антиоксидантная сыворотка с витамином C и E, 30 мл',
      price: 16900,
      stock: 6,
    },
  },
  {
    id: 'cart-2',
    quantity: 1,
    price: 6450,
    subtotal: 6450,
    image: 'https://images.unsplash.com/photo-1556228578-8c89e6adf883?auto=format&fit=crop&w=420&q=85',
    product: {
      id: 'hydra-hyal-serum',
      slug: 'hydra-hyal-serum',
      title: 'Filorga Hydra-Hyal Serum',
      description: 'Увлажняющая сыворотка для восстановления кожи, 30 мл',
      price: 6450,
      stock: 4,
    },
  },
];

const accessTokenKeys = ['beatris_access_token', 'accessToken', 'authToken'];

function getStoredAccessToken() {
  return accessTokenKeys.map((key) => window.localStorage.getItem(key)).find(Boolean);
}

function formatMoney(value: number) {
  return `${new Intl.NumberFormat('ru-RU').format(value)} ₽`;
}

function mapCartItem(item: CartItem, index: number): CartViewItem {
  const fallbackImages = [
    'https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?auto=format&fit=crop&w=420&q=85',
    'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=420&q=85',
    'https://images.unsplash.com/photo-1617897903246-719242758050?auto=format&fit=crop&w=420&q=85',
  ];

  return {
    ...item,
    image: item.product.imageUrl ?? fallbackImages[index % fallbackImages.length],
  };
}

export function PatientCartPage() {
  const navigate = useNavigate();
  const [state, setState] = useState<ViewState>('loading');
  const [items, setItems] = useState<CartViewItem[]>([]);
  const [promo, setPromo] = useState('');
  const [message, setMessage] = useState('');
  const token = useMemo(() => getStoredAccessToken(), []);

  useEffect(() => {
    let isMounted = true;

    if (!token) {
      setItems(demoItems);
      setState('success');
      return;
    }

    getCart(token)
      .then((cart) => {
        if (!isMounted) return;
        const mappedItems = cart.items.map(mapCartItem);
        setItems(mappedItems);
        setState(mappedItems.length ? 'success' : 'empty');
      })
      .catch((error: unknown) => {
        if (!isMounted) return;
        setState(error instanceof ApiError && error.status === 401 ? 'unauthorized' : 'error');
      });

    return () => {
      isMounted = false;
    };
  }, [token]);

  const totals = useMemo(() => {
    const productsTotal = items.reduce((sum, item) => sum + item.price * item.quantity, 0);
    const discount = promo.trim().toUpperCase() === 'BEATRIS10' ? Math.round(productsTotal * 0.1) : 0;
    const delivery = productsTotal > 0 && productsTotal < 15000 ? 450 : 0;

    return {
      productsTotal,
      discount,
      delivery,
      total: Math.max(productsTotal - discount + delivery, 0),
    };
  }, [items, promo]);

  const changeQuantity = async (item: CartViewItem, nextQuantity: number) => {
    if (nextQuantity < 1) return;

    if (!token) {
      setItems((currentItems) =>
        currentItems.map((currentItem) =>
          currentItem.id === item.id ? { ...currentItem, quantity: nextQuantity, subtotal: currentItem.price * nextQuantity } : currentItem,
        ),
      );
      return;
    }

    const cart = await updateCartItem(item.id, nextQuantity, token);
    setItems(cart.items.map(mapCartItem));
  };

  const removeItem = async (item: CartViewItem) => {
    if (!token) {
      setItems((currentItems) => currentItems.filter((currentItem) => currentItem.id !== item.id));
      return;
    }

    await deleteCartItem(item.id, token);
    setItems((currentItems) => currentItems.filter((currentItem) => currentItem.id !== item.id));
  };

  const applyPromo = () => {
    setMessage(promo.trim().toUpperCase() === 'BEATRIS10' ? 'Промокод применён' : 'Промокод не найден');
  };

  return (
    <main className="cart-page">
      <div className="cart-container">
        <nav className="cart-breadcrumb" aria-label="Хлебные крошки">
          <Link to="/"><Home size={15} /> Главная</Link>
          <ChevronRight size={14} />
          <Link to="/account">Личный кабинет</Link>
          <ChevronRight size={14} />
          <span>Корзина</span>
        </nav>

        <div className="cart-heading">
          <div>
            <h1>Корзина</h1>
          </div>
        </div>

        <div className="cart-layout">
          <aside className="cart-sidebar" aria-label="Навигация личного кабинета">
            {navItems.map((item) => (
              <Link className={item.active ? 'is-active' : ''} key={item.label} to={item.to}>
                {item.icon}
                <span>{item.label}</span>
                {item.badge && <b>{String(items.length || item.badge)}</b>}
              </Link>
            ))}
            <button type="button" onClick={() => navigate('/login')}>
              <LogOut />
              <span>Выйти</span>
            </button>
          </aside>

          <section className="cart-content">
            {state === 'loading' && <CartSkeleton />}
            {state === 'error' && <StatePanel title="Не удалось загрузить корзину" text="Проверьте подключение к API и повторите попытку позже." />}
            {state === 'unauthorized' && (
              <StatePanel title="Нужно войти в аккаунт" text="Корзина доступна только после авторизации." action={<Button onClick={() => navigate('/login')}>Войти</Button>} />
            )}
            {(state === 'empty' || (state === 'success' && items.length === 0)) && (
              <StatePanel title="Корзина пуста" text="Добавьте товары из магазина, чтобы оформить заказ." action={<Button onClick={() => navigate('/shop')}>Перейти в магазин</Button>} />
            )}

            {state === 'success' && items.length > 0 && (
              <div className="cart-list">
                {items.map((item) => (
                  <article className="cart-item-card" key={item.id}>
                    <Link to={`/shop/${item.product.slug}`} className="cart-item-card__image">
                      <img alt={item.product.title} src={item.image} />
                    </Link>
                    <div className="cart-item-card__main">
                      <Link to={`/shop/${item.product.slug}`}>{item.product.title}</Link>
                      <p>{item.product.description}</p>
                      <span>{item.product.stock > 0 ? 'В наличии' : 'Нет в наличии'}</span>
                    </div>
                    <div className="cart-quantity" aria-label="Количество">
                      <button type="button" onClick={() => changeQuantity(item, item.quantity - 1)}><Minus size={16} /></button>
                      <strong>{item.quantity}</strong>
                      <button type="button" onClick={() => changeQuantity(item, item.quantity + 1)}><Plus size={16} /></button>
                    </div>
                    <div className="cart-item-price">
                      <span>{formatMoney(item.price)}</span>
                      <strong>{formatMoney(item.price * item.quantity)}</strong>
                    </div>
                    <button className="cart-remove" type="button" aria-label="Удалить товар" onClick={() => removeItem(item)}>
                      <Trash2 size={20} />
                    </button>
                  </article>
                ))}
              </div>
            )}
          </section>

          <aside className="cart-summary">
            <h2>Итого</h2>
            <dl>
              <dt>Товары</dt>
              <dd>{formatMoney(totals.productsTotal)}</dd>
              <dt>Скидка</dt>
              <dd>{totals.discount ? `− ${formatMoney(totals.discount)}` : '0 ₽'}</dd>
              <dt>Доставка</dt>
              <dd>{totals.delivery ? formatMoney(totals.delivery) : 'Бесплатно'}</dd>
            </dl>
            <div className="cart-summary__total">
              <span>К оплате</span>
              <strong>{formatMoney(totals.total)}</strong>
            </div>
            <div className="cart-promo">
              <label htmlFor="cart-promo">Промокод</label>
              <div>
                <input id="cart-promo" value={promo} onChange={(event) => setPromo(event.target.value)} placeholder="BEATRIS10" />
                <button type="button" onClick={applyPromo}>OK</button>
              </div>
              {message && <p>{message}</p>}
            </div>
            <Button type="button" onClick={() => navigate('/account/orders')}>Оформить заказ</Button>
            <div className="cart-summary__note">
              <ShieldCheck size={18} />
              <span>Безопасная онлайн-оплата и подтверждение заказа администратором.</span>
            </div>
            <div className="cart-summary__note">
              <Truck size={18} />
              <span>Бесплатная доставка при заказе от 15 000 ₽.</span>
            </div>
          </aside>
        </div>
      </div>
    </main>
  );
}

function StatePanel({ title, text, action }: { title: string; text: string; action?: React.ReactNode }) {
  return (
    <section className="cart-state">
      <ShoppingCart size={34} />
      <h2>{title}</h2>
      <p>{text}</p>
      {action}
    </section>
  );
}

function CartSkeleton() {
  return (
    <div className="cart-skeleton" aria-label="Загрузка корзины">
      {[1, 2, 3].map((item) => (
        <div key={item}>
          <span />
          <span />
          <span />
        </div>
      ))}
    </div>
  );
}
