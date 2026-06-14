import { useState } from 'react';
import { Link, NavLink } from 'react-router-dom';
import { ShoppingBag, Star, UserRound } from 'lucide-react';

import { Button } from '@/shared/ui/Button';
import { IconButton } from '@/shared/ui/IconButton';

const navItems = [
  { to: '/services', label: 'Услуги' },
  { to: '/promotions', label: 'Акции' },
  { to: '/shop', label: 'Магазин' },
  { to: '/contacts', label: 'Контакты' },
];

const aboutItems = [
  { to: '/about/clinic', label: 'Клиника' },
  { to: '/about/specialists', label: 'Специалисты' },
  { to: '/about/equipment', label: 'Оборудование' },
  { to: '/about/reviews', label: 'Отзывы' },
];

export function Header() {
  const [isAboutOpen, setIsAboutOpen] = useState(false);
  const [isAboutDismissed, setIsAboutDismissed] = useState(false);

  return (
    <>
      <div className="top-strip">
        <Star size={13} fill="currentColor" />
        <span>Эстетическая медицина • индивидуальный подход • естественные результаты</span>
      </div>
      <header className="site-header">
        <div className="site-header__inner">
          <Link className="site-header__logo" to="/">
            Beatris
          </Link>
          <nav className="site-header__nav" aria-label="Основная навигация">
            <div
              className="site-nav-group"
              onMouseLeave={() => {
                setIsAboutOpen(false);
                setIsAboutDismissed(false);
              }}
            >
              <NavLink
                className="site-nav-group__trigger"
                to="/about/clinic"
                onMouseEnter={() => {
                  setIsAboutDismissed(false);
                  setIsAboutOpen(true);
                }}
                onFocus={() => {
                  setIsAboutDismissed(false);
                  setIsAboutOpen(true);
                }}
              >
                О нас
              </NavLink>
              <div className={`site-header__dropdown ${isAboutOpen && !isAboutDismissed ? 'is-open' : ''}`.trim()}>
                {aboutItems.map((item) => (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    onClick={() => {
                      setIsAboutDismissed(true);
                      setIsAboutOpen(false);
                    }}
                  >
                    {item.label}
                  </NavLink>
                ))}
              </div>
            </div>
            {navItems.map((item) => (
              <NavLink key={item.to} to={item.to}>
                {item.label}
              </NavLink>
            ))}
          </nav>
          <div className="site-header__actions">
            <IconButton label="Корзина" icon={<ShoppingBag size={19} />} />
            <Link className="icon-button" to="/login" aria-label="Личный кабинет" title="Личный кабинет">
              <UserRound size={19} />
            </Link>
            <Button type="button">Записаться</Button>
          </div>
        </div>
      </header>
    </>
  );
}
