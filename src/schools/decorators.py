import functools
from django.http import HttpResponseForbidden
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test


def site_su_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='/login/'):
    '''
    Decorator for views that checks that the logged in user is a site super user,
    redirects to the log-in page if necessary.
    '''
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_superuser,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator