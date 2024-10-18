from django.conf import settings

def bing_maps_processor(request):
    if request.user.is_authenticated:
        bk = settings.BING_MAPS_API_KEY
    else:
        bk = None
    return {'BING_MAPS_API_KEY': bk}