from django.contrib import admin
from .models import AddressModel, VehicleModel, StartLocationModel, EndLocationModel, OptimisedLocation, OptimisedVehicle, OptimisedRoute, OptimisedStartLocation, OptimisedEndLocation

# Register your models here.

admin.site.register(AddressModel)
admin.site.register(VehicleModel)
admin.site.register(StartLocationModel)
admin.site.register(EndLocationModel)
admin.site.register(OptimisedLocation)
admin.site.register(OptimisedVehicle)
admin.site.register(OptimisedRoute)
admin.site.register(OptimisedStartLocation)
admin.site.register(OptimisedEndLocation)
