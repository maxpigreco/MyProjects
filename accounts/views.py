from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import SignUpForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm
from .models import Profile

@login_required
def edit_profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    return render(request, "accounts/profile_edit.html", {"form": form})

@login_required
def profile_view(request):
    """Show the signed-in user's account details and profile bio."""
    profile, _ = Profile.objects.get_or_create(user=request.user)
    post_count = request.user.posts.count()

    return render(
        request,
        "accounts/profile.html",
        {"profile": profile, "post_count": post_count},
    )

def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created! Please log in.")
            return redirect("login")
    else:
        form = SignUpForm()
    
    return render(request, "accounts/signup.html", {"form": form})
