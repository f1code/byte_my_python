Your database is not elastic!
=============================

:category: Django
:date: 2024-04-17
:summary: Reality of web development when dealing with elastic compute resources and a relational database

.. image:: images/database-melting.jpeg
   :width: 500
   :alt: Image of a melting database server with a scared developer

In the world of web applications, scalability is often celebrated as a key feature. Yet, amidst the hype of flexible infrastructure, one crucial element remains stubbornly inflexible: the database tier.

Unlike the nimble front-end and application layers that can effortlessly adjust to fluctuating demands, databases tend to lag behind in terms of adaptability. While the application servers can easily expand or contract based on load, databases often struggle to keep pace due to their inherent design constraints.

A major hurdle lies in the architecture of relational databases, which have long been the backbone of web development. These databases adhere to strict principles to ensure data integrity and consistency. While these principles are critical, they can make scaling a cumbersome task.

Scaling a relational database typically involves beefing up a single server, known as vertical scaling. While this can temporarily boost performance, it's not a sustainable solution. Eventually, even the mightiest servers hit their limits, leading to escalating costs and diminishing returns.

Horizontal scaling, the preferred method for achieving elasticity in distributed systems, poses its own challenges for relational databases. Splitting data across multiple instances while maintaining consistency is no easy feat. Techniques like sharding and replication can help, but they add complexity and overhead.

Non-relational databases offer some relief from these constraints. Document-oriented databases and key-value stores are more flexible, allowing for easier horizontal scaling. However, they may sacrifice some transactional guarantees, making them less suitable for certain applications.  Many tools that we take for granted working with a relational database are no longer applicable
when coding a web application for these new(ish?) beasts.

In reality, many web applications struggle with their rigid database tiers. Surges in traffic can overwhelm databases, leading to slowdowns or outages. Conversely, periods of low activity result in wasted resources and unnecessary costs.

This reality hit home for me last week: a deployment which had been carefully planned and tested for weeks quickly went south
when it became obvious that too much of a burden was shifted to the database.  The web workers happily scaled out to try and
answer the requests faster, which actually compounded the problem since it added to the load on the one thing that would not,
could not scale: the database.

Eventually we were able to resolve this with not too much broken bones by scaling up (vertically) the database, until the application could be corrected.  The cloud managed database service made that easier but it was still not a seamless process
(and is also rather costly since it can't automatically scale back down either).
