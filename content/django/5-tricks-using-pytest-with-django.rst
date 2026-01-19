My 5 Best Tricks using Pytest with Django
=========================================

:date: 2024-04-25
:category: Django
:summary:
:status: published

Test driven development is THE way I code, without compromise.  **Maybe** if I am doing a quick spike of throw away code...
or some strictly UI code that I know is going to evolve a lot... but anything on the backend, I always start with setting up tests.
Often I work with legacy or semi-legacy code bases that don't have good tests and a big part of the work is setting those up - after
that the code practically writes itself :)

Anyway, back to pytest.  Pytest is that awesome library and test runner for Python that makes it easy (well, easier) to write small and readable tests,
decoupling the part that is going to create all the bits of data that the test needs, from the test code itself.  It does this using 2 neat
features: fixtures, and test parametrization.  It also has a quite large ecosystem for integrating with application frameworks, like of course Django.

Of course, all the examples in the Django documentation, refer to the TestCase classes they provide, and it's not always straightforward to adapt
to pytest cases.  The big problem I ran into with TestCase is that they tend to lead to large, self-contained classes that become very hard to understand.
You can get away from that by crafting utility classes... or mixins for your test cases, etc... but if you have complex relationships between your models
this can devolve into a spiderweb since your utility methods have to account for the potential intricacies of the tests.  Fixtures are one way to
address that, and the big advantage they have is that they can be locally overridden as the test needs it - I will get to that. 

I had used pytest before, quite a bit, but I ran into some unique difficulties with Django that I wanted to document.  I am not going to go into
the details of pytest itself because there is already quite a lot about it, except in specific cases where the interaction with Django is important.

Install the pytest-django package
*********************************

Probably the first hit when you googled "pytest" and "django".  Install that.  It will give you a bunch of fixtures that you can use to
test the Django application.  The full documentation is at https://pytest-django.readthedocs.io/en/latest/ and worth a read.  The fixtures
I use the most are the ones related to the database (db, transactional_db), there are also some wrappers for the custom assertions
normally available through Django TestCase subclassing (like assertRedirects, assertTemplateUsed, etc) and some Django helpers
that are made available as fixtures instead (like rf for RequestFactory, client, or django_assert_num_queries)

One thing you have to do is to point pytest to your Django settings module.  You can do that by setting DJANGO_SETTINGS_MODULE in your pytest.ini
file (if it does not exist, create it in the root of your project):

.. code-block:: ini

    [pytest]
    DJANGO_SETTINGS_MODULE = myproject.settings


Using --reuse-db
****************

For us it was a big deal to be able to reuse the database between tests - initializing the schema from scratch takes about 15 minutes on a 
good day.  The --reuse-db flag is a lifesaver.  It will keep the database around between test runs, and only reinitialize the schema if
you add migrations.  Keep in mind that if you modify migrations, it will not pick that up - you have to either manually reset the test database,
or use the --create-db flag to force a new database to be created.

You can add that flag in your pytest.ini file:

.. code-block:: ini

    [pytest]
    addopts = --reuse-db

Understand transaction scope and database fixtures
**************************************************

This is a really important one to understand because the tests are less "self-contained" than with TestCase.
By default, pytest will prevent any database access.  This is a good thing, because it makes the tests run faster, and it makes it
easier to reason about the tests.  But sometimes you need to access the database, and that's where the fixtures come in.  ``pytest-django``
provides 2 different fixtures for this: ``db`` and ``transactional_db``.  Internally this will map to Django ``TestCase`` and ``TransactionTestCase`` 
classes.  The difference is that ``db`` will run the whole test within a transaction and roll it back at the end of the test.
``transactional_db`` will start by serializing the state of the whole database, then run the test without a transaction, and at the end
it will reset the database using the saved state.  This is useful if you need to test code that will manipulate transactions explicitly
or use multiple database connections.  With a large database it's also very slow.  Because pytest encourages small, focused tests, and
can use test parametrization to quickly generate a large number of tests, ``transactional_db`` can be **very** slow.  Another problem of
``transactional_db`` is that if the test crashes in an abnormal way (say, your computer crashes, or you run in a debugger and stop the session),
the cleanup will not run, and the database will be left in the dirty state.  Again these problems are not specific to pytest, they also
exists with ``TestCase`` and ``TransactionTestCase``, but as pytest lets you write more tests more easily you are more likely to run into them.

Generally, use no database if you can afford it (but often Django apps are designed to use the ORM extensively so this is not always possible),
or use the ``db`` fixture.  Use the ``transactional_db`` fixture only if you absolutely need to.

If you have fixtures that need to access the database, you have 2 choices:

 - you can have ``db`` or ``transactional_db`` as a dependency to the fixture.  But then this means the fixture, not the test, will decide how the
   db is managed (if multiple fixtures request different database fixtures, pytest will use ``transactional_db``).
 - you can request the fixture from the test itself.  I prefer this method because it makes it clear that the test is using the database.  You can
   put a mark at the module level, if all tests within the file are going to need the database.

Use django_db_blocker for custom database setup
***********************************************

This is where you absolutely need to master the concept of fixture scope.  By default, fixtures are function-scoped, which means that
they are created and destroyed for each test function.  This is also the case for the ``db`` and ``transactional_db`` fixtures, which means you
**cannot** have a fixture with a wider scope that uses the database.  This is a problem if you want to share fixtures between tests.
You can then use ``django_db_blocker`` to manually control the database access.  This is a context manager that will allow you to run code
that access the database.  You also need to request the ``django_db_setup`` fixture in that case, which runs once per session and ensures
the migrations are run on the test database.  Here is an example:

.. code-block:: python

    import pytest

    @pytest.fixture(scope='module')
    def my_model(django_db_setup, django_db_blocker):
        with django_db_blocker.unblock():
            # this runs once per module, but will be seen by all the tests
            some_complicated_model_setup_that_takes_a_long_time()
        yield
        with django_db_blocker.unblock():
            # I need to do this since nobody is going to do it for me!
            some_complicated_model_teardown()

    def test_my_model(my_model, db):
        # I run within a transaction
        assert my_model.objects.count() == 1
        # and at the end of the test, the transaction is rolled back

    def test_my_model_more(my_model, db):
        # I also run within a (different) transaction
        assert my_model.objects.count() == 1

Normally, with a function-scoped fixture, the ``my_model`` fixture would be created and destroyed for each test.  But with the ``module`` scope,
it only runs once.  Note how I still have to request the ``db`` fixture in the test, because I exited the context manager before the test,
so that the tests are still isolated from each other.

I don't really like this code because it is not very readable and it makes the tests less isolated.  
But if you absolutely have to do a long-running setup you might need this.
There is no equivalent to the class level ``setUpTestData`` of Django, because this conflicts with the concept of fixture scope in 
pytest - you have to achieve the same result by using a module-scoped fixture, but this also requires you to do a little bit of work
to ensure the database is properly set up and torn down.  The next tip will show a safer way to do this.

Use a larger-scope transaction for complex initialization
*********************************************************

By combining the above 2 tips, it is possible to offer a fixture that runs at a higher than function scope and provides a transactional
context.  The tests will then operate within their own, nested transaction, and will still be isolated from each other.
This is only possible if the database backend supports nested transactions (or savepoints, as Django will automatically use that within
a transaction).  Which is the case for most popular databases supported by Django.

You use ``django_db_blocker`` to open the transaction at a higher scope, ``yield`` within it so that your test function can run and
create a nested transaction within that scope, then close the transaction at the end of the test (simply by exiting the context manager).

Here is an example:

.. code-block:: python

    import pytest
    from django.db import transaction

    @pytest.fixture(scope='module')
    def my_model_transaction(django_db_setup, django_db_blocker):
        with (django_db_blocker.unblock(), transaction.atomic()):
            # this runs once per module, but will be seen by all the tests
            some_complicated_model_setup_that_takes_a_long_time()
            # yield within the transaction context
            yield
            # no need for teardown, since we use a transaction

    def test_my_model(my_model_transaction, db):
        # I run within a nested transaction
        assert my_model_transaction.objects.count() == 1
        # and at the end of the test, the transaction is rolled back
        # (but not the outer transaction which has the model setup)

    def test_my_model_more(my_model_transaction, db):
        # I also run within a (different) transaction
        assert my_model_transaction.objects.count() == 1

One big downside is that this cannot be combined with ``transactional_db`` since there is always a transaction running.  So if you have
even one test that needs to run without a transaction, this will not work.  In my case I had a pretty neat setup using this but realized
toward the end that some tests needed to run outside of the transaction, so I had to refactor the whole thing.

Sharing fixtures between Django apps
************************************

Something about scope and pytest_plugins vs import

Django TestCase still work!
***************************

Pytest will still pick up and run your Django TestCase classes.  This is useful if you have a lot of tests already written in that style, and you
don't want to convert them all at once.  You can run them in parallel with your pytest tests, and slowly convert them over time.

Bonus: Some useful links
*************************
