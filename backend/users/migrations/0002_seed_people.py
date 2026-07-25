from datetime import date

from django.db import migrations

PEOPLE = [
    ('Ana', 'Torres', 'ana.torres@example.com', '+51 987 654 321', 'Peru', '1990-03-14'),
    ('Diego', 'Ramirez', 'diego.ramirez@example.com', '+52 55 1234 5678', 'Mexico', '1985-11-02'),
    ('Carla', 'Mendez', 'carla.mendez@example.com', '+57 310 555 0143', 'Colombia', '1993-07-21'),
    ('Javier', 'Soto', 'javier.soto@example.com', '+56 9 8765 4321', 'Chile', '1988-01-30'),
    ('Lucia', 'Fernandez', 'lucia.fernandez@example.com', '+34 612 345 678', 'Spain', '1996-05-09'),
    ('Mateo', 'Rojas', 'mateo.rojas@example.com', '+54 11 4321 8765', 'Argentina', '1991-09-17'),
    ('Valentina', 'Castro', 'valentina.castro@example.com', '+598 99 123 456', 'Uruguay', '1994-12-03'),
    ('Sebastian', 'Vargas', 'sebastian.vargas@example.com', '+591 7 123 4567', 'Bolivia', '1987-04-25'),
    ('Camila', 'Herrera', 'camila.herrera@example.com', '+593 99 876 5432', 'Ecuador', '1992-08-11'),
    ('Andres', 'Molina', 'andres.molina@example.com', '+507 6123 4567', 'Panama', '1989-02-18'),
    ('Emily', 'Carter', 'emily.carter@example.com', '+1 415 555 0198', 'United States', '1995-06-27'),
    ('James', 'Whitfield', 'james.whitfield@example.com', '+44 20 7946 0958', 'United Kingdom', '1983-10-05'),
    ('Sophie', 'Laurent', 'sophie.laurent@example.com', '+33 6 12 34 56 78', 'France', '1997-03-22'),
    ('Lukas', 'Bauer', 'lukas.bauer@example.com', '+49 151 2345 6789', 'Germany', '1990-11-14'),
    ('Giulia', 'Ricci', 'giulia.ricci@example.com', '+39 320 123 4567', 'Italy', '1993-01-08'),
    ('Pedro', 'Alves', 'pedro.alves@example.com', '+351 912 345 678', 'Portugal', '1986-07-19'),
    ('Marta', 'Nowak', 'marta.nowak@example.com', '+48 512 345 678', 'Poland', '1994-09-30'),
    ('Hiroshi', 'Tanaka', 'hiroshi.tanaka@example.com', '+81 90 1234 5678', 'Japan', '1982-05-12'),
    ('Priya', 'Nair', 'priya.nair@example.com', '+91 98765 43210', 'India', '1998-04-06'),
    ('Thabo', 'Mokoena', 'thabo.mokoena@example.com', '+27 82 123 4567', 'South Africa', '1991-12-24'),
]


def create_people(apps, schema_editor):
    Person = apps.get_model('users', 'Person')
    Person.objects.bulk_create(
        [
            Person(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                country=country,
                birth_date=date.fromisoformat(birth_date),
            )
            for first_name, last_name, email, phone, country, birth_date in PEOPLE
        ]
    )


def delete_people(apps, schema_editor):
    Person = apps.get_model('users', 'Person')
    Person.objects.filter(email__in=[row[2] for row in PEOPLE]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_people, delete_people),
    ]
