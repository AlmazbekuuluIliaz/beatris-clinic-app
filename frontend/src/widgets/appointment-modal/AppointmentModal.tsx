import { useEffect, useMemo, useState } from 'react';
import {
  CalendarDays,
  Check,
  CheckCircle2,
  Clock3,
  ShieldCheck,
  Sparkles,
  Tag,
  UserRound,
  X,
} from 'lucide-react';

import './AppointmentModal.css';

const categories = ['Инъекционная косметология', 'Аппаратная косметология', 'Уходовые процедуры', 'Пластическая хирургия', 'Другое'];

const servicesByCategory: Record<string, string[]> = {
  'Инъекционная косметология': ['Ботулинотерапия (Botox)', 'Биоревитализация', 'Мезотерапия'],
  'Аппаратная косметология': ['SMAS-лифтинг', 'Лазерная эпиляция', 'RF-лифтинг'],
  'Уходовые процедуры': ['Чистка лица', 'Пилинг PRX-T33', 'Уход после процедур'],
  'Пластическая хирургия': ['Консультация хирурга', 'Коррекция рубцов'],
  Другое: ['Первичная консультация', 'Подбор домашнего ухода'],
};

const specialists = [
  {
    name: 'Иванова Анна Сергеевна',
    role: 'Врач-косметолог',
    image: 'https://images.unsplash.com/photo-1594824476967-48c8b964273f?auto=format&fit=crop&w=240&q=85',
  },
  {
    name: 'Петрова Ольга Михайловна',
    role: 'Врач-косметолог',
    image: 'https://images.unsplash.com/photo-1559839734-2b71ea197ec2?auto=format&fit=crop&w=240&q=85',
  },
  {
    name: 'Соколова Юлия Андреевна',
    role: 'Врач-дерматолог, косметолог',
    image: 'https://images.unsplash.com/photo-1651008376811-b90baee60c1f?auto=format&fit=crop&w=240&q=85',
  },
];

const times = ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30'];
const calendarDays = [
  ['26', '27', '28', '29', '30', '31', '1'],
  ['2', '3', '4', '5', '6', '7', '8'],
  ['9', '10', '11', '12', '13', '14', '15'],
  ['16', '17', '18', '19', '20', '21', '22'],
  ['23', '24', '25', '26', '27', '28', '29'],
  ['30', '1', '2', '3', '4', '5', '6'],
];

export function AppointmentModal() {
  const [isOpen, setIsOpen] = useState(false);
  const [category, setCategory] = useState(categories[0]);
  const [service, setService] = useState(servicesByCategory[categories[0]][0]);
  const [specialist, setSpecialist] = useState(specialists[0]);
  const [day, setDay] = useState('12');
  const [time, setTime] = useState('12:30');
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [comment, setComment] = useState('');
  const [agreement, setAgreement] = useState(true);
  const [success, setSuccess] = useState(false);

  const currentServices = useMemo(() => servicesByCategory[category], [category]);

  useEffect(() => {
    const onClick = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      const trigger = target.closest('button, a');
      const text = trigger?.textContent?.toLowerCase().trim() ?? '';

      if (trigger && (text.includes('записаться') || text.includes('открыть запись'))) {
        event.preventDefault();
        setIsOpen(true);
      }
    };

    document.addEventListener('click', onClick);
    return () => document.removeEventListener('click', onClick);
  }, []);

  useEffect(() => {
    if (!currentServices.includes(service)) {
      setService(currentServices[0]);
    }
  }, [currentServices, service]);

  useEffect(() => {
    document.body.style.overflow = isOpen ? 'hidden' : '';
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  if (!isOpen) {
    return success ? <SuccessToast onClose={() => setSuccess(false)} /> : null;
  }

  const canSubmit = name.trim().length > 1 && phone.trim().length > 5 && agreement;

  const submit = () => {
    if (!canSubmit) return;
    setIsOpen(false);
    setSuccess(true);
    window.setTimeout(() => setSuccess(false), 3600);
  };

  return (
    <>
      <div className="appointment-overlay" onMouseDown={() => setIsOpen(false)}>
        <section className="appointment-modal" role="dialog" aria-modal="true" aria-labelledby="appointment-title" onMouseDown={(event) => event.stopPropagation()}>
          <button className="appointment-close" type="button" aria-label="Закрыть" onClick={() => setIsOpen(false)}>
            <X size={24} />
          </button>
          <div className="appointment-main">
            <header>
              <h2 id="appointment-title">Запись на приём</h2>
              <p>Выберите услугу, специалиста, дату и удобное время для посещения клиники.</p>
            </header>

            <Step number="1" title="Услуга" />
            <div className="appointment-tabs">
              {categories.map((item) => (
                <button className={item === category ? 'is-active' : ''} key={item} type="button" onClick={() => setCategory(item)}>
                  {item}
                </button>
              ))}
            </div>
            <select value={service} onChange={(event) => setService(event.target.value)}>
              {currentServices.map((item) => <option key={item}>{item}</option>)}
            </select>

            <Step number="2" title="Специалист" />
            <div className="specialist-picker">
              {specialists.map((item) => (
                <button className={item.name === specialist.name ? 'is-active' : ''} key={item.name} type="button" onClick={() => setSpecialist(item)}>
                  <img alt={item.name} src={item.image} />
                  <span><strong>{item.name}</strong><small>{item.role}</small></span>
                  {item.name === specialist.name && <Check size={18} />}
                </button>
              ))}
            </div>

            <div className="date-time-grid">
              <div>
                <Step number="3" title="Дата" />
                <div className="calendar-card">
                  <div className="calendar-head"><button type="button">‹</button><strong>Июнь 2025</strong><button type="button">›</button></div>
                  <div className="calendar-week"><span>Пн</span><span>Вт</span><span>Ср</span><span>Чт</span><span>Пт</span><span>Сб</span><span>Вс</span></div>
                  <div className="calendar-grid">
                    {calendarDays.flat().map((item, index) => (
                      <button className={`${item === day ? 'is-active' : ''} ${index < 6 || index > 34 ? 'is-muted' : ''}`.trim()} key={`${item}-${index}`} type="button" onClick={() => setDay(item)}>
                        {item}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
              <div>
                <Step number="4" title="Время" />
                <div className="time-grid">
                  {times.map((item) => (
                    <button className={item === time ? 'is-active' : ''} key={item} type="button" onClick={() => setTime(item)}>
                      {item}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <Step number="5" title="Ваши данные" />
            <div className="patient-fields">
              <input value={name} onChange={(event) => setName(event.target.value)} placeholder="ФИО" />
              <input value={phone} onChange={(event) => setPhone(event.target.value)} placeholder="+7 (___) ___-__-__" />
            </div>

            <Step number="6" title="Комментарий" muted="необязательно" />
            <textarea value={comment} onChange={(event) => setComment(event.target.value)} placeholder="Укажите пожелания или дополнительные детали" />

            <label className="agreement-row">
              <input checked={agreement} onChange={(event) => setAgreement(event.target.checked)} type="checkbox" />
              <span>Я даю согласие на <u>обработку персональных данных</u></span>
            </label>

            <button className="appointment-submit" type="button" disabled={!canSubmit} onClick={submit}>
              Подтвердить запись
            </button>
          </div>

          <aside className="booking-summary">
            <h3>Ваше бронирование</h3>
            <SummaryRow icon={<Sparkles />} label="Услуга" value={service} />
            <SummaryRow icon={<UserRound />} label="Специалист" value={specialist.name} />
            <SummaryRow icon={<CalendarDays />} label="Дата" value={`${day} июня 2025`} />
            <SummaryRow icon={<Clock3 />} label="Время" value={time} />
            <SummaryRow icon={<Tag />} label="Стоимость" value="≈ 22 000 ₸" />
            <p>Окончательная стоимость может быть скорректирована после консультации специалиста.</p>
            <div className="summary-note">
              <ShieldCheck size={24} />
              <span>Мы гарантируем конфиденциальность ваших данных и бережный подход к каждому пациенту.</span>
            </div>
          </aside>
        </section>
      </div>
      {success && <SuccessToast onClose={() => setSuccess(false)} />}
    </>
  );
}

function Step({ number, title, muted }: { number: string; title: string; muted?: string }) {
  return (
    <div className="appointment-step">
      <span>{number}</span>
      <strong>{title}</strong>
      {muted && <small>{muted}</small>}
    </div>
  );
}

function SummaryRow({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="summary-row">
      {icon}
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function SuccessToast({ onClose }: { onClose: () => void }) {
  return (
    <div className="appointment-toast" role="status" onClick={onClose}>
      <CheckCircle2 size={28} />
      <span>Запись прошла успешно</span>
    </div>
  );
}
