import uuid
from django.db import models

class Animal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    scientific_name = models.TextField(unique=True, blank=True, null=True)
    image_url = models.TextField(blank=True, null=True)
    max_probability = models.FloatField(blank=True, null=True)
    entropy = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'animals'

class AnimalLocation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    animal = models.ForeignKey(Animal, models.DO_NOTHING, blank=True, null=True)
    h3_index = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    count = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'animal_locations'

class AnimalCharacteristic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    animal = models.ForeignKey(Animal, models.DO_NOTHING, blank=True, null=True)
    prey = models.TextField(blank=True, null=True)
    gestation_period = models.TextField(blank=True, null=True)
    habitat = models.TextField(blank=True, null=True)
    predators = models.TextField(blank=True, null=True)
    average_litter_size = models.TextField(blank=True, null=True)
    top_speed = models.TextField(blank=True, null=True)
    lifespan = models.TextField(blank=True, null=True)
    weight = models.TextField(blank=True, null=True)
    length = models.TextField(blank=True, null=True)
    skin_type = models.TextField(blank=True, null=True)
    color = models.TextField(blank=True, null=True)
    age_of_sexual_maturity = models.TextField(blank=True, null=True)
    age_of_weaning = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'animal_characteristics'
