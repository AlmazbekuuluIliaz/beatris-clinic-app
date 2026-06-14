import {
  Car,
  ChevronDown,
  Clock,
  Instagram,
  Mail,
  MapPin,
  MessageCircle,
  Navigation,
  Phone,
  Send,
  UserRound,
} from 'lucide-react';

import { Button } from '@/shared/ui/Button';

import './ContactsPage.css';

const clinicImage =
  'https://images.unsplash.com/photo-1629909613654-28e377c37b09?auto=format&fit=crop&w=1400&q=85';

const contactCards = [
  { icon: <Phone />, title: 'Телефон', value: '+7 (495) 150-50-15', text: 'Звонки и консультации' },
  { icon: <MessageCircle />, title: 'WhatsApp / Telegram', value: '@beatris_clinic', text: 'Напишите нам в мессенджер' },
  { icon: <MapPin />, title: 'Адрес', value: 'Москва, ул. Поварская, 31/29', text: 'Схема проезда ниже' },
  { icon: <Clock />, title: 'Время работы', value: 'Пн–Вс, 10:00–21:00', text: 'Без выходных' },
  { icon: <Mail />, title: 'E-mail', value: 'info@beatris-clinic.ru', text: 'Ответим в течение часа' },
];

const routeCards = [
  {
    icon: <span className="metro-icon">M</span>,
    title: 'Метро',
    text: 'Ближайшие станции: «Арбатская» и «Покровская линия», выход 7 — 6 минут пешком.',
  },
  {
    icon: <Car />,
    title: 'Парковка',
    text: 'Для гостей клиники доступна городская парковка на ул. Поварская и в соседних переулках.',
  },
  {
    icon: <Navigation />,
    title: 'Навигация',
    text: 'Введите в навигатор «ул. Поварская, 31/29» — мы находимся в тихом дворе за особняком.',
  },
  {
    icon: <UserRound />,
    title: 'Для пациентов',
    text: 'Рекомендуем приезжать за 10 минут до приёма, чтобы комфортно оформить документы.',
  },
];

const messengers = [
  ['WhatsApp', <MessageCircle />],
  ['Telegram', <Send />],
  ['Viber', <MessageCircle />],
  ['VK', <MessageCircle />],
  ['Instagram', <Instagram />],
];

const faq = [
  'Где находится клиника Beatris?',
  'Есть ли парковка рядом с клиникой?',
  'Как записаться на консультацию онлайн?',
  'Можно ли перенести или отменить запись?',
];

export function ContactsPage() {
  return (
    <main className="contacts-page">
      <div className="contacts-container">
        <section className="contacts-hero">
          <div>
            <p className="contacts-breadcrumb">Главная / Контакты</p>
            <h1>Контакты Beatris</h1>
            <p>
              Мы всегда на связи и рады помочь вам. Свяжитесь с нами любым удобным способом, запишитесь на консультацию
              или получите помощь в навигации до клиники.
            </p>
          </div>
          <div className="contacts-hero__image">
            <img alt="Ресепшен клиники Beatris" src={clinicImage} />
            <div>
              <Phone size={28} />
              <span>Позвоните нам или напишите в мессенджер</span>
              <ChevronDown size={17} />
            </div>
          </div>
        </section>

        <section className="contact-card-grid">
          {contactCards.map((card) => (
            <article key={card.title}>
              {card.icon}
              <div>
                <span>{card.title}</span>
                <strong>{card.value}</strong>
                <small>{card.text}</small>
              </div>
            </article>
          ))}
        </section>

        <section className="contacts-map">
          <div>
            <h2>Как нас найти</h2>
            <p>Клиника Beatris находится в центре Москвы, в шаговой доступности от метро и основных парковочных зон.</p>
            <button type="button">Построить маршрут</button>
          </div>
          <div className="contacts-map__canvas">
            <span className="map-chip map-chip--main">BEATRIS<br />ул. Поварская, 31/29</span>
            <span className="map-pin"><MapPin size={34} fill="currentColor" /></span>
            <span className="map-chip map-chip--one">Консерватория<br />им. П.И. Чайковского</span>
            <span className="map-chip map-chip--two">Музей<br />А.С. Пушкина</span>
            <span className="map-chip map-chip--three">Большой театр</span>
            <span className="map-metro map-metro--one">M<br /><small>Арбатская</small></span>
            <span className="map-metro map-metro--two">M<br /><small>Александровский сад</small></span>
          </div>
        </section>

        <section className="contacts-section">
          <h2>Как добраться</h2>
          <div className="route-grid">
            {routeCards.map((card) => (
              <article key={card.title}>
                {card.icon}
                <div>
                  <h3>{card.title}</h3>
                  <p>{card.text}</p>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="contact-main-grid">
          <article className="contact-form-card">
            <h2>Связаться с нами</h2>
            <p>Оставьте сообщение — мы свяжемся с вами в ближайшее время.</p>
            <form>
              <input aria-label="Имя" placeholder="Имя*" />
              <input aria-label="Телефон" placeholder="Телефон*" />
              <textarea aria-label="Комментарий" placeholder="Комментарий" />
              <Button type="button">Отправить</Button>
            </form>
            <small>Нажимая кнопку «Отправить», вы соглашаетесь с политикой обработки персональных данных.</small>
          </article>

          <article className="online-booking-card">
            <img alt="Кабинет Beatris" src="https://images.unsplash.com/photo-1631217868264-e5b90bb7e133?auto=format&fit=crop&w=620&q=85" />
            <div>
              <h2>Запишитесь онлайн в удобное время</h2>
              <p>Выберите специалиста, услугу и подходящее время в нашем онлайн-расписании.</p>
              <Button>Записаться на консультацию</Button>
              <small><Clock size={18} /> Подтверждение записи придёт вам на телефон или в мессенджер.</small>
            </div>
          </article>
        </section>

        <section className="contact-bottom-grid">
          <article className="messenger-card">
            <h2>Мы на связи в мессенджерах</h2>
            <p>Напишите нам в удобном для вас мессенджере — ответим быстро и поможем.</p>
            <div>
              {messengers.map(([name, icon]) => (
                <button type="button" key={String(name)}>
                  {icon}
                  {name}
                </button>
              ))}
            </div>
          </article>

          <article className="contact-faq-card">
            <h2>Часто задаваемые вопросы</h2>
            <div>
              {faq.map((item) => (
                <button type="button" key={item}>
                  {item}
                  <ChevronDown size={17} />
                </button>
              ))}
            </div>
          </article>
        </section>
      </div>
    </main>
  );
}
