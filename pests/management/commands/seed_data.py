"""
Seed the database with reference data (plant parts, plant types, pests, diseases)
and an optional demo grower with farms, sessions and observations.

Usage:
    python manage.py seed_data              # reference data + demo account
    python manage.py seed_data --no-demo    # reference data only

Demo login:  demo / cropmedic123
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from pests.models import (
    Disease,
    Farm,
    Grower,
    Observation,
    Pest,
    PlantPart,
    PlantType,
    SurveillanceSession,
)

# ---------------------------------------------------------------- reference data

PLANT_PARTS = ["Leaf", "Stem", "Branch", "Flower", "Root", "Trunk", "Seed"]

PLANT_TYPES = ["Mango", "Avocado", "Banana", "Citrus", "Grapevine"]

PESTS = [
    {
        "name": "Fruit Fly",
        "brief_description": "Insect pest that damages fruits.",
        "image_url": "https://www.terro.com/media/Articles/TERRO/The-10-Most-Common-Fruit-Fly-Questions-Answered.jpg",
        "details": "Fruit flies lay eggs inside ripening mangoes. Larvae feed on pulp, causing rotting and fruit drop.",
        "control": "Use pheromone traps to monitor populations. Remove fallen fruits and apply bait sprays during fruit development.",
        "impact": "Damages internal fruit quality, causing economic loss and export rejections.",
        "infestation_rate": "High",
        "sampling_multiplier": 1.0,
    },
    {
        "name": "Mango Hopper",
        "brief_description": "Sap-sucking pest that causes flower shedding.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/a/a0/Two-lined_gum_treehopper03.jpg",
        "details": "Mango hoppers suck sap from inflorescences and young shoots. Their excretion encourages fungal growth, severely affecting pollination and fruit set.",
        "control": "Use insecticides like imidacloprid pre- and post-flowering. Maintain orchard sanitation and prune infested branches.",
        "impact": "Can lead to nearly 60% flower drop under heavy infestation, lowering yield.",
        "infestation_rate": "Severe",
        "sampling_multiplier": 1.0,
    },
    {
        "name": "Scale Insect",
        "brief_description": "Hard-shelled pest on stems sucking plant sap.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/76/%27Cercospora_capsici.jpg/640px-%27Cercospora_capsici.jpg",
        "details": "Scales settle on bark and branches, appearing like crusty spots. They weaken branches by continuous sap-sucking.",
        "control": "Introduce predatory beetles or apply horticultural oil in early infestation. Avoid over-fertilization.",
        "impact": "Leads to canopy thinning and long-term reduction in fruiting potential.",
        "infestation_rate": "Moderate",
        "sampling_multiplier": 1.0,
    },
    {
        "name": "Mealybug",
        "brief_description": "Sap-sucking insect covered in white wax.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Mealybugs_on_flower_stem%2C_Yogyakarta%2C_2014-10-31.jpg/1024px-Mealybugs_on_flower_stem%2C_Yogyakarta%2C_2014-10-31.jpg",
        "details": "Infests tender shoots, flower clusters, and fruit peduncles. Secretes honeydew that fosters sooty mold.",
        "control": "Apply neem oil or insecticidal soap. Introduce natural predators like lady beetles. Prune infested shoots.",
        "impact": "Reduces photosynthesis and stunts plant growth. In severe cases, fruit drop occurs.",
        "infestation_rate": "Moderate to Severe",
        "sampling_multiplier": 1.0,
    },
    {
        "name": "Leaf Webber",
        "brief_description": "Larvae web leaves together and feed within.",
        "image_url": "https://thumbs.dreamstime.com/b/leaf-webber-larvae-injure-mulberry-leaf-fruit-viet-nam-pest-pupular-insect-leaf-webber-larvae-injure-mulberry-212251965.jpg",
        "details": "Causes skeletonization of leaves; reduces photosynthetic ability.",
        "control": "Remove and burn webbed leaves. Use biological controls like Trichogramma. Spray Bacillus thuringiensis (Bt) for larvae.",
        "impact": "Leads to poor plant vigor and reduced yield.",
        "infestation_rate": "Low to Moderate",
        "sampling_multiplier": 1.0,
    },
    {
        "name": "Stem Borer",
        "brief_description": "Larvae bore into young stems and branches.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/31/Eucomatocera_vittata-Kadavoor-2017-05-23-001.jpg/1024px-Eucomatocera_vittata-Kadavoor-2017-05-23-001.jpg",
        "details": "Feeding causes drying of twigs and dieback.",
        "control": "Inject systemic insecticides into affected stems. Remove and burn infested branches. Keep orchard clean.",
        "impact": "Structural damage to tree. Reduces productivity.",
        "infestation_rate": "Moderate",
        "sampling_multiplier": 1.0,
    },
    {
        "name": "Gall Midge",
        "brief_description": "Small fly whose larvae cause gall formation on leaves.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Fly_December_2007-4.jpg/1024px-Fly_December_2007-4.jpg",
        "details": "Galls distort young leaves and suppress growth.",
        "control": "Remove galled leaves. Use light traps to catch adults. Apply recommended insecticides if infestation spreads.",
        "impact": "Affects photosynthesis and leads to malformed shoots.",
        "infestation_rate": "Low",
        "sampling_multiplier": 1.0,
    },
]

DISEASES = [
    {
        "name": "Anthracnose",
        "brief_description": "Fungal disease with dark spots on fruits.",
        "image_url": "https://www.planetnatural.com/wp-content/uploads/2012/12/anthracnose-1.jpg",
        "details": "Anthracnose is caused by Colletotrichum gloeosporioides. It causes dark lesions on mangoes, resulting in premature fruit drop and reduced marketability.",
        "control": "Apply copper-based fungicides during flowering. Ensure proper pruning for air circulation and avoid overhead irrigation.",
        "impact": "Leads to fruit spoilage and significant reduction in yield during peak seasons.",
        "severity": "High",
    },
    {
        "name": "Powdery Mildew",
        "brief_description": "White powdery growth on young leaves and flowers.",
        "image_url": "https://www.gardendesign.com/pictures/images/400x320Exact_0x0/site_3/powdery-mildew-powdery-mildew-on-squash-leaf-shutterstock-com_13365.jpg",
        "details": "Caused by Oidium mangiferae, it forms a white powder-like layer over the surface, hampering fruit development and reducing flower viability.",
        "control": "Use sulfur-based sprays early in bloom. Improve air circulation through pruning.",
        "impact": "Severely reduces fruit set and results in unmarketable yields.",
        "severity": "Moderate",
    },
    {
        "name": "Sooty Mold",
        "brief_description": "Black coating on leaves caused by honeydew excretion.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Wax_Scale.jpg/800px-Wax_Scale.jpg",
        "details": "Sooty mold is a black fungus that grows on sugary honeydew. It reduces photosynthesis and impacts leaf health.",
        "control": "Control honeydew-producing pests. Wash leaves with soap solution or prune heavily affected areas.",
        "impact": "Impairs photosynthesis and causes fruit blemishes reducing visual appeal.",
        "severity": "Low",
    },
    {
        "name": "Bacterial Canker",
        "brief_description": "Bacterial infection causing sunken cankers on branches.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Butternut_canker.jpg/800px-Butternut_canker.jpg",
        "details": "Gummy exudates may be present. Dieback and leaf spots are common.",
        "control": "Use copper-based bactericides. Prune infected twigs and sterilize tools. Avoid overhead watering.",
        "impact": "Affects overall plant health and yield.",
        "severity": "Low to Moderate",
    },
    {
        "name": "Dieback",
        "brief_description": "Progressive drying of twigs and branches from tip downward.",
        "image_url": "https://www.hants.gov.uk/-/media/Images/landplanningandenvironment/ash-dieback-disease/lesion-on-tree.png",
        "details": "Caused by fungi like Botryodiplodia. Entry through wounds.",
        "control": "Cut and burn affected branches. Apply systemic fungicides. Improve orchard sanitation.",
        "impact": "Reduces productivity and can lead to tree death.",
        "severity": "Moderate",
    },
]

# ---------------------------------------------------------------- demo data

DEMO_USERNAME = "demo"
DEMO_PASSWORD = "cropmedic123"
DEMO_EMAIL = "demo@example.com"

DEMO_FARMS = [
    # (location, num_plants, stocking_rate)
    ("Sample Orchard", 100, 3.5),
    ("Humpty Doo", 40, 12),
    ("Palmerston", 130, 35),
]

# (farm_index, date, time_of_day, plant_part, [(pest|None, disease|None, result), ...])
DEMO_SESSIONS = [
    (0, "2025-05-25", "morning", "Leaf", [("Fruit Fly", None, "low")]),
    (0, "2025-05-24", "afternoon", "Leaf", [("Mango Hopper", None, "mid")]),
    (0, "2025-05-20", "evening", "Flower", [(None, "Anthracnose", "high")]),
    (0, "2025-05-18", "morning", "Stem", [("Scale Insect", None, "mid")]),
    (1, "2025-05-24", "morning", "Flower", [(None, "Bacterial Canker", "low")]),
    (1, "2025-06-20", "afternoon", "Leaf", [("Scale Insect", None, "high")]),
    (2, "2025-05-24", "morning", "Root", [("Scale Insect", None, "mid")]),
    (2, "2025-06-23", "afternoon", "Branch", [(None, "Dieback", "low")]),
    (2, "2025-05-07", "afternoon", "Root", [(None, "Powdery Mildew", "mid")]),
]


class Command(BaseCommand):
    help = "Seed reference data and (optionally) a demo grower account."

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-demo",
            action="store_true",
            help="Only seed reference data; skip the demo grower, farms and observations.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self._seed_reference()
        if not options["no_demo"]:
            self._seed_demo()
        self.stdout.write(self.style.SUCCESS("\nDone."))

    # ------------------------------------------------------------ reference

    def _seed_reference(self):
        self.stdout.write(self.style.MIGRATE_HEADING("Reference data"))

        for name in PLANT_PARTS:
            obj, created = PlantPart.objects.get_or_create(name=name)
            self._report("PlantPart", name, created)

        for name in PLANT_TYPES:
            obj, created = PlantType.objects.get_or_create(name=name)
            self._report("PlantType", name, created)

        for data in PESTS:
            obj, created = Pest.objects.get_or_create(
                name=data["name"], defaults=data
            )
            self._report("Pest", data["name"], created)

        for data in DISEASES:
            obj, created = Disease.objects.get_or_create(
                name=data["name"], defaults=data
            )
            self._report("Disease", data["name"], created)

    # ------------------------------------------------------------ demo

    def _seed_demo(self):
        from django.contrib.auth.models import User

        self.stdout.write(self.style.MIGRATE_HEADING("\nDemo account"))

        user, created = User.objects.get_or_create(
            username=DEMO_USERNAME, defaults={"email": DEMO_EMAIL}
        )
        if created:
            user.set_password(DEMO_PASSWORD)
            user.save()
            self.stdout.write(f"  + user {DEMO_USERNAME} (password: {DEMO_PASSWORD})")
        else:
            self.stdout.write(f"  = user {DEMO_USERNAME} already exists")

        grower, g_created = Grower.objects.get_or_create(
            user=user,
            defaults={"name": "Demo Grower", "age": 38, "email": DEMO_EMAIL},
        )
        self._report("Grower", grower.name, g_created)

        farms = []
        for location, num_plants, rate in DEMO_FARMS:
            farm, f_created = Farm.objects.get_or_create(
                grower=grower,
                location=location,
                defaults={"num_plants": num_plants, "stocking_rate": rate},
            )
            farms.append(farm)
            self._report("Farm", location, f_created)

        self.stdout.write(self.style.MIGRATE_HEADING("\nDemo sessions"))
        for farm_idx, date, tod, part_name, observations in DEMO_SESSIONS:
            farm = farms[farm_idx]
            part = PlantPart.objects.filter(name=part_name).first()
            session, s_created = SurveillanceSession.objects.get_or_create(
                farm=farm,
                date=date,
                time_of_day=tod,
                defaults={"plant_part": part, "plant_type": None},
            )
            self._report("Session", f"{farm.location} {date} {tod}", s_created)

            for pest_name, disease_name, result in observations:
                pest = Pest.objects.filter(name=pest_name).first() if pest_name else None
                disease = (
                    Disease.objects.filter(name=disease_name).first()
                    if disease_name
                    else None
                )
                obs, o_created = Observation.objects.get_or_create(
                    session=session,
                    pest=pest,
                    disease=disease,
                    result=result,
                )
                label = pest_name or disease_name or "?"
                self._report("  Observation", f"{label} -> {result}", o_created)

    # ------------------------------------------------------------ helpers

    def _report(self, kind, name, created):
        if created:
            self.stdout.write(f"  + {kind}: {name}")
        else:
            self.stdout.write(f"  = {kind}: {name} (exists)")
