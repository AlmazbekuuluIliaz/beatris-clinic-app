export function Footer() {
  return (
    <footer className="site-footer">
      <div className="site-footer__inner">
        <div className="site-footer__brand">
          <span>Beatris</span>
          <p>Лицензированная клиника эстетической медицины. Индивидуальный подход к вашей красоте.</p>
          <small>© Beatris, 2026. Все права защищены.</small>
        </div>
        <nav aria-label="Основное">
          <strong>Основное</strong>
          <a href="/about/clinic">О нас</a>
          <a href="/services">Услуги</a>
          <a href="/promotions">Акции</a>
          <a href="/contacts">Контакты</a>
        </nav>
        <nav aria-label="Магазин">
          <strong>Магазин</strong>
          <a href="/shop">Каталог</a>
          <a href="/account/orders">Доставка и оплата</a>
          <a href="/promotions">Акции</a>
          <a href="/contacts">Возврат и обмен</a>
        </nav>
        <div className="site-footer__contacts">
          <strong>Контакты</strong>
          <span>г. Атырау ул. Азаттык, 24а</span>
          <span>Пн-Вс 9.00 - 20.00</span>
          <span>+7 (775) 450 97-76</span>
          <span>beatris-clinic@gmail.com</span>
        </div>
      </div>
    </footer>
  );
}
