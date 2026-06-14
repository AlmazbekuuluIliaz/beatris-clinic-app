import {
  BriefcaseMedical,
  CalendarDays,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  ClipboardList,
  Heart,
  LogOut,
  RotateCcw,
  ShoppingBag,
  ShoppingCart,
  UserRound,
} from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import { ApiError } from '@/shared/api/client';
import { getMyRecommendations, type Recommendation } from '@/shared/api/recommendations';
import { Button } from '@/shared/ui/Button';

import './PatientRecommendationsPage.css';

type Doctor = {
  id: string;
  name: string;
  position: string;
  photo: string;
};

type Product = {
  id: string;
  title: string;
  description: string;
  price: string;
  image: string;
};

type RecommendationView = {
  id: string;
  visitDate: string;
  visitDateValue: string;
  procedure: string;
  doctor: Doctor;
  comment: string;
  careTips: string[];
  products: Product[];
  procedures: string[];
};

type ViewState = 'loading' | 'success' | 'empty' | 'error' | 'unauthorized';

const doctors: Doctor[] = [
  {
    id: 'doctor-smirnova',
    name: 'Смирнова Екатерина Владимировна',
    position: 'Врач-косметолог, дерматовенеролог',
    photo: 'https://images.unsplash.com/photo-1594824476967-48c8b964273f?auto=format&fit=crop&w=160&q=85',
  },
  {
    id: 'doctor-petrova',
    name: 'Петрова Ольга Сергеевна',
    position: 'Врач-косметолог',
    photo: 'https://images.unsplash.com/photo-1559839734-2b71ea197ec2?auto=format&fit=crop&w=160&q=85',
  },
  {
    id: 'doctor-kozlova',
    name: 'Козлова Мария Андреевна',
    position: 'Врач-косметолог',
    photo: 'https://images.unsplash.com/photo-1582750433449-648ed127bb54?auto=format&fit=crop&w=160&q=85',
  },
];

const products: Product[] = [
  {
    id: 'gentle-cleanser',
    title: 'SkinCeuticals Gentle Cleanser',
    description: 'Мягкий очищающий гель для чувствительной кожи',
    price: '3 800 ₸',
    image: 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=220&q=85',
  },
  {
    id: 'cicaplast',
    title: 'Cicaplast Baume B5+',
    description: 'Восстанавливающий бальзам для раздраженной кожи',
    price: '1 550 ₸',
    image: 'https://images.unsplash.com/photo-1617897903246-719242758050?auto=format&fit=crop&w=220&q=85',
  },
  {
    id: 'ce-ferulic',
    title: 'SkinCeuticals C E Ferulic',
    description: 'Антиоксидантная сыворотка для сияния кожи',
    price: '14 900 ₸',
    image: 'https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?auto=format&fit=crop&w=220&q=85',
  },
];

const demoRecommendations: RecommendationView[] = [
  {
    id: 'demo-1',
    visitDate: '12 мая 2024, 11:00',
    visitDateValue: '2024-05-12',
    procedure: 'Контурная пластика губ',
    doctor: doctors[0],
    comment:
      'Проведена процедура контурной пластики губ препаратом на основе гиалуроновой кислоты. Цель — восстановление объема и коррекция контура. Результат проявляется постепенно в течение 3–5 дней.',
    careTips: [
      'В течение 24 часов избегать прикосновений к губам',
      'Не посещать сауну, баню и солярий в течение 3 дней',
      'Исключить интенсивные физические нагрузки на 2 дня',
      'Не употреблять алкоголь в течение 24 часов',
      'Использовать увлажняющий бальзам для губ по мере необходимости',
      'При появлении отеков — холодные компрессы через ткань',
    ],
    products: [products[0], products[1]],
    procedures: ['Биоревитализация', 'Плазмотерапия (PRP)', 'Мезотерапия губ'],
  },
  {
    id: 'demo-2',
    visitDate: '25 апр. 2024, 16:30',
    visitDateValue: '2024-04-25',
    procedure: 'Биоревитализация',
    doctor: doctors[1],
    comment: 'Рекомендован курс увлажняющего восстановления и ежедневная SPF-защита для поддержания ровного тона кожи.',
    careTips: ['Использовать мягкое очищение утром и вечером', 'Наносить SPF 50 перед выходом на улицу', 'Исключить пилинги на 5 дней'],
    products: [products[2]],
    procedures: ['Уход HydraFacial', 'LED-терапия', 'Консультация косметолога'],
  },
  {
    id: 'demo-3',
    visitDate: '10 апр. 2024, 13:00',
    visitDateValue: '2024-04-10',
    procedure: 'Чистка лица',
    doctor: doctors[0],
    comment: 'После процедуры важно поддерживать барьер кожи и не использовать агрессивные кислоты в домашнем уходе.',
    careTips: ['Не трогать лицо руками в течение дня', 'Использовать восстанавливающий крем', 'Отложить декоративную косметику на 24 часа'],
    products: [products[0]],
    procedures: ['Атравматичная чистка', 'Ультразвуковая чистка'],
  },
  {
    id: 'demo-4',
    visitDate: '28 мар. 2024, 11:30',
    visitDateValue: '2024-03-28',
    procedure: 'RF-лифтинг лица',
    doctor: doctors[2],
    comment: 'Для усиления результата рекомендовано повторить процедуру по индивидуальному графику и добавить поддерживающий домашний уход.',
    careTips: ['Пить достаточно воды', 'Не перегревать кожу 48 часов', 'Использовать увлажняющую сыворотку'],
    products: [products[1], products[2]],
    procedures: ['SMAS-лифтинг', 'Биоревитализация', 'Массаж лица'],
  },
];

const navItems = [
  { label: 'Профиль', to: '/account', icon: <UserRound /> },
  { label: 'Мои записи', to: '/account/appointments', icon: <CalendarDays /> },
  { label: 'Рекомендации врача', to: '/account/recommendations', icon: <ClipboardList />, active: true },
  { label: 'Мои заказы', to: '/account/orders', icon: <ShoppingBag /> },
  { label: 'Избранное', to: '/account/wishlist', icon: <Heart /> },
  { label: 'Корзина', to: '/account/cart', icon: <ShoppingCart />, badge: '2' },
];

const accessTokenKeys = ['beatris_access_token', 'accessToken', 'authToken'];

function getStoredAccessToken() {
  return accessTokenKeys.map((key) => window.localStorage.getItem(key)).find(Boolean);
}

function mapApiRecommendation(item: Recommendation, index: number): RecommendationView {
  const doctor = doctors[index % doctors.length];
  const linkedProducts = item.productIds.length
    ? item.productIds.map((id, productIndex) => products.find((product) => product.id === id) ?? products[productIndex % products.length])
    : [products[index % products.length]];

  return {
    id: item.id,
    visitDate: new Intl.DateTimeFormat('ru-RU', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(new Date(item.createdAt)),
    visitDateValue: item.createdAt.slice(0, 10),
    procedure: item.appointmentId ? 'Рекомендация после приема' : 'Индивидуальная рекомендация',
    doctor,
    comment: item.text,
    careTips: item.text
      .split(/\n|;/)
      .map((tip) => tip.trim())
      .filter(Boolean)
      .slice(0, 5),
    products: linkedProducts,
    procedures: ['Консультация косметолога', 'Поддерживающий уход', 'Контрольный прием'],
  };
}

export function PatientRecommendationsPage() {
  const navigate = useNavigate();
  const [state, setState] = useState<ViewState>('loading');
  const [recommendations, setRecommendations] = useState<RecommendationView[]>([]);
  const [selectedDoctor, setSelectedDoctor] = useState('');
  const [selectedDate, setSelectedDate] = useState('');
  const [openId, setOpenId] = useState('');

  useEffect(() => {
    let isMounted = true;
    const token = getStoredAccessToken();

    if (!token) {
      setRecommendations(demoRecommendations);
      setOpenId(demoRecommendations[0]?.id ?? '');
      setState('success');
      return;
    }

    getMyRecommendations(token)
      .then((items) => {
        if (!isMounted) return;

        const mappedItems = items.map(mapApiRecommendation);
        setRecommendations(mappedItems);
        setOpenId(mappedItems[0]?.id ?? '');
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

  const filteredRecommendations = useMemo(() => {
    return recommendations.filter((item) => {
      const doctorMatch = selectedDoctor ? item.doctor.id === selectedDoctor : true;
      const dateMatch = selectedDate ? item.visitDateValue === selectedDate : true;
      return doctorMatch && dateMatch;
    });
  }, [recommendations, selectedDate, selectedDoctor]);

  const resetFilters = () => {
    setSelectedDoctor('');
    setSelectedDate('');
  };

  return (
    <main className="recommendations-page">
      <div className="recommendations-container">
        <nav className="recommendations-breadcrumb" aria-label="Хлебные крошки">
          <Link to="/">Главная</Link>
          <ChevronRight size={14} />
          <Link to="/account">Личный кабинет</Link>
          <ChevronRight size={14} />
          <span>Рекомендации врача</span>
        </nav>

        <h1>Рекомендации врача</h1>

        <div className="recommendations-layout">
          <aside className="recommendations-sidebar" aria-label="Навигация личного кабинета">
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

          <section className="recommendations-main">
            <section className="recommendations-filter" aria-label="Фильтры рекомендаций">
              <label>
                Врач
                <select value={selectedDoctor} onChange={(event) => setSelectedDoctor(event.target.value)}>
                  <option value="">Выберите врача</option>
                  {doctors.map((doctor) => (
                    <option key={doctor.id} value={doctor.id}>{doctor.name}</option>
                  ))}
                </select>
              </label>
              <label>
                Дата посещения
                <input type="date" value={selectedDate} onChange={(event) => setSelectedDate(event.target.value)} />
              </label>
              <button type="button" onClick={resetFilters}>
                Сбросить фильтры
                <RotateCcw size={16} />
              </button>
            </section>

            {state === 'loading' && <RecommendationsSkeleton />}
            {state === 'error' && <StatePanel title="Не удалось загрузить рекомендации" text="Проверьте подключение к API и повторите попытку позже." />}
            {state === 'unauthorized' && (
              <StatePanel title="Нужно войти в аккаунт" text="Рекомендации врача доступны только пациенту после авторизации." action={<Button onClick={() => navigate('/login')}>Войти</Button>} />
            )}
            {state === 'empty' && <StatePanel title="Рекомендаций пока нет" text="После приема врач добавит назначения, средства ухода и рекомендуемые процедуры." />}

            {state === 'success' && filteredRecommendations.length === 0 && (
              <StatePanel title="По фильтрам ничего не найдено" text="Измените врача или дату посещения, чтобы увидеть другие рекомендации." />
            )}

            {state === 'success' && filteredRecommendations.length > 0 && (
              <div className="recommendations-list">
                {filteredRecommendations.map((item) => (
                  <RecommendationCard
                    key={item.id}
                    recommendation={item}
                    isOpen={openId === item.id}
                    onToggle={() => setOpenId(openId === item.id ? '' : item.id)}
                  />
                ))}
              </div>
            )}
          </section>
        </div>
      </div>
    </main>
  );
}

function RecommendationCard({
  recommendation,
  isOpen,
  onToggle,
}: {
  recommendation: RecommendationView;
  isOpen: boolean;
  onToggle: () => void;
}) {
  return (
    <article className={`recommendation-card ${isOpen ? 'is-open' : ''}`.trim()}>
      <button className="recommendation-card__summary" type="button" onClick={onToggle} aria-expanded={isOpen}>
        <span className="recommendation-card__date"><CalendarDays size={18} /> {recommendation.visitDate}</span>
        <span className="recommendation-card__doctor">
          <img alt={recommendation.doctor.name} src={recommendation.doctor.photo} />
          <span><strong>{recommendation.doctor.name}</strong><small>{recommendation.doctor.position}</small></span>
        </span>
        <span className="recommendation-card__procedure">{recommendation.procedure}</span>
        <ChevronDown className="recommendation-card__chevron" size={20} />
      </button>

      {isOpen && (
        <div className="recommendation-card__body">
          <section className="recommendation-note">
            <h2>Комментарий врача</h2>
            <p>{recommendation.comment}</p>
            <h3>Рекомендации по уходу</h3>
            <ul>
              {recommendation.careTips.map((tip) => (
                <li key={tip}><CheckCircle2 size={16} /> {tip}</li>
              ))}
            </ul>
          </section>

          <section className="recommendation-products">
            <h2>Рекомендованные средства</h2>
            {recommendation.products.map((product) => (
              <article key={product.id}>
                <img alt={product.title} src={product.image} />
                <div>
                  <h3>{product.title}</h3>
                  <p>{product.description}</p>
                  <strong>{product.price}</strong>
                </div>
                <Link to={`/shop/${product.id}`}>Подробнее</Link>
              </article>
            ))}
          </section>

          <section className="recommendation-procedures">
            <h2>Дополнительные рекомендуемые процедуры</h2>
            <div>
              {recommendation.procedures.map((procedure) => (
                <Link key={procedure} to="/services">
                  {procedure}
                  <ChevronRight size={18} />
                </Link>
              ))}
            </div>
            <Button type="button"><BriefcaseMedical size={18} /> Перейти к записи</Button>
          </section>
        </div>
      )}
    </article>
  );
}

function StatePanel({ title, text, action }: { title: string; text: string; action?: React.ReactNode }) {
  return (
    <section className="recommendations-state">
      <ClipboardList size={34} />
      <h2>{title}</h2>
      <p>{text}</p>
      {action}
    </section>
  );
}

function RecommendationsSkeleton() {
  return (
    <div className="recommendations-skeleton" aria-label="Загрузка рекомендаций">
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
