import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect

from .forms import ContactForm, SearchForm
from .models import ContactMessage, Post

logger = logging.getLogger(__name__)


def index_view(request):
    return render(request, "blog/index.html")

@login_required
def dashboard_view(request):
    return render(request, "blog/dashboard.html")

def contact_view(request):
    if request.method == "POST":
        if request.POST.get("website", "").strip():
            return redirect("contact_thanks")

        form = ContactForm(request.POST)

        if form.is_valid():
            contact_message = ContactMessage.objects.create(
                name=form.cleaned_data["name"],
                email=form.cleaned_data["email"],
                message=form.cleaned_data["message"],
            )
            _send_contact_notification(contact_message)
            return redirect("contact_thanks")
    else:
        form = ContactForm(
            initial={"name": request.user.username}
            if request.user.is_authenticated
            else None
        )

    return render(request, "blog/contact.html", {"form": form})


def _send_contact_notification(contact_message: ContactMessage) -> None:
    """Email a contact message, logging failures without losing the record."""
    email = EmailMessage(
        subject=f"New contact message from {contact_message.name}",
        body=(
            f"From: {contact_message.name} <{contact_message.email}>\n\n"
            f"{contact_message.message}"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.CONTACT_EMAIL],
        reply_to=[contact_message.email],
    )

    try:
        email.send()
    except Exception:
        logger.exception(
            "Failed to send contact notification for message %s",
            contact_message.pk,
        )


def search_view(request):
    form = SearchForm(request.GET or None)
    results = Post.objects.all()

    if form.is_valid() and form.cleaned_data['q']:
        term = form.cleaned_data['q']
        # search in title or content
        results = results.filter(title__icontains=term) | (results.filter(content__icontains=term))

    return render(request, "blog/search.html", {"form": form, "results": results})