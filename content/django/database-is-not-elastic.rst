Your database is not elastic!
=============================

:category: Django
:date: 2024-04-17
:summary: Reality of web development when dealing with elastic compute resources and a relational database

Recently, I had a tough experience with a web app that didn’t scale as planned. We built the app to easily add more servers, but the database couldn’t keep up. This is a common issue in web development and often gets overlooked until it’s too late. Databases, especially relational ones, aren’t as flexible as other parts of the app. While you can quickly add more web servers or queue workers, scaling a database horizontally (adding more servers) is tricky and costly.

You can create read-only replicas, but setting them up isn’t easy or cheap. Sharding, another option, involves splitting the database into pieces, but it’s complicated and expensive. Handling transactions across these pieces is also a headache. Scaling up (making one server bigger) isn’t a long-term fix. Eventually, you’ll hit the limit of the biggest server you can afford.

It’s a strange reversal. In the past, when I worked on distributed apps like Windows-based CRM systems, the database was often the only part that could scale, while client machines couldn’t. Now, it’s the opposite.

.. image:: images/desktop_vs_web_app_scaling.png
    :alt: Desktop vs Web App Scaling
    :align: center

This reality hit home for me last week: a deployment which had been carefully planned and tested for weeks quickly went south
when it became obvious that too much of a burden was shifted to the database.  The web workers happily scaled out to try and
answer the requests faster, which actually compounded the problem since it added to the load on the one thing that would not,
could not scale: the database.  

Eventually we were able to resolve this with not too much broken bones by scaling up the database, until the application could be corrected.
The cloud managed database service made that easier but it was still not a seamless process (and is also rather costly since it can't automatically scale back down either).
And the feature had to be re-architected to be less database intensive - thankfully the change was rather isolated so we could turn that around quickly.

This experience taught us an important lesson: databases are a critical part of web development that require careful planning to avoid major problems down the line.
