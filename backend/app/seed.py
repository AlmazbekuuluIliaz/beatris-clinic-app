from datetime import date, datetime, time
from decimal import Decimal

from app import models
from app.core.database import SessionLocal
from app.core.security import get_password_hash

# Temporary development seed. SQL_Beatrice_simple.sql defines the schema only
# and does not contain INSERT data, so these rows are sample records for local
# API testing until real clinic data is provided.


def seed() -> None:
    db = SessionLocal()
    try:
        db.merge(
            models.ClinicInfo(
                id="0db33154-9a88-41c3-91de-dc24cc2a4f18",
                name="Beatris",
                description="Медицинский центр эстетической медицины",
                address="Казахстан, г. Атырау, ул. Абая, 10",
                phone="+77001234567",
                whatsapp="+77001234567",
                instagram="https://instagram.com/beatris",
                working_hours="Пн-Сб 09:00-20:00",
                map_url="https://maps.example.com/beatris",
            )
        )

        db.merge(
            models.User(
                id="b6eb7f36-8f3c-45ea-8ce6-64781f6b6c24",
                full_name="Admin Beatris",
                phone="+77000000000",
                email="admin@beatris.kz",
                password_hash=get_password_hash("admin12345"),
                role=models.UserRole.ADMIN,
            )
        )

        users = [
            models.User(
                id="cf3f6a43-98d4-47f1-bb0b-112b7c76e524",
                full_name="Ильяз",
                phone="+79774669995",
                email="almazbek-03@mail.ru",
                password_hash="pbkdf2_sha256$260000$qdM3AkpRdY7CfvxEqtVuHw$PnuMTgvrIQgbL-qY_8ga2YAMNOvlU9cQnKDP87PpLWc",
                role=models.UserRole.ADMIN,
            ),
            models.User(
                id="1eac5c6a-33a9-4219-ba5d-6356473296d8",
                full_name="Феликс",
                phone="+79944078944",
                email="felix@gmail.com",
                password_hash="pbkdf2_sha256$260000$69g0_O3N4RXlX3uYOi-XlQ$6VAxtmSmaPSAEHHxHwvn7DZIR5RX3B3aVtN4und9EWY",
                role=models.UserRole.ADMIN,
            ),
            models.User(
                id="b291f12e-f3f3-4aef-a747-40cdd927f9fa",
                full_name="Айжан Сериккызы Нуртаева",
                phone="/",
                email="aizhan@gmail.com",
                password_hash="pbkdf2_sha256$260000$98ZahQ969jW4Z0xHDksiJg$tFPl4sATsFajdT688z6z9Sc0MV3cuBbdRdwtpCH5Hn8",
                role=models.UserRole.DOCTOR,
            ),
            models.User(
                id="f6cc3054-49af-4e95-aa86-38f541ce05fa",
                full_name="Динара Ерлановна Сагинтаева",
                phone="\\",
                email="dinara@gmail.com",
                password_hash="pbkdf2_sha256$260000$r6qW6Bi90k5p8SST-F0LtQ$s0tPBS8veotd4maJ6fAafq19Ks_KKi5Lz-ITiHYyfpg",
                role=models.UserRole.DOCTOR,
            ),
            models.User(
                id="1afd7d40-3786-48ce-8900-15270dc3c62f",
                full_name="Мария Игоревна Ким",
                phone="|",
                email="mkim@gmail.com",
                password_hash="pbkdf2_sha256$260000$_WoWN16NBOV3TT7lLBftWg$RNMx04d7CzDUdhnJGzFnbjKwmzl33Pp3_6X8RktzTuw",
                role=models.UserRole.DOCTOR,
            ),
            models.User(
                id="de6f9708-19c5-45f3-909a-9d0837266d87",
                full_name="Соколова Юлия Андреевна",
                phone="=",
                email="sokolova@yandex.ru",
                password_hash="pbkdf2_sha256$260000$08yk3Ym5EJZuvC8MJa99JQ$FrQEMKmnnnpi_wSWvY5fNMPYnxe2ItyuQRdKZhH6hbc",
                role=models.UserRole.DOCTOR,
            ),
            models.User(
                id="738a18ff-8f3b-424f-92cb-546cf609339b",
                full_name="Иванова Анна Сергеевна",
                phone="-",
                email="ivanova@yandex.ru",
                password_hash="pbkdf2_sha256$260000$Zy9BCHCX_fXUi2ftzCKuzg$X1LTi_ABVjqb0CX7kcZEBQy5iQCr8fj9RHiViEtMRMA",
                role=models.UserRole.DOCTOR,
            ),
            models.User(
                id="df6a14ad-5e11-45c4-ae80-d7ffb6b7d8c8",
                full_name="Омарова Динара Муратовна",
                phone="+",
                email="omarova@bk.ru",
                password_hash="pbkdf2_sha256$260000$86aC8CDpVbVdTjfBfqpObg$PJWa8NeXSx55zae1rrEcERBqg5WraAER97R6E75Y3II",
                role=models.UserRole.DOCTOR,
            ),
            models.User(
                id="68ea2a8a-9f06-4883-8af2-a8fb3a59893d",
                full_name="Test Doctor",
                phone="+77000000111",
                email=None,
                password_hash="pbkdf2_sha256$260000$vujsdzl7xpPns7cTRA-O0A$7ymiptV-PquZdA9JAVgVpFL6ZGKhhcjPZfwNVeoTcgQ",
                role=models.UserRole.DOCTOR,
            ),
            models.User(
                id="2283e677-f1e3-4fe3-9bdc-185018d26b30",
                full_name="Test Patient",
                phone="+79000000000",
                email=None,
                password_hash="pbkdf2_sha256$260000$TcHxO_4UK-0JGc1SplDuag$4Pyzh7mbZJpGCTufUrk5yS8ZbizDNhyfCg4kjCL2x14",
                role=models.UserRole.PATIENT,
            ),
        ]
        for user in users:
            db.merge(user)

        categories = [
            models.ServiceCategory(
                id="2c0b07ae-4b62-4c5f-b4bc-4edb886725e2",
                title="Инъекционная косметология",
                slug="injection-cosmetology",
                description=(
                    "Контурная пластика, биоревитализация, мезотерапия и "
                    "ботулинотерапия — инъекционные методики для увлажнения, "
                    "омоложения и коррекции возрастных изменений кожи."
                ),
                image_url="/uploads/categories/injection-cosmetology.jpg",
                sort_order=1,
            ),
            models.ServiceCategory(
                id="3f690fe9-c4b0-4cc1-8b10-645ed042fb8d",
                title="Аппаратная косметология",
                slug="hardware-cosmetology",
                description=(
                    "Безоперационные процедуры на современном оборудовании: "
                    "лазерные методики, SMAS- и RF-лифтинг, фотоомоложение для "
                    "подтяжки, обновления и оздоровления кожи."
                ),
                image_url="/uploads/categories/hardware-cosmetology.jpg",
                sort_order=2,
            ),
            models.ServiceCategory(
                id="df9bfa66-ec18-40d7-b7ee-d716862d86d4",
                title="Эстетическая косметология",
                slug="aesthetic-cosmetology",
                description=(
                    "Чистки, пилинги, уходовые программы и массаж лица — "
                    "базовый уход за кожей для чистоты, тонуса и здорового "
                    "сияния."
                ),
                image_url="/uploads/categories/aesthetic-cosmetology.jpg",
                sort_order=3,
            ),
            models.ServiceCategory(
                id="163ba87d-1b0e-45de-bd09-c35b27e142a9",
                title="Трихология",
                slug="trihologiya",
                description=(
                    "Диагностика и лечение волос и кожи головы: борьба с "
                    "выпадением, перхотью и нарушениями роста волос под "
                    "контролем врача-трихолога."
                ),
                image_url="/uploads/categories/trihologiya.jpg",
                sort_order=4,
            ),
            models.ServiceCategory(
                id="7e9c1a2b-4d3f-4a6b-8c1d-2e3f4a5b6c7d",
                title="Пластическая хирургия",
                slug="plastic-surgery",
                description=(
                    "Хирургическая коррекция черт лица и контуров тела: "
                    "консультации и операции, которые проводят "
                    "сертифицированные пластические хирурги."
                ),
                image_url="/uploads/categories/plastic-surgery.jpg",
                sort_order=5,
            ),
            models.ServiceCategory(
                id="1f2e3d4c-5b6a-4798-9a0b-1c2d3e4f5a6b",
                title="Консультации специалистов",
                slug="specialist-consultations",
                description=(
                    "Первичный приём косметолога, дерматолога и трихолога: "
                    "осмотр, индивидуальный подбор процедур и составление "
                    "плана лечения."
                ),
                image_url="/uploads/categories/specialist-consultations.jpg",
                sort_order=6,
            ),
        ]
        for category in categories:
            db.merge(category)

        services = [
            models.Service(
                id="661b9091-86a4-4512-aa0d-162c8d0c2db0",
                category_id="2c0b07ae-4b62-4c5f-b4bc-4edb886725e2",
                title="Биоревитализация",
                slug="biorevitalizatsiya",
                description="Инъекционная процедура для увлажнения и восстановления кожи",
                price=Decimal("25000.00"),
                duration_minutes=60,
                image_url="/uploads/services/biorevitalizatsiya.jpg",
                contraindications="Беременность, воспалительные процессы, индивидуальные противопоказания",
                is_active=True,
            ),
            models.Service(
                id="6a070d8b-b2fa-4207-bab5-df716983ef74",
                category_id="2c0b07ae-4b62-4c5f-b4bc-4edb886725e2",
                title="Мезотерапия",
                slug="mezoterapiya",
                description=(
                    "Инъекционная косметологическая процедура, при которой в "
                    "средние слои кожи вводятся индивидуально подобранные "
                    "«мезококтейли» из витаминов, аминокислот, пептидов и "
                    "гиалуроновой кислоты."
                ),
                price=Decimal("15000.00"),
                duration_minutes=50,
                image_url="/uploads/services/mezoterapiya.jpg",
                contraindications=(
                    "Беременность и лактация, воспалительные и инфекционные "
                    "процессы кожи в зоне инъекции, нарушения свёртываемости "
                    "крови, аллергия на компоненты коктейля, обострение "
                    "хронических заболеваний, онкологические заболевания."
                ),
                is_active=True,
            ),
            models.Service(
                id="bd584505-14aa-4f7a-974f-b23e88cb65c5",
                category_id="2c0b07ae-4b62-4c5f-b4bc-4edb886725e2",
                title="Ботулинотерапия",
                slug="botulinoterapiya",
                description=(
                    "Инъекционная методика, направленная на коррекцию "
                    "мимических морщин и предотвращение их углубления."
                ),
                price=Decimal("20000.00"),
                duration_minutes=30,
                image_url="/uploads/services/botulinoterapiya.jpg",
                contraindications=(
                    "Беременность и лактация, миастения и нервно-мышечные "
                    "заболевания, воспаления и повреждения кожи в зоне "
                    "инъекции, нарушения свёртываемости крови, приём "
                    "антикоагулянтов, индивидуальная непереносимость "
                    "препарата, онкологические заболевания."
                ),
                is_active=True,
            ),
            models.Service(
                id="c3d4e5f6-3333-4c4d-8e5f-3a4b5c6d7e8f",
                category_id="7e9c1a2b-4d3f-4a6b-8c1d-2e3f4a5b6c7d",
                title="Контурная пластика",
                slug="konturnaya-plastika",
                description=(
                    "Инъекционное введение филлеров на основе гиалуроновой "
                    "кислоты для восполнения объёма, коррекции формы губ и "
                    "скул и разглаживания глубоких складок. Стоимость зависит "
                    "от препарата и объёма (за 1 мл)."
                ),
                price=Decimal("60000.00"),
                duration_minutes=60,
                image_url="/uploads/services/konturnaya-plastika.jpg",
                contraindications=(
                    "Беременность и лактация, воспаления и повреждения кожи в "
                    "зоне коррекции, склонность к келоидным рубцам, нарушения "
                    "свёртываемости крови, аутоиммунные заболевания, "
                    "индивидуальная непереносимость гиалуроновой кислоты, "
                    "онкологические заболевания."
                ),
                is_active=True,
            ),
            models.Service(
                id="d4e5f6a7-4444-4d5e-9f6a-4b5c6d7e8f90",
                category_id="2c0b07ae-4b62-4c5f-b4bc-4edb886725e2",
                title="Плазмолифтинг",
                slug="plazmolifting",
                description=(
                    "Инъекции собственной обогащённой тромбоцитами плазмы "
                    "пациента для стимуляции регенерации, улучшения тонуса и "
                    "цвета кожи."
                ),
                price=Decimal("22000.00"),
                duration_minutes=45,
                image_url="/uploads/services/plazmolifting.jpg",
                contraindications=(
                    "Беременность и лактация, заболевания крови и нарушения "
                    "свёртываемости, острые инфекционные и воспалительные "
                    "процессы, приём антикоагулянтов, аутоиммунные и "
                    "онкологические заболевания."
                ),
                is_active=True,
            ),
            models.Service(
                id="e5f6a7b8-5555-4e6f-8a7b-5c6d7e8f9012",
                category_id="2c0b07ae-4b62-4c5f-b4bc-4edb886725e2",
                title="Биоармирование",
                slug="bioarmirovanie",
                description=(
                    "Создание поддерживающего каркаса в коже введением "
                    "гиалуроновой кислоты по специальным линиям для лифтинга "
                    "и профилактики возрастного птоза."
                ),
                price=Decimal("50000.00"),
                duration_minutes=60,
                image_url="/uploads/services/bioarmirovanie.jpg",
                contraindications=(
                    "Беременность и лактация, воспаления и повреждения кожи в "
                    "зоне процедуры, нарушения свёртываемости крови, "
                    "склонность к келоидным рубцам, индивидуальная "
                    "непереносимость препарата, онкологические заболевания."
                ),
                is_active=True,
            ),
            models.Service(
                id="f6a7b8c9-6666-4f70-9b8c-6d7e8f901234",
                category_id="2c0b07ae-4b62-4c5f-b4bc-4edb886725e2",
                title="Липолитики",
                slug="lipolitiki",
                description=(
                    "Инъекции липолитических препаратов для коррекции "
                    "локальных жировых отложений и моделирования контуров "
                    "лица и тела. Стоимость зависит от зоны и количества "
                    "процедур."
                ),
                price=Decimal("16000.00"),
                duration_minutes=40,
                image_url="/uploads/services/lipolitiki.jpg",
                contraindications=(
                    "Беременность и лактация, нарушения свёртываемости крови, "
                    "заболевания печени и почек, желчнокаменная болезнь, "
                    "аутоиммунные и онкологические заболевания, "
                    "индивидуальная непереносимость."
                ),
                is_active=True,
            ),
            models.Service(
                id="a1c2e3f4-1212-4abc-8def-111213141516",
                category_id="2c0b07ae-4b62-4c5f-b4bc-4edb886725e2",
                title="Коллагеностимуляция",
                slug="kollagenostimulyaciya",
                description=(
                    "Инъекционное введение препаратов-стимуляторов (на основе "
                    "полимолочной кислоты или гидроксиапатита кальция), которые "
                    "запускают выработку собственного коллагена и повышают "
                    "плотность и упругость кожи."
                ),
                price=Decimal("45000.00"),
                duration_minutes=60,
                image_url="/uploads/services/kollagenostimulyaciya.jpg",
                contraindications=(
                    "Беременность и лактация, воспаления и повреждения кожи в "
                    "зоне инъекции, склонность к келоидным рубцам, аутоиммунные "
                    "заболевания, нарушения свёртываемости крови, "
                    "онкологические заболевания, индивидуальная непереносимость "
                    "препарата."
                ),
                is_active=True,
            ),
            models.Service(
                id="c3e4a5b6-1414-4cde-8f01-313233343536",
                category_id="2c0b07ae-4b62-4c5f-b4bc-4edb886725e2",
                title="PRP-плазмотерапия",
                slug="prp-plazmoterapiya",
                description=(
                    "Процедура по технологии PRP (Platelet-Rich Plasma): "
                    "введение концентрированной обогащённой тромбоцитами плазмы "
                    "для активации обновления тканей и восстановления кожи."
                ),
                price=Decimal("25000.00"),
                duration_minutes=50,
                image_url="/uploads/services/prp-plazmoterapiya.jpg",
                contraindications=(
                    "Беременность и лактация, заболевания крови и нарушения "
                    "свёртываемости, острые инфекционные и воспалительные "
                    "процессы, приём антикоагулянтов, аутоиммунные и "
                    "онкологические заболевания."
                ),
                is_active=True,
            ),
            models.Service(
                id="cfb67935-1d0e-4f75-b78e-b1a96f7bcf5c",
                category_id="3f690fe9-c4b0-4cc1-8b10-645ed042fb8d",
                title="SMAS-лифтинг",
                slug="smas-lifting",
                description="Аппаратная методика безоперационной подтяжки кожи",
                price=Decimal("45000.00"),
                duration_minutes=90,
                image_url="/uploads/services/smas-lifting.jpg",
                contraindications="Беременность, кардиостимулятор, острые воспаления",
                is_active=True,
            ),
            models.Service(
                id="a7b8c9d0-7777-4071-8c9d-7e8f90123456",
                category_id="3f690fe9-c4b0-4cc1-8b10-645ed042fb8d",
                title="RF-лифтинг",
                slug="rf-lifting",
                description=(
                    "Радиочастотное воздействие прогревает глубокие слои "
                    "кожи, стимулирует выработку коллагена и обеспечивает "
                    "безоперационную подтяжку и уплотнение кожи."
                ),
                price=Decimal("30000.00"),
                duration_minutes=60,
                image_url="/uploads/services/rf-lifting.jpg",
                contraindications=(
                    "Беременность и лактация, кардиостимулятор и "
                    "металлические импланты в зоне воздействия, "
                    "онкологические заболевания, острые воспалительные "
                    "процессы и повреждения кожи, повышенная температура тела."
                ),
                is_active=True,
            ),
            models.Service(
                id="b8c9d0e1-8888-4182-9d0e-8f9012345678",
                category_id="3f690fe9-c4b0-4cc1-8b10-645ed042fb8d",
                title="Лазерное омоложение",
                slug="lazernoe-omolozhenie",
                description=(
                    "Лазерное воздействие для обновления кожи, разглаживания "
                    "мелких морщин, выравнивания тона и рельефа и сокращения "
                    "следов постакне."
                ),
                price=Decimal("35000.00"),
                duration_minutes=60,
                image_url="/uploads/services/lazernoe-omolozhenie.jpg",
                contraindications=(
                    "Беременность и лактация, свежий загар, онкологические "
                    "заболевания, фотодерматозы и приём фотосенсибилизирующих "
                    "препаратов, острые воспаления и повреждения кожи, "
                    "склонность к келоидным рубцам."
                ),
                is_active=True,
            ),
            models.Service(
                id="c9d0e1f2-9999-4293-8e1f-901234567890",
                category_id="3f690fe9-c4b0-4cc1-8b10-645ed042fb8d",
                title="Фотоомоложение",
                slug="fotoomolozhenie",
                description=(
                    "Воздействие широкополосным импульсным светом (IPL) для "
                    "устранения пигментации и сосудистых звёздочек, "
                    "выравнивания цвета и повышения тонуса кожи."
                ),
                price=Decimal("25000.00"),
                duration_minutes=45,
                image_url="/uploads/services/fotoomolozhenie.jpg",
                contraindications=(
                    "Беременность и лактация, свежий загар, фотодерматозы и "
                    "приём фотосенсибилизирующих препаратов, онкологические "
                    "заболевания, острые воспаления кожи в зоне воздействия."
                ),
                is_active=True,
            ),
            models.Service(
                id="d0e1f2a3-aaaa-43a4-9f20-012345678901",
                category_id="163ba87d-1b0e-45de-bd09-c35b27e142a9",
                title="Лазерная эпиляция",
                slug="lazernaya-epilyatsiya",
                description=(
                    "Удаление нежелательных волос лазером за счёт разрушения "
                    "волосяных фолликулов. Стоимость зависит от обрабатываемой "
                    "зоны."
                ),
                price=Decimal("8000.00"),
                duration_minutes=30,
                image_url="/uploads/services/lazernaya-epilyatsiya.jpg",
                contraindications=(
                    "Беременность и лактация, свежий загар, онкологические "
                    "заболевания, фотодерматозы и приём фотосенсибилизирующих "
                    "препаратов, воспаления и повреждения кожи в зоне "
                    "эпиляции, сахарный диабет в стадии декомпенсации."
                ),
                is_active=True,
            ),
            models.Service(
                id="e1f2a3b4-bbbb-44b5-8a31-123456789012",
                category_id="3f690fe9-c4b0-4cc1-8b10-645ed042fb8d",
                title="Микротоковая терапия",
                slug="mikrotokovaya-terapiya",
                description=(
                    "Воздействие слабыми импульсными токами для лимфодренажа, "
                    "повышения тонуса кожи и мышц, уменьшения отёчности и "
                    "улучшения микроциркуляции."
                ),
                price=Decimal("12000.00"),
                duration_minutes=40,
                image_url="/uploads/services/mikrotokovaya-terapiya.jpg",
                contraindications=(
                    "Беременность, кардиостимулятор и нарушения сердечного "
                    "ритма, онкологические заболевания, эпилепсия, "
                    "индивидуальная непереносимость тока, повреждения кожи в "
                    "зоне воздействия."
                ),
                is_active=True,
            ),
            models.Service(
                id="d4f5a6b7-1515-4def-9012-414243444546",
                category_id="3f690fe9-c4b0-4cc1-8b10-645ed042fb8d",
                title="LPG-массаж",
                slug="lpg-massazh",
                description=(
                    "Аппаратный вакуумно-роликовый массаж (LPG) для коррекции "
                    "фигуры, уменьшения проявлений целлюлита, улучшения "
                    "лимфодренажа, тонуса и упругости кожи."
                ),
                price=Decimal("10000.00"),
                duration_minutes=45,
                image_url="/uploads/services/lpg-massazh.jpg",
                contraindications=(
                    "Беременность и лактация, варикозная болезнь в зоне "
                    "воздействия, нарушения свёртываемости крови, острые "
                    "воспалительные и инфекционные процессы, грыжи в зоне "
                    "воздействия, онкологические заболевания, повреждения кожи."
                ),
                is_active=True,
            ),
            models.Service(
                id="3b874a33-0844-452c-960a-8ecb5ccbd7f2",
                category_id="df9bfa66-ec18-40d7-b7ee-d716862d86d4",
                title="Комбинированная чистка лица",
                slug="kombinirovannaya-chistka-lica",
                description=(
                    "Комплексное очищение кожи лица: распаривание, "
                    "ультразвуковая и механическая чистка, удаление "
                    "загрязнений и комедонов с последующим успокаивающим "
                    "уходом и маской."
                ),
                price=Decimal("15000.00"),
                duration_minutes=60,
                image_url="/uploads/services/chistka-lica.jpg",
                contraindications=(
                    "Острые воспалительные и гнойничковые процессы кожи, "
                    "герпес в стадии обострения, свежие повреждения и травмы "
                    "кожи, тяжёлый купероз, индивидуальная непереносимость "
                    "используемых средств."
                ),
                is_active=True,
            ),
            models.Service(
                id="f2a3b4c5-cccc-4506-9b42-234567890123",
                category_id="df9bfa66-ec18-40d7-b7ee-d716862d86d4",
                title="Химический пилинг",
                slug="himicheskiy-piling",
                description=(
                    "Контролируемое нанесение кислотных составов для "
                    "отшелушивания ороговевшего слоя, выравнивания тона и "
                    "рельефа кожи, сокращения пигментации и следов постакне."
                ),
                price=Decimal("12000.00"),
                duration_minutes=45,
                image_url="/uploads/services/himicheskiy-piling.jpg",
                contraindications=(
                    "Беременность и лактация, свежий загар, активные "
                    "воспаления и герпес в стадии обострения, повреждения "
                    "кожи, индивидуальная непереносимость кислот, "
                    "онкологические заболевания."
                ),
                is_active=True,
            ),
            models.Service(
                id="a3b4c5d6-dddd-4617-8c53-345678901234",
                category_id="df9bfa66-ec18-40d7-b7ee-d716862d86d4",
                title="Уходовая программа для лица",
                slug="uhodovaya-programma-dlya-lica",
                description=(
                    "Комплексный уход за кожей лица с очищением, увлажнением "
                    "и питанием, подобранный индивидуально под тип и состояние "
                    "кожи."
                ),
                price=Decimal("10000.00"),
                duration_minutes=60,
                image_url="/uploads/services/uhodovaya-programma-dlya-lica.jpg",
                contraindications=(
                    "Острые воспалительные процессы и повреждения кожи, "
                    "индивидуальная непереносимость компонентов средств."
                ),
                is_active=True,
            ),
            models.Service(
                id="b4c5d6e7-eeee-4728-9d64-456789012345",
                category_id="df9bfa66-ec18-40d7-b7ee-d716862d86d4",
                title="Альгинатная маска",
                slug="alginatnaya-maska",
                description=(
                    "Пластифицирующая маска на основе альгинатов для "
                    "увлажнения, повышения тонуса и улучшения цвета кожи; "
                    "часто завершает уходовые процедуры."
                ),
                price=Decimal("5000.00"),
                duration_minutes=30,
                image_url="/uploads/services/alginatnaya-maska.jpg",
                contraindications=(
                    "Индивидуальная непереносимость компонентов, повреждения "
                    "и острые воспаления кожи в зоне нанесения."
                ),
                is_active=True,
            ),
            models.Service(
                id="c5d6e7f8-ffff-4839-8e75-567890123456",
                category_id="df9bfa66-ec18-40d7-b7ee-d716862d86d4",
                title="Массаж лица",
                slug="massazh-lica",
                description=(
                    "Ручной массаж лица для улучшения микроциркуляции, "
                    "повышения тонуса мышц и кожи, уменьшения отёчности и "
                    "расслабления."
                ),
                price=Decimal("7000.00"),
                duration_minutes=45,
                image_url="/uploads/services/massazh-lica.jpg",
                contraindications=(
                    "Острые воспалительные и гнойничковые процессы кожи, "
                    "герпес в стадии обострения, повреждения кожи, "
                    "онкологические заболевания, повышенная температура тела."
                ),
                is_active=True,
            ),
            models.Service(
                id="d6e7f8a9-0a0a-494a-9f86-678901234567",
                category_id="df9bfa66-ec18-40d7-b7ee-d716862d86d4",
                title="Карбокситерапия",
                slug="karboksiterapiya",
                description=(
                    "Неинвазивная карбокситерапия — нанесение составов, "
                    "насыщающих кожу углекислым газом, для активизации "
                    "кровообращения, насыщения тканей кислородом и улучшения "
                    "тонуса и цвета лица."
                ),
                price=Decimal("9000.00"),
                duration_minutes=40,
                image_url="/uploads/services/karboksiterapiya.jpg",
                contraindications=(
                    "Беременность и лактация, острые воспаления и повреждения "
                    "кожи, индивидуальная непереносимость компонентов, "
                    "тяжёлые заболевания дыхательной и сердечно-сосудистой "
                    "систем."
                ),
                is_active=True,
            ),
        ]
        for service in services:
            db.merge(service)

        product_categories = [
            models.ProductCategory(
                id="7db385db-1164-41d3-935b-4137a95afde6",
                title="Косметическая продукция",
                slug="kosmeticheskaya-produkciya",
            ),
        ]
        for product_category in product_categories:
            db.merge(product_category)

        specialists = [
            models.Specialist(
                id="4bd38fe7-6d07-43c6-81c1-47e7e1279356",
                full_name="Иванова Анна Сергеевна",
                position="Врач-косметолог",
                specialization="Инъекционная косметология",
                experience_years=8,
                photo_url="/uploads/specialists/ivanova.jpg",
                is_active=True,
            ),
            models.Specialist(
                id="fc108ab7-29b8-4cb0-89bf-e522408594c0",
                full_name="Омарова Динара Муратовна",
                position="Дерматолог",
                specialization="Аппаратная косметология",
                experience_years=7,
                photo_url="/uploads/specialists/omarova.jpg",
                is_active=True,
            ),
            models.Specialist(
                id="fde77300-d61d-4ad0-958e-1ddc7d7726ca",
                user_id="b291f12e-f3f3-4aef-a747-40cdd927f9fa",
                full_name="Айжан Сериккызы Нуртаева",
                position="Врач-косметолог",
                specialization="Аппаратная косметология",
                experience_years=5,
                photo_url="/uploads/specialists/aizhan.png",
                is_active=True,
            ),
            models.Specialist(
                id="0632b426-905f-4ee1-8bfb-520c44eb5500",
                user_id="f6cc3054-49af-4e95-aa86-38f541ce05fa",
                full_name="Динара Ерлановна Сагинтаева",
                position="Косметолог-эстетист",
                specialization="Эстетическая косметология",
                experience_years=3,
                photo_url="/uploads/specialists/dinara.png",
                is_active=True,
            ),
            models.Specialist(
                id="2eb96bf9-61b9-4a59-8f93-b671d9ff1fb4",
                user_id="1afd7d40-3786-48ce-8900-15270dc3c62f",
                full_name="Мария Игоревна Ким",
                position="Врач-дерматолог",
                specialization="Аппаратная косметология",
                experience_years=9,
                photo_url="/uploads/specialists/maria.png",
                is_active=True,
            ),
            models.Specialist(
                id="3cf1afdc-08ad-42c0-a4e1-2624752a837d",
                user_id="de6f9708-19c5-45f3-909a-9d0837266d87",
                full_name="Соколова Юлия Андреевна",
                position="Врач-дерматолог",
                specialization="Аппаратная косметология",
                experience_years=5,
                photo_url="/uploads/specialists/sokolova.jpg",
                is_active=True,
            ),
        ]
        for specialist in specialists:
            db.merge(specialist)

        specialist_services = [
            ("4bd38fe7-6d07-43c6-81c1-47e7e1279356", "661b9091-86a4-4512-aa0d-162c8d0c2db0"),
            ("4bd38fe7-6d07-43c6-81c1-47e7e1279356", "3b874a33-0844-452c-960a-8ecb5ccbd7f2"),
            ("fc108ab7-29b8-4cb0-89bf-e522408594c0", "cfb67935-1d0e-4f75-b78e-b1a96f7bcf5c"),
            ("fc108ab7-29b8-4cb0-89bf-e522408594c0", "3b874a33-0844-452c-960a-8ecb5ccbd7f2"),
            ("0632b426-905f-4ee1-8bfb-520c44eb5500", "a3b4c5d6-dddd-4617-8c53-345678901234"),
            ("fde77300-d61d-4ad0-958e-1ddc7d7726ca", "a7b8c9d0-7777-4071-8c9d-7e8f90123456"),
            ("fde77300-d61d-4ad0-958e-1ddc7d7726ca", "b8c9d0e1-8888-4182-9d0e-8f9012345678"),
            ("2eb96bf9-61b9-4a59-8f93-b671d9ff1fb4", "c9d0e1f2-9999-4293-8e1f-901234567890"),
            ("3cf1afdc-08ad-42c0-a4e1-2624752a837d", "cfb67935-1d0e-4f75-b78e-b1a96f7bcf5c"),
            ("2eb96bf9-61b9-4a59-8f93-b671d9ff1fb4", "e1f2a3b4-bbbb-44b5-8a31-123456789012"),
        ]
        for specialist_id, service_id in specialist_services:
            db.merge(models.SpecialistService(specialist_id=specialist_id, service_id=service_id))

        schedules = [
            models.DoctorSchedule(
                id="2987c34e-8b39-498a-b847-cc58ea412001",
                specialist_id="4bd38fe7-6d07-43c6-81c1-47e7e1279356",
                schedule_date=date(2026, 5, 20),
                start_time=time(9, 0),
                end_time=time(15, 0),
                is_available=True,
            ),
            models.DoctorSchedule(
                id="2987c34e-8b39-498a-b847-cc58ea412002",
                specialist_id="fc108ab7-29b8-4cb0-89bf-e522408594c0",
                schedule_date=date(2026, 5, 20),
                start_time=time(10, 0),
                end_time=time(18, 0),
                is_available=True,
            ),
            models.DoctorSchedule(
                id="44dd2a34-dddf-4326-89f9-6efb8492b222",
                specialist_id="4bd38fe7-6d07-43c6-81c1-47e7e1279356",
                schedule_date=date(2026, 5, 26),
                start_time=time(14, 0),
                end_time=time(16, 0),
                is_available=True,
            ),
            models.DoctorSchedule(
                id="4ae16b65-958c-4888-b30d-6d5766c5c1a9",
                specialist_id="4bd38fe7-6d07-43c6-81c1-47e7e1279356",
                schedule_date=date(2026, 5, 27),
                start_time=time(12, 0),
                end_time=time(16, 0),
                is_available=True,
            ),
            models.DoctorSchedule(
                id="492d51f0-3619-4eb5-b481-959141503316",
                specialist_id="fc108ab7-29b8-4cb0-89bf-e522408594c0",
                schedule_date=date(2026, 5, 27),
                start_time=time(12, 22),
                end_time=time(17, 22),
                is_available=True,
            ),
            models.DoctorSchedule(
                id="cf38a847-2ed4-4e3e-a9ee-4008c9f417be",
                specialist_id="fc108ab7-29b8-4cb0-89bf-e522408594c0",
                schedule_date=date(2026, 5, 27),
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_available=True,
            ),
            models.DoctorSchedule(
                id="fd537e0a-dfb8-4b71-8a0c-16a1f97e0e74",
                specialist_id="fc108ab7-29b8-4cb0-89bf-e522408594c0",
                schedule_date=date(2026, 5, 10),
                start_time=time(8, 0),
                end_time=time(16, 0),
                is_available=True,
            ),
            models.DoctorSchedule(
                id="947de64b-f1ae-4fad-b6f9-1ac01bab9104",
                specialist_id="3cf1afdc-08ad-42c0-a4e1-2624752a837d",
                schedule_date=date(2026, 5, 10),
                start_time=time(14, 0),
                end_time=time(16, 0),
                is_available=True,
            ),
            models.DoctorSchedule(
                id="db0e5916-8c8b-400b-86fa-df2d55b0e366",
                specialist_id="3cf1afdc-08ad-42c0-a4e1-2624752a837d",
                schedule_date=date(2026, 5, 26),
                start_time=time(12, 0),
                end_time=time(14, 0),
                is_available=True,
            ),
            models.DoctorSchedule(
                id="9e92e1c7-82fe-4d04-855f-e3089d4bb412",
                specialist_id="fde77300-d61d-4ad0-958e-1ddc7d7726ca",
                schedule_date=date(2026, 6, 6),
                start_time=time(12, 0),
                end_time=time(20, 0),
                is_available=True,
            ),
        ]
        for schedule_item in schedules:
            db.merge(schedule_item)

        db.merge(
            models.Appointment(
                id="19d00e0f-9ce0-4fa1-8074-3e2f24020ad3",
                patient_id=None,
                patient_name="Айгуль Нурланова",
                patient_phone="+77001234567",
                service_id="661b9091-86a4-4512-aa0d-162c8d0c2db0",
                specialist_id="4bd38fe7-6d07-43c6-81c1-47e7e1279356",
                appointment_date=date(2026, 5, 20),
                appointment_time=time(10, 0),
                status=models.AppointmentStatus.CONFIRMED,
                comment="Первичная консультация",
            )
        )

        appointments = [
            models.Appointment(
                id="0b46ee38-69e0-4b8f-80c9-e2f0e58fb7eb",
                patient_id=None,
                patient_name="Анна",
                patient_phone="+79876543210",
                service_id="3b874a33-0844-452c-960a-8ecb5ccbd7f2",
                specialist_id="3cf1afdc-08ad-42c0-a4e1-2624752a837d",
                appointment_date=date(2026, 5, 10),
                appointment_time=time(15, 0),
                status=models.AppointmentStatus.COMPLETED,
                comment="Первичная консультация",
            ),
            models.Appointment(
                id="36a392de-f82c-4def-ab73-0228e393ef9d",
                patient_id=None,
                patient_name="Ильяз",
                patient_phone="+7 701 777 18 45",
                service_id="cfb67935-1d0e-4f75-b78e-b1a96f7bcf5c",
                specialist_id="fc108ab7-29b8-4cb0-89bf-e522408594c0",
                appointment_date=date(2026, 5, 20),
                appointment_time=time(10, 0),
                status=models.AppointmentStatus.CANCELLED,
                comment="Первичная консультация, чувствительная кожа.",
            ),
            models.Appointment(
                id="768404cd-992b-40e5-90a1-82ff0ddfac39",
                patient_id=None,
                patient_name="Айгуль Нурланова",
                patient_phone="+77001234567",
                service_id="661b9091-86a4-4512-aa0d-162c8d0c2db0",
                specialist_id="4bd38fe7-6d07-43c6-81c1-47e7e1279356",
                appointment_date=date(2026, 5, 27),
                appointment_time=time(13, 0),
                status=models.AppointmentStatus.PENDING,
                comment="Вторичная консультация",
            ),
            models.Appointment(
                id="79b51fd2-8ba5-4495-b06b-c9ffb3ca5a06",
                patient_id=None,
                patient_name="Гульмира Садыкова",
                patient_phone="+7 701 777 18 44",
                service_id="3b874a33-0844-452c-960a-8ecb5ccbd7f2",
                specialist_id="3cf1afdc-08ad-42c0-a4e1-2624752a837d",
                appointment_date=date(2026, 5, 26),
                appointment_time=time(12, 0),
                status=models.AppointmentStatus.CANCELLED,
                comment="Вторичная консультация",
            ),
            models.Appointment(
                id="79dae7c8-269a-4338-9656-85b82fa79299",
                patient_id=None,
                patient_name="Феликс",
                patient_phone="+79944078944",
                service_id="661b9091-86a4-4512-aa0d-162c8d0c2db0",
                specialist_id="4bd38fe7-6d07-43c6-81c1-47e7e1279356",
                appointment_date=date(2026, 5, 26),
                appointment_time=time(15, 0),
                status=models.AppointmentStatus.CONFIRMED,
                comment="Третья консультация",
            ),
            models.Appointment(
                id="9e236666-8425-4c92-982a-e2740e9b39cf",
                patient_id=None,
                patient_name="Ильяз",
                patient_phone="+7 701 777 18 45",
                service_id="cfb67935-1d0e-4f75-b78e-b1a96f7bcf5c",
                specialist_id="fc108ab7-29b8-4cb0-89bf-e522408594c0",
                appointment_date=date(2026, 5, 27),
                appointment_time=time(15, 0),
                status=models.AppointmentStatus.PENDING,
                comment="Вторичная консультация",
            ),
            models.Appointment(
                id="9f7238c7-b780-417a-b988-249d269ffc69",
                patient_id=None,
                patient_name="Некий",
                patient_phone="+71111111111",
                service_id="cfb67935-1d0e-4f75-b78e-b1a96f7bcf5c",
                specialist_id="fc108ab7-29b8-4cb0-89bf-e522408594c0",
                appointment_date=date(2026, 5, 27),
                appointment_time=time(12, 0),
                status=models.AppointmentStatus.CANCELLED,
                comment="Проверка записи на прием",
            ),
            models.Appointment(
                id="a135130b-6863-4785-9586-e728fbfe3cb3",
                patient_id=None,
                patient_name="Иван",
                patient_phone="+7 777 777 77 77",
                service_id="cfb67935-1d0e-4f75-b78e-b1a96f7bcf5c",
                specialist_id="fc108ab7-29b8-4cb0-89bf-e522408594c0",
                appointment_date=date(2026, 5, 10),
                appointment_time=time(12, 30),
                status=models.AppointmentStatus.COMPLETED,
                comment="Первичная консультация",
            ),
            models.Appointment(
                id="a9167948-a331-4f2d-905c-dd52fdbc6640",
                patient_id=None,
                patient_name="Марина",
                patient_phone="+77776665544",
                service_id="b8c9d0e1-8888-4182-9d0e-8f9012345678",
                specialist_id="fde77300-d61d-4ad0-958e-1ddc7d7726ca",
                appointment_date=date(2026, 6, 6),
                appointment_time=time(16, 0),
                status=models.AppointmentStatus.PENDING,
                comment="Первичная консультация для ознакомления",
            ),
        ]
        for appointment in appointments:
            db.merge(appointment)

        review_source_url = "https://2gis.kz/atyrau/firm/70000001034947642/tab/reviews"
        reviews = [
            models.Review(
                id="7b1f43f1-0a01-4f1d-9f10-000000000001",
                author_name="Snezhana Saparova",
                rating=2,
                text="Хочу оставить отзыв о посещении салона. Записала свою бабушку на 9.03 на маникюр, педикюр и стрижку. Заранее предупредила администратора, что привезу её и попросила написать, когда она закончит, чтобы мы могли за ней заехать. Администратор написал, что бабушка уже заканчивает, и мы приехали. Однако по факту оказалось, что ей сделали только стрижку, а на маникюр она только собиралась идти. То есть запись была организована некорректно, либо часть услуг просто забыли. Отдельно хочу отметить, что я приехала с отцом, у которого опухоль в ноге и ему нежелательно лишний раз двигаться. В итоге мы зря приехали, пришлось уехать обратно и потом снова возвращаться — это доставило дополнительные неудобства. Маникюр сделали очень быстро, при этом записали к другому мастеру, хотя изначально мы просили конкретного специалиста. Качество услуг заметно ухудшилось. Мы долгое время были клиентами этого салона, но после данного случая остались крайне разочарованы и приняли решение больше не обращаться.",
                source="2gis",
                source_url=review_source_url,
                is_published=True,
                sort_order=1,
                published_at=datetime(2026, 4, 1, 12, 0),
            ),
            models.Review(
                id="7b1f43f1-0a01-4f1d-9f10-000000000002",
                author_name="Maria",
                rating=1,
                text="Это был негативный опыт посещения данного салона, перечислю основные моменты, которых к сожалению оказалось не мало. 1. Изначально выбирая мастера решила поспрашивать у знакомых к кому стоит идти. После записи к выбранному мастеру, ни онлайн ни по приходу в салон меня не предупредили о замене мастера, узнала я об этом уже после, когда мне пришла ссылка на оценивание мастера. 2. Сама стрижка меня не удовлетворила, от каскада там кажется одно слово, хотя казалось ничего сложно быть не должно. 3. Я не буду уходить в детали общения с мастером, поэтому ограничусь тем, что мне не подошел стиль общения мастера. Думаю в 2026 году с клиентоориентированностью и умением общаться с клиентом проблем быть не должно, особенно в салоне которому не 5 и даже не 10 лет. После выхода с салона осталась в унылом, расстроенном настроении.Хотя я была бы и не против если мастер молчал всю стрижку а не давал комментарии по поводу моих волос. 4. После стрижки и сушки мастер дала выбор, либо выпрямить утюжком (она не рекомендовала этого делать основываясь на моих волосах) либо оставить так как есть (не уложенными грубо говоря) феном она сказала что укладывать не будет (вроде как в связи с мягкостью волос но это не точно). Я сделала выбор в пользу утюжка в связи с тем что, у меня планировалась мероприятие вечером (в любой другой день я бы и не стала выпрямлять) Но конечно же мастер не предупредил и не поставил меня в известность что выпрямление утюжком как оказалось не входит в стоимость стрижки ( к примеру укладка феном туда входит) Об этом мастер мне сказала постфактум, когда мы уже закончили и стояли у ресепшен. Как итог мне пришлось доплатить , и самое простое выпрямление утюжком обошлось в плюс 7.000 от первоначальной суммы. Это мой первый негативный опыт при стрижке, я в целом человек лояльный и неконфликтный, но кажется этим в тот момент и воспользовались. Девушки которые думают о посещении данного салоне надеюсь мой отзыв поможет вам и вы будете иметь все эти моменты ввиду.",
                source="2gis",
                source_url=review_source_url,
                is_published=True,
                sort_order=2,
                published_at=datetime(2026, 4, 1, 12, 5),
            ),
            models.Review(
                id="7b1f43f1-0a01-4f1d-9f10-000000000003",
                author_name="Айжан Тулетаева",
                rating=5,
                text="Хочу выразить благодарность, девушке Досказиевой Диане, за классный педикюр. Девушка очень скромная, нежная. Сделала все аккуратно и классно! ❤️ Советую!",
                source="2gis",
                source_url=review_source_url,
                is_published=True,
                sort_order=3,
                published_at=datetime(2026, 3, 20, 12, 0),
            ),
            models.Review(
                id="7b1f43f1-0a01-4f1d-9f10-000000000004",
                author_name="A",
                rating=5,
                text="Всегда приветливый администратор Светлана, самые чистые инструменты и кабинеты, мастера со знанием дела. Хожу более 10 лет в маникюрный кабинет, всегда качественно и быстро оказывают услуги.",
                source="2gis",
                source_url=review_source_url,
                is_published=True,
                sort_order=4,
                published_at=datetime(2025, 10, 14, 12, 0),
            ),
            models.Review(
                id="7b1f43f1-0a01-4f1d-9f10-000000000005",
                author_name="Natalia Makisheva",
                rating=5,
                text="Уже несколько лет являюсь клиенткой мастера Раи, профессионал своего дела 👍👍👍 всегда прислушивается к пожеланиям, отлично подбирает цвет, супер корректирует брови! 🥰🥰🥰",
                source="2gis",
                source_url=review_source_url,
                is_published=True,
                sort_order=5,
                published_at=datetime(2025, 10, 14, 12, 5),
            ),
            models.Review(
                id="7b1f43f1-0a01-4f1d-9f10-000000000006",
                author_name="Aiman B",
                rating=5,
                text="Хожу в этот салон около 5 лет, нашла своего мастера-Раю!🌸Очень нравится как она подбирает стрижку, не отходя от референса. За стрижкой только к ней😍",
                source="2gis",
                source_url=review_source_url,
                is_published=True,
                sort_order=6,
                published_at=datetime(2025, 8, 25, 12, 0),
            ),
            models.Review(
                id="7b1f43f1-0a01-4f1d-9f10-000000000007",
                author_name="Эльмира Садыкова",
                rating=5,
                text="Услугами салона Беатрис пользуюсь около 8-9 лет, хочу отметить его и оставить честный отзыв как постоянного клиента по разным услугам. Это салон хорошего уровня с предоставлением широкого спектра услуг, многими из которых пользуемся я и мои дочки. В последние годы уровень сервиса значительно повысился, появилось свое удобное приложение для легкой записи, предлагают чай/кофе/воду со сладостями, проводятся разные интересные акции, презентации, салон работает с хорошими профессиональными уходовыми средствами, отличные мастера. Я лично и часто мои дочери чаще всего пользуемся услугами мастера Раи уже более 7 лет и получаем всегда хороший результат по парикмахерским услугам, наращиваю ресниц, а так же полезные советы, интересную беседу, заботу и соответственно хорошее настроение 😊 Администрация салона своевременно отвечает на запросы и лояльны бывают к нашим просьбам/предпочтениям. Рекомендую к посещению салон Беатрис🔥.",
                source="2gis",
                source_url=review_source_url,
                is_published=True,
                sort_order=7,
                published_at=datetime(2026, 2, 8, 12, 0),
            ),
            models.Review(
                id="7b1f43f1-0a01-4f1d-9f10-000000000008",
                author_name="Айгуль Кейкешева",
                rating=5,
                text="Добрый день! Хожу в этот центр красоты к мастеру Рая💕 Всегда выхожу оттуда с хорошим настроением и классной стрижкой! Рада, что я нашла своего мастера-профессионала 🍀",
                source="2gis",
                source_url=review_source_url,
                is_published=True,
                sort_order=8,
                published_at=datetime(2026, 1, 12, 12, 0),
            ),
            models.Review(
                id="7b1f43f1-0a01-4f1d-9f10-000000000009",
                author_name="Жумагуль Габдуллина",
                rating=5,
                text="Очень довольна услугами, Спасибо косметологу Наргиз Муратовне",
                source="2gis",
                source_url=review_source_url,
                is_published=True,
                sort_order=9,
                published_at=datetime(2025, 12, 17, 12, 0),
            ),
            models.Review(
                id="7b1f43f1-0a01-4f1d-9f10-000000000010",
                author_name="Mirgul Bekmuratova",
                rating=1,
                text="Был любимым салоном до вчерашнего дня. Вчера мне испортила волос мастер Рая. Я была записана на покраску волос и не планировала стричься, но мастер настоятельно утверждала что надо освежить кончики, я ей отказывала, но она не переставала говорить что надо подстричь кончики. В конце я сказала ну хорошо, и она мне показала длину которую нужно состричь, около 3 см и договорились. Но потом она начала стричь и якобы делать выравнивание, и в конце концов по чуть чуть она в итоге состригла 15 см, и было уже поздно. В итоге мою красивую длину которую я годами отращивала, этот «мастер» мне испортила за 10 мин, так еще и утверждала что сделала мне красивую, грамотную стрижку. Меня такая длина не устраивает, и волосы не так быстро растут, мое настроение испорчено на многие месяцы. А администрация салона в качестве компенсации мне предлагает лечение волос, а мне в это случае нужно наращивание. Не знаю что делать, буду думать в какие органы обратиться. Никогда не обращайтесь к Рае если не хотите испортить волосы.",
                source="2gis",
                source_url=review_source_url,
                is_published=True,
                sort_order=10,
                published_at=datetime(2025, 12, 17, 12, 5),
            ),
            models.Review(
                id="7b1f43f1-0a01-4f1d-9f10-000000000011",
                author_name="Екатерина Денисенко",
                rating=5,
                text='Вчера была в салоне "Беатрис", хожу туда уже много лет, очень внимательные и квалифицированные мастера, я даже могу сказать Мастера своего дела!!! Особенно хочу выделить мастера-парикмахера Раю и по стрижке и по окрашиванию. Всё супер!!! Очень общительна, приятна, с ней можно поговорить на разные темы, а ещё у неё есть уникальная способность - поднимать настроение, особенно в те моменты, когда ничего не хочется. Именно она нашла подход к моим волосам. С самого первого прихода к ней, она почти без слов поняла как меня нужно постричь. Окрашивание отдельная тема, я , вот честное слово, услышала много комплиментов о цвете моих волос. Про стрижку вообще молчу, мне постоянно говорят какая у меня красивая стрижка, спрашивают где и кто меня стрижёт. Также с удовольствием пользуюсь услугами маникюра и педикюра, очень качественно, красиво и всегда всё стерильно. Рае и всем девочкам из салона желаю здоровья, счастья, успехов в труде, чтобы они всё также продолжали нас делать красивыми, неотразимыми и очаровательными!!!❤️❤️❤️',
                source="2gis",
                source_url=review_source_url,
                is_published=True,
                sort_order=11,
                published_at=datetime(2025, 11, 16, 12, 0),
            ),
            models.Review(
                id="7b1f43f1-0a01-4f1d-9f10-000000000012",
                author_name="Тогжан Жубанова",
                rating=1,
                text="Здравствуйте. Хотела постричся и покрасить седые волосы. Во первых кресло не удобное, спина болела целый день. Во вторых у мастера треслись руки, стрижка ужас, без укладки утяжком и без платка не выйди. В третьих седина как была, так и осталась. За что такие деньги? Еше и техничка ругалась с персоналом на весь салон. Неприятно было поситить это место. Не советую 👎",
                source="2gis",
                source_url=review_source_url,
                is_published=True,
                sort_order=12,
                published_at=datetime(2025, 10, 18, 12, 0),
            ),
        ]
        for review in reviews:
            db.merge(review)

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
    print("Seed data loaded.")
