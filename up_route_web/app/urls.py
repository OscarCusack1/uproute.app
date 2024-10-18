from django.urls import path
from . import views

urlpatterns = [
    # path('', views.home, name='home'),
    path('address/', views.address_view, name='address_view'),
    path('address/add_address/', views.add_address, name='add_address'),
    path('update_address_table/', views.update_address_table, name='update_address_table'),
    path('update_vehicle_table/', views.update_vehicle_table, name='update_vehicle_table'),
    path('update_depot_table/', views.update_depot_table, name='update_depot_table'),
    path('address/delete/<int:address_id>/', views.delete_address, name='delete_address'),
    path('address/update_demand/<int:address_id>/', views.update_demand, name='update_demand'),
    path('address/update_start_address/<int:address_id>/', views.update_start_address, name='update_start_address'),
    path('address/update_end_address/<int:address_id>/', views.update_end_address, name='update_end_address'),
    path('address/update_time_window/<int:address_id>/', views.update_time_window, name='update_time_window'),
    path('vehicle/delete/<int:vehicle_id>/', views.delete_vehicle, name='delete_vehicle'),
    path('vehicle/create/', views.add_vehicle, name='add_vehicle'),
    path('address/update_capacity/<int:vehicle_id>/', views.update_capacity, name='update_capacity'),
    path('address/update_vehicle_time_window/<int:vehicle_id>/', views.update_vehicle_time_window, name='update_vehicle_time_window'),
    path('address/update_start_location_time_window/<int:location_id>/', views.update_start_location_time_window, name='update_start_location_time_window'),
    path('address/update_end_location_time_window/<int:location_id>/', views.update_end_location_time_window, name='update_end_location_time_window'),
    path('address/send_optimisation_request/', views.send_optimisation_request, name='send_optimisation_request'),
    path('address/delete_optimised_route/<int:route_id>/', views.delete_optimised_route, name='delete_optimised_route'),
    path('address/get_map/', views.get_map, name='get_map'),
]