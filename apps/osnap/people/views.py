# -*- coding: utf-8 -*-
"""
osnap.people.views
==================
Views for users to display and edit their profile.

:copyright: (C) 2013 Matthew Frazier
:license:   GNU GPL version 2 or later, see LICENSE for details
"""
from __future__ import unicode_literals
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.sites.models import get_current_site
from django.core.mail import send_mail
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView
from django.views.generic.edit import CreateView

from .forms import RegistrationForm
from .models import User

class ProfileView(DetailView):
    model = User

    slug_field = 'username'
    slug_url_kwarg = 'username'

    template_name = 'osnap/people/profile.html'
    context_object_name = 'subject'


class RegisterView(CreateView):
    model = User
    form_class = RegistrationForm

    template_name = "osnap/accounts/registration/form.html"
    context_object_name = "new_user"

    def form_valid(self, form):
        new_user = form.save()
        # Email the user!
        send_activation_email(new_user, self.request)

        return render(self.request, "osnap/accounts/done.html", {
            "action": "registered"
        })


def activate_account(request, token):
    signer = TimestampSigner(salt='account activation', sep='.')
    try:
        user_id = int(signer.unsign(token, 8 * 60 * 60))
        user = User.objects.get(id=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist,
            BadSignature, SignatureExpired) as e:
        user = None

    if user is not None:
        user.is_active = True
        user.save()

        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)

        messages.info(request, _("Your account is active! You may now participate on the site."))
        return redirect('osnap_front_page')
    else:
        return render(request, "osnap/accounts/done.html", {
            "action": "bad link"
        })


def send_activation_email(new_user, request):
    current_site = get_current_site(request)
    site_name = current_site.name
    domain = current_site.domain

    signer = TimestampSigner(salt='account activation', sep='.')
    token = signer.sign(str(new_user.pk))

    c = {
        'user': new_user,
        'email': new_user.email,
        'token': token,
        'domain': domain,
        'site_name': site_name,
        'protocol': 'https' if request.is_secure() else 'http'
    }

    subject = render_to_string("osnap/accounts/registration/email-subject.txt", c)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    email = render_to_string("osnap/accounts/registration/email.txt", c)

    send_mail(subject, email, None, [new_user.email])

