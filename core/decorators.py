from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def admin_required(view_func):
    """
    Decorator to ensure user is admin (staff or superuser)
    Redirects to admin dashboard if user is admin
    """
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_staff or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            else:
                return redirect('frontpage')
        return redirect('login')
    return wrapper

def redirect_admin_to_dashboard(view_func):
    """
    Decorator to redirect admin users to dashboard
    """
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
            return redirect('admin_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
