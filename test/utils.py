import pytest_asyncio
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from database import Base
from main import app
from fastapi.testclient import TestClient
from models import users, requests, ai_model
from routers.auth import get_db, get_current_user, bcrypt_context

SQL_ALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    SQL_ALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

AsyncTestingSessionLocal = async_sessionmaker(autoflush=False, autocommit=False, bind=engine)


class SenkronSessionTaklidi:
    def __init__(self):
        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

    def _run(self, coro):
        if self.loop.is_running():
            new_loop = asyncio.new_event_loop()
            try:
                return new_loop.run_until_complete(coro)
            finally:
                new_loop.close()
        else:
            return self.loop.run_until_complete(coro)

    def query(self, model):
        return QueryProxy(model, self)

    def add(self, instance):
        async def _add():
            async with AsyncTestingSessionLocal() as session:
                session.add(instance)
                await session.commit()
                await session.refresh(instance)

        self._run(_add())

    def commit(self):
        pass

    def delete(self, instance):
        async def _delete():
            async with AsyncTestingSessionLocal() as session:
                # Merge ederek session'a ekleyip siliyoruz
                merged = await session.merge(instance)
                await session.delete(merged)
                await session.commit()

        self._run(_delete())

    def close(self):
        pass


class QueryProxy:
    def __init__(self, model, session_proxy):
        self.model = model
        self.session_proxy = session_proxy
        self.filters = []

    def filter(self, *criterion):
        self.filters.extend(criterion)
        return self

    def first(self):
        from sqlalchemy import select
        async def _first():
            async with AsyncTestingSessionLocal() as session:
                stmt = select(self.model)
                for f in self.filters:
                    stmt = stmt.filter(f)
                res = await session.execute(stmt)
                return res.scalars().first()

        return self.session_proxy._run(_first())

    def all(self):
        from sqlalchemy import select
        async def _all():
            async with AsyncTestingSessionLocal() as session:
                stmt = select(self.model)
                for f in self.filters:
                    stmt = stmt.filter(f)
                res = await session.execute(stmt)
                return res.scalars().all()

        return self.session_proxy._run(_all())


def TestingSessionLocal():
    return SenkronSessionTaklidi()


client = TestClient(app)


def override_get_current_user():
    return {"userID": 1, "user_name": "Mike", "is_admin": True}


app.dependency_overrides[get_current_user] = override_get_current_user


@pytest_asyncio.fixture(autouse=True, scope="function")
async def setup_and_teardown_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_db():
        async with AsyncTestingSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture()
async def test_user():
    user = users(
        userID=1,
        user_name="Test User",
        first_name="Mike",
        last_name="Tylor",
        hashed_password=bcrypt_context.hash("test1234"),
        is_active=True,
        subscription=False,
    )
    async with AsyncTestingSessionLocal() as db:
        db.add(user)
        await db.commit()
        user = await db.merge(user)
    yield user


@pytest_asyncio.fixture()
async def test_request():
    async with AsyncTestingSessionLocal() as db:
        import models
        test_model = models.ai_model(modelID=1, model_name="GPT4.0")
        test_input = models.inputs(inputID=1, input_text="Input")
        test_output = models.outputs(outputID=1, output_text="Output")
        db.add(test_model)
        db.add(test_input)
        db.add(test_output)
        await db.flush()

        request = requests(
            requestID=1,
            userID=1,
            modelID=1,
            inputID=1,
            outputID=1
        )
        db.add(request)
        await db.commit()
        request = await db.merge(request)
    yield request


@pytest_asyncio.fixture()
async def test_request2():
    async with AsyncTestingSessionLocal() as db:
        import models
        test_model = models.ai_model(modelID=1, model_name="GPT4.0")
        test_input = models.inputs(inputID=1, input_text="Input")
        test_output = models.outputs(outputID=1, output_text="Output")
        db.add(test_model)
        db.add(test_input)
        db.add(test_output)
        await db.flush()

        request = requests(
            requestID=1,
            userID=2,
            modelID=1,
            inputID=1,
            outputID=1
        )
        db.add(request)
        await db.commit()
        request = await db.merge(request)
    yield request


@pytest_asyncio.fixture()
async def test_ai_model():
    model = ai_model(
        modelID=1,
        model_name="GPT4.0"
    )
    async with AsyncTestingSessionLocal() as db:
        db.add(model)
        await db.commit()
        model = await db.merge(model)
    yield model