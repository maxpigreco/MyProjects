import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ContactForm, SearchForm
from .models import ContactMessage, Post

logger = logging.getLogger(__name__)
POSTS_PER_PAGE = 6


def _paginate(request, queryset):
    """Return the requested page of posts, six per page."""
    paginator = Paginator(queryset, POSTS_PER_PAGE)
    return paginator.get_page(request.GET.get("page"))


def index_view(request):
    posts = Post.objects.filter(
        status=Post.Status.PUBLISHED
    ).select_related("author")
    return render(
        request,
        "blog/index.html",
        {"page_obj": _paginate(request, posts)},
    )

@login_required
def dashboard_view(request):
    """Show the signed-in user's summary and their own posts."""
    posts = Post.objects.filter(
        author=request.user
    ).select_related("author")
    stats = posts.aggregate(
        total=Count("pk"),
        published=Count(
            "pk",
            filter=Q(status=Post.Status.PUBLISHED),
        ),
        drafts=Count(
            "pk",
            filter=Q(status=Post.Status.DRAFT),
        ),
    )

    return render(
        request,
        "blog/dashboard.html",
        {
            "page_obj": _paginate(request, posts),
            "stats": stats,
        },
    )

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


def post_detail_view(request, slug):
    post = get_object_or_404(
        Post.objects.select_related("author"),
        slug=slug,
        status=Post.Status.PUBLISHED,
    )
    Post.objects.filter(pk=post.pk).update(views=F("views") + 1)
    post.refresh_from_db(fields=["views"])

    return render(request, "blog/post_detail.html", {"post": post})


def search_view(request):
    form = SearchForm(request.GET or None)
    term = ""
    if form.is_valid():
        term = form.cleaned_data["q"].strip()

    results = Post.objects.filter(
        status=Post.Status.PUBLISHED
    ).select_related("author")
    if term:
        results = results.filter(
            Q(title__icontains=term) | Q(content__icontains=term)
        )

    return render(
        request,
        "blog/search.html",
        {
            "form": form,
            "page_obj": _paginate(request, results),
            "term": term,
        },
    )