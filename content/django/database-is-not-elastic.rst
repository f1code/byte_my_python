Your database is not elastic!
=============================

:category: Django
:date: 2024-04-17
:summary: Reality of web development when dealing with elastic compute resources and a relational database

.. image:: images/elastic-database.jpeg
   :align: left
   :width: 300
   :alt: Image of a melting database server with a scared developer

This post stems from a recent experience with a web application that was not scaling as expected.  The application was designed to be able to scale horizontally, but the database was not.
This is a common problem in web development, and one that is often overlooked until it is too late.  The problem is that databases, especially relational databases,
are not as elastic as the rest of the application stack.  You can spin a new web server up in seconds, add some queue workers even faster, but the database is a different beast.
Because of the strict principles it has to adhere to in order to ensure data integrity and consistency through a convenient API, scaling it horizontally 
(adding more servers to share the load) is quite complex - read-only replicas are possible, but not particularly cheap or easy to set up (cloud vendors will 
make that easier of course).  Sharding is another option, but it is not trivial to implement and maintain (and can be quite costly too).
And then there is the problem of transactions that span multiple shards, which is a whole other can of worms.
You can scale it up (vertically) but that is not a sustainable solution.  Eventually you will hit the limits of the biggest server you can afford, and then what?
It can be counter intuitive.  In the early days of distributed application development, before the cloud, the database was often the only thing that could scale, and the application
was limited by the performance of the client machines, which were essentially not upgradeable (or at least not easily).  Now it is the other way around.

This reality hit home for me last week: a deployment which had been carefully planned and tested for weeks quickly went south
when it became obvious that too much of a burden was shifted to the database.  The web workers happily scaled out to try and
answer the requests faster, which actually compounded the problem since it added to the load on the one thing that would not,
could not scale: the database.  

Eventually we were able to resolve this with not too much broken bones by scaling up the database, until the application could be corrected.
The cloud managed database service made that easier but it was still not a seamless process (and is also rather costly since it can't automatically scale back down either).
And the feature had to be re-architected to be less database intensive - thankfully the change was rather isolated so we could turn that around quickly.

