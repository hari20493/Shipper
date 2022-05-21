
from functools import wraps

from django.contrib import messages

from django.shortcuts import redirect


def super_user_only(view_func):
    """
    Decorator for views that checks that the user is logged in and is
    staff, displaying message if provided.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'You are not authorized to view this page.')
                return redirect('login')

        return _wrapped_view

    return decorator
