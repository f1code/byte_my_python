Title: A Python-powered blog on AWS Cloudfront
Date: 2024-04-08 06:29
Category: Tools

To start this blog, naturally I wanted to use a Python tool.  I was attracted by the philosophy of
Jekyll for static site generation, and as it seems every language has his static site generator
(SSG) nowadays, I picked a popular Python equivalent: Pelican.  Why Pelican?  I actually started
with "Nikola", but ran into some issue as their published package did not support Python 3.11.
I decided to host it on Cloudfront, I have a lot of experience with the more "backend" AWS services so it should be a fun learning
experiment.

This short article serves to document my journey as a howto if you are interested in replicating it.

Create a repo for the blog.

Install pelican.  I used `yay -S pelican` on Arch Linux.  can also use `pip install
pelican[markdown]`, ideally within a Python virtual env.

Use `pelican-quickstart` to generate a skeleton.  Initially I had already created the `content`
folder and it errored out, but no biggy as it only serves to create an empty directory anyway.
