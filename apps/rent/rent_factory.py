import factory
from factory.django import DjangoModelFactory
from faker import Faker
from random import choice, uniform
from decimal import Decimal

from apps.rent.models import Rent
from apps.location.models import Location
from apps.users.models import User
from apps.rent.choices.room_type import RoomType

fake = Faker("en_US")


class RentFactory(DjangoModelFactory):
    class Meta:
        model = Rent

    title = factory.LazyAttribute(lambda _: fake.sentence(nb_words=4))
    description = factory.LazyAttribute(lambda _: fake.paragraph(nb_sentences=3))
    rooms = factory.LazyAttribute(lambda _: fake.random_int(min=1, max=5))
    property_type = factory.LazyAttribute(lambda _: choice([rt.name for rt in RoomType]))

    is_active = True
    is_deleted = False

    is_daily_available = True
    daily_price = factory.LazyAttribute(lambda _: Decimal(f"{uniform(25, 100):.2f}"))

    is_monthly_available = True
    monthly_price = factory.LazyAttribute(lambda _: Decimal(f"{uniform(800, 3000):.2f}"))

    owner = factory.Iterator(User.objects.filter(is_host=True))
    location = factory.Iterator(Location.objects.all())
