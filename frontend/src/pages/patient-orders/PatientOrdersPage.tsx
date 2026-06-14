import {
  Banknote,
  CalendarDays,
  ChevronDown,
  ChevronRight,
  ClipboardList,
  CreditCard,
  Download,
  Heart,
  Home,
  LogOut,
  MapPin,
  PackageCheck,
  RefreshCw,
  ShoppingBag,
  ShoppingCart,
  Truck,
  UserRound,
} from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import { ApiError } from '@/shared/api/client';
import { getMyOrders, type Order, type OrderStatus, type PaymentStatus } from '@/shared/api/orders';
import { Button } from '@/shared/ui/Button';

import './PatientOrdersPage.css';

type OrderView = {
  id: string;
  number: string;
  createdAt: string;
  status: OrderStatus;
  statusText: string;
  paymentStatus: PaymentStatus;
  total: number;
  totalText: string;
  recipientName: string;
  recipientPhone: string;
  deliveryAddress: string;
  deliveryMethod: string;
  deliveryDate: string;
  paymentMethod: string;
  paidAt: string;
  items: Array<{
    title: string;
    price: number;
    priceText: string;
    quantity: number;
    subtotalText: string;
    image: string;
  }>;
};

type ViewState = 'loading' | 'success' | 'empty' | 'error' | 'unauthorized';
type TabKey = 'all' | 'paid' | 'processing' | 'delivering' | 'completed';

const productImages = [
  'https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?auto=format&fit=crop&w=220&q=85',
  'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=220&q=85',
  'https://images.unsplash.com/photo-1556228578-8c89e6adf883?auto=format&fit=crop&w=220&q=85',
  'https://images.unsplash.com/photo-1617897903246-719242758050?auto=format&fit=crop&w=220&q=85',
];

const navItems = [
  { label: 'Профиль', to: '/account', icon: <UserRound /> },
  { label: 'Мои записи', to: '/account/appointments', icon: <CalendarDays /> },
  { label: 'Рекомендации врача', to: '/account/recommendations', icon: <ClipboardList /> },
  { label: 'Мои заказы', to: '/account/orders', icon: <ShoppingBag />, active: true },
  { label: 'Избранное', to: '/account/wishlist', icon: <Heart /> },
  { label: 'Корзина', to: '/account/cart', icon: <ShoppingCart />, badge: '2' },
];

const tabs: Array<{ key: TabKey; label: string }> = [
  { key: 'all', label: 'Все' },
  { key: 'paid', label: 'Оплаченные' },
  { key: 'processing', label: 'В обработке' },
  { key: 'delivering', label: 'Доставляются' },
  { key: 'completed', label: 'Завершённые' },
];

const demoOrders: OrderView[] = [
  {
    id: 'demo-9876',
    number: '9876',
    createdAt: '12 мая 2024 в 11:24',
    status: 'processing',
    statusText: 'Доставляется',
    paymentStatus: 'paid',
    total: 8450,
    totalText: '8 450 ₽',
    recipientName: 'Анна Иванова',
    recipientPhone: '+7 (910) 123-45-67',
    deliveryAddress: 'Москва, ул. Малая Бронная, 18, кв. 12',
    deliveryMethod: 'Курьером',
    deliveryDate: '14 мая 2024 с 10:00 до 14:00',
    paymentMethod: 'Банковской картой онлайн',
    paidAt: '12 мая 2024 в 11:25',
    items: [
      { title: 'SkinCeuticals C E Ferulic', price: 6900, priceText: '6 900 ₽', quantity: 1, subtotalText: '6 900 ₽', image: productImages[0] },
      { title: 'Солнцезащитный крем SPF 50', price: 2300, priceText: '2 300 ₽', quantity: 1, subtotalText: '2 300 ₽', image: productImages[1] },
      { title: 'Увлажняющая сыворотка Hydrating B5', price: 4200, priceText: '4 200 ₽', quantity: 1, subtotalText: '4 200 ₽', image: productImages[2] },
      { title: 'Подарочный пакет BEATRIS', price: 250, priceText: '250 ₽', quantity: 1, subtotalText: '250 ₽', image: productImages[3] },
      { title: 'Пробник крема (подарок)', price: 0, priceText: '0 ₽', quantity: 1, subtotalText: '0 ₽', image: productImages[1] },
    ],
  },
  {
    id: 'demo-9761',
    number: '9761',
    createdAt: '28 апреля 2024',
    status: 'created',
    statusText: 'В обработке',
    paymentStatus: 'pending',
    total: 4200,
    totalText: '4 200 ₽',
    recipientName: 'Анна Иванова',
    recipientPhone: '+7 (910) 123-45-67',
    deliveryAddress: 'Москва, ул. Малая Бронная, 18',
    deliveryMethod: 'Курьером',
    deliveryDate: 'Согласуется',
    paymentMethod: 'Банковской картой онлайн',
    paidAt: 'Ожидает оплаты',
    items: [{ title: 'Увлажняющая сыворотка Hydrating B5', price: 4200, priceText: '4 200 ₽', quantity: 1, subtotalText: '4 200 ₽', image: productImages[2] }],
  },
  {
    id: 'demo-9654',
    number: '9654',
    createdAt: '15 апреля 2024',
    status: 'processing',
    statusText: 'Доставляется',
    paymentStatus: 'paid',
    total: 3750,
    totalText: '3 750 ₽',
    recipientName: 'Анна Иванова',
    recipientPhone: '+7 (910) 123-45-67',
    deliveryAddress: 'Москва, ул. Малая Бронная, 18',
    deliveryMethod: 'Пункт выдачи',
    deliveryDate: '16 апреля 2024',
    paymentMethod: 'Банковской картой онлайн',
    paidAt: '15 апреля 2024',
    items: [{ title: 'Мягкий очищающий гель', price: 3750, priceText: '3 750 ₽', quantity: 1, subtotalText: '3 750 ₽', image: productImages[1] }],
  },
  {
    id: 'demo-9520',
    number: '9520',
    createdAt: '3 апреля 2024',
    status: 'delivered',
    statusText: 'Завершён',
    paymentStatus: 'paid',
    total: 7100,
    totalText: '7 100 ₽',
    recipientName: 'Анна Иванова',
    recipientPhone: '+7 (910) 123-45-67',
    deliveryAddress: 'Москва, ул. Малая Бронная, 18',
    deliveryMethod: 'Курьером',
    deliveryDate: '4 апреля 2024',
    paymentMethod: 'Банковской картой онлайн',
    paidAt: '3 апреля 2024',
    items: [{ title: 'SkinCeuticals C E Ferulic', price: 7100, priceText: '7 100 ₽', quantity: 1, subtotalText: '7 100 ₽', image: productImages[0] }],
  },
  {
    id: 'demo-9405',
    number: '9405',
    createdAt: '21 марта 2024',
    status: 'delivered',
    statusText: 'Завершён',
    paymentStatus: 'paid',
    total: 2850,
    totalText: '2 850 ₽',
    recipientName: 'Анна Иванова',
    recipientPhone: '+7 (910) 123-45-67',
    deliveryAddress: 'Москва, ул. Малая Бронная, 18',
    deliveryMethod: 'Пункт выдачи',
    deliveryDate: '22 марта 2024',
    paymentMethod: 'Банковской картой онлайн',
    paidAt: '21 марта 2024',
    items: [{ title: 'Подарочный набор ухода', price: 2850, priceText: '2 850 ₽', quantity: 1, subtotalText: '2 850 ₽', image: productImages[3] }],
  },
];

const accessTokenKeys = ['beatris_access_token', 'accessToken', 'authToken'];

function getStoredAccessToken() {
  return accessTokenKeys.map((key) => window.localStorage.getItem(key)).find(Boolean);
}

function formatMoney(value: number) {
  return `${new Intl.NumberFormat('ru-RU').format(value)} ₽`;
}

function formatDate(value?: string | null) {
  if (!value) return 'Дата не указана';
  return new Intl.DateTimeFormat('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  }).format(new Date(value));
}

function getStatusText(status: OrderStatus) {
  const labels: Record<OrderStatus, string> = {
    created: 'В обработке',
    paid: 'Оплачен',
    processing: 'Доставляется',
    delivered: 'Завершён',
    cancelled: 'Отменён',
  };
  return labels[status];
}

function mapApiOrder(order: Order, index: number): OrderView {
  const createdDate = formatDate(order.createdAt);
  const total = order.totalPrice;

  return {
    id: order.id,
    number: order.id.slice(0, 8).toUpperCase(),
    createdAt: createdDate,
    status: order.orderStatus,
    statusText: getStatusText(order.orderStatus),
    paymentStatus: order.paymentStatus,
    total,
    totalText: formatMoney(total),
    recipientName: order.recipientName ?? 'Получатель не указан',
    recipientPhone: order.recipientPhone ?? 'Телефон не указан',
    deliveryAddress: order.deliveryAddress ?? 'Адрес доставки не указан',
    deliveryMethod: 'Курьером',
    deliveryDate: order.orderStatus === 'delivered' ? createdDate : 'Согласуется',
    paymentMethod: 'Банковской картой онлайн',
    paidAt: order.paymentStatus === 'paid' ? createdDate : 'Ожидает оплаты',
    items: order.items.map((item, itemIndex) => ({
      title: item.product.title,
      price: item.price,
      priceText: formatMoney(item.price),
      quantity: item.quantity,
      subtotalText: formatMoney(item.subtotal),
      image: item.product.imageUrl ?? productImages[(index + itemIndex) % productImages.length],
    })),
  };
}

export function PatientOrdersPage() {
  const navigate = useNavigate();
  const [state, setState] = useState<ViewState>('loading');
  const [orders, setOrders] = useState<OrderView[]>([]);
  const [activeTab, setActiveTab] = useState<TabKey>('all');
  const [openId, setOpenId] = useState('');

  useEffect(() => {
    let isMounted = true;
    const token = getStoredAccessToken();

    if (!token) {
      setOrders(demoOrders);
      setOpenId(demoOrders[0]?.id ?? '');
      setState('success');
      return;
    }

    getMyOrders(token)
      .then((items) => {
        if (!isMounted) return;
        const mappedOrders = items.map(mapApiOrder);
        setOrders(mappedOrders);
        setOpenId(mappedOrders[0]?.id ?? '');
        setState(mappedOrders.length ? 'success' : 'empty');
      })
      .catch((error: unknown) => {
        if (!isMounted) return;
        setState(error instanceof ApiError && error.status === 401 ? 'unauthorized' : 'error');
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const filteredOrders = useMemo(() => {
    return orders.filter((order) => {
      if (activeTab === 'all') return true;
      if (activeTab === 'paid') return order.paymentStatus === 'paid';
      if (activeTab === 'processing') return order.status === 'created' || order.status === 'paid';
      if (activeTab === 'delivering') return order.status === 'processing';
      return order.status === 'delivered';
    });
  }, [activeTab, orders]);

  const stats = useMemo(() => {
    const spent = orders.reduce((sum, order) => sum + order.total, 0);
    const activeDeliveries = orders.filter((order) => order.status === 'processing').length;

    return {
      count: orders.length,
      spentText: formatMoney(spent),
      activeDeliveries,
    };
  }, [orders]);

  return (
    <main className="orders-page">
      <div className="orders-container">
        <nav className="orders-breadcrumb" aria-label="Хлебные крошки">
          <Link to="/"><Home size={15} /> Главная</Link>
          <ChevronRight size={14} />
          <Link to="/account">Личный кабинет</Link>
          <ChevronRight size={14} />
          <span>Мои заказы</span>
        </nav>

        <h1>Мои заказы</h1>

        <div className="orders-layout">
          <aside className="orders-sidebar" aria-label="Навигация личного кабинета">
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

          <section className="orders-content">
            <div className="orders-tabs" role="tablist" aria-label="Статусы заказов">
              {tabs.map((tab) => (
                <button className={activeTab === tab.key ? 'is-active' : ''} key={tab.key} type="button" onClick={() => setActiveTab(tab.key)}>
                  {tab.label}
                </button>
              ))}
            </div>

            {state === 'loading' && <OrdersSkeleton />}
            {state === 'error' && <StatePanel title="Не удалось загрузить заказы" text="Проверьте подключение к API и повторите попытку позже." />}
            {state === 'unauthorized' && (
              <StatePanel title="Нужно войти в аккаунт" text="Заказы доступны только после авторизации." action={<Button onClick={() => navigate('/login')}>Войти</Button>} />
            )}
            {state === 'empty' && <StatePanel title="Заказов пока нет" text="Когда вы оформите покупку в магазине, заказ появится в этом разделе." action={<Button onClick={() => navigate('/shop')}>Перейти в магазин</Button>} />}
            {state === 'success' && filteredOrders.length === 0 && <StatePanel title="Заказов с таким статусом нет" text="Выберите другую вкладку, чтобы посмотреть остальные заказы." />}

            {state === 'success' && filteredOrders.length > 0 && (
              <div className="orders-list">
                {filteredOrders.map((order) => (
                  <OrderCard key={order.id} order={order} isOpen={openId === order.id} onToggle={() => setOpenId(openId === order.id ? '' : order.id)} />
                ))}
              </div>
            )}
          </section>

          <aside className="orders-summary">
            <SummaryCard icon={<PackageCheck />} title="Всего заказов" value={String(stats.count)} text={`на сумму ${stats.spentText}`} />
            <SummaryCard icon={<CreditCard />} title="Потрачено всего" value={stats.spentText} text="за всё время" />
            <SummaryCard icon={<Truck />} title="Активные доставки" value={String(stats.activeDeliveries)} text="ожидают получения" />
            <Button type="button" onClick={() => navigate('/account/cart')}>Перейти в корзину</Button>
          </aside>
        </div>
      </div>
    </main>
  );
}

function OrderCard({ order, isOpen, onToggle }: { order: OrderView; isOpen: boolean; onToggle: () => void }) {
  const visibleImages = order.items.slice(0, 4);
  const hiddenCount = Math.max(order.items.length - visibleImages.length, 0);

  return (
    <article className={`order-card ${isOpen ? 'is-open' : ''}`.trim()}>
      <button className="order-card__summary" type="button" onClick={onToggle} aria-expanded={isOpen}>
        <span className="order-card__number">Заказ №{order.number}</span>
        <span className="order-card__date">{order.createdAt}</span>
        <StatusBadge status={order.status} label={order.statusText} />
        <strong>{order.totalText}</strong>
        <ChevronDown size={19} />
      </button>

      {isOpen && (
        <div className="order-card__body">
          <div className="order-card__top">
            <div className="order-products-preview">
              {visibleImages.map((item) => (
                <img alt={item.title} key={item.title} src={item.image} />
              ))}
              {hiddenCount > 0 && <span>+{hiddenCount}<small>товаров</small></span>}
            </div>
            <div className="order-total">
              <span>Сумма заказа</span>
              <strong>{order.totalText}</strong>
            </div>
            <div className="order-actions">
              <Button>Подробнее</Button>
              <button type="button"><RefreshCw size={16} /> Повторить заказ</button>
              <button type="button"><MapPin size={16} /> Отследить</button>
            </div>
          </div>

          <div className="order-details-grid">
            <section>
              <h2>Информация о доставке</h2>
              <dl>
                <dt>Получатель</dt><dd>{order.recipientName}</dd>
                <dt>Телефон</dt><dd>{order.recipientPhone}</dd>
                <dt>Адрес доставки</dt><dd>{order.deliveryAddress}</dd>
                <dt>Способ доставки</dt><dd>{order.deliveryMethod}</dd>
                <dt>Дата доставки</dt><dd>{order.deliveryDate}</dd>
              </dl>
            </section>
            <section>
              <h2>Информация об оплате</h2>
              <dl>
                <dt>Способ оплаты</dt><dd>{order.paymentMethod}</dd>
                <dt>Статус оплаты</dt><dd><span className={order.paymentStatus === 'paid' ? 'is-paid' : 'is-pending'}>{order.paymentStatus === 'paid' ? 'Оплачено' : 'Ожидает оплаты'}</span></dd>
                <dt>Сумма оплаты</dt><dd>{order.totalText}</dd>
                <dt>Дата оплаты</dt><dd>{order.paidAt}</dd>
                <dt>Чек</dt><dd><button className="order-receipt" type="button">Скачать <Download size={15} /></button></dd>
              </dl>
            </section>
            <section className="order-composition">
              <h2>Состав заказа</h2>
              <table>
                <thead>
                  <tr>
                    <th>Товар</th>
                    <th>Цена</th>
                    <th>Кол-во</th>
                    <th>Сумма</th>
                  </tr>
                </thead>
                <tbody>
                  {order.items.map((item) => (
                    <tr key={item.title}>
                      <td>{item.title}</td>
                      <td>{item.priceText}</td>
                      <td>{item.quantity}</td>
                      <td>{item.subtotalText}</td>
                    </tr>
                  ))}
                  <tr>
                    <td colSpan={3}>Итого</td>
                    <td>{order.totalText}</td>
                  </tr>
                </tbody>
              </table>
            </section>
          </div>
        </div>
      )}
    </article>
  );
}

function StatusBadge({ status, label }: { status: OrderStatus; label: string }) {
  const Icon = status === 'created' ? Banknote : status === 'processing' ? Truck : PackageCheck;
  return (
    <span className={`order-status order-status--${status}`}>
      <Icon size={14} />
      {label}
    </span>
  );
}

function SummaryCard({ icon, title, value, text }: { icon: React.ReactNode; title: string; value: string; text: string }) {
  return (
    <article className="orders-summary-card">
      <h2>{title}</h2>
      <div>
        <span>{icon}</span>
        <strong>{value}</strong>
      </div>
      <p>{text}</p>
    </article>
  );
}

function StatePanel({ title, text, action }: { title: string; text: string; action?: React.ReactNode }) {
  return (
    <section className="orders-state">
      <ShoppingBag size={34} />
      <h2>{title}</h2>
      <p>{text}</p>
      {action}
    </section>
  );
}

function OrdersSkeleton() {
  return (
    <div className="orders-skeleton" aria-label="Загрузка заказов">
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
