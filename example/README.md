#Running the example application

Assuming you use virtualenv, follow these steps to download and run the
Spirit example application in this directory:


    $ git clone https://github.com/nitely/Spirit.git
    $ cd Spirit
    $ virtualenv venv
    $ source ./venv/bin/activate
    $ pip install .
    $ cd example
    $ python manage.py migrate
	$ python manage.py createcachetable spirit_cache
    $ export SECRET_KEY="My dev box"
    $ python manage.py runserver

> **Note:**
>
> When running on production, remember to set the SECRET_KEY environment 
> variable or use your own setting file to set it.
>
> If you want to give it a quick spin, run `$ python manage.py runserver --settings=project.settings.dev`

You should then be able to open your browser on http://127.0.0.1:8000 and
see the Spirit homepage.
