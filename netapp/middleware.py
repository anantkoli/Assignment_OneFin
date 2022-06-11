from netapp.models import Counts

def simple_middleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        count = Counts.objects.get(id=1)
        count_till = count.val
        count.val = count_till + 1
        count.save()

        response = get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
    return middleware