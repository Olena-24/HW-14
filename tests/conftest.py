import asyncio
import contextlib
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine

from main import app
from src.entity.models import Base, User
from src.database.db import get_db
from src.services.auth import auth_service

DB_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    DB_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)

TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)

test_user = {"username": "deadpool", "email": "deadpool@example.com", "password": "12345678"}


@pytest.fixture(scope="module", autouse=True)
def init_models_wrap():
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            hash_password = auth_service.get_password_hash(test_user["password"])
            current_user = User(username=test_user["username"], email=test_user["email"], password=hash_password,
                                confirmed=True, role="admin")
            session.add(current_user)
            await session.commit()

    asyncio.run(init_models())


"""@pytest.fixture(scope="module")
def client():
    # Dependency override

    @contextlib.asynccontextmanager
    async def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        except Exception as err:
            print(err)
            await session.rollback()
        finally:
            await session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

"""
@pytest_asyncio.fixture()
async def get_token():
    token = await auth_service.create_access_token(data={"sub": test_user["email"]})
    return token

class DatabaseSessionManager:
    def __init__(self, url: str):
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(autoflush=False, autocommit=False,
                                                                     bind=self._engine)

    @contextlib.asynccontextmanager
    async def session(self):
        if self._session_maker is None:
            raise Exception("Session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except:
            await session.rollback()
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(DB_URL)

@pytest.fixture(scope="module")
def client():
    # Dependency override

    async def override_get_db():
        async with sessionmanager.session() as session:
            return session 

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)
    
