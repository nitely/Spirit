import django.dispatch

# args: sender, instance
search_index_update = django.dispatch.Signal()
