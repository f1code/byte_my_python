Title: Stop Fighting Circular Imports
Date: 2025-10-05
Modified: 2025-10-05
Category: Language
Tags: type-checking, import

> The code is good, but you are missing the type hints!

>> Oh, I know, but as soon as I add them, I get these circular import errors!

> Mmm, that's often a smell, let's dig a little

Sounds familiar?  Yet sometimes even when digging in, the design is fine, and the modules really need to import each other, especially if you want to keep things simple and not introduce a Java-style interface hierarchy.

Turns out, modern Python has a solution for this, in fact, several of them.  Let's check it out :) 

Here a simple example:

```python
# post.py
from models.user import User

class Post:
    def __init__(self, author: User):
        self.author = author

# user.py
from models.post import Post

class User:
    def __init__(self, name: str, posts: list[Post]):
        self.name = name
        self.posts = posts
```

This gives:

> ImportError: cannot import name 'Post' from partially initialized module 'models.post' (most likely due to a circular import) (/home/nico/scratch/models/post.py)

So, first solution, from PEP-563, was to be able to do the annotations as strings.

```python
class Post:
    def __init__(self, author: "User"):
        self.author = author
```

But that's not enough for most tools, you also need to tell it where to find `User`... yet you can't just import it as it would be back to a circular import, so you use a special "TYPE_CHECKING" guard:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.user import User 

class Post:
    def __init__(self, author: "User"):
        self.author = author
```

And finally you can turn on these string annotations for the whole module using a __future__ import:

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.user import User 

class Post:
    def __init__(self, author: User):
        self.author = author
```


Now, as often in Python, there are a few layers added over time.  For the full details, you'll want to read the PEPs: 

 * start with [PEP-563](https://peps.python.org/pep-0563/), which is rather simple, and is available **today** (and as early as Python 3.7)
 * then move on [PEP-649](https://peps.python.org/pep-0649/)
and its little sister [PEP-749](https://peps.python.org/pep-0749/).  They change the way this is done, but this won't be available until Python 3.14.

Then, under the hood things will be quite different and it won't use the "string" annotations anymore.  For most usage (when annotating code for static type hints), you will just be able to drop the `__future__` import.  
