from django.shortcuts import render, redirect
from .forms import ContactForm
from .forms import SearchForm
from .models import Post
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def index_view(request):
    return render(request, "blog/index.html")

@login_required
def dashboard_view(request):
    return render(request, "blog/dashboard.html")

def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)

        if form.is_valid():
            # print("Cleaned data: ", form.cleaned_data)
            messages.success(request, "Thanks! We'll be in touch.")
            return redirect("contact")   # back to blank form
    else:
        form = ContactForm(initial={"name": request.user.username} if request.user.is_authenticated else None)

    return render(request, "blog/contact.html", {"form": form})


def search_view(request):
    form = SearchForm(request.GET or None)
    results = Post.objects.all()

    if form.is_valid() and form.cleaned_data['q']:
        term = form.cleaned_data['q']
        # search in title or content
        results = results.filter(title__icontains=term) | (results.filter(content__icontains=term))

    return render(request, "blog/search.html", {"form": form, "results": results})