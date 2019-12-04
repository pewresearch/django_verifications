# Django Verifications

Django Verifications is a lightweight coding interface to manually review and freeze various model attributes
using simple metadata toggles.  By specifying models as a `VerifiedModel` with the proper model metadata,
Django Verifications will expose a web interface for reviewing and confirming object attributes in your app.
For example, we found this to come in handy for reviewing and confirming the Facebook accounts of US congress members.
After loading in accounts from a variety of sources - many of which had errors - Django Verifications allowed us to
review each account manually and confirm that it was associated with the correct politician.  Once an account has been
verified, Django Verifications yells at you if you try to change that value - which can be very useful when your app
has a lot of moving parts, and maintaining data accuracy is of the utmost importance.

## Installation

### Dependencies

django_verifications requires:

- Python (>= 2.7)
- Django (>= 1.10)
- [Pewtils (our own in-house Python utilities)](https://github.com/pewresearch/pewtils)
- [Django Pewtils (our own in-house Django utilities)](https://github.com/pewresearch/django_pewtils)

You'll need to install Pewtils and Django Pewtils in order for Django Verifications to work, but other than that,
there are no special requirements.

### Configuring Your Models

All you need to do to use django_verifications is make sure that your models inherit from
`django_verifications.VerifiedModel` instead of the traditional `django.db.models.Model` class, and it will take
care of the rest.  Django Verifications then requires you to specify two special `Meta` variables, so it knows
how to treat your table.

- `fields_to_verify`: This should be a list, with the names of all of the fields that you want to verify as correct.
- `verification_filters`: This is a list of dictionaries, that are used as keyword arguments to a Django QuerySet filter.
This allows you to narrow the scope of rows in your table that you want to verify.  For example, in our Facebook account
verification project, we had a lot of other accounts in the database that we were less concerned with - we only wanted
to verify politician accounts.  So we added a special filter to this list: `{"politician__isnull": False}`

`VerifiedModel` instances also have a `get_verification_metadata()` function that, by default, returns all of the 
values on the model for each object to be verified. These values are displayed in the coding interface to assist you in 
determining whether fields are correct or not. You can overwrite this function to return any dictionary of values 
you desire. 

All of this comes together like so:

```python

from django_verifications.models import VerifiedModel

class FacebookProfile(VerifiedModel):

    page_name = models.CharField(max_length=200)
    document = models.OneToOneField("django_learning.Document", related_name="facebook_post", null=True)
    politician = models.ForeignKey("my_models.Politician", related_name="facebook_profiles", null=True)
    
    class Meta:

        fields_to_verify = ["politician"]
        verification_filters = [{"politician__isnull": False}]
        
    def get_verification_metadata(self):
        return {
            "page": self.page_name,
            "text": self.document.text,
            "politician": self.politician.name
        }

```

It's not a great example, but in this `VerifiedModel`, we've specified that we want to verify all Facebook profiles 
that are associated with a politician, and we want to confirm that the `politician` in the database correctly matches 
the page's name and description. We've stored the page's description and other text in a `django_learning` Document, 
and we'll show that text alongside the name of the profile.  When we go through and verify these profiles, we'll 
be able to see this text, the name of the page, and the name of the politician it's linked to in the database, and 
flag whether or not the page has the correct politician.

Once you've set up all of the models you want to verify by inheriting from `VerifiedModel`, you'll need to make
and run migrations:

```
$ python manage.py makemigrations
$ python manage.py migrate
```

### Using the interface

Django Verifications provides templates and views for an interface, allowing you to easily verify all of the fields 
on any objects in your database, and make corrections to those values as needed. To access the interface, 
you just need to import the URLs specified in `django_verifications.urls` and navigate to the Django Verifications 
home page. 

### Managers

Any models that inherit from `VerifiedModel` will be given an extended `VerifiedModelManager` manager that overwrites 
the normal `objects` attribute on the model. This manager provides a variety of helper functions for accessing and 
filtering the objects on your model based on their verification status. Examples include `flagged_for_verification`, 
which returns a QuerySet of all of the objects on your model that have been flagged for verification based on the 
`verification_filters` metadata attribute, and `all_fields_good_or_corrected`, which returns all of the objects on your 
model that have had all of their verifiable fields (specified in `fields_to_verify`) examined, verified, and/or 
corrected.

### VerifiedFieldLock

Once a field on your model has been verified or corrected, the value is locked. All `VerifiedModel` instances have a 
modified save function that checks an objects related verifications and any attempt to modify a value that has been 
marked as correct will raise a `VerifiedFieldLock`.