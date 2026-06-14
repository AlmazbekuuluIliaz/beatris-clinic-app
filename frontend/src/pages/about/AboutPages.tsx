import {
  ArrowRight,
  Award,
  BadgeCheck,
  CalendarDays,
  Check,
  CircleAlert,
  Clock,
  Heart,
  MapPin,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  Star,
  Target,
  ThumbsUp,
  UserRound,
  UsersRound,
  X,
} from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

import { getSpecialists, type Specialist } from '@/shared/api/specialists';
import { Button } from '@/shared/ui/Button';

import './AboutPages.css';

const clinicImage = 'https://images.unsplash.com/photo-1629909613654-28e377c37b09?auto=format&fit=crop&w=1400&q=85';
const equipmentImage = 'https://images.unsplash.com/photo-1579154341098-e4e158cc7f55?auto=format&fit=crop&w=1400&q=85';
const doctorImages = [
  'https://images.unsplash.com/photo-1559839734-2b71ea197ec2?auto=format&fit=crop&w=620&q=85',
  'https://images.unsplash.com/photo-1594824476967-48c8b964273f?auto=format&fit=crop&w=620&q=85',
  'https://images.unsplash.com/photo-1582750433449-648ed127bb54?auto=format&fit=crop&w=620&q=85',
  'https://images.unsplash.com/photo-1651008376811-b90baee60c1f?auto=format&fit=crop&w=620&q=85',
  'https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?auto=format&fit=crop&w=620&q=85',
  'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=620&q=85',
];
const standardSpecialistImage = doctorImages[0];

function AboutHero({
  eyebrow,
  title,
  text,
  image,
  children,
}: {
  eyebrow: string;
  title: string;
  text: string;
  image: string;
  children?: React.ReactNode;
}) {
  return (
    <section className="about-hero">
      <div>
        <p className="about-breadcrumb">Главная / О нас</p>
        <p className="about-eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        <p className="about-hero__text">{text}</p>
        {children}
      </div>
      <img alt={title} src={image} />
    </section>
  );
}

const Stat = ({ icon, value, label }: { icon: React.ReactNode; value: string; label: string }) => (
  <article className="about-stat">
    {icon}
    <strong>{value}</strong>
    <span>{label}</span>
  </article>
);

export function AboutClinicPage() {
  const [isLicenseOpen, setIsLicenseOpen] = useState(false);

  const spaces = [
    ['Ресепшен', 'Просторная зона встречи и комфортного ожидания', clinicImage],
    ['Кабинет консультации', 'Приватное пространство для диагностики и подбора плана', 'https://images.unsplash.com/photo-1631217868264-e5b90bb7e133?auto=format&fit=crop&w=720&q=85'],
    ['Процедурный кабинет', 'Современное оборудование и максимальная безопасность', 'https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=720&q=85'],
    ['Зона ожидания', 'Уют, тишина и забота о вашем комфорте', 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=720&q=85'],
  ];

  return (
    <main className="about-page">
      <div className="about-container">
        <AboutHero
          eyebrow="О нас"
          title="Клиника Beatris"
          text="Пространство эстетической медицины, где наука, забота и индивидуальный подход объединяются для вашей естественной красоты и уверенности."
          image={clinicImage}
        >
          <Button>Записаться на консультацию</Button>
        </AboutHero>

        <section className="about-intro">
          <div>
            <p className="about-eyebrow">О клинике</p>
            <h2>Медицина, основанная на заботе и доверии</h2>
            <p>
              Beatris — это экспертная клиника эстетической медицины, где каждый пациент получает внимательное отношение,
              точную диагностику и грамотно подобранные решения.
            </p>
            <p>
              Мы сочетаем доказательные методики, современные технологии и искреннюю заботу, чтобы вы выглядели
              естественно и чувствовали себя уверенно каждый день.
            </p>
          </div>
          <div className="about-intro-side">
            <article className="about-intro-card">
              <div>
                <span><ShieldCheck size={20} /></span>
                <h3>Пространство для спокойного медицинского ухода</h3>
              </div>
              <p>
                В клинике продуманы путь пациента, приватность приёма и сопровождение после процедур: от первичной
                консультации до домашнего ухода.
              </p>
              <ul>
                <li><Check size={16} /> Врачебная диагностика перед процедурой</li>
                <li><Check size={16} /> Сертифицированные препараты и аппараты</li>
                <li><Check size={16} /> Рекомендации после каждого визита</li>
              </ul>
            </article>
            <div className="about-stats">
              <Stat icon={<Award />} value="25" label="кабинетов экспертного уровня" />
              <Stat icon={<Sparkles />} value="27" label="лет заботы о пациентах" />
              <Stat icon={<UserRound />} value="40" label="специалиста в команде" />
              <Stat icon={<CalendarDays />} value="24/7" label="онлайн-запись удобно и быстро" />
            </div>
          </div>
        </section>

        <section className="about-section">
          <p className="about-eyebrow">Наши принципы</p>
          <div className="about-card-grid about-card-grid--four">
            {[
              ['Медицинский подход', 'Все процедуры выполняются врачами с соблюдением доказательных протоколов и стандартов.', <Sparkles />],
              ['Безопасность', 'Используем сертифицированные препараты и оборудование, строго соблюдаем протоколы безопасности.', <ShieldCheck />],
              ['Индивидуальный план', 'Подбираем решения с учётом особенностей вашей кожи, здоровья и желаемого результата.', <UserRound />],
              ['Сопровождение', 'Мы рядом на каждом этапе — от консультации до результата и поддержки после процедур.', <Heart />],
            ].map(([title, text, icon]) => (
              <article className="about-info-card" key={String(title)}>
                <span>{icon}</span>
                <h3>{title}</h3>
                <p>{text}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="about-section">
          <p className="about-eyebrow">Пространство клиники</p>
          <div className="about-image-grid">
            {spaces.map(([title, text, image]) => (
              <article key={title}>
                <img alt={title} src={image} />
                <div>
                  <h3>{title}</h3>
                  <p>{text}</p>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="about-docs">
          <div>
            <p className="about-eyebrow">Лицензии и документы</p>
            <h2>Прозрачность и законность</h2>
            <p>Наша клиника работает на основании всех необходимых лицензий и разрешительных документов.</p>
          </div>
          <button
            className="about-doc"
            onClick={() => setIsLicenseOpen(true)}
            type="button"
          >
            <img
              alt="Первая страница медицинской лицензии"
              src="https://drive.google.com/thumbnail?id=1pT51oA2WyYeGFL4EtXMskDeVJ5SEOmU-&sz=w1000"
            />
            <span>Медицинская лицензия</span>
          </button>
        </section>

        {isLicenseOpen && (
          <div
            aria-label="Просмотр медицинской лицензии"
            aria-modal="true"
            className="document-modal"
            onClick={() => setIsLicenseOpen(false)}
            role="dialog"
          >
            <div className="document-modal__content" onClick={(event) => event.stopPropagation()}>
              <div className="document-modal__header">
                <h2>Медицинская лицензия</h2>
                <button
                  aria-label="Закрыть"
                  className="document-modal__close"
                  onClick={() => setIsLicenseOpen(false)}
                  type="button"
                >
                  <X size={22} />
                </button>
              </div>
              <iframe
                src="https://drive.google.com/file/d/1pT51oA2WyYeGFL4EtXMskDeVJ5SEOmU-/preview"
                title="Медицинская лицензия"
              />
            </div>
          </div>
        )}

        <section className="about-map">
          <div>
            <h2>Посетите клинику Beatris</h2>
            <p>Мы находимся в центре города и создали пространство, куда приятно возвращаться.</p>
            <span><MapPin size={18} /> г. Атырау ул. Азаттык, 24а</span>
            <span><Clock size={18} /> Пн-Вс 9.00 - 20.00</span>
          </div>
          <aside>
            <h3>Запишитесь на консультацию</h3>
            <p>Подберём удобное время и ответим на все вопросы.</p>
            <Button>Записаться</Button>
          </aside>
        </section>
      </div>
    </main>
  );
}

export function AboutSpecialistsPage() {
  const [specialists, setSpecialists] = useState<Specialist[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [selectedPosition, setSelectedPosition] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    getSpecialists()
      .then((items) => {
        if (!isMounted) {
          return;
        }

        setSpecialists(items);
        setHasError(false);
      })
      .catch(() => {
        if (!isMounted) {
          return;
        }

        setSpecialists([]);
        setHasError(true);
      })
      .finally(() => {
        if (isMounted) {
          setIsLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const specialistPositions = Array.from(new Set(specialists.map((specialist) => specialist.position).filter(Boolean)));
  const filteredSpecialists = selectedPosition
    ? specialists.filter((specialist) => specialist.position === selectedPosition)
    : specialists;
  return (
    <main className="about-page">
      <div className="about-container">
        <AboutHero
          eyebrow="О нас"
          title="Специалисты Beatris"
          text="Команда врачей и специалистов, которые сочетают медицинскую экспертизу, деликатный подход и современные методики."
          image="https://images.unsplash.com/photo-1631217868264-e5b90bb7e133?auto=format&fit=crop&w=1400&q=85"
        />

        {specialistPositions.length > 0 && (
          <div className="about-filter-row">
            <button
              className={selectedPosition === null ? 'is-active' : ''}
              onClick={() => setSelectedPosition(null)}
              type="button"
            >
              Все специалисты
            </button>
            {specialistPositions.map((position) => (
              <button
                className={selectedPosition === position ? 'is-active' : ''}
                key={position}
                onClick={() => setSelectedPosition(position)}
                type="button"
              >
                {position}
              </button>
            ))}
          </div>
        )}
        {isLoading && <p className="about-section-state">Загружаем специалистов...</p>}
        {hasError && <p className="about-section-state">Не удалось загрузить специалистов. Попробуйте обновить страницу.</p>}
        {!isLoading && !hasError && specialists.length === 0 && (
          <p className="about-section-state">Пока нет доступных специалистов.</p>
        )}
        {!isLoading && !hasError && filteredSpecialists.length > 0 && (
          <section className="specialists-list">
            {filteredSpecialists.map((specialist) => (
              <article className="specialist-profile-card" key={specialist.id}>
                <img alt={specialist.fullName} src={standardSpecialistImage} />
                <div>
                  <h2>{specialist.fullName}</h2>
                  <p>{specialist.position}</p>
                  <span>Стаж {specialist.experienceYears} лет</span>
                  {specialist.specialization && (
                    <div className="about-tags">
                      <small>{specialist.specialization}</small>
                    </div>
                  )}
                  <div className="specialist-profile-card__actions">
                    <Button>Записаться</Button>
                  </div>
                </div>
              </article>
            ))}
          </section>
        )}

        <section className="about-section">
          <div className="about-section-head">
            <h2>Как выбрать специалиста</h2>
          </div>
          <div className="about-card-grid about-card-grid--three">
            {[
              ['По услуге', 'Выберите необходимую процедуру или направление, и мы покажем подходящих специалистов.', <Sparkles />],
              ['По проблеме', 'Опишите вашу задачу, и мы подберём врача с релевантным опытом.', <CircleAlert />],
              ['С помощью администратора', 'Наши администраторы помогут подобрать специалиста и ответят на вопросы.', <UsersRound />],
            ].map(([title, text, icon]) => (
              <article className="about-info-card" key={String(title)}>
                <span>{icon}</span>
                <h3>{title}</h3>
                <p>{text}</p>
              </article>
            ))}
          </div>
        </section>

        <AboutCta title="Выберите своего специалиста и запишитесь на приём" />
      </div>
    </main>
  );
}

export function AboutEquipmentPage() {
  const equipment = [
    ['Fotona StarWalker® MaQX', 'Многофункциональный лазер для омоложения кожи, шлифовки, сосудистых и пигментных проблем.', ['Лазерное омоложение', 'Удаление сосудов']],
    ['Ulthera System®', 'Ультразвуковой лифтинг-аппарат для воздействия на глубокие слои SMAS.', ['SMAS-лифтинг', 'Лифтинг шеи']],
    ['Morpheus8™', 'Фракционный RF-лифтинг с микроиглами для подтяжки, улучшения текстуры кожи и пор.', ['RF-лифтинг лица', 'Лечение рубцов']],
    ['HydraFacial® MD Elite', 'Глубокое очищение, увлажнение и антиоксидантная защита кожи.', ['HydraFacial', 'Чистка лица']],
    ['VISIA® Complexion Analysis', 'Мультиспектральная диагностика кожи для точной оценки состояния.', ['Диагностика кожи', 'План омоложения']],
    ['Accent Prime™', 'RF-лифтинг и контуринг тела для моделирования и улучшения качества кожи.', ['Контуринг тела', 'Коррекция целлюлита']],
  ];

  return (
    <main className="about-page">
      <div className="about-container">
        <AboutHero
          eyebrow="Технологии красоты"
          title="Оборудование Beatris"
          text="Мы используем только сертифицированные аппараты последнего поколения, клинически подтверждённые методики и точные протоколы."
          image={equipmentImage}
        />

        <section className="about-feature-strip">
          {[
            ['Сертифицированное оборудование', 'Аппараты с регистрационными удостоверениями и гарантиями.', <BadgeCheck />],
            ['Экспертная настройка', 'Индивидуальные протоколы для максимальной эффективности.', <SlidersHorizontal />],
            ['Безопасные протоколы', 'Строгие стандарты стерильности и контроль качества.', <ShieldCheck />],
            ['Комплексный подход', 'Оборудование работает в связке для лучшего результата.', <Sparkles />],
          ].map(([title, text, icon]) => (
            <article key={String(title)}>
              {icon}
              <strong>{title}</strong>
              <span>{text}</span>
            </article>
          ))}
        </section>

        <section className="about-section">
          <div className="about-section-head">
            <h2>Наше оборудование</h2>
            <p>Подбираем технологии под ваши задачи и особенности кожи. Каждый аппарат прошёл тщательный отбор.</p>
          </div>
          <div className="equipment-grid">
            {equipment.map(([title, text, tags], index) => (
              <article className="equipment-card" key={String(title)}>
                <img alt={String(title)} src={`${equipmentImage}&sig=${index}`} />
                <div>
                  <h3>{title}</h3>
                  <p>{text}</p>
                  <div className="about-tags">{(tags as string[]).map((tag) => <small key={tag}>{tag}</small>)}</div>
                  <Link to="/services">Связанные услуги <ArrowRight size={16} /></Link>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="about-section">
          <h2>Почему оборудование имеет значение</h2>
          <div className="about-card-grid about-card-grid--four">
            {[
              ['Безопасность', 'Сертифицированные аппараты и строгие протоколы безопасности.', <ShieldCheck />],
              ['Точность', 'Технологии позволяют работать деликатно и эффективно.', <Target />],
              ['Предсказуемый результат', 'Современные аппараты обеспечивают стабильный результат.', <Award />],
              ['Комфорт пациента', 'Быстрые и максимально комфортные процедуры.', <Heart />],
            ].map(([title, text, icon]) => (
              <article className="about-info-card about-info-card--compact" key={String(title)}>
                <span>{icon}</span>
                <h3>{title}</h3>
                <p>{text}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="equipment-flow">
          <h2>Оборудование и услуги — в связке</h2>
          <p>Комплексный подход и современные технологии позволяют получать выраженный результат и сохранять его дольше.</p>
          <div>
            <article><strong>Morpheus8™</strong><span>RF-лифтинг микроигольчатый</span></article>
            <ArrowRight />
            <ul><li>Дряблость кожи</li><li>Рубцы и постакне</li><li>Расширенные поры</li></ul>
            <ArrowRight />
            <ul><li>RF-лифтинг лица</li><li>Лечение рубцов</li><li>Омоложение декольте</li></ul>
          </div>
        </section>

        <AboutCta title="Подберём технологии под ваши цели" />
      </div>
    </main>
  );
}

const reviewData = [
  ['Анна С.', 'Контурная пластика', 'Делала контурную пластику в Beatris. Результат превзошёл ожидания — всё естественно и деликатно.', 12],
  ['Екатерина Л.', 'SMAS-лифтинг Ulthera', 'Процедура прошла комфортно, эффект заметила уже через пару недель. Очень довольна.', 8],
  ['Мария К.', 'Мезотерапия кожи головы', 'После курса выпадение волос значительно уменьшилось. Волосы стали гуще и сильнее.', 5],
  ['Ольга П.', 'Чистка лица', 'Деликатная чистка и уход — кожа как после отпуска. Очень приятная атмосфера.', 3],
  ['Наталья В.', 'Ботулинотерапия', 'Делала ботокс впервые, очень волновалась. Врач подробно объяснила, процедура прошла быстро.', 7],
  ['Дарья М.', 'RF-лифтинг', 'Отличная процедура для уплотнения кожи. После курса кожа стала более подтянутой.', 4],
  ['Ирина Т.', 'Пилинг PRX-T33', 'Кожа стала ровнее и светлее уже после первой процедуры.', 6],
  ['Светлана Г.', 'Лазерная эпиляция', 'Прошла уже 4 процедуры — результат превосходный.', 9],
  ['Татьяна Л.', 'Консультация косметолога', 'Получила подробную консультацию и индивидуальный план ухода.', 2],
];

export function AboutReviewsPage() {
  return (
    <main className="about-page">
      <div className="about-container">
        <section className="reviews-hero">
          <div>
            <p className="about-breadcrumb">Главная / О нас / Отзывы</p>
            <h1>Отзывы пациентов Beatris</h1>
            <p>Доверие и результат — лучшее подтверждение качества нашей работы. Мы благодарны каждому пациенту за обратную связь.</p>
          </div>
          <img alt="Ресепшен Beatris" src={clinicImage} />
          <article>
            <strong>4.9 <span>/5</span></strong>
            <div>{Array.from({ length: 5 }).map((_, index) => <Star key={index} size={18} fill="currentColor" />)}</div>
            <small>Средняя оценка на основе 582 отзывов</small>
          </article>
        </section>

        <div className="about-filter-row">
          {['Все отзывы', 'Косметология', 'Трихология', 'Аппаратные процедуры', 'Интернет-магазин'].map((item, index) => (
            <button className={index === 0 ? 'is-active' : ''} key={item} type="button">
              {item}
            </button>
          ))}
        </div>

        <section className="about-section">
          <div className="about-section-head">
            <h2>Отзывы наших пациентов</h2>
            <p>Сортировать: Новые сначала</p>
          </div>
          <div className="reviews-grid">
            {reviewData.map(([name, service, text, likes]) => (
              <article className="review-full-card" key={String(name)}>
                <div className="review-full-card__head">
                  <span>{String(name).slice(0, 1)}</span>
                  <div><strong>{name}</strong><Stars /></div>
                </div>
                <h3>{service}</h3>
                <p>{text}</p>
                <footer><small>май 2024</small><span><ThumbsUp size={15} /> {likes}</span></footer>
              </article>
            ))}
          </div>
        </section>

        <section className="review-quotes">
          <article><img alt="Алина" src={doctorImages[0]} /><p>Beatris — это место, где чувствуешь себя в надёжных руках. Спасибо за вашу работу.</p><strong>Алина С.</strong></article>
          <article><img alt="Юлия" src={doctorImages[3]} /><p>Мой путь к уверенности начался с консультации в Beatris. Результат превзошёл ожидания.</p><strong>Юлия Р.</strong></article>
        </section>

        <section className="about-section">
          <h2>Нас рекомендуют и нам доверяют</h2>
          <div className="about-card-grid about-card-grid--four">
            <Stat icon={<Star />} value="4.9/5" label="Средняя оценка на основе отзывов" />
            <Stat icon={<UsersRound />} value="78%" label="Пациентов приходят по рекомендации" />
            <Stat icon={<Heart />} value="92%" label="Пациентов возвращаются на процедуры" />
            <Stat icon={<CalendarDays />} value="Онлайн" label="Удобная запись на сайте" />
          </div>
        </section>

        <AboutCta title="Готовы к преображению?" />
      </div>
    </main>
  );
}

function Stars() {
  return <span className="stars">{Array.from({ length: 5 }).map((_, index) => <Star key={index} size={13} fill="currentColor" />)}</span>;
}

function AboutCta({ title }: { title: string }) {
  return (
    <section className="about-cta">
      <div>
        <h2>{title}</h2>
        <p>Запишитесь на консультацию к специалисту Beatris и получите индивидуальный план процедур.</p>
      </div>
      <Button>Записаться</Button>
    </section>
  );
}
