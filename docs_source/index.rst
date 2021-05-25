Django Verifications
===================================================================

Django Verifications is a lightweight coding interface to manually review and freeze various model attributes
using simple metadata toggles.  By specifying models as a `VerifiedModel` with the proper model metadata,
Django Verifications will expose a web interface for reviewing and confirming object attributes in your app.
For example, we found this to come in handy for reviewing and confirming the Facebook accounts of US congress members.
After loading in accounts from a variety of sources - many of which had errors - Django Verifications allowed us to
review each account manually and confirm that it was associated with the correct politician.  Once an account has been
verified, Django Verifications yells at you if you try to change that value - which can be very useful when your app
has a lot of moving parts, and maintaining data accuracy is of the utmost importance.

.. toctree::
   :maxdepth: 1
   :caption: Table of Contents:

   Installation <installation>
   Getting Started <getting_started>
   User interface <user_interface>
   Manager functions <managers>
   Model functions <models>



