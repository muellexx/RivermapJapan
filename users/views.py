from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import gettext as _
from django.template.loader import render_to_string
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView

from blog.models import Post
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .tokens import account_activation_token


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = _('Activate your Account')
            message = render_to_string('users/account_activation_email.txt', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            html_message = render_to_string('users/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject=subject, message=message, html_message=html_message)
            messages.success(request, _('An email with a registration link has been sent to your email address'))
            return redirect('blog-home')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, _('Your account has been activated!'))
        return redirect('blog-home')
    else:
        messages.warning(request, _('Invalid activation link'))
        return redirect('blog-home')


class ProfileView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'users/profile.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = self.request.user
        return Post.objects.filter(author=user).order_by('-date_posted')


@login_required
def profile_edit(request):
    print(request.user)
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, _('Your account has been updated!'))
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'users/profile_edit.html', context)


@login_required
def profile_delete(request):
    messages.warning(request, _('Warning: Deleting your account cannot be undone!'))
    return render(request, 'users/profile_delete.html')


@login_required
def profile_delete_done(request):
    request.user.delete()
    messages.success(request, _('Your account has successfully been deleted!'))
    return redirect('blog-home')
