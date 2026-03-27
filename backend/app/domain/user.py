"""Доменная сущность пользователя."""

import uuid
from datetime import datetime
import re
from datetime import datetime
from dataclasses import dataclass, field

from .exceptions import InvalidEmailError


# TODO: Реализовать класс User
# - Использовать @dataclass
# - Поля: email, name, id, created_at
# - Реализовать валидацию email в __post_init__
# - Regex: r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"


@dataclass
class User:
    email: str
    name: str = ""
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        email = (self.email or "").strip()
        if not email or not re.match(EMAIL_REGEX, email):
            raise InvalidEmailError(self.email)
        self.email = email
        