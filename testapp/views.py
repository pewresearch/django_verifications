from future import standard_library

standard_library.install_aliases()

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth import authenticate


def login(request):

    pass

    # if request.user.is_authenticated():
    #     return home(request)
    # else:
    #
    #     username = request.POST.get("username")
    #     password = request.POST.get("password")
    #
    #     user = authenticate(username=username, password=password)
    #     if user is not None:
    #         if user.is_active:
    #             django_login(request, user)
    #             return home(request)
    #         else:
    #             return render(request, 'logos/login.html', {})
    #     else:
    #         return render(request, 'logos/login.html', {})


@login_required
def logout(request):

    pass

    # django_logout(request)
    # return render(request, 'logos/login.html', {})
