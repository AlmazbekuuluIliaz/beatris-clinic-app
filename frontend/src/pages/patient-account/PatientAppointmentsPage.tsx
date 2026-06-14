import {
  CalendarDays,
  CheckCircle2,
  ChevronDown,
  Clock,
  ClipboardList,
  LogOut,
  MapPin,
  MoreVertical,
  RotateCcw,
  ShoppingBag,
  ShoppingCart,
  UserRound,
  XCircle,
  Heart,
} from 'lucide-react';
import { NavLink } from 'react-router-dom';

import { Button } from '@/shared/ui/Button';

import './PatientAppointmentsPage.css';

const sidebar = [
  ['Профиль', '/account', <UserRound />],
  ['Мои записи', '/account/appointments', <CalendarDays />],
  ['Рекомендации врача', '/account/recommendations', <ClipboardList />],
  ['Мои заказы', '/account/orders', <ShoppingBag />],
  ['Избранное', '/account/wishlist', <Heart />],
  ['Корзина', '/account/cart', <ShoppingCart />],
];

const appointments = [
  {
    title: 'Контурная пластика губ',
    doctor: 'Смирнова Екатерина Владимировна',
    date: '25 мая 2024, суббота',
    time: '11:00',
    place: 'Клиника Beatris на Патриарших',
    address: 'ул. Малая Бронная, 18, Москва',
    status: 'Подтверждена',
    image: 'https://images.unsplash.com/photo-1631217868264-e5b90bb7e133?auto=format&fit=crop&w=420&q=85',
  },
  {
    title: 'Ботулинотерапия (лоб, межбровье)',
    doctor: 'Смирнова Екатерина Владимировна',
    date: '8 июня 2024, суббота',
    time: '14:30',
    place: 'Клиника Beatris на Патриарших',
    address: 'ул. Малая Бронная, 18, Москва',
    status: 'Ожидает подтверждения',
    image: 'https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=420&q=85',
  },
  {
    title: 'Плазмотерапия лица',
    doctor: 'Петрова Ольга Сергеевна',
    date: '22 июня 2024, суббота',
    time: '12:00',
    place: 'Клиника Beatris на Цветном',
    address: 'Цветной б-р, 2, Москва',
    status: 'Подтверждена',
    image: 'https://images.unsplash.com/photo-1629909613654-28e377c37b09?auto=format&fit=crop&w=420&q=85',
  },
];

export function PatientAppointmentsPage() {
  return (
    <main className="appointments-page">
      <div className="appointments-container">
        <div className="appointments-breadcrumb">Главная › Личный кабинет › Мои записи</div>
        <h1>Мои записи</h1>

        <div className="appointments-layout">
          <aside className="appointments-sidebar">
            {sidebar.map(([label, to, icon]) => (
              <NavLink to={String(to)} end={to === '/account'} key={String(label)}>
                {icon}
                <span>{label}</span>
                {label === 'Корзина' && <b>2</b>}
              </NavLink>
            ))}
            <button className="appointments-logout" type="button"><LogOut /> Выйти</button>
          </aside>

          <section className="appointments-content">
            <div className="appointment-tabs-row">
              {['Предстоящие', 'Прошедшие', 'Отменённые'].map((tab, index) => (
                <button className={index === 0 ? 'is-active' : ''} type="button" key={tab}>{tab}</button>
              ))}
            </div>

            <div className="appointment-main-grid">
              <div>
                <div className="appointment-filters">
                  <Filter label="Клиника" value="Все клиники" />
                  <Filter label="Специалист" value="Все специалисты" />
                  <Filter label="Дата" value="Выберите дату" icon={<CalendarDays size={18} />} />
                  <button type="button"><RotateCcw size={18} /> Сбросить</button>
                </div>

                <div className="appointment-list">
                  {appointments.map((appointment) => (
                    <article className="appointment-item-card" key={appointment.title}>
                      <img alt={appointment.title} src={appointment.image} />
                      <div className="appointment-item-body">
                        <div className="appointment-item-head">
                          <h2>{appointment.title}</h2>
                          <span className={appointment.status.includes('Ожидает') ? 'is-pending' : ''}>{appointment.status}</span>
                        </div>
                        <p>Врач: {appointment.doctor}</p>
                        <div className="appointment-meta">
                          <small><CalendarDays size={16} /> {appointment.date}</small>
                          <small><Clock size={16} /> {appointment.time}</small>
                          <small><MapPin size={16} /> {appointment.place}<br />{appointment.address}</small>
                        </div>
                        <div className="appointment-actions">
                          <Button>Подробнее</Button>
                          <button type="button">Перенести</button>
                          <button type="button">Отменить</button>
                        </div>
                      </div>
                      <button className="appointment-more" type="button" aria-label="Дополнительно"><MoreVertical size={20} /></button>
                    </article>
                  ))}
                </div>
              </div>

              <aside className="appointments-stat-card">
                <h2>Статистика записей</h2>
                <div><CalendarDays /> <span>Предстоящие</span> <strong>3</strong></div>
                <div><CheckCircle2 /> <span>Прошедшие</span> <strong>12</strong></div>
                <div><XCircle /> <span>Отменённые</span> <strong>2</strong></div>
                <Button>Записаться на приём</Button>
                <p>Вы можете записаться на приём к любому специалисту клиники в удобное для вас время.</p>
              </aside>
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}

function Filter({ label, value, icon }: { label: string; value: string; icon?: React.ReactNode }) {
  return (
    <button className="appointment-filter" type="button">
      <span>{label}</span>
      <strong>{value}</strong>
      {icon ?? <ChevronDown size={18} />}
    </button>
  );
}
