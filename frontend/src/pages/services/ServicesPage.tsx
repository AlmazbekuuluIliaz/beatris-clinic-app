import { ArrowRight, Search, SlidersHorizontal } from 'lucide-react';
import { Link } from 'react-router-dom';

import { Button } from '@/shared/ui/Button';

import { serviceCategories, services } from './servicesData';
import './ServicesPage.css';

export function ServicesPage() {
  return (
    <main className="services-page">
      <div className="services-container">
        <section className="services-hero">
          <div>
            <p className="services-eyebrow">Услуги Beatris</p>
            <h1>Каталог процедур</h1>
            <p>
              Выберите направление, сравните процедуры и перейдите на детальную страницу услуги, чтобы узнать стоимость,
              показания, этапы и рекомендации после приёма.
            </p>
            <div className="services-search">
              <Search size={18} />
              <span>Поиск по услугам, процедурам и задачам</span>
            </div>
          </div>
          <aside>
            <SlidersHorizontal size={24} />
            <strong>Подберём процедуру</strong>
            <span>Администратор поможет выбрать специалиста и удобное время.</span>
            <Button>Записаться</Button>
          </aside>
        </section>

        <div className="services-filter-row">
          {serviceCategories.map((category, index) => (
            <button className={index === 0 ? 'is-active' : ''} key={category} type="button">
              {category}
            </button>
          ))}
        </div>

        <section className="services-grid">
          {services.map((service) => (
            <article className="service-catalog-card" key={service.slug}>
              <img alt={service.title} src={service.image} />
              <div>
                <span>{service.category}</span>
                <h2>{service.title}</h2>
                <p>{service.description}</p>
                <div className="service-catalog-card__meta">
                  {service.stats.slice(0, 3).map((stat) => (
                    <small key={stat.label}>
                      {stat.label}: <b>{stat.value}</b>
                    </small>
                  ))}
                </div>
                <Link to={`/services/${service.slug}`}>
                  Подробнее <ArrowRight size={16} />
                </Link>
              </div>
            </article>
          ))}
        </section>
      </div>
    </main>
  );
}
