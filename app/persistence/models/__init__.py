"""Import every model so that ``Base.metadata`` is complete for Alembic and tests."""

from app.persistence.models.catalog import (
    Category,
    Product,
    ProductImage,
    ProductSpecification,
    ProductVariant,
)
from app.persistence.models.engagement import Notification, Review
from app.persistence.models.identity import AuthSession, LoginThrottleState, User
from app.persistence.models.ledger import AuditEvent, IdempotencyRecord, InventoryMovement
from app.persistence.models.orders import (
    Order,
    OrderAddressSnapshot,
    OrderItem,
    OrderStatusHistory,
    PaymentAttempt,
    Refund,
)
from app.persistence.models.pricing import Coupon, CouponUsage, ShippingOption
from app.persistence.models.shopping import Address, Cart, CartLine, WishlistItem

__all__ = [
    "Address",
    "AuditEvent",
    "AuthSession",
    "Cart",
    "CartLine",
    "Category",
    "Coupon",
    "CouponUsage",
    "IdempotencyRecord",
    "InventoryMovement",
    "LoginThrottleState",
    "Notification",
    "Order",
    "OrderAddressSnapshot",
    "OrderItem",
    "OrderStatusHistory",
    "PaymentAttempt",
    "Product",
    "ProductImage",
    "ProductSpecification",
    "ProductVariant",
    "Refund",
    "Review",
    "ShippingOption",
    "User",
    "WishlistItem",
]
