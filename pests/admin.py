from django.contrib import admin
from .models import Grower, Farm, PlantType, PlantPart, SurveillanceSession, Observation
from django.contrib import admin
from .models import Pest, Disease  # 👈 Import them

admin.site.register(Pest)
admin.site.register(Disease)
admin.site.register(Grower)
admin.site.register(Farm)
admin.site.register(PlantType)
admin.site.register(PlantPart)
admin.site.register(SurveillanceSession)
admin.site.register(Observation)
