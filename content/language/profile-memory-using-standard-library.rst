Tracemalloc: using standard lib tools to profile Python memory usage
====================================================================

:status: draft
:summary: A useful trick for your bag of tools 

Python (from 3.4) includes a module to track resource usage: tracemalloc.  https://docs.python.org/3/library/tracemalloc.html



.. code-block:: python

   import tracemalloc

   tracemalloc.start()

   # take a snapshot
   snapshot = tracemalloc.take_snapshot()

   # get stats by line
   stats = snapshot.statistics('lineno', False)
   
   # display top 10
   for stat in stats[:10]:
    print(stat)
