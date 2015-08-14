#Running the example application

Assuming you use virtualenv, follow these steps to download and run the
Spirit example application in this directory:


    $ git clone https://github.com/nitely/Spirit.git
    $ cd Spirit
    $ virtualenv venv
    $ source ./venv/bin/activate
    $ pip install .
    $ cd example
    $ python manage.py spiritinstall
    $ python manage.py runserver

You should then be able to open your browser on http://127.0.0.1:8000 and
see the Spirit homepage.

> This will run using the *developer* settings,
> which are not suitable for production environments.

> In production, you should create a `prod_local.py`,
> import the production settings `from .prod import *`
> and overwrite settings such as `SECRET_KEY`, `DATABASES` and `ALLOWED_HOSTS`.