from functools import wraps

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.shortcuts import resolve_url
from django.contrib.contenttypes.models import ContentType
from django.utils.decorators import available_attrs
from django.utils.six.moves.urllib.parse import urlparse
from django.http import Http404


def request_passes_test(test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME, *args, **kwargs):
    '''
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.

    Adapted from `django/contrib/auth/decorator.py`
    '''

    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request, *args, **kwargs):
                return view_func(request, *args, **kwargs)

            path = request.build_absolute_uri()
            resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if ((not login_scheme or login_scheme == current_scheme) and
                    (not login_netloc or login_netloc == current_netloc)):
                path = request.get_full_path()
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(
                path, resolved_login_url, redirect_field_name)
        return _wrapped_view
    return decorator

def _collect_args(fieldlookups, args):
    results = {}

    if not fieldlookups:
        return results
    if not args:
        return fieldlookups

    for lookup, arg_name in fieldlookups.iteritems():
        if arg_name in args:
            results[lookup] = args[arg_name]
        else:
            results[lookup] = arg_name

    return results

def _get_permissible_items(request, applabel__action_modelname, fieldlookups):
    if fieldlookups is None:
        return None

    applabel, action_modelname = applabel__action_modelname.split('.', 1)
    action, modelname = action_modelname.split('_', 1)
    try:
        ctype = ContentType.objects.get_by_natural_key(applabel, modelname)

        return ctype.model_class().objects.filter(**fieldlookups)
    except ObjectDoesNotExist:
        raise ValueError("Permission code must be of the form 'app_label.action_modelname'.")


def permission_required(perm, or_404=False, raise_exception=True, login_url=None,
        fieldlookups_kwargs=None, fieldlookups_getparams=None, fieldlookups_postparams=None, **kwargs):
    '''
    Decorator for views that checks whether a user has a particular permission
    enabled, redirecting to the log-in page if necessary.
    If the raise_exception parameter is given the PermissionDenied exception
    is raised.

    Adapted from `django-trusts/trusts/decorators` and `django/contrib/auth/decorator.py`
    '''

    def check_perms(request, *args, **kwargs):
        if not isinstance(perm, (list, tuple)):
            perms = (perm, )
        else:
            perms = perm

        fieldlookups = None
        if fieldlookups_kwargs is not None or fieldlookups_getparams is not None or fieldlookups_postparams is not None:
            fieldlookups = {}
            fieldlookups.update(_collect_args(fieldlookups_kwargs, kwargs))
            fieldlookups.update(_collect_args(fieldlookups_getparams, request.GET))
            fieldlookups.update(_collect_args(fieldlookups_postparams, request.POST))

        items = None
        if fieldlookups is not None:
            items = _get_permissible_items(request, perm, fieldlookups)
            if items is None:
                raise Http404

        if request.user.has_perms(perms, items):
            return True

        # In case the 403 handler should be called raise the exception
        if raise_exception:
            raise PermissionDenied
        return False

    return request_passes_test(check_perms, login_url=login_url)
