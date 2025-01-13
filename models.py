from peewee import (
    CharField,
    IntegerField,
    Model,
    SqliteDatabase, ForeignKeyField, TextField
)

from settings import DB_PATH

db = SqliteDatabase(DB_PATH)


class BaseModel(Model):
    """
    Базовый Класс
    """
    class Meta:
        database = db


class User(BaseModel):
    """
    Класс. Описывает пользователя. Наследуется от базового класса
    :return: None
    """
    user_id: int = IntegerField(primary_key=True)
    username: str = CharField(null=True)


class Bio(BaseModel):
    """
    Класс. Описывает данные пользователя. Наследуется от базового класса
    :return: None
    """
    id: int = IntegerField(primary_key=True)
    user = ForeignKeyField(User, backref="bio")
    name: str = CharField(null=True)
    category: int = CharField(null=True)
    phone: str = CharField(null=True)
    about: str = TextField(null=True)
    instagram: str = CharField(null=True)
    tiktok: str = CharField(null=True)
    portfolio: str = CharField(null=True)


def create_models() -> None:
    """
    Функция. Создает все модели.
    :return: None
    """
    db.create_tables(BaseModel.__subclasses__())
