"""Доменные сущности заказа."""

import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List
from dataclasses import dataclass, field

from .exceptions import (
    OrderAlreadyPaidError,
    OrderCancelledError,
    InvalidQuantityError,
    InvalidPriceError,
    InvalidAmountError,
)


# TODO: Реализовать OrderStatus (str, Enum)
# Значения: CREATED, PAID, CANCELLED, SHIPPED, COMPLETED
class OrderStatus(str, Enum):
    CREATED = "created"
    PAID = "paid"
    CANCELLED = "cancelled"
    SHIPPED = "shipped"
    COMPLETED = "completed"


# TODO: Реализовать OrderItem (dataclass)
# Поля: product_name, price, quantity, id, order_id
# Свойство: subtotal (price * quantity)
# Валидация: quantity > 0, price >= 0
@dataclass
class OrderItem:
    product_name: str
    price: Decimal
    quantity: int
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    order_id: uuid.UUID | None = None

    def __post_init__(self):
        self.price = Decimal(self.price)

        if self.quantity <= 0:
            raise InvalidQuantityError(self.quantity)

        if self.price < 0:
            raise InvalidPriceError(self.price)

        self.product_name = (self.product_name or "").strip()

    @property
    def subtotal(self) -> Decimal:
        return self.price * self.quantity


# TODO: Реализовать OrderStatusChange (dataclass)
# Поля: order_id, status, changed_at, id
@dataclass
class OrderStatusChange:
    order_id: uuid.UUID
    status: OrderStatus
    changed_at: datetime = field(default_factory=datetime.utcnow)
    id: uuid.UUID = field(default_factory=uuid.uuid4)


# TODO: Реализовать Order (dataclass)
# Поля: user_id, id, status, total_amount, created_at, items, status_history
# Методы:
#   - add_item(product_name, price, quantity) -> OrderItem
#   - pay() -> None  [КРИТИЧНО: нельзя оплатить дважды!]
#   - cancel() -> None
#   - ship() -> None
#   - complete() -> None
@dataclass
class Order:
    user_id: uuid.UUID
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    status: OrderStatus = OrderStatus.CREATED
    total_amount: Decimal = field(default_factory=lambda: Decimal("0"))
    created_at: datetime = field(default_factory=datetime.utcnow)
    items: List[OrderItem] = field(default_factory=list)
    status_history: List[OrderStatusChange] = field(default_factory=list)

    def __post_init__(self):
        self.total_amount = Decimal(self.total_amount)

        if self.total_amount < 0:
            raise InvalidAmountError(self.total_amount)

        if not self.status_history:
            self.status_history.append(
                OrderStatusChange(order_id=self.id, status=self.status)
            )

    def _add_status_history(self, status: OrderStatus) -> None:
        self.status_history.append(OrderStatusChange(order_id=self.id, status=status))

    def _recalculate_total(self) -> None:
        self.total_amount = sum((item.subtotal for item in self.items), Decimal("0"))
        if self.total_amount < 0:
            raise InvalidAmountError(self.total_amount)

    def add_item(self, product_name, price, quantity) -> OrderItem:
        if self.status == OrderStatus.CANCELLED:
            raise OrderCancelledError(self.id)

        item = OrderItem(
            product_name=product_name,
            price=Decimal(price),
            quantity=quantity,
            order_id=self.id,
        )
        self.items.append(item)
        self._recalculate_total()
        return item

    def pay(self) -> None:
        if self.status == OrderStatus.PAID:
            raise OrderAlreadyPaidError(self.id)

        if self.status == OrderStatus.CANCELLED:
            raise OrderCancelledError(self.id)

        self.status = OrderStatus.PAID
        self._add_status_history(self.status)

    def cancel(self) -> None:
        if self.status == OrderStatus.PAID:
            raise OrderAlreadyPaidError(self.id)

        if self.status != OrderStatus.CANCELLED:
            self.status = OrderStatus.CANCELLED
            self._add_status_history(self.status)

    def ship(self) -> None:
        if self.status != OrderStatus.PAID:
            raise ValueError("Only paid orders can be shipped")

        self.status = OrderStatus.SHIPPED
        self._add_status_history(self.status)

    def complete(self) -> None:
        if self.status != OrderStatus.SHIPPED:
            raise ValueError("Only shipped orders can be completed")

        self.status = OrderStatus.COMPLETED
        self._add_status_history(self.status)
        