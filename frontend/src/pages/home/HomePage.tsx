import {
  ArrowRight,
  Award,
  BadgeCheck,
  CalendarDays,
  Check,
  ClipboardList,
  Heart,
  PackageCheck,
  ShieldCheck,
  Sparkles,
  Star,
  UsersRound,
} from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

import { getProducts, type Product } from '@/shared/api/products';
import { getServiceCategories, type ServiceCategory } from '@/shared/api/services';
import { getSpecialists, type Specialist } from '@/shared/api/specialists';
import { Button } from '@/shared/ui/Button';

import './HomePage.css';

const heroStats = [
  { icon: <Award size={28} />, value: '6', label: 'направлений услуг' },
  { icon: <UsersRound size={28} />, value: '12+', label: 'специалистов клиники' },
  { icon: <CalendarDays size={28} />, value: '24/7', label: 'забота о вашем комфорте' },
];

const defaultDirectionDescription = 'Подберём подходящие процедуры и специалиста по вашему запросу.';

const defaultDirectionImage =
  'https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?auto=format&fit=crop&w=360&q=85';

type DirectionsState = 'loading' | 'success' | 'empty' | 'error';
type SpecialistsState = 'loading' | 'success' | 'empty' | 'error';
type ProductsState = 'loading' | 'success' | 'fallback';

const specialistFallbackImage =
  'https://images.unsplash.com/photo-1559839734-2b71ea197ec2?auto=format&fit=crop&w=520&q=85';

const reasons = [
  'Медицинский подход и квалификация специалистов',
  'Проверенные методики с акцентом на естественность',
  'Комфорт, безопасность и забота',
  'Индивидуальный подбор ухода и плана лечения для стойкого результата',
];

const trustItems = [
  { icon: <ShieldCheck size={22} />, title: 'Безопасность', text: 'Сертифицированные методики' },
  { icon: <Heart size={22} />, title: 'Прозрачность', text: 'Честные рекомендации и цены' },
  { icon: <BadgeCheck size={22} />, title: 'Современность', text: 'Новейшие аппараты и препараты' },
];

const reviews = [
  {
    text: 'Прекрасная клиника с внимательным подходом и отличным результатом после процедур.',
    name: 'Алина',
    rating: 5,
  },
  {
    text: 'Удобное расположение и уютная атмосфера располагают. Доступные и профессиональные врачи.',
    name: 'Екатерина',
    rating: 5,
  },
  {
    text: 'После консультации и курса рекомендованной косметики кожа заметно улучшилась.',
    name: 'Марина',
    rating: 5,
  },
];

const productFallbackImage =
  'https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?auto=format&fit=crop&w=520&q=85';

const fallbackProducts = Array.from({ length: 4 }, (_, index) => ({
  id: `fallback-product-${index}`,
  title: 'Ждём карточку',
  price: '1.000 т',
  imageUrl: productFallbackImage,
  link: '/shop',
}));

function formatPrice(price: number) {
  return `${new Intl.NumberFormat('ru-RU').format(price)} ₸`;
}

const recommendationCards = [
  { icon: <ClipboardList size={22} />, text: 'Памятки после процедур' },
  { icon: <UsersRound size={22} />, text: 'Подбор средств по типу кожи' },
  { icon: <Award size={22} />, text: 'Истории нашей пациентки' },
  { icon: <Sparkles size={22} />, text: 'Как ухаживать за кожей' },
  { icon: <Check size={22} />, text: 'Ограничения и рекомендации' },
  { icon: <Heart size={22} />, text: 'Связаться с врачом' },
];

export function HomePage() {
  const [directionsState, setDirectionsState] = useState<DirectionsState>('loading');
  const [directions, setDirections] = useState<ServiceCategory[]>([]);
  const [specialistsState, setSpecialistsState] = useState<SpecialistsState>('loading');
  const [specialists, setSpecialists] = useState<Specialist[]>([]);
  const [productsState, setProductsState] = useState<ProductsState>('loading');
  const [products, setProducts] = useState<Product[]>([]);

  useEffect(() => {
    let isMounted = true;

    getServiceCategories()
      .then((items) => {
        if (!isMounted) {
          return;
        }

        setDirections(items);
        setDirectionsState(items.length > 0 ? 'success' : 'empty');
      })
      .catch(() => {
        if (!isMounted) {
          return;
        }

        setDirections([]);
        setDirectionsState('error');
      });

    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    let isMounted = true;

    getSpecialists()
      .then((items) => {
        if (!isMounted) {
          return;
        }

        setSpecialists(items);
        setSpecialistsState(items.length > 0 ? 'success' : 'empty');
      })
      .catch(() => {
        if (!isMounted) {
          return;
        }

        setSpecialists([]);
        setSpecialistsState('error');
      });

    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    let isMounted = true;

    getProducts()
      .then((items) => {
        if (!isMounted) {
          return;
        }

        setProducts(items);
        setProductsState(items.length > 0 ? 'success' : 'fallback');
      })
      .catch(() => {
        if (!isMounted) {
          return;
        }

        setProducts([]);
        setProductsState('fallback');
      });

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div className="home-page">
      <section className="home-hero home-container">
        <div className="home-hero__content">
          <p className="home-eyebrow">Эстетическая медицина Beatris</p>
          <h1>Осознанный уход, процедуры и врачебное сопровождение</h1>
          <p className="home-hero__lead">
            Сайт помогает пациенту выбрать услугу, специалиста и удобное время приёма, а также перейти к
            профессиональной поддержке после процедур.
          </p>
          <div className="home-hero__actions">
            <Button>Записаться на приём</Button>
            <Link className="home-button-link" to="/services">
              Посмотреть услуги
            </Link>
          </div>
          <div className="home-hero__stats">
            {heroStats.map((item) => (
              <div className="home-stat" key={item.value}>
                {item.icon}
                <strong>{item.value}</strong>
                <span>{item.label}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="home-hero__image">
          <img
            alt="Светлая зона ресепшен медицинского центра Beatris"
            src="https://images.unsplash.com/photo-1629909613654-28e377c37b09?auto=format&fit=crop&w=1400&q=85"
          />
        </div>
      </section>

      <section className="home-section home-container">
        <div className="home-section__heading">
          <h2>Направления клиники</h2>
        </div>
        {directionsState === 'loading' && <p className="home-section-state">Загружаем направления...</p>}
        {directionsState === 'error' && (
          <p className="home-section-state">Не удалось загрузить направления. Попробуйте обновить страницу.</p>
        )}
        {directionsState === 'empty' && <p className="home-section-state">Пока нет доступных направлений.</p>}
        {directionsState === 'success' && (
          <div className="direction-grid">
            {directions.map((direction, index) => {
              const image = direction.image ?? direction.imageUrl ?? defaultDirectionImage;
              const description = direction.description ?? defaultDirectionDescription;

              return (
                <article className="direction-card" key={direction.id}>
                  <span className="direction-card__number">{String(index + 1).padStart(2, '0')}</span>
                  <img className="direction-card__image" alt="" src={image} />
                  <div>
                    <h3>{direction.title}</h3>
                    <p>{description}</p>
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </section>

      <section className="home-section home-container">
        <div className="home-section__heading">
          <h2>Специалисты</h2>
        </div>
        {specialistsState === 'loading' && <p className="home-section-state">Загружаем специалистов...</p>}
        {specialistsState === 'error' && (
          <p className="home-section-state">Не удалось загрузить специалистов. Попробуйте обновить страницу.</p>
        )}
        {specialistsState === 'empty' && <p className="home-section-state">Пока нет доступных специалистов.</p>}
        {specialistsState === 'success' && (
          <div className="specialist-grid">
            {specialists.map((specialist) => {
              const image = specialist.photoUrl ?? specialistFallbackImage;
              const meta = specialist.experienceYears
                ? `Стаж ${specialist.experienceYears} лет`
                : specialist.specialization;

              return (
                <article className="specialist-card" key={specialist.id}>
                  <img
                    alt={specialist.fullName}
                    src={image}
                    onError={(event) => {
                      event.currentTarget.src = specialistFallbackImage;
                    }}
                  />
                  <div>
                    <h3>{specialist.fullName}</h3>
                    <p>
                      {specialist.position} <span>•</span> {meta}
                    </p>
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </section>

      <section className="home-container">
        <div className="promo-banner">
          <div>
            <h2>Специальные предложения месяца</h2>
            <p>Акции и программы месяца на уход, услуги, сеансы, особые предложения и новинки процедур для вашей красоты.</p>
          </div>
          <Link className="button button--primary" to="/promotions">
            Смотреть акции
          </Link>
        </div>
      </section>

      <section className="home-split home-container">
        <div>
          <h2>Почему выбирают Beatris</h2>
          <ul className="reason-list">
            {reasons.map((reason) => (
              <li key={reason}>
                <Check size={18} />
                <span>{reason}</span>
              </li>
            ))}
          </ul>
          <div className="trust-grid">
            {trustItems.map((item) => (
              <article key={item.title}>
                {item.icon}
                <strong>{item.title}</strong>
                <span>{item.text}</span>
              </article>
            ))}
          </div>
        </div>
        <div>
          <div className="home-section__heading home-section__heading--inline">
            <h2>Отзывы пациентов</h2>
            <Link to="/about/reviews">Смотреть все отзывы <ArrowRight size={16} /></Link>
          </div>
          <div className="review-grid">
            {reviews.map((review) => (
              <article className="review-card" key={review.name}>
                <span className="review-card__quote">“</span>
                <div className="review-card__author">
                  <strong>{review.name}</strong>
                  <span aria-label={`${review.rating} из 5`}>
                    {Array.from({ length: review.rating }).map((_, index) => (
                      <Star key={index} size={15} fill="currentColor" />
                    ))}
                  </span>
                </div>
                <p>{review.text}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="home-section home-container">
        <div className="home-section__heading home-section__heading--compact">
          <h2>Интернет-магазин косметики</h2>
          <Link className="home-section-more-link" to="/shop">
            В магазин <ArrowRight size={12} />
          </Link>
        </div>
        {productsState === 'loading' && <p className="home-section-state">Загружаем товары...</p>}
        {productsState !== 'loading' && (
          <div className="product-grid">
            {(productsState === 'success'
              ? products.map((product) => ({
                  id: product.id,
                  title: product.title,
                  price: formatPrice(product.price),
                  imageUrl: product.imageUrl ?? productFallbackImage,
                  link: `/shop/${product.slug}`,
                }))
              : fallbackProducts
            ).map((product) => (
              <article className="product-card" key={product.id}>
                <button aria-label="Добавить в избранное" className="product-card__favorite" type="button">
                  <Heart size={18} />
                </button>
                <Link className="product-card__link" to={product.link}>
                  <img
                    alt={product.title}
                    src={product.imageUrl}
                    onError={(event) => {
                      event.currentTarget.src = productFallbackImage;
                    }}
                  />
                  <div>
                    <h3>{product.title}</h3>
                    <strong>{product.price}</strong>
                  </div>
                </Link>
              </article>
            ))}
          </div>
        )}
      </section>

      <section className="recommendations home-container">
        <div className="recommendations__intro">
          <h2>Рекомендации после процедур</h2>
          <p>
            Полезные советы и список профессиональной косметики для восстановления, сохранения и поддержания результата
            после процедур.
          </p>
          <Link className="home-button-link" to="/account/recommendations">
            Подробнее о рекомендациях
          </Link>
        </div>
        <div className="recommendations__grid">
          {recommendationCards.map((card) => (
            <article key={card.text}>
              {card.icon}
              <span>{card.text}</span>
            </article>
          ))}
        </div>
      </section>

      <section className="consultation home-container">
        <img
          alt="Специалист Beatris готовит консультацию"
          src={specialistFallbackImage}
        />
        <div>
          <h2>Записаться на консультацию</h2>
          <p>
            Поможем сориентироваться и подобрать процедуры по вашим потребностям и особенностям: комфортно, чутко,
            безопасно.
          </p>
        </div>
        <Button>Открыть запись</Button>
      </section>
    </div>
  );
}
