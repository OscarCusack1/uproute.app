from django.db.models import Model, CharField, FloatField, IntegerField, TimeField, BooleanField, ManyToManyField, JSONField, OneToOneField, CASCADE, ForeignKey
from django.conf import settings

# Create your models here.

class AddressModel(Model):
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, null=True, blank=True)
    address = CharField(max_length=255)
    longitude = FloatField()
    latitude = FloatField()
    demand = IntegerField(null=True, blank=True)
    window_time_start = TimeField(null=True, blank=True)  # New window time start field
    window_time_end = TimeField(null=True, blank=True)    # New window time end field

    def __str__(self):
        return self.address
    
class RouteParametersModel(Model):
    address = ManyToManyField(AddressModel)
    use_demand = BooleanField(default=False)
    use_time_window = BooleanField(default=False)

    def __str__(self):
        return f"Collection for {self.address}"
    
class VehicleModel(Model):
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, null=True, blank=True)
    name = CharField(max_length=255, null=True, blank=True)
    start_time = TimeField(null=True, blank=True)
    end_time = TimeField(null=True, blank=True)
    capacity = IntegerField(null=True, blank=True)

class StartLocationModel(Model):
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, null=True, blank=True)
    address = CharField(max_length=255, null=True, blank=True)
    longitude = FloatField(null=True, blank=True)
    latitude = FloatField(null=True, blank=True)
    start_time = TimeField(null=True, blank=True)  # New window time start field
    end_time = TimeField(null=True, blank=True)    # New window time end field
    
class EndLocationModel(Model):
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, null=True, blank=True)
    address = CharField(max_length=255, null=True, blank=True)
    longitude = FloatField(null=True, blank=True)
    latitude = FloatField(null=True, blank=True)
    start_time = TimeField(null=True, blank=True)  # New window time start field
    end_time = TimeField(null=True, blank=True)    # New window time end field

class OptimisedRoute(Model):
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, null=True, blank=True)
    total_duration = FloatField(null=True, blank=True)
    maximum_duration = FloatField(null=True, blank=True)
    total_demand = IntegerField(null=True, blank=True)
    maximum_demand = IntegerField(null=True, blank=True)
    total_stops = IntegerField(null=True, blank=True)
    maximum_stops = IntegerField(null=True, blank=True)
    latest_arrival = TimeField(null=True, blank=True)
    use_demand = BooleanField(default=False)
    use_time_window = BooleanField(default=False)

class OptimisedVehicle(Model):
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, null=True, blank=True)
    capacity = IntegerField(null=True, blank=True)
    start_time = TimeField(null=True, blank=True)
    end_time = TimeField(null=True, blank=True)
    arrival_time = TimeField(null=True, blank=True)
    depart_time = TimeField(null=True, blank=True)
    total_duration = FloatField(null=True, blank=True)
    total_demand = IntegerField(null=True, blank=True)
    total_stops = IntegerField(null=True, blank=True)
    route = ForeignKey(OptimisedRoute, on_delete=CASCADE, null=True, blank=True)

class OptimisedEndLocation(Model):
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, null=True, blank=True)
    address = CharField(max_length=255, null=True, blank=True)
    longitude = FloatField(null=True, blank=True)
    latitude = FloatField(null=True, blank=True)
    arrival_time = TimeField(null=True, blank=True)
    time_from_previous = FloatField(null=True, blank=True)
    demand = IntegerField(null=True, blank=True)
    vehicle = ForeignKey(OptimisedVehicle, on_delete=CASCADE, null=True, blank=True)

class OptimisedStartLocation(Model):
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, null=True, blank=True)
    address = CharField(max_length=255, null=True, blank=True)
    longitude = FloatField(null=True, blank=True)
    latitude = FloatField(null=True, blank=True)
    depart_time = TimeField(null=True, blank=True)
    wait_time = FloatField(null=True, blank=True)
    time_to_next = FloatField(null=True, blank=True)
    demand = IntegerField(null=True, blank=True)
    route_to_next = JSONField(null=True, blank=True)
    vehicle = ForeignKey(OptimisedVehicle, on_delete=CASCADE, null=True, blank=True)

class OptimisedLocation(Model):
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, null=True, blank=True)
    address = CharField(max_length=255, null=True, blank=True)
    longitude = FloatField(null=True, blank=True)
    latitude = FloatField(null=True, blank=True)
    arrival_time = TimeField(null=True, blank=True)
    depart_time = TimeField(null=True, blank=True)
    wait_time = FloatField(null=True, blank=True)
    time_to_next = FloatField(null=True, blank=True)
    time_from_previous = FloatField(null=True, blank=True)
    demand = IntegerField(null=True, blank=True)
    route_to_next = JSONField(null=True, blank=True)
    vehicle = ForeignKey(OptimisedVehicle, on_delete=CASCADE, null=True, blank=True)
    
