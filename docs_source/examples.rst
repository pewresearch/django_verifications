*************************************
Examples
*************************************

Django Verifications is designed to make it easier to check database
data for accuracy and make corrections where necessary. It also prevents
any accidental modifications to data once it’s been checked. Let’s take
a look at Logos, where we use Django Verifications to check our list of
politicians’ Facebook pages. We’ll take a look at Bernie Sanders’
personal Facebook page, which is an instance of the FacebookPage model
in Logos.

.. code:: ipython3

    bernie = FacebookPage.objects.get(facebook_id="124955570892789")
    bernie




.. parsed-literal::

    <FacebookPage: berniesanders (Bernard 'Bernie' Sanders)>



.. code:: ipython3

    type(bernie)




.. parsed-literal::

    logos.models.facebook.FacebookPage



Configuration
~~~~~~~~~~~~~

To configure Django Verifications, you need to tell it a few things:

1) Which tables you want to verify. You do this by simply having those
   models inherit from ``django_verifications.models.VerifiedModel``

.. code:: ipython3

    from django_verifications.models import VerifiedModel
    isinstance(bernie, VerifiedModel)




.. parsed-literal::

    True



2) Which fields on the table you want to verify. You do this by defining
   a ``fields_to_verify`` list as one of your model’s ``Meta``
   attributes

.. code:: ipython3

    FacebookPage._meta.fields_to_verify




.. parsed-literal::

    ['politician', 'is_official', 'account_type']



3) Which rows in the table you care about. You do this by defining
   Django filters in a ``verification_filters`` list in your model’s
   ``Meta`` attributes

.. code:: ipython3

    FacebookPage._meta.verification_filters




.. parsed-literal::

    [{'politician__isnull': False}]



4) What information you want to use when you’re coding. You do this by
   defining a custom ``get_verification_metadata()`` function on your
   model - it just needs to return a dictionary. If you don’t define
   this function, Django Verifications will just pull everything it can
   from the table

.. code:: ipython3

    bernie.get_verification_metadata()




.. parsed-literal::

    {'name': 'Bernie Sanders',
     'username': 'berniesanders',
     'city': 'Burlington',
     'state': <State: Vermont>,
     'link': 'https://www.facebook.com/berniesanders/',
     'category': 'Public Figure',
     'websites': ['https://berniesanders.com'],
     'about': 'This is the official page for Bernie Sanders. Join our political revolution!',
     'bio': None,
     'politician': "Bernard 'Bernie' Sanders --- latest term: Bernard 'Bernie' Sanders term as Senator of Vermont, U.S. Senate (Class 1), 2019 - 2025",
     'other_accounts': ['senatorsanders'],
     'facebook_id': '124955570892789'}



Verification objects
~~~~~~~~~~~~~~~~~~~~

Django Verifications provides an interface for verifying and correcting
data, but behind the scenes, what it’s actually doing is creating
associations between your app’s VerifiedModel models, and its own
Verification model. Let’s see everything we’ve verified in Logos:

.. code:: ipython3

    from django_verifications.models import Verification
    
    Verification.objects.all().count()




.. parsed-literal::

    22738



The Verification model actually has its own ``VerificationManager`` with
some handy filtering functions to help sort through everything.

.. code:: ipython3

    Verification.objects.available_model_names()




.. parsed-literal::

    ['politician', 'twitter_profile', 'facebook_page']



.. code:: ipython3

    Verification.objects.filter_by_model_name("facebook_page").count()




.. parsed-literal::

    10672



.. code:: ipython3

    Verification.objects.flagged_for_verification("facebook_page").count()




.. parsed-literal::

    3058



You usually don’t need to worry about this though - not only is
everything taken care of through the interface, but your own
``VerifiedModel`` instances also get their own ``VerifiedModelManager``
that provides all this functionality in the opposite direction, so
there’s no need to import anything from Django Verifications.

.. code:: ipython3

    FacebookPage.objects.flagged_for_verification().count()




.. parsed-literal::

    3058



Making corrections
==================

Let’s take a look at Bernie

.. code:: ipython3

    bernie.verifications.all()




.. parsed-literal::

    <VerificationManager [<Verification: Verification object (459124)>, <Verification: Verification object (459125)>, <Verification: Verification object (459126)>]>



.. code:: ipython3

    pd.DataFrame.from_records(bernie.verifications.values())




.. raw:: html

    <div>
    <style scoped>
        .dataframe tbody tr th:only-of-type {
            vertical-align: middle;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    
        .dataframe thead th {
            text-align: right;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>id</th>
          <th>field</th>
          <th>user_id</th>
          <th>timestamp</th>
          <th>is_good</th>
          <th>notes</th>
          <th>corrected</th>
          <th>content_type_id</th>
          <th>object_id</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>0</th>
          <td>459124</td>
          <td>politician</td>
          <td>2</td>
          <td>2021-05-25 11:26:08.845798</td>
          <td>True</td>
          <td></td>
          <td>False</td>
          <td>14</td>
          <td>1316</td>
        </tr>
        <tr>
          <th>1</th>
          <td>459125</td>
          <td>is_official</td>
          <td>2</td>
          <td>2021-05-25 11:26:47.201979</td>
          <td>True</td>
          <td></td>
          <td>True</td>
          <td>14</td>
          <td>1316</td>
        </tr>
        <tr>
          <th>2</th>
          <td>459126</td>
          <td>account_type</td>
          <td>2</td>
          <td>2021-05-25 11:26:47.207914</td>
          <td>True</td>
          <td></td>
          <td>True</td>
          <td>14</td>
          <td>1316</td>
        </tr>
      </tbody>
    </table>
    </div>



We’ve already verified everything, so if we try to change any of those
fields, we’ll get an error:

.. code:: ipython3

    bernie.account_type = None
    bernie.save()


::


    ---------------------------------------------------------------------------

    VerifiedFieldLock                         Traceback (most recent call last)

    <ipython-input-18-0656a88d47e0> in <module>
          1 bernie.account_type = None
    ----> 2 bernie.save()
    

    /apps/prod/logos/logos/models/facebook.py in save(self, *args, **kwargs)
        203             self.facebook_user.facebook_id = self.facebook_id
        204             self.facebook_user.save()
    --> 205         super(FacebookPage, self).save(*args, **kwargs)
        206 
        207     def update_from_json(self, page_data=None):


    /apps/prod/logos/src/django_verifications/django_verifications/models.py in save(self, *args, **kwargs)
         83                     if original_val != current_val:
         84                         setattr(self, field, original_val)
    ---> 85                         raise VerifiedFieldLock(
         86                             "Cannot modify field {} on object {} due to existing verification (currently '{}', "
         87                             "attempted to replace with '{}')".format(


    VerifiedFieldLock: Cannot modify field account_type on object berniesanders (Bernard 'Bernie' Sanders) due to existing verification (currently 'pol_personal', attempted to replace with 'None')


As a demonstration, though - let’s get rid of those verifications and
get Bernie back in the queue so we can check out the interface.

.. code:: ipython3

    bernie.verifications.all().delete()
    bernie.account_type = None
    bernie.save()

.. code:: ipython3

    print(FacebookPage.objects.flagged_for_verification().count())
    print(FacebookPage.objects.has_unexamined_fields().count())
    print(FacebookPage.objects.all_fields_good_or_corrected().count())
    print(FacebookPage.objects.any_field_incorrect().count())
    print(FacebookPage.objects.all_fields_examined().count())


.. parsed-literal::

    3058
    1
    3057
    0
    3057


**Let’s go into the interface and make corrections**
====================================================

https://logos.pewresearch.tech/verifications

.. code:: ipython3

    print(FacebookPage.objects.flagged_for_verification().count())
    print(FacebookPage.objects.has_unexamined_fields().count())
    print(FacebookPage.objects.all_fields_good_or_corrected().count())
    print(FacebookPage.objects.any_field_incorrect().count())
    print(FacebookPage.objects.all_fields_examined().count())

.. code:: ipython3

    print(FacebookPage.objects.flagged_for_verification().count())
    print(FacebookPage.objects.has_unexamined_fields().count())
    print(FacebookPage.objects.all_fields_good_or_corrected().count())
    print(FacebookPage.objects.any_field_incorrect().count())
    print(FacebookPage.objects.all_fields_examined().count())


.. parsed-literal::

    3058
    0
    3058
    0
    3058


.. code:: ipython3

    pd.DataFrame.from_records(bernie.verifications.values())




.. raw:: html

    <div>
    <style scoped>
        .dataframe tbody tr th:only-of-type {
            vertical-align: middle;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    
        .dataframe thead th {
            text-align: right;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>id</th>
          <th>field</th>
          <th>user_id</th>
          <th>timestamp</th>
          <th>is_good</th>
          <th>notes</th>
          <th>corrected</th>
          <th>content_type_id</th>
          <th>object_id</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>0</th>
          <td>459127</td>
          <td>politician</td>
          <td>2</td>
          <td>2021-05-25 14:19:49.404860</td>
          <td>True</td>
          <td></td>
          <td>False</td>
          <td>14</td>
          <td>1316</td>
        </tr>
        <tr>
          <th>1</th>
          <td>459128</td>
          <td>is_official</td>
          <td>2</td>
          <td>2021-05-25 14:19:49.418054</td>
          <td>True</td>
          <td></td>
          <td>False</td>
          <td>14</td>
          <td>1316</td>
        </tr>
        <tr>
          <th>2</th>
          <td>459129</td>
          <td>account_type</td>
          <td>2</td>
          <td>2021-05-25 14:20:43.635416</td>
          <td>True</td>
          <td></td>
          <td>True</td>
          <td>14</td>
          <td>1316</td>
        </tr>
      </tbody>
    </table>
    </div>



.. code:: ipython3

    bernie.account_type = None
    bernie.save()


::


    ---------------------------------------------------------------------------

    VerifiedFieldLock                         Traceback (most recent call last)

    <ipython-input-23-0656a88d47e0> in <module>
          1 bernie.account_type = None
    ----> 2 bernie.save()
    

    /apps/prod/logos/logos/models/facebook.py in save(self, *args, **kwargs)
        203             self.facebook_user.facebook_id = self.facebook_id
        204             self.facebook_user.save()
    --> 205         super(FacebookPage, self).save(*args, **kwargs)
        206 
        207     def update_from_json(self, page_data=None):


    /apps/prod/logos/src/django_verifications/django_verifications/models.py in save(self, *args, **kwargs)
         83                     if original_val != current_val:
         84                         setattr(self, field, original_val)
    ---> 85                         raise VerifiedFieldLock(
         86                             "Cannot modify field {} on object {} due to existing verification (currently '{}', "
         87                             "attempted to replace with '{}')".format(


    VerifiedFieldLock: Cannot modify field account_type on object berniesanders (Bernard 'Bernie' Sanders) due to existing verification (currently 'pol_personal', attempted to replace with 'None')


