import {
  CalendarDays,
  ChevronRight,
  ClipboardList,
  Heart,
  Home,
  LogOut,
  ShoppingBag,
  ShoppingCart,
  UserRound,
} from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import { ApiError } from '@/shared/api/client';
import { getWishlist, type WishlistItem } from '@/shared/api/wishlist';
import { Button } from '@/shared/ui/Button';

import './PatientWishlistPage.css';

type WishlistProduct = {
  id: string;
  slug: string;
  brand: string;
  title: string;
  price: string;
  image: string;
};

type FavoriteService = {
  title: string;
  slug: string;
  price: string;
  text: string;
  image: string;
};

type ViewState = 'loading' | 'success' | 'empty' | 'error' | 'unauthorized';

const navItems = [
  { label: 'Профиль', to: '/account', icon: <UserRound /> },
  { label: 'Мои записи', to: '/account/appointments', icon: <CalendarDays /> },
  { label: 'Рекомендации врача', to: '/account/recommendations', icon: <ClipboardList /> },
  { label: 'Мои заказы', to: '/account/orders', icon: <ShoppingBag /> },
  { label: 'Избранное', to: '/account/wishlist', icon: <Heart />, active: true },
  { label: 'Корзина', to: '/account/cart', icon: <ShoppingCart />, badge: '2' },
];

const demoProducts: WishlistProduct[] = [
  {
    id: 'c-e-ferulic',
    slug: 'c-e-ferulic',
    brand: 'SkinCeuticals',
    title: 'C E Ferulic',
    price: '16 900 ₽',
    image: 'https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?auto=format&fit=crop&w=420&q=85',
  },
  {
    id: 'daily-power-defense',
    slug: 'daily-power-defense',
    brand: 'ZO Skin Health',
    title: 'Daily Power Defense',
    price: '12 500 ₽',
    image: 'https://images.unsplash.com/photo-1617897903246-719242758050?auto=format&fit=crop&w=420&q=85',
  },
  {
    id: 'daily-radiance-vitamin-c',
    slug: 'daily-radiance-vitamin-c',
    brand: 'Medik8',
    title: 'Daily Radiance Vitamin C',
    price: '9 850 ₽',
    image: 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=420&q=85',
  },
  {
    id: 'hydra-hyal-serum',
    slug: 'hydra-hyal-serum',
    brand: 'Filorga',
    title: 'Hydra-Hyal Serum',
    price: '6 450 ₽',
    image: 'https://images.unsplash.com/photo-1556228578-8c89e6adf883?auto=format&fit=crop&w=420&q=85',
  },
];

const favoriteServices: FavoriteService[] = [
  {
    title: 'RF-лифтинг лица',
    slug: 'smas-lifting',
    price: 'от 7 500 ₽',
    text: 'Безоперационная подтяжка кожи с помощью радиочастотной энергии.',
    image: 'https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?auto=format&fit=crop&w=520&q=85',
  },
  {
    title: 'Биоревитализация',
    slug: 'biorevitalizatsiya',
    price: 'от 9 000 ₽',
    text: 'Глубокое увлажнение кожи и восстановление её упругости.',
    image: 'https://images.unsplash.com/photo-1606811971618-4486d14f3f99?auto=format&fit=crop&w=520&q=85',
  },
  {
    title: 'УЗ-чистка лица',
    slug: 'lazernaya-epilyatsiya',
    price: 'от 4 500 ₽',
    text: 'Деликатное очищение кожи от загрязнений и излишков себума.',
    image: 'https://images.unsplash.com/photo-1616391182219-e080b4d1043a?auto=format&fit=crop&w=520&q=85',
  },
];

const accessTokenKeys = ['beatris_access_token', 'accessToken', 'authToken'];

function getStoredAccessToken() {
  return accessTokenKeys.map((key) => window.localStorage.getItem(key)).find(Boolean);
}

function formatMoney(value: number) {
  return `${new Intl.NumberFormat('ru-RU').format(value)} ₽`;
}

function mapWishlistItem(item: WishlistItem): WishlistProduct {
  return {
    id: item.id,
    slug: item.product.slug,
    brand: item.product.title.split(' ')[0] ?? 'Beatris',
    title: item.product.title,
    price: formatMoney(item.product.price),
    image: item.product.imageUrl ?? 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=420&q=85',
  };
}

export function PatientWishlistPage() {
  const navigate = useNavigate();
  const [state, setState] = useState<ViewState>('loading');
  const [products, setProducts] = useState<WishlistProduct[]>([]);
  const [activeTab, setActiveTab] = useState<'products' | 'services'>('products');

  useEffect(() => {
    let isMounted = true;
    const token = getStoredAccessToken();

    if (!token) {
      setProducts(demoProducts);
      setState('success');
      return;
    }

    getWishlist(token)
      .then((items) => {
        if (!isMounted) return;
        const mappedItems = items.map(mapWishlistItem);
        setProducts(mappedItems);
        setState(mappedItems.length ? 'success' : 'empty');
      })
      .catch((error: unknown) => {
        if (!isMounted) return;
        setState(error instanceof ApiError && error.status === 401 ? 'unauthorized' : 'error');
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const summary = useMemo(() => `${products.length} товаров и ${favoriteServices.length} услуги`, [products.length]);

  const removeProduct = (id: string) => {
    setProducts((currentProducts) => currentProducts.filter((product) => product.id !== id));
  };

  return (
    <main className="wishlist-page">
      <div className="wishlist-container">
        <nav className="wishlist-breadcrumb" aria-label="Хлебные крошки">
          <Link to="/"><Home size={15} /> Главная</Link>
          <ChevronRight size={14} />
          <Link to="/account">Личный кабинет</Link>
          <ChevronRight size={14} />
          <span>Избранное</span>
        </nav>

        <div className="wishlist-heading">
          <h1>Избранное</h1>
          <aside>
            <Heart size={28} />
            <span>Всего в избранном<strong>{summary}</strong></span>
          </aside>
        </div>

        <div className="wishlist-layout">
          <aside className="wishlist-sidebar" aria-label="Навигация личного кабинета">
            {navItems.map((item) => (
              <Link className={item.active ? 'is-active' : ''} key={item.label} to={item.to}>
                {item.icon}
                <span>{item.label}</span>
                {item.badge && <b>{item.badge}</b>}
              </Link>
            ))}
            <button type="button" onClick={() => navigate('/login')}>
              <LogOut />
              <span>Выйти</span>
            </button>
          </aside>

          <section className="wishlist-content">
            <div className="wishlist-tabs" role="tablist" aria-label="Разделы избранного">
              <button className={activeTab === 'products' ? 'is-active' : ''} type="button" onClick={() => setActiveTab('products')}>
                Товары
              </button>
              <button className={activeTab === 'services' ? 'is-active' : ''} type="button" onClick={() => setActiveTab('services')}>
                Услуги
              </button>
            </div>

            {activeTab === 'products' && (
              <>
                {state === 'loading' && <WishlistSkeleton />}
                {state === 'error' && <StatePanel title="Не удалось загрузить избранное" text="Проверьте подключение к API и повторите попытку позже." />}
                {state === 'unauthorized' && (
                  <StatePanel title="Нужно войти в аккаунт" text="Избранные товары доступны только после авторизации." action={<Button onClick={() => navigate('/login')}>Войти</Button>} />
                )}
                {(state === 'empty' || (state === 'success' && products.length === 0)) && (
                  <StatePanel title="В избранном пока пусто" text="Добавляйте товары из магазина, чтобы быстро возвращаться к ним позже." action={<Button onClick={() => navigate('/shop')}>Перейти в магазин</Button>} />
                )}
                {state === 'success' && products.length > 0 && (
                  <div className="wishlist-product-grid">
                    {products.map((product) => (
                      <article className="wishlist-product-card" key={product.id}>
                        <button aria-label="Удалить из избранного" type="button" onClick={() => removeProduct(product.id)}>
                          <Heart size={24} />
                        </button>
                        <Link to={`/shop/${product.slug}`} className="wishlist-product-card__image">
                          <img alt={product.title} src={product.image} />
                        </Link>
                        <span>{product.brand}</span>
                        <h2>{product.title}</h2>
                        <strong>{product.price}</strong>
                        <Button type="button">В корзину</Button>
                        <button className="wishlist-remove" type="button" onClick={() => removeProduct(product.id)}>Удалить</button>
                      </article>
                    ))}
                  </div>
                )}
              </>
            )}

            {activeTab === 'services' && (
              <section className="wishlist-services">
                <div className="wishlist-services__head">
                  <h2>Избранные услуги</h2>
                  <Link to="/services">Смотреть все услуги <ChevronRight size={18} /></Link>
                </div>
                <div className="wishlist-service-grid">
                  {favoriteServices.map((service) => (
                    <article className="wishlist-service-card" key={service.title}>
                      <Link to={`/services/${service.slug}`}>
                        <img alt={service.title} src={service.image} />
                      </Link>
                      <div>
                        <h3>{service.title}</h3>
                        <strong>{service.price}</strong>
                        <p>{service.text}</p>
                        <Button type="button">Записаться</Button>
                      </div>
                      <button aria-label="Удалить услугу из избранного" type="button"><Heart size={24} /></button>
                    </article>
                  ))}
                </div>
              </section>
            )}
          </section>
        </div>
      </div>
    </main>
  );
}

function StatePanel({ title, text, action }: { title: string; text: string; action?: React.ReactNode }) {
  return (
    <section className="wishlist-state">
      <Heart size={34} />
      <h2>{title}</h2>
      <p>{text}</p>
      {action}
    </section>
  );
}

function WishlistSkeleton() {
  return (
    <div className="wishlist-skeleton" aria-label="Загрузка избранного">
      {[1, 2, 3, 4].map((item) => (
        <div key={item}>
          <span />
          <span />
          <span />
        </div>
      ))}
    </div>
  );
}
