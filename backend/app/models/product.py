from __future__ import annotations

from decimal import Decimal

from sqlalchemy import (
    Boolean, CHAR, CheckConstraint, Computed, DateTime, ForeignKey,
    Index, Integer, Numeric, String, Text, UniqueConstraint, func, text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ProductCategory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "product_categories"
    __table_args__ = (UniqueConstraint("slug", name="uq_product_categories_slug"),)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)

    products: Mapped[list[Product]] = relationship(back_populates="category")


class Product(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_products_slug"),
        CheckConstraint("price >= 0", name="chk_products_price"),
        CheckConstraint("stock >= 0", name="chk_products_stock"),
        Index("ix_products_category_id", "category_id"),
        Index("ix_products_title", "title"),
    )

    category_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("product_categories.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(500))
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=text("1"))

    category: Mapped[ProductCategory] = relationship(back_populates="products")
    wishlist_items = relationship("WishlistItem", back_populates="product")
    cart_items = relationship("CartItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")
    recommendation_links = relationship("RecommendationProduct", back_populates="product", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", secondary="recommendation_products", back_populates="products", viewonly=True)


class WishlistItem(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "wishlist_items"
    __table_args__ = (UniqueConstraint("user_id", "product_id", name="uq_wishlist_items_user_product"),)

    user_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    created_at = mapped_column(DateTime, nullable=False, server_default=func.current_timestamp())

    user = relationship("User", back_populates="wishlist_items")
    product: Mapped[Product] = relationship(back_populates="wishlist_items")


class CartItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "cart_items"
    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_cart_items_user_product"),
        CheckConstraint("quantity >= 1", name="chk_cart_items_quantity"),
        CheckConstraint("price >= 0", name="chk_cart_items_price"),
    )

    user_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), Computed("quantity * price", persisted=True))

    user = relationship("User", back_populates="cart_items")
    product: Mapped[Product] = relationship(back_populates="cart_items")
