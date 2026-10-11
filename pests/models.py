from django.db import models
from django.contrib.auth.models import User

# Base class already present (Item)
class Item(models.Model):
    name = models.CharField(max_length=100)
    brief_description = models.TextField()
    image_url = models.URLField()
    details = models.TextField()
    control = models.TextField()
    impact = models.TextField()

    class Meta:
        abstract = True

class Pest(Item):
    infestation_rate = models.CharField(max_length=50)
    sampling_multiplier = models.FloatField(default=1.0)

    def __str__(self):
        return f"Pest: {self.name}"

    def get_type(self):
        return "pest"

class Disease(Item):
    severity = models.CharField(max_length=50)

    def __str__(self):
        return f"Disease: {self.name}"

    def get_type(self):
        return "disease"

# ✅ New models start here

class Grower(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    email = models.EmailField()

    def __str__(self):
        return self.name

class Farm(models.Model):
    grower = models.ForeignKey(Grower, on_delete=models.CASCADE, related_name='farms')
    location = models.CharField(max_length=255)
    num_plants = models.PositiveIntegerField()
    stocking_rate = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.location} ({self.grower.name})"

class PlantType(models.Model):
    name = models.CharField(max_length=100)
    density_factor = models.FloatField(default=1.0)

    def __str__(self):
        return self.name

class PlantPart(models.Model):
    name = models.CharField(max_length=100)
    sensitivity = models.FloatField(default=1.0)

    def __str__(self):
        return self.name

class SurveillanceSession(models.Model):
    TIME_CHOICES = [
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening'),
    ]

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='sessions')
    plant_type = models.ForeignKey(PlantType, on_delete=models.SET_NULL, null=True, blank=True)
    plant_part = models.ForeignKey(PlantPart, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    time_of_day = models.CharField(max_length=10, choices=TIME_CHOICES)

    def __str__(self):
        return f"Session on {self.date} ({self.farm.location})"

class Observation(models.Model):
    RESULT_CHOICES = [
        ('low', 'Low'),
        ('mid', 'Mid'),
        ('high', 'High'),
    ]
    session = models.ForeignKey(
        SurveillanceSession,
        on_delete=models.CASCADE,
        related_name='observations'
    )
    pest = models.ForeignKey(
        'Pest',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    disease = models.ForeignKey(
        'Disease',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    result = models.CharField(
        max_length=10,
        choices=RESULT_CHOICES
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when this observation was recorded"
    )

    def __str__(self):
        pest_name = self.pest.name if self.pest else "No pest"
        disease_name = self.disease.name if self.disease else "No disease"
        return f"{self.session.farm.location} - {pest_name} / {disease_name}"
