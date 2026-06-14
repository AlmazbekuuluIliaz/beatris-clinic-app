import { ChevronDown, Grid2X2, Heart, List, Search } from "lucide-react"
import { Link } from "react-router-dom"

import { Button } from "@/shared/ui/Button"

import { products } from "./productsData"
import "./ShopPage.css"

const categories = [
  "Популярное",
  "Для лица",
  "Для тела",
  "Для волос",
  "SPF",
  "Наборы",
  "Бренды",
]
const brands = [
  "SkinCeuticals (24)",
  "Obagi Medical (18)",
  "Medik8 (20)",
  "iS Clinical (16)",
  "EtamD (12)",
]
const problems = [
  "Возрастные изменения",
  "Обезвоженность",
  "Пигментация",
  "Акне и воспаления",
  "Чувствительность",
]

export function ShopPage() {
  return (
    <main className="shop-page">
      <div className="shop-container">
        <p className="shop-breadcrumb">Главная / Магазин</p>
        <div className="shop-toolbar">
          <label className="shop-search">
            <span>Поиск по товарам, брендам, категориям...</span>
            <Search size={22} />
          </label>
          <button className="shop-sort" type="button">
            Сортировать: Популярные <ChevronDown size={18} />
          </button>
          <div className="shop-view">
            <Grid2X2 size={22} />
            <List size={22} />
          </div>
        </div>
        <div className="shop-tabs">
          {categories.map((category, index) => (
            <button
              className={index === 0 ? "is-active" : ""}
              key={category}
              type="button"
            >
              {category}
            </button>
          ))}
        </div>
        <div className="shop-layout">
          <aside className="shop-filters">
            <Filter title="Бренд" items={brands} />
            <Filter title="Проблема кожи" items={problems} />
            <section className="filter-card">
              <h2>
                Цена, ₸ <ChevronDown size={18} />
              </h2>
              <div className="price-line">
                <span />
                <span />
              </div>
              <div className="price-inputs">
                <span>от 1 000</span>
                <span>до 25 000</span>
              </div>
            </section>
            <section className="shop-help">
              <img
                alt="Специалист Beatris"
                src="https://images.unsplash.com/photo-1559839734-2b71ea197ec2?auto=format&fit=crop&w=360&q=85"
              />
              <h2>Нужна помощь в выборе?</h2>
              <p>Наши специалисты подберут уход, подходящий именно вам.</p>
              <Button>Задать вопрос</Button>
            </section>
          </aside>
          <section className="shop-grid">
            {products.map((product) => (
              <article className="shop-product-card" key={product.slug}>
                <button
                  className="shop-product-card__heart"
                  type="button"
                  aria-label="В избранное"
                >
                  <Heart size={22} />
                </button>
                <Link
                  to={`/shop/${product.slug}`}
                  className="shop-product-card__image"
                >
                  <img alt={product.title} src={product.image} />
                </Link>
                <div>
                  <span>{product.brand}</span>
                  <Link to={`/shop/${product.slug}`}>
                    <h2>{product.title}</h2>
                  </Link>
                  <p>{product.subtitle}</p>
                  <strong>{product.price}</strong>
                  <Button>В корзину</Button>
                </div>
              </article>
            ))}
          </section>
        </div>
      </div>
    </main>
  )
}

export default ShopPage

function Filter({ title, items }: { title: string; items: string[] }) {
  return (
    <section className="filter-card">
      <h2>
        {title} <ChevronDown size={18} />
      </h2>
      {items.map((item) => (
        <label key={item}>
          <input type="checkbox" /> {item}
        </label>
      ))}
      <button type="button">Показать все</button>
    </section>
  )
}
