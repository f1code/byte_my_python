A Python-powered blog on AWS Cloudfront
=======================================

:date: 2024-04-08 06:29
:category: Tools
:summary: Easy setup of a blog using a popular Python-powered static site generator and AWS tools.

To start this blog, naturally I wanted to use a Python tool.  I was attracted by the philosophy of
Jekyll for static site generation, and as it seems every language has his static site generator
(SSG) nowadays, I picked a popular Python equivalent: Pelican.  Why Pelican?  I actually started
with "Nikola", but ran into a few minor annoyances.  The Pelican package seems quite polished: they have a
large plugin repository, they support reStructuredText by default (and I liked that they used docinfo
for the metadata which seemed more appropriate than directives), and a modular architecture.  Their documentation
is pretty good too.  Importantly, having a static site generator means my data remains easily exploitable
by another engine, so it was not too important to spend much time on this decision now (indeed a large part
of the job of a software engineer is knowing which decisions are important to spend time on, which ones
can be deferred, and how to keep these decisions flexible).
I decided to host it on Cloudfront, I have a lot of experience with the more "backend" AWS services so it should be a fun learning
experiment (again, an easy to modify later decision).  Cloudfront used to be rather pricey but now has a generous free tier
that is more than sufficient for a personal blog.

This short article serves to document my journey as a howto if you are interested in replicating it.


Create a repo
-------------

The first step to anything :)
I picked github, by default.  Remember having to pick between RCS and CVS?  Yeah, I'm that old.

Install Pelican
---------------

I used ``pipenv install pelican``.   By default it does not have Markdown support.  Installing
with pipenv means it will be kept separate from the system packages and installed within its own isolated environment.
It's a good practice in general for Python development.  From that point on you have to prefix all commands with
``pipenv run``, or use ``pipenv shell`` to drop into a shell with the path to the virtual environment activated.

Generate blog skeleton
----------------------

Use ``pelican-quickstart`` (but actually ``pipenv run pelican-quickstart``!) to generate a skeleton.  Initially I had already
created the ``content`` folder and it errored out, but no biggy as it only serves to create an empty directory anyway.
When running the quickstart, enter the name of the S3 bucket you will publish to.  It doesn't have to exist yet.

I added a post under ``content`` so it would have something to show.  Pelican will automatically determine the category based
on the post path, so I put mine under ``content/tools//pelican-aws-cloudfront-blog.rst``.

At that point ``pelican -r -l`` will build and serve locally.  Pelican generated a Makefile so you can also do ``make
devserver``.  This was a nice touch, I like Makefile.  Just stop with Ctrl+C when done.


Push to AWS
-----------

You must have a correctly configured AWS CLI for this step.  Refer to the `Amazon documentation
<https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html>`_ for this.

#. First, create the bucket.  The easiest is to do it in the AWS console.  Make sure you uncheck "Block public access".
   Also check "ACLs Enabled".  The best practice is to leave ACL disabled, and create a policy, but it's a bit of a hassle and
   does not really make a difference in this case since we'll be the only one uploading to the bucket.

#. Run ``pipenv make s3_upload`` to upload the files.  You may have to edit the Makefile to correct the name of the bucket.
   I also edited the Makefile at that point to remove 

#. Create a CloudFront distribution in the AWS Console.  Specify the bucket as the "origin".  Leave the WAF (web application
   firewall) disabled.  Also change "Origin access" to public.  Again, it would be possible / best practice to specify this
   using a policy... but no real purpose here.  Lastly, set the "Default root object" to "index.html".  We'll come back later to
   configure the custom domain.
   Without configuring an alternate domain, CloudFront will set up a random
   ``cloudfront.net`` domain name I can use for testing (something like `d2dl3dxwttz643.cloudfront.net
   <https://d2dl3dxwttz643.cloudfront.net/>`_ I ran into some "Access Denied" error here... to troubleshoot, first run a curl
   command to retrieve the file directly from S3:

   .. code:: bash

    curl www.bytemypython.com.s3.us-east-1.amazonaws.com/index.html

   That got me "Access Denied" so I knew something was up with the bucket permissions.  I found that I had messed up one of
   the previous steps: I had left ACL disabled on the bucket.  I went back and re-enabled them through the console, and redid
   the upload.


#. Register a domain.  This is pretty easy with AWS Route53 and it will integrate with the rest.  Go to `AWS Route53 in the
   AWS Console <https://console.aws.amazon.com/route53/domains/home>`_, click Register Domain, and follow the prompt - it
   will take a little while to complete.
