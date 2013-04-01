from totems import settings

def some_context_processor(request):
    my_dict = {
        'TOTEMS_SECRET':settings.TOTEMS_SECRET,
        'STATIC_URL':settings.STATIC_URL,
    }

    return my_dict
