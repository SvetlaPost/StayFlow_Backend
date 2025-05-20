import factory
from factory.django import DjangoModelFactory
from faker import Faker

from apps.rent.models import Rent
from apps.rent.choices.room_type import RoomType


fake = Faker("en_US")


class RentHouseFactory(DjangoModelFactory):

    class Meta:
        model = Rent

    title = factory.LazyAttribute(lambda _: fake.sentence(nb_words=4))
    description = factory.LazyAttribute(lambda _: fake.paragraph(nb_sentences=3))
    address = factory.LazyAttribute(lambda _: fake.address())
    price = factory.LazyAttribute(lambda _: round(
        fake.pydecimal(
            left_digits=4,
            right_digits=2,
            positive=True
        ), 2
    ))
    rooms_count = factory.LazyAttribute(lambda _: fake.random_int(
        min=1,
        max=6
    ))
    room_type = factory.LazyAttribute(lambda _: fake.random_element(
        RoomType.faker_choices()
    ))


RentHouseFactory().create_batsh()