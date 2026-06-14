import { ArrowLeft, BadgeCheck, Heart, Home, ShieldCheck, ShoppingBag, Sparkles, Star, ZoomIn } from 'lucide-react';
import { Link, useParams } from 'react-router-dom';

import { Button } from '@/shared/ui/Button';
import { PlaceholderPage } from '@/shared/ui/PlaceholderPage';

import { productBySlug, products } from '@/pages/shop/productsData';
import './ProductDetailPage.css';

export function ProductDetailPage() {
  const { slug } = useParams();
  const product = slug ? productBySlug.get(slug) : undefined;
  if (!product) return <PlaceholderPage title="Товар не найден" />;
  const related = products.filter((item) => item.slug !== product.slug).slice(0, 5);

  return (
    <main className="product-page">
      <div className="product-container">
        <Link className="product-back-link" to="/shop">
          <ArrowLeft size={18} />
          Вернуться в магазин
        </Link>
        <section className="product-hero">
          <div className="product-info">
            <span className="product-brand">{product.brand}</span>
            <h1>{product.title}</h1>
            <p>{product.subtitle}</p>
            <div className="product-rating">{Array.from({ length: 5 }).map((_, i) => <Star key={i} size={18} fill="currentColor" />)} <span>4.9 (128 отзывов)</span></div>
            <strong className="product-price">{product.price}</strong>
            <div className="product-stock"><span>✓ В наличии</span><i /> Объём: {product.volume}</div>
            <div className="product-tags">{product.tags.map((tag) => <small key={tag}>{tag}</small>)}</div>
            <p className="product-description">{product.description}</p>
            <div className="product-actions">
              <div className="qty"><button>-</button><span>1</span><button>+</button></div>
              <button className="favorite-btn"><Heart size={26} /> Добавить в избранное</button>
            </div>
            <Button><ShoppingBag size={22} /> Добавить в корзину</Button>
            <button className="one-click" type="button">Купить в 1 клик</button>
          </div>
          <div className="product-gallery">
            <div className="product-main-image"><img alt={product.title} src={product.image} /><button><ZoomIn size={20} /></button></div>
            <div className="product-thumbs">
              {[product.image, product.image, 'https://images.unsplash.com/photo-1611073761523-645e8de127f2?auto=format&fit=crop&w=500&q=85', product.image].map((img, i) => (
                <button className={i === 0 ? 'is-active' : ''} key={i}><img alt="" src={img} /></button>
              ))}
            </div>
          </div>
        </section>
        <section className="product-tabs">
          {['Описание', 'Способ применения', 'Состав', 'Характеристики'].map((tab, i) => <button className={i === 0 ? 'is-active' : ''} key={tab}>{tab}</button>)}
        </section>
        <p className="product-long-text">{product.title} — профессиональное средство для домашнего ухода Beatris. Подходит для ежедневного использования по рекомендации специалиста и помогает поддерживать результат процедур.</p>
        <section className="product-benefits">
          {[
            { icon: <ShieldCheck size={32} />, text: 'Антиоксидантная защита' },
            { icon: <Sparkles size={32} />, text: 'Выравнивание тона' },
            { icon: <Home size={32} />, text: 'Подходит для домашнего ухода' },
            { icon: <BadgeCheck size={32} />, text: 'Оригинальная продукция' },
          ].map((item) => (
            <article key={item.text}>
              {item.icon}
              <span>{item.text}</span>
            </article>
          ))}
        </section>
        <section className="related-products">
          <div><h2>С этим товаром покупают</h2><Link to="/shop">Смотреть все →</Link></div>
          <div className="related-row">
            {related.map((item) => (
              <article key={item.slug}>
                <img alt={item.title} src={item.image} />
                <div><span>{item.brand}</span><h3>{item.title}</h3><p>{item.subtitle}</p><strong>{item.price}</strong><Button>В корзину</Button></div>
              </article>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}
