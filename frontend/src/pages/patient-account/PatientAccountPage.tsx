import {
  Bell,
  CalendarDays,
  ChevronRight,
  ClipboardList,
  Heart,
  LogOut,
  Mail,
  MapPin,
  Package,
  Phone,
  ShoppingBag,
  ShoppingCart,
  Star,
  UserRound,
} from 'lucide-react';
import { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';

import { Button } from '@/shared/ui/Button';

import './PatientAccountPage.css';

const nav = [
  ['Профиль', '/account', <UserRound />],
  ['Мои записи', '/account/appointments', <CalendarDays />],
  ['Рекомендации врача', '/account/recommendations', <ClipboardList />],
  ['Мои заказы', '/account/orders', <ShoppingBag />],
  ['Избранное', '/account/wishlist', <Heart />],
  ['Корзина', '/account/cart', <ShoppingCart />],
];

const stats = [
  ['3', 'Мои записи', '1 предстоящая', <CalendarDays />],
  ['4', 'Заказы', '1 в доставке', <ShoppingBag />],
  ['7', 'Избранное', 'товаров', <Heart />],
  ['2', 'Корзина', 'товара', <ShoppingCart />],
  ['2', 'Рекомендации', 'активные', <ClipboardList />],
];

export function PatientAccountPage() {
  const navigate = useNavigate();
  const [logoutMessage, setLogoutMessage] = useState('');

  const logout = () => {
    setLogoutMessage('Вы вышли из аккаунта');
    window.setTimeout(() => navigate('/login'), 700);
  };

  return (
    <main className="account-page">
      <div className="account-container">
        <div className="account-breadcrumb">Главная <ChevronRight size={14} /> Личный кабинет <ChevronRight size={14} /> Профиль</div>
        <h1>Профиль</h1>

        <div className="account-layout">
          <aside className="account-sidebar">
            {nav.map(([label, to, icon]) => (
              <NavLink to={String(to)} end={to === '/account'} key={String(label)}>
                {icon}
                <span>{label}</span>
                {label === 'Корзина' && <b>2</b>}
              </NavLink>
            ))}
            <button type="button" className="account-logout" onClick={logout}><LogOut /> Выйти</button>
          </aside>

          <section className="account-content">
            <section className="profile-hero-card">
              <img alt="Анна Иванова" src="https://images.unsplash.com/photo-1594824476967-48c8b964273f?auto=format&fit=crop&w=320&q=85" />
              <div>
                <h2>Анна Сергеевна Иванова</h2>
                <p>ID пациента: BEA-10245</p>
                <span><Star size={16} fill="currentColor" /> Постоянный клиент</span>
                <div className="profile-contacts">
                  <small><Phone size={16} /> +7 (910) 123-45-67</small>
                  <small><Mail size={16} /> anna.ivanova@mail.ru</small>
                  <small><CalendarDays size={16} /> 12 мая 1988</small>
                  <small><MapPin size={16} /> Москва</small>
                </div>
              </div>
              <div className="bonus-card">
                <span>Ваши бонусы</span>
                <strong>2 450 <Star size={18} fill="currentColor" /></strong>
                <small>бонусных баллов</small>
                <Button>Редактировать профиль</Button>
              </div>
            </section>

            <section className="account-stats">
              {stats.map(([value, title, subtitle, icon]) => (
                <article key={String(title)}>
                  <span>{icon}</span>
                  <strong>{value}</strong>
                  <div>{title}<small>{subtitle}</small></div>
                </article>
              ))}
            </section>

            <section className="account-grid">
              <Card title="Личные данные" action="Изменить">
                <dl>
                  <dt>Имя</dt><dd>Анна</dd>
                  <dt>Фамилия</dt><dd>Иванова</dd>
                  <dt>Отчество</dt><dd>Сергеевна</dd>
                  <dt>Дата рождения</dt><dd>12 мая 1988</dd>
                  <dt>Телефон</dt><dd>+7 (910) 123-45-67</dd>
                  <dt>E-mail</dt><dd>anna.ivanova@mail.ru</dd>
                  <dt>Город</dt><dd>Москва</dd>
                </dl>
              </Card>
              <Card title="Безопасность" action="Изменить пароль">
                <dl>
                  <dt>Пароль</dt><dd>••••••••••</dd>
                  <dt>Последний вход</dt><dd>25 мая 2024, 11:24</dd>
                </dl>
                <button className="outline-wide" type="button">Изменить пароль</button>
              </Card>
              <Card title="Уведомления">
                {['SMS-уведомления', 'E-mail рассылки', 'Напоминания о приёмах', 'Обновления о заказах'].map((item) => (
                  <label className="notify-row" key={item}>
                    <span><Bell size={16} /> {item}<small>Получать уведомления</small></span>
                    <input type="checkbox" defaultChecked />
                  </label>
                ))}
              </Card>
            </section>

            <section className="account-bottom-grid">
              <article className="next-appointment">
                <h2>Ближайшая запись</h2>
                <div>
                  <CalendarDays />
                  <div>
                    <h3>Контурная пластика губ</h3>
                    <p>Врач: Смирнова Е. В.</p>
                    <p>25 мая 2024, суббота • 11:00</p>
                    <p>Клиника Beatris на Патриарших</p>
                    <Button>Подробнее</Button>
                  </div>
                </div>
              </article>
              <article className="last-order">
                <h2>Последний заказ <a>Все заказы →</a></h2>
                <div>
                  <img alt="Сыворотка" src="https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?auto=format&fit=crop&w=220&q=85" />
                  <div>
                    <strong>Заказ №9876 <span>Доставлен</span></strong>
                    <p>Дата заказа: 12 мая 2024</p>
                    <p>Сумма: 8 450 ₸</p>
                  </div>
                </div>
              </article>
              <article className="last-recommendation">
                <h2>Последняя рекомендация врача <a>Все рекомендации →</a></h2>
                <div>
                  <img alt="Врач" src="https://images.unsplash.com/photo-1559839734-2b71ea197ec2?auto=format&fit=crop&w=220&q=85" />
                  <p>Рекомендовано продолжить курс увлажнения и антиоксидантной защиты для поддержания результата.</p>
                </div>
                <div className="recommend-product">
                  <img alt="SkinCeuticals C E Ferulic" src="https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?auto=format&fit=crop&w=220&q=85" />
                  <span><strong>SkinCeuticals C E Ferulic</strong>Сыворотка с антиоксидантным действием</span>
                </div>
              </article>
            </section>
          </section>
        </div>
      </div>
      {logoutMessage && <div className="account-toast">{logoutMessage}</div>}
    </main>
  );
}

function Card({ title, action, children }: { title: string; action?: string; children: React.ReactNode }) {
  return (
    <article className="account-card">
      <header><h2>{title}</h2>{action && <button type="button">{action}</button>}</header>
      {children}
    </article>
  );
}
