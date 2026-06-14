import {
  ArrowRight,
  CalendarClock,
  ChevronDown,
  CircleDollarSign,
  Clock3,
  Droplet,
  HelpCircle,
  PackageCheck,
  Syringe,
  UserRound,
} from 'lucide-react';
import { Link, useParams } from 'react-router-dom';

import { Button } from '@/shared/ui/Button';
import { PlaceholderPage } from '@/shared/ui/PlaceholderPage';

import { detailDoctors, serviceBySlug } from '@/pages/services/servicesData';
import './ServiceDetailPage.css';

const doctorImage =
  'https://images.unsplash.com/photo-1559839734-2b71ea197ec2?auto=format&fit=crop&w=360&q=85';

const statIcons = [<CircleDollarSign />, <Clock3 />, <CalendarClock />, <PackageCheck />];

export function ServiceDetailPage() {
  const { slug } = useParams();
  const service = slug ? serviceBySlug.get(slug) : undefined;

  if (!service) {
    return <PlaceholderPage title="Услуга не найдена" />;
  }

  return (
    <main className="service-detail-page">
      <div className="service-detail-container">
        <section className="service-detail-hero">
          <div>
            <p className="service-breadcrumb">Главная / Услуги / {service.category} / {service.title}</p>
            <h1>{service.title}</h1>
            <p>{service.description}</p>
            <div className="service-stats">
              {service.stats.map((stat, index) => (
                <article key={stat.label}>
                  {statIcons[index]}
                  <span>{stat.label}</span>
                  <strong>{stat.value}</strong>
                </article>
              ))}
            </div>
            <div className="service-hero-actions">
              <Button>Записаться на приём</Button>
              <button type="button">Задать вопрос</button>
            </div>
          </div>
          <img alt={service.title} src={service.image} />
        </section>

        <section className="service-benefits">
          {service.benefits.map((benefit) => (
            <article key={benefit.title}>
              {benefit.icon}
              <div>
                <h3>{benefit.title}</h3>
                <p>{benefit.text}</p>
              </div>
            </article>
          ))}
        </section>

        <section className="service-section">
          <h2>О процедуре</h2>
          <p className="service-about-text">{service.about}</p>
          <div className="service-two-columns">
            <InfoList title="Показания" items={service.indications} />
            <InfoList title="Противопоказания" items={service.contraindications} />
          </div>
        </section>

        <section className="service-section">
          <h2>Как проходит процедура</h2>
          <div className="service-steps">
            {service.steps.map((step, index) => (
              <article key={step.title}>
                <span>{index + 1}</span>
                {index === 2 ? <Syringe /> : index === 4 ? <Clock3 /> : index === 0 ? <HelpCircle /> : <Droplet />}
                <h3>{step.title}</h3>
                <p>{step.text}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="service-after-grid">
          <article className="service-result-card">
            <h2>Ожидаемый результат</h2>
            <div>
              {service.results.map((result) => (
                <span key={result.text}>
                  {result.icon}
                  <small>{result.text}</small>
                </span>
              ))}
            </div>
          </article>
          <article className="service-recommend-card">
            <h2>Рекомендации после процедуры</h2>
            <ul>
              {service.recommendations.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </article>
        </section>

        <section className="service-linked-grid">
          <div>
            <h2>Специалисты, выполняющие процедуру</h2>
            <div className="service-doctors">
              {detailDoctors.map(([name, role, exp]) => (
                <article key={name}>
                  <img alt={name} src={doctorImage} />
                  <div>
                    <h3>{name}</h3>
                    <p>{role}</p>
                    <span>{exp}</span>
                    <Link to="/about/specialists">Подробнее</Link>
                  </div>
                </article>
              ))}
            </div>
          </div>
          <div>
            <h2>Вам также может подойти</h2>
            <div className="service-related">
              {service.related.map((item) => (
                <Link to={`/services/${item.slug}`} key={item.title}>
                  <img alt={item.title} src={item.image} />
                  <span>{item.title}</span>
                  <strong>{item.price}</strong>
                </Link>
              ))}
            </div>
          </div>
        </section>

        <section className="service-section">
          <h2>Часто задаваемые вопросы</h2>
          <div className="service-faq">
            {service.faq.map((question) => (
              <button type="button" key={question}>
                {question}
                <ChevronDown size={18} />
              </button>
            ))}
          </div>
        </section>

        <section className="service-cta">
          <div className="service-cta__image" />
          <div>
            <h2>Запишитесь на консультацию</h2>
            <p>Наши специалисты подберут оптимальную программу ухода и помогут сохранить вашу красоту и молодость.</p>
          </div>
          <Button>Записаться на приём</Button>
        </section>
      </div>
    </main>
  );
}

function InfoList({ title, items }: { title: string; items: string[] }) {
  return (
    <article className="service-info-list">
      <h3>{title}</h3>
      <ul>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </article>
  );
}
