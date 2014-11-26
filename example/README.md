#Running the example application

Assuming you use virtualenv, follow these steps to download and run the
Spirit example application in this directory:


    $ git clone https://github.com/nitely/Spirit.git
    $ cd Spirit
    $ virtualenv venv
    $ . venv/bin/activate
    $ pip install .
    $ python manage.py migrate
	$ python manage.py createcachetable spirit_cache
    $ python manage.py runserver

You should then be able to open your browser on http://127.0.0.1:8000 and
see the Spirit homepage.

##Credits

This example project is inspired by django-allauth [example.](https://github.com/pennersr/django-allauth/tree/master/example)
