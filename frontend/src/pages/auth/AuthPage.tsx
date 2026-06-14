import { useState } from 'react';
import { Bell, CalendarDays, Eye, Heart, LockKeyhole, Mail, Package, ShieldCheck, Star, UserRound } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';

import { Button } from '@/shared/ui/Button';

import './AuthPage.css';

const accountFeatures = [
  { icon: <CalendarDays />, title: 'История записей', text: 'Все ваши приёмы и процедуры в одном месте' },
  { icon: <UserRound />, title: 'Рекомендации врача', text: 'Персональные рекомендации и план процедур' },
  { icon: <Heart />, title: 'Избранное', text: 'Сохраняйте любимые услуги и товары' },
  { icon: <Package />, title: 'Заказы', text: 'Отслеживайте заказы из интернет-магазина' },
];

const trust = [
  { icon: <ShieldCheck />, title: 'Ваши данные под защитой' },
  { icon: <Bell />, title: 'Напоминания о записях и акциях' },
  { icon: <Star />, title: 'Индивидуальный подход' },
  { icon: <CalendarDays />, title: 'Экономия времени при записи' },
];

export function AuthPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [mode, setMode] = useState(location.pathname.includes('register') ? 'register' : 'login');
  const [success, setSuccess] = useState('');

  const submit = () => {
    if (mode === 'register') {
      setSuccess('Регистрация прошла успешно. Теперь войдите в аккаунт');
      setMode('login');
      window.setTimeout(() => setSuccess(''), 3000);
      return;
    }

    setSuccess('Вход выполнен успешно');
    window.setTimeout(() => navigate('/account'), 700);
  };

  return (
    <main className="auth-page">
      <section className="auth-hero">
        <div className="auth-container">
          <h1>Вход и регистрация</h1>
          <p>Войдите в личный кабинет или создайте новый аккаунт, чтобы получить доступ ко всем возможностям клиники Beatris</p>

          <div className="auth-card">
            <div className="auth-tabs">
              <button className={mode === 'login' ? 'is-active' : ''} type="button" onClick={() => setMode('login')}>Вход</button>
              <button className={mode === 'register' ? 'is-active' : ''} type="button" onClick={() => setMode('register')}>Регистрация</button>
            </div>

            <div className="auth-card__body">
              <section className="auth-form-panel">
                {mode === 'login' ? <LoginForm onSubmit={submit} /> : <RegisterForm onSubmit={submit} />}
              </section>

              <section className="auth-info-panel">
                <h2>{mode === 'login' ? 'Ещё нет аккаунта?' : 'Уже есть аккаунт?'}</h2>
                <p>
                  {mode === 'login'
                    ? 'Зарегистрируйтесь и получите доступ к возможностям личного кабинета'
                    : 'Войдите, чтобы открыть профиль пациента, записи и рекомендации врача'}
                </p>
                <div className="auth-feature-list">
                  {accountFeatures.map((feature) => (
                    <article key={feature.title}>
                      <span>{feature.icon}</span>
                      <div><h3>{feature.title}</h3><p>{feature.text}</p></div>
                    </article>
                  ))}
                </div>
                <button className="auth-outline-button" type="button" onClick={() => setMode(mode === 'login' ? 'register' : 'login')}>
                  {mode === 'login' ? 'Создать аккаунт' : 'Войти в аккаунт'}
                </button>
              </section>
            </div>
          </div>

          <section className="auth-trust">
            <h2>Личный кабинет — это удобно и безопасно</h2>
            <div>
              {trust.map((item) => (
                <article key={item.title}>{item.icon}<span>{item.title}</span></article>
              ))}
            </div>
          </section>
        </div>
      </section>
      {success && <div className="auth-toast">{success}</div>}
    </main>
  );
}

function LoginForm({ onSubmit }: { onSubmit: () => void }) {
  return (
    <>
      <h2>Вход в личный кабинет</h2>
      <label>E-mail или телефон<Field icon={<Mail />} placeholder="Введите e-mail или телефон" /></label>
      <label>Пароль<Field icon={<LockKeyhole />} placeholder="Введите пароль" type="password" action={<Eye size={18} />} /></label>
      <div className="auth-row">
        <label><input type="checkbox" defaultChecked /> Запомнить меня</label>
        <button type="button">Забыли пароль?</button>
      </div>
      <Button type="button" onClick={onSubmit}>Войти</Button>
      <div className="auth-divider"><span />или<span /></div>
      <button className="google-button" type="button"><b>G</b> Войти через Google</button>
    </>
  );
}

function RegisterForm({ onSubmit }: { onSubmit: () => void }) {
  return (
    <>
      <h2>Создание аккаунта</h2>
      <label>ФИО<Field icon={<UserRound />} placeholder="Введите ваше имя" /></label>
      <label>Телефон<Field icon={<Mail />} placeholder="+7 (___) ___-__-__" /></label>
      <label>E-mail<Field icon={<Mail />} placeholder="Введите e-mail" /></label>
      <label>Пароль<Field icon={<LockKeyhole />} placeholder="Придумайте пароль" type="password" action={<Eye size={18} />} /></label>
      <div className="auth-row auth-row--single">
        <label><input type="checkbox" defaultChecked /> Согласен на обработку персональных данных</label>
      </div>
      <Button type="button" onClick={onSubmit}>Зарегистрироваться</Button>
    </>
  );
}

function Field({ icon, action, ...props }: React.InputHTMLAttributes<HTMLInputElement> & { icon: React.ReactNode; action?: React.ReactNode }) {
  return (
    <div className="auth-field">
      {icon}
      <input {...props} />
      {action && <button type="button">{action}</button>}
    </div>
  );
}
