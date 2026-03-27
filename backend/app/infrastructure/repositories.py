"""Реализация репозиториев с использованием SQLAlchemy."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.user import User
from app.domain.order import Order, OrderItem, OrderStatus, OrderStatusChange


class UserRepository:
    """Репозиторий для User."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # TODO: Реализовать save(user: User) -> None
    # Используйте INSERT ... ON CONFLICT DO UPDATE
    async def save(self, user: User) -> None:
        query = text(
            """
            INSERT INTO users (id, email, name, created_at)
            VALUES (:id, :email, :name, :created_at)
            ON CONFLICT (id) DO UPDATE SET
                email = EXCLUDED.email,
                name = EXCLUDED.name,
                created_at = EXCLUDED.created_at
            """
        )
        await self.session.execute(
            query,
            {
                "id": str(user.id),
                "email": user.email,
                "name": user.name,
                "created_at": user.created_at,
            },
        )

    # TODO: Реализовать find_by_id(user_id: UUID) -> Optional[User]
    async def find_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        result = await self.session.execute(
            text("SELECT id, email, name, created_at FROM users WHERE id = :id"),
            {"id": str(user_id)},
        )
        row = result.mappings().first()
        if row is None:
            return None

        user = object.__new__(User)
        user.id = uuid.UUID(str(row["id"]))
        user.email = row["email"]
        user.name = row["name"]
        user.created_at = row["created_at"]
        return user

    # TODO: Реализовать find_by_email(email: str) -> Optional[User]
    async def find_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            text("SELECT id, email, name, created_at FROM users WHERE email = :email"),
            {"email": email.strip()},
        )
        row = result.mappings().first()
        if row is None:
            return None

        user = object.__new__(User)
        user.id = uuid.UUID(str(row["id"]))
        user.email = row["email"]
        user.name = row["name"]
        user.created_at = row["created_at"]
        return user

    # TODO: Реализовать find_all() -> List[User]
    async def find_all(self) -> List[User]:
        result = await self.session.execute(
            text("SELECT id, email, name, created_at FROM users ORDER BY created_at, id")
        )

        users = []
        for row in result.mappings().all():
            user = object.__new__(User)
            user.id = uuid.UUID(str(row["id"]))
            user.email = row["email"]
            user.name = row["name"]
            user.created_at = row["created_at"]
            users.append(user)

        return users


class OrderRepository:
    """Репозиторий для Order."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # TODO: Реализовать save(order: Order) -> None
    # Сохранить заказ, товары и историю статусов
    async def save(self, order: Order) -> None:
        await self.session.execute(
            text(
                """
                INSERT INTO orders (id, user_id, status, total_amount, created_at)
                VALUES (:id, :user_id, :status, :total_amount, :created_at)
                ON CONFLICT (id) DO UPDATE SET
                    user_id = EXCLUDED.user_id,
                    status = EXCLUDED.status,
                    total_amount = EXCLUDED.total_amount,
                    created_at = EXCLUDED.created_at
                """
            ),
            {
                "id": str(order.id),
                "user_id": str(order.user_id),
                "status": order.status.value,
                "total_amount": order.total_amount,
                "created_at": order.created_at,
            },
        )

        await self.session.execute(
            text("DELETE FROM order_items WHERE order_id = :order_id"),
            {"order_id": str(order.id)},
        )

        for item in order.items:
            await self.session.execute(
                text(
                    """
                    INSERT INTO order_items (id, order_id, product_name, price, quantity, subtotal)
                    VALUES (:id, :order_id, :product_name, :price, :quantity, :subtotal)
                    """
                ),
                {
                    "id": str(item.id),
                    "order_id": str(order.id),
                    "product_name": item.product_name,
                    "price": item.price,
                    "quantity": item.quantity,
                    "subtotal": item.subtotal,
                },
            )

        await self.session.execute(
            text("DELETE FROM order_status_history WHERE order_id = :order_id"),
            {"order_id": str(order.id)},
        )

        for history_item in order.status_history:
            await self.session.execute(
                text(
                    """
                    INSERT INTO order_status_history (id, order_id, status, changed_at)
                    VALUES (:id, :order_id, :status, :changed_at)
                    """
                ),
                {
                    "id": str(history_item.id),
                    "order_id": str(order.id),
                    "status": history_item.status.value,
                    "changed_at": history_item.changed_at,
                },
            )

    # TODO: Реализовать find_by_id(order_id: UUID) -> Optional[Order]
    # Загрузить заказ со всеми товарами и историей
    # Используйте object.__new__(Order) чтобы избежать __post_init__
    async def find_by_id(self, order_id: uuid.UUID) -> Optional[Order]:
        result = await self.session.execute(
            text(
                """
                SELECT id, user_id, status, total_amount, created_at
                FROM orders
                WHERE id = :id
                """
            ),
            {"id": str(order_id)},
        )
        row = result.mappings().first()
        if row is None:
            return None

        order = object.__new__(Order)
        order.id = uuid.UUID(str(row["id"]))
        order.user_id = uuid.UUID(str(row["user_id"]))
        order.status = OrderStatus(row["status"])
        order.total_amount = Decimal(row["total_amount"])
        order.created_at = row["created_at"]
        order.items = []
        order.status_history = []

        items_result = await self.session.execute(
            text(
                """
                SELECT id, order_id, product_name, price, quantity
                FROM order_items
                WHERE order_id = :order_id
                ORDER BY id
                """
            ),
            {"order_id": str(order.id)},
        )

        for item_row in items_result.mappings().all():
            item = object.__new__(OrderItem)
            item.id = uuid.UUID(str(item_row["id"]))
            item.order_id = uuid.UUID(str(item_row["order_id"]))
            item.product_name = item_row["product_name"]
            item.price = Decimal(item_row["price"])
            item.quantity = item_row["quantity"]
            order.items.append(item)

        history_result = await self.session.execute(
            text(
                """
                SELECT id, order_id, status, changed_at
                FROM order_status_history
                WHERE order_id = :order_id
                ORDER BY changed_at, id
                """
            ),
            {"order_id": str(order.id)},
        )

        for history_row in history_result.mappings().all():
            history_item = object.__new__(OrderStatusChange)
            history_item.id = uuid.UUID(str(history_row["id"]))
            history_item.order_id = uuid.UUID(str(history_row["order_id"]))
            history_item.status = OrderStatus(history_row["status"])
            history_item.changed_at = history_row["changed_at"]
            order.status_history.append(history_item)

        return order

    # TODO: Реализовать find_by_user(user_id: UUID) -> List[Order]
    async def find_by_user(self, user_id: uuid.UUID) -> List[Order]:
        result = await self.session.execute(
            text("SELECT id FROM orders WHERE user_id = :user_id ORDER BY created_at, id"),
            {"user_id": str(user_id)},
        )

        orders = []
        for row in result.mappings().all():
            order = await self.find_by_id(row["id"])
            if order is not None:
                orders.append(order)

        return orders

    # TODO: Реализовать find_all() -> List[Order]
    async def find_all(self) -> List[Order]:
        result = await self.session.execute(
            text("SELECT id FROM orders ORDER BY created_at, id")
        )

        orders = []
        for row in result.mappings().all():
            order = await self.find_by_id(row["id"])
            if order is not None:
                orders.append(order)

        return orders