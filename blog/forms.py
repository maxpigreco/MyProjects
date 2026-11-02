from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label="Your name")
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea, min_length=50)
    # Honeypot: hidden in the template; bots that fill it are ignored.
    website = forms.CharField(
        required=False,
        label="Website",
        widget=forms.TextInput(
            attrs={
                "autocomplete": "off",
                "tabindex": "-1",
            }
        ),
    )

class SearchForm(forms.Form):
    q = forms.CharField(label="Search", max_length=100, required=False)