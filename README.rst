==============
turtlecrossing
==============
This is the code that will eventually power <http://turtlecrossing.org/>.
Turtle Crossing (TXing for short) is a news aggregator in the style of
Hacker News or Reddit focused on the free and open source software community.

Right now, this repository includes the TXing project source, as well as
OSNAP, the Open Source News Aggregation Project. OSNAP is a bunch of reusable
apps, but until TXing is off the ground we're keeping them all in the same
repository to avoid having to put stuff on PyPI or make setup.py files or
do ridiculous things to Heroku to make dependencies update.


Prerequisites
=============
* python >= 2.7
* pip
* virtualenv
* A database


Getting Set Up
==============
First, clone the code from Git and `cd` into the directory.

Creating the environment
------------------------
Create a virtual Python environment for the project. ::

    $ virtualenv --no-site-packages --distribute env
    $ source env/bin/activate

Install requirements
--------------------
Install all the packages you'll need for the site. ::

    $ pip install -r requirements/local.txt

Configure project
-----------------
Edit the local settings file for your environment.
(This file will not be checked in to the git repository.)

    $ cp lug_site/__local_settings.py lug_site/local_settings.py
    $ $EDITOR lug_site/local_settings.py

Sync database
-------------
Create all the database tables etcetera.

    $ cd turtlecrossing
    $ python manage.py syncdb


Running a development server
============================
Now, to actually see the site:

    $ python manage.py runserver

Open <http://localhost:8000/> in your browser.
Congratulations! You have a Turtle Crossing!

