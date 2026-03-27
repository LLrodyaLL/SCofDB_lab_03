"""
Тест для демонстрации РЕШЕНИЯ проблемы race condition.

Этот тест должен ПРОХОДИТЬ, подтверждая, что при использовании
pay_order_safe() заказ оплачивается только один раз.
"""

import asyncio
import pytest_asyncio
import pytest
import uuid
import time
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import DBAPIError

from app.application.payment_service import PaymentService
from app.domain.exceptions import OrderAlreadyPaidError


# TODO: Настроить подключение к тестовой БД
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/marketplace"
engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
async def db_session():
    """
    Создать сессию БД для тестов.
    
    TODO: Реализовать фикстуру (см. test_concurrent_payment_unsafe.py)
    """
    # TODO: Реализовать создание сессии
    async with SessionLocal() as session:
        yield session


@pytest.fixture
async def test_order(db_session):
    """
    Создать тестовый заказ со статусом 'created'.
    
    TODO: Реализовать фикстуру (см. test_concurrent_payment_unsafe.py)
    """
    # TODO: Реализовать создание тестового заказа
    user_id = uuid.uuid4()
    order_id = uuid.uuid4()

    await db_session.execute(
        text(
            """
            INSERT INTO users (id, email, name, created_at)
            VALUES (:id, :email, :name, NOW())
            """
        ),
        {
            "id": user_id,
            "email": f"safe_{user_id.hex[:8]}@example.com",
            "name": "Safe Test User",
        },
    )

    await db_session.execute(
        text(
            """
            INSERT INTO orders (id, user_id, status, total_amount, created_at)
            VALUES (:id, :user_id, 'created', 0, NOW())
            """
        ),
        {"id": order_id, "user_id": user_id},
    )

    await db_session.execute(
        text(
            """
            INSERT INTO order_status_history (id, order_id, status, changed_at)
            VALUES (:id, :order_id, 'created', NOW())
            """
        ),
        {"id": uuid.uuid4(), "order_id": order_id},
    )

    await db_session.commit()

    yield order_id

    await db_session.execute(
        text("DELETE FROM order_status_history WHERE order_id = :order_id"),
        {"order_id": order_id},
    )
    await db_session.execute(
        text("DELETE FROM orders WHERE id = :order_id"),
        {"order_id": order_id},
    )
    await db_session.execute(
        text("DELETE FROM users WHERE id = :user_id"),
        {"user_id": user_id},
    )
    await db_session.commit()


@pytest.mark.asyncio
async def test_concurrent_payment_safe_prevents_race_condition(db_session, test_order):
    """
    Тест демонстрирует решение проблемы race condition с помощью pay_order_safe().
    
    ОЖИДАЕМЫЙ РЕЗУЛЬТАТ: Тест ПРОХОДИТ, подтверждая, что заказ был оплачен только один раз.
    Это показывает, что метод pay_order_safe() защищен от конкурентных запросов.
    
    TODO: Реализовать тест следующим образом:
    
    1. Создать два экземпляра PaymentService с РАЗНЫМИ сессиями
       (это имитирует два независимых HTTP-запроса)
       
    2. Запустить два параллельных вызова pay_order_safe():
       
       async def payment_attempt_1():
           service1 = PaymentService(session1)
           return await service1.pay_order_safe(order_id)
           
       async def payment_attempt_2():
           service2 = PaymentService(session2)
           return await service2.pay_order_safe(order_id)
           
       results = await asyncio.gather(
           payment_attempt_1(),
           payment_attempt_2(),
           return_exceptions=True
       )
       
    3. Проверить результаты:
       - Одна попытка должна УСПЕШНО завершиться
       - Вторая попытка должна выбросить OrderAlreadyPaidError ИЛИ вернуть ошибку
       
       success_count = sum(1 for r in results if not isinstance(r, Exception))
       error_count = sum(1 for r in results if isinstance(r, Exception))
       
       assert success_count == 1, "Ожидалась одна успешная оплата"
       assert error_count == 1, "Ожидалась одна неудачная попытка"
       
    4. Проверить историю оплат:
       
       service = PaymentService(session)
       history = await service.get_payment_history(order_id)
       
       # ОЖИДАЕМ ОДНУ ЗАПИСЬ 'paid' - проблема решена!
       assert len(history) == 1, "Ожидалась 1 запись об оплате (БЕЗ RACE CONDITION!)"
       
    5. Вывести информацию об успешном решении:
       
       print(f"✅ RACE CONDITION PREVENTED!")
       print(f"Order {order_id} was paid only ONCE:")
       print(f"  - {history[0]['changed_at']}: status = {history[0]['status']}")
       print(f"Second attempt was rejected: {results[1]}")
    """
    # TODO: Реализовать тест, демонстрирующий решение race condition
    order_id = test_order

    async def payment_attempt():
        async with SessionLocal() as session:
            service = PaymentService(session)
            return await service.pay_order_safe(order_id)

    results = await asyncio.gather(
        payment_attempt(),
        payment_attempt(),
        return_exceptions=True,
    )

    success_count = sum(1 for r in results if not isinstance(r, Exception))
    error_count = sum(1 for r in results if isinstance(r, Exception))

    service = PaymentService(db_session)
    history = await service.get_payment_history(order_id)

    assert success_count == 1, "Ожидалась одна успешная оплата"
    assert error_count == 1, "Ожидалась одна неудачная попытка"
    assert len(history) == 1, "Ожидалась 1 запись об оплате (БЕЗ RACE CONDITION!)"
    assert any(
        isinstance(r, OrderAlreadyPaidError) or
        (isinstance(r, DBAPIError) and "could not serialize access due to concurrent update" in str(r))
        for r in results
    ), "Ожидалась OrderAlreadyPaidError или SerializationError"

    rejected = next(r for r in results if isinstance(r, Exception))

    print("\n✅ RACE CONDITION PREVENTED!")
    print(f"Order {order_id} was paid only ONCE:")
    print(f"  - {history[0]['changed_at']}: status = {history[0]['status']}")
    print(f"Second attempt was rejected: {rejected}")


async def _create_order(session: AsyncSession, prefix: str = "multi"):
    user_id = uuid.uuid4()
    order_id = uuid.uuid4()

    await session.execute(
        text(
            """
            INSERT INTO users (id, email, name, created_at)
            VALUES (:id, :email, :name, NOW())
            """
        ),
        {
            "id": user_id,
            "email": f"{prefix}_{user_id.hex[:8]}@example.com",
            "name": f"{prefix} user",
        },
    )

    await session.execute(
        text(
            """
            INSERT INTO orders (id, user_id, status, total_amount, created_at)
            VALUES (:id, :user_id, 'created', 0, NOW())
            """
        ),
        {"id": order_id, "user_id": user_id},
    )

    await session.execute(
        text(
            """
            INSERT INTO order_status_history (id, order_id, status, changed_at)
            VALUES (:id, :order_id, 'created', NOW())
            """
        ),
        {"id": uuid.uuid4(), "order_id": order_id},
    )

    await session.commit()
    return user_id, order_id


@pytest.mark.asyncio
async def test_concurrent_payment_safe_with_explicit_timing(db_session):
    """
    Дополнительный тест: проверить работу блокировок с явной задержкой.
    
    TODO: Реализовать тест с добавлением задержки в первой транзакции:
    
    1. Первая транзакция:
       - Начать транзакцию
       - Заблокировать заказ (FOR UPDATE)
       - Добавить задержку (asyncio.sleep(1))
       - Оплатить
       - Commit
       
    2. Вторая транзакция (запустить через 0.1 секунды после первой):
       - Начать транзакцию
       - Попытаться заблокировать заказ (FOR UPDATE)
       - ДОЛЖНА ЖДАТЬ освобождения блокировки от первой транзакции
       - После освобождения - увидеть обновленный статус 'paid'
       - Выбросить OrderAlreadyPaidError
       
    3. Проверить временные метки:
       - Вторая транзакция должна завершиться ПОЗЖЕ первой
       - Разница должна быть >= 1 секунды (время задержки)
       
    Это подтверждает, что FOR UPDATE действительно блокирует строку.
    """
    # TODO: Реализовать тест с проверкой блокировки
    user_id, order_id = await _create_order(db_session, prefix="timing")

    async def payment_attempt_1():
        async with SessionLocal() as session:
            start = time.monotonic()
            async with session.begin():
                await session.execute(
                    text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
                )
                result = await session.execute(
                    text(
                        """
                        SELECT status
                        FROM orders
                        WHERE id = :order_id
                        FOR UPDATE
                        """
                    ),
                    {"order_id": order_id},
                )
                status = result.scalar_one()
                assert status == "created"

                await asyncio.sleep(1)

                await session.execute(
                    text(
                        """
                        UPDATE orders
                        SET status = 'paid'
                        WHERE id = :order_id AND status = 'created'
                        """
                    ),
                    {"order_id": order_id},
                )
                await session.execute(
                    text(
                        """
                        INSERT INTO order_status_history (id, order_id, status, changed_at)
                        VALUES (:id, :order_id, 'paid', NOW())
                        """
                    ),
                    {"id": uuid.uuid4(), "order_id": order_id},
                )
            return time.monotonic() - start

    async def payment_attempt_2():
        await asyncio.sleep(0.1)
        async with SessionLocal() as session:
            start = time.monotonic()
            service = PaymentService(session)
            try:
                await service.pay_order_safe(order_id)
            except OrderAlreadyPaidError:
                return time.monotonic() - start
            except DBAPIError as e:
                if "could not serialize access due to concurrent update" in str(e):
                    return time.monotonic() - start
                raise
            raise AssertionError(
                "Ожидалось OrderAlreadyPaidError или SerializationError во второй транзакции"
            )

    duration_1, duration_2 = await asyncio.gather(
        payment_attempt_1(),
        payment_attempt_2(),
    )

    service = PaymentService(db_session)
    history = await service.get_payment_history(order_id)

    assert len(history) == 1, "После блокировки должна быть только одна оплата"
    assert duration_2 >= 0.8, "Вторая транзакция должна была ждать освобождения блокировки"

    await db_session.execute(
        text("DELETE FROM order_status_history WHERE order_id = :order_id"),
        {"order_id": order_id},
    )
    await db_session.execute(
        text("DELETE FROM orders WHERE id = :order_id"),
        {"order_id": order_id},
    )
    await db_session.execute(
        text("DELETE FROM users WHERE id = :user_id"),
        {"user_id": user_id},
    )
    await db_session.commit()


@pytest.mark.asyncio
async def test_concurrent_payment_safe_multiple_orders(db_session):
    """
    Дополнительный тест: проверить, что блокировки не мешают разным заказам.
    
    TODO: Реализовать тест:
    1. Создать ДВА разных заказа
    2. Оплатить их ПАРАЛЛЕЛЬНО с помощью pay_order_safe()
    3. Проверить, что ОБА успешно оплачены
    
    Это показывает, что FOR UPDATE блокирует только конкретную строку,
    а не всю таблицу, что важно для производительности.
    """
    # TODO: Реализовать тест с несколькими заказами
    user_id_1, order_id_1 = await _create_order(db_session, prefix="multi1")
    user_id_2, order_id_2 = await _create_order(db_session, prefix="multi2")

    async def pay(order_id):
        async with SessionLocal() as session:
            service = PaymentService(session)
            return await service.pay_order_safe(order_id)

    results = await asyncio.gather(
        pay(order_id_1),
        pay(order_id_2),
        return_exceptions=True,
    )

    assert all(not isinstance(r, Exception) for r in results), "Оба разных заказа должны оплатиться успешно"

    service = PaymentService(db_session)
    history_1 = await service.get_payment_history(order_id_1)
    history_2 = await service.get_payment_history(order_id_2)

    assert len(history_1) == 1
    assert len(history_2) == 1

    await db_session.execute(
        text("DELETE FROM order_status_history WHERE order_id IN (:o1, :o2)"),
        {"o1": order_id_1, "o2": order_id_2},
    )
    await db_session.execute(
        text("DELETE FROM orders WHERE id IN (:o1, :o2)"),
        {"o1": order_id_1, "o2": order_id_2},
    )
    await db_session.execute(
        text("DELETE FROM users WHERE id IN (:u1, :u2)"),
        {"u1": user_id_1, "u2": user_id_2},
    )
    await db_session.commit()


if __name__ == "__main__":
    """
    Запуск теста:
    
    cd backend
    export PYTHONPATH=$(pwd)
    pytest app/tests/test_concurrent_payment_safe.py -v -s
    
    ОЖИДАЕМЫЙ РЕЗУЛЬТАТ:
    ✅ test_concurrent_payment_safe_prevents_race_condition PASSED
    
    Вывод должен показывать:
    ✅ RACE CONDITION PREVENTED!
    Order XXX was paid only ONCE:
      - 2024-XX-XX: status = paid
    Second attempt was rejected: OrderAlreadyPaidError(...)
    """
    pytest.main([__file__, "-v", "-s"])
    