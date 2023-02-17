import hashlib
from dataclasses import dataclass
from hashlib import sha256
from typing import Optional

import aiohttp_session


@dataclass
class Admin:
    id: int
    email: str
    password: Optional[str] = None
    session: Optional[aiohttp_session.Session] = None
