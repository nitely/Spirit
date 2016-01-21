from functools import wraps

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.exceptions import PermissionDenied
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

def _get_permissible_items(request, applabel_modelname):
    applabel, modelname = applabel_modelname.rsplit('_', 1)

    typematched = []
    for item in request.permissible_items or []:
        if item['contenttype'] == applabel_modelname:
            typematched.append(item)

    # @todo -- Need to work `or_404` in
    if not typematched:
        return None
    if len(typematched) > 1:
        raise ValueError('Multiple obj or qs on the same type is not yet supported.')

    type = typematched[0]
    ctype = ContentType.objects.get_by_natural_key(applabel, modelname)
    if type['kind'] == 'obj':
        return ctype.get_object_for_this_type(**type['params'])
    else:
        return ctype.model_class().objects.filter(**type['params'])

def _collect_args(fieldlookups, args):
    results = {}
    for lookup, arg_name in fieldlookups.iteritems():
        if arg_name in args:
            results[lookup] = args[arg_name]
        else:
            results[lookup] = arg_name

    return results

def permissible_object(func=None, contenttype=None, or_404=True, kind='obj',
            fieldlookups_kwargs={}, fieldlookups_getparams={}, fieldlookups_postparams={}, **kwargs):
    '''
    Decorator for `permission` decorated (such as @permission_required) views for
    object-level permission check. This decorators add `permissible_items` to the
    request object.

    Adapted from `django-trusts/decorators.py`
    '''

    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if not hasattr(request, 'permissible_items'):
                request.permissible_items = []

            params = {}
            if fieldlookups_kwargs:
                params.update(_collect_args(fieldlookups_kwargs, kwargs))

            if fieldlookups_getparams:
                params.update(_collect_args(fieldlookups_getparams, request.GET))

            if fieldlookups_postparams:
                params.update(_collect_args(fieldlookups_postparams, request.POST))

            request.permissible_items.append({
                'kind': kind,
                'or_404': or_404,
                'contenttype': contenttype,
                'params': params,
                'extra': kwargs
            })

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    if func:
        return decorator(func)
    return decorator

def permissible_queryset(func=None, contenttype=None, or_404=True,
            fieldlookups_kwargs={}, fieldlookups_getparams={}, fieldlookups_postparams={}, **kwargs):
    return permissible_object(
        func, contenttype, or_404=or_404,
        fieldlookups_kwargs=fieldlookups_kwargs,
        fieldlookups_getparams=fieldlookups_getparams,
        fieldlookups_postparams=fieldlookups_getparams,
        **kwargs
    )

def permission_required(func=None, perm=None, login_url=None, raise_exception=False):
    '''
    Decorator for views that checks whether a user has a particular permission
    enabled, redirecting to the log-in page if necessary.
    If the raise_exception parameter is given the PermissionDenied exception
    is raised.

    Adapted from `django-trusts/decorators.py` and `django/contrib/auth/decorator.py`
    '''

    backends = get_backends()

    def check_perms(request, *args, **kwargs):
        if not isinstance(perm, (list, tuple)):
            perms = (perm, )
        else:
            perms = perm

        all_passed = True
        applabel_modelname, can_action = perm.split('.', 1)
        items = _get_permissible_items(request, applabel_modelname)

        if request.user.has_perms(perms):
            if (len(self.backends) == 0):
                return True
            for backend in self.backends:
                if backend.has_perms(request, perms, obj):
                    return True

        # In case the 403 handler should be called raise the exception
        if raise_exception:
            raise PermissionDenied
        return False

    decorator = request_passes_test(check_perms, login_url=login_url)
    if func:
        return decorator(func)
    return decorator
