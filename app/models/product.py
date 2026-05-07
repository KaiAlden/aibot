from decimal import Decimal

from sqlalchemy import Boolean, DECIMAL, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        Index("idx_products_tenant_form", "tenant_id", "form"),
        Index("idx_products_tenant_category", "tenant_id", "category"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str | None] = mapped_column(String(64))
    form: Mapped[str | None] = mapped_column(String(32))
    description: Mapped[str | None] = mapped_column(Text)
    price: Mapped[Decimal | None] = mapped_column(DECIMAL(10, 2))
    weight: Mapped[str | None] = mapped_column(String(32))
    image_url: Mapped[str | None] = mapped_column(String(512))
    is_universal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    business_weight: Mapped[Decimal] = mapped_column(DECIMAL(5, 2), default=Decimal("1.00"), nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[str] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    constitutions: Mapped[list["ProductConstitution"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
    ingredients: Mapped[list["ProductIngredient"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )


class ProductConstitution(Base):
    __tablename__ = "product_constitution"

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), primary_key=True)
    constitution: Mapped[str] = mapped_column(String(16), primary_key=True)

    product: Mapped[Product] = relationship(back_populates="constitutions")


class ProductIngredient(Base):
    __tablename__ = "product_ingredient"

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), primary_key=True)
    ingredient: Mapped[str] = mapped_column(String(64), primary_key=True)

    product: Mapped[Product] = relationship(back_populates="ingredients")
