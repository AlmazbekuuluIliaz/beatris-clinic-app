import {
  ArrowRight,
  BadgePercent,
  CalendarDays,
  ChevronDown,
  Gift,
  HeartHandshake,
  Leaf,
  Package,
  ShieldPlus,
  Sparkles,
  Star,
  UserRoundCheck,
} from 'lucide-react';

import { Button } from '@/shared/ui/Button';

import './PromotionsPage.css';

const promoHeroImage =
  'https://images.unsplash.com/photo-1629909613654-28e377c37b09?auto=format&fit=crop&w=1400&q=85';

const promoCards = [
  {
    label: 'до 31 мая',
    title: '-15% на курс биоревитализации',
    text: 'Глубокое увлажнение и сияние кожи. Курс из 3 процедур со скидкой 15%.',
    image: 'https://images.unsplash.com/photo-1606811971618-4486d14f3f99?auto=format&fit=crop&w=720&q=85',
  },
  {
    label: 'хит',
    title: 'SMAS-лифтинг + консультация врача',
    text: 'Ультразвуковой лифтинг на аппарате Ultraformer MPT и консультация врача — в подарок.',
    image: 'https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?auto=format&fit=crop&w=720&q=85',
  },
  {
    label: 'в день рождения',
    title: 'Скидка в день рождения 10%',
    text: 'Дарим скидку 10% на любые процедуры в ваш день рождения и 7 дней после.',
    image: 'https://images.unsplash.com/photo-1513201099705-a9746e1e201f?auto=format&fit=crop&w=720&q=85',
  },
  {
    label: 'новинка',
    title: 'Комплексное лечение акне',
    text: 'Индивидуальная программа для чистой и здоровой кожи. Первичная консультация со скидкой 20%.',
    image: 'https://images.unsplash.com/photo-1616391182219-e080b4d1043a?auto=format&fit=crop&w=720&q=85',
  },
  {
    label: 'подарок',
    title: 'Подарок при покупке профессиональной косметики',
    text: 'Мини-набор для домашнего ухода в подарок при покупке от 15 000 ₸.',
    image: 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=720&q=85',
  },
  {
    label: 'ограничено',
    title: 'Лазерная эпиляция: курс из 6 процедур',
    text: 'Гладкая кожа надолго. Курс из 6 зон со скидкой 20%.',
    image: 'https://images.unsplash.com/photo-1616391182219-e080b4d1043a?auto=format&fit=crop&w=720&q=85',
  },
];

const reasons = [
  {
    icon: <UserRoundCheck />,
    title: 'Экспертный подбор',
    text: 'Индивидуальные программы от врачей-косметологов с медицинским образованием.',
  },
  {
    icon: <BadgePercent />,
    title: 'Выгодные курсы',
    text: 'Курсовые предложения помогают достичь максимального результата и сэкономить.',
  },
  {
    icon: <ShieldPlus />,
    title: 'Медицинский подход',
    text: 'Безопасность и эффективность подтверждены опытом и современными протоколами.',
  },
  {
    icon: <Gift />,
    title: 'Бонусы и подарки',
    text: 'Дополнительные бонусы на процедуры и профессиональный домашний уход.',
  },
];

const faq = [
  'Можно ли совместить акцию с другими предложениями?',
  'Можно ли оформить подарок для близкого человека?',
  'Как узнать, какие акции действуют сейчас?',
  'Можно ли вернуть деньги, если я передумал воспользоваться акцией?',
  'Распространяются ли акции на онлайн-запись?',
];

export function PromotionsPage() {
  return (
    <main className="promotions-page">
      <div className="promotions-container">
        <section className="promotions-hero">
          <div className="promotions-hero__content">
            <p className="promotions-breadcrumb">Главная / Акции</p>
            <h1>Акции и специальные предложения</h1>
            <p>
              Выгодные условия на процедуры, курсы и косметику для вашей красоты и уверенности каждый день.
            </p>
            <div className="promotions-hero__actions">
              <Button>Записаться на приём</Button>
              <button type="button">Подобрать предложение</button>
            </div>
            <div className="promo-category-row">
              <Category icon={<Leaf />} title="Сезонные предложения" />
              <Category icon={<Star />} title="Курсы процедур" />
              <Category icon={<Gift />} title="Подарочные сертификаты" />
              <Category icon={<Package />} title="Акции на косметику" />
            </div>
          </div>
          <div className="promotions-hero__image">
            <img alt="Ресепшен клиники Beatris" src={promoHeroImage} />
            <div>
              <span>Забота о вашей красоте с выгодой</span>
              <Gift size={28} />
            </div>
          </div>
        </section>

        <section className="promo-grid">
          {promoCards.map((card) => (
            <article className="promo-card" key={card.title}>
              <div className="promo-card__image">
                <img alt={card.title} src={card.image} />
                <span>{card.label}</span>
              </div>
              <div className="promo-card__body">
                <h2>{card.title}</h2>
                <p>{card.text}</p>
                <button type="button">Подробнее</button>
              </div>
            </article>
          ))}
        </section>

        <section className="promo-feature">
          <img
            alt="Месяц обновления кожи"
            src="https://images.unsplash.com/photo-1616391182219-e080b4d1043a?auto=format&fit=crop&w=700&q=85"
          />
          <div>
            <span>Специальное предложение</span>
            <h2>Месяц обновления кожи</h2>
            <p>Комплексная программа для сияния и молодости кожи</p>
            <div className="promo-feature__benefits">
              <small><Sparkles size={18} /> Глубокое увлажнение и восстановление</small>
              <small><BadgePercent size={18} /> Выравнивание тона и текстуры</small>
              <small><HeartHandshake size={18} /> Здоровое сияние и свежий вид</small>
            </div>
          </div>
          <aside>
            <strong>Скидка до 20%</strong>
            <button type="button">Подробнее</button>
          </aside>
        </section>

        <section className="promo-section">
          <h2>Почему это выгодно</h2>
          <div className="promo-reasons">
            {reasons.map((reason) => (
              <article key={reason.title}>
                {reason.icon}
                <div>
                  <h3>{reason.title}</h3>
                  <p>{reason.text}</p>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="promo-extra-grid">
          <article className="promo-terms">
            <h2>Условия участия</h2>
            <ul>
              <li><strong>Как воспользоваться:</strong> сообщите администратору о выбранной акции при записи.</li>
              <li><strong>Совмещение акций:</strong> большинство предложений не суммируются между собой.</li>
              <li><strong>Сроки действия:</strong> каждая акция имеет ограниченный срок.</li>
              <li><strong>Предварительная запись:</strong> количество мест и предложений ограничено.</li>
            </ul>
          </article>
          <article className="promo-mini-card">
            <h2>Подарочный сертификат Beatris</h2>
            <p>Идеальный подарок для тех, кто ценит заботу о себе.</p>
            <button type="button">Подробнее</button>
          </article>
          <article className="promo-mini-card promo-mini-card--people">
            <h2>Приведи подругу — получи бонус</h2>
            <p>Скидка 10% для вас и вашей подруги на любые процедуры.</p>
            <button type="button">Подробнее</button>
          </article>
        </section>

        <section className="promo-section">
          <h2>Часто задаваемые вопросы</h2>
          <div className="promo-faq">
            {faq.map((question) => (
              <button type="button" key={question}>
                {question}
                <ChevronDown size={18} />
              </button>
            ))}
          </div>
        </section>

        <section className="promo-cta">
          <div>
            <h2>Выберите выгодное предложение и запишитесь на консультацию</h2>
            <p>Поможем подобрать идеальный уход и процедуры для вашей красоты и уверенности.</p>
            <Button>Записаться на приём</Button>
          </div>
        </section>
      </div>
    </main>
  );
}

function Category({ icon, title }: { icon: React.ReactNode; title: string }) {
  return (
    <article>
      {icon}
      <span>{title}</span>
    </article>
  );
}
