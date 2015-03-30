# Spirit [![Build Status](https://travis-ci.org/nitely/Spirit.png)](https://travis-ci.org/nitely/Spirit) [![Coverage Status](https://coveralls.io/repos/nitely/Spirit/badge.png)](https://coveralls.io/r/nitely/Spirit)

Spirit is a Python based forum built using the Django framework.

To see it in action, please visit [The Spirit Project](http://spirit-project.com/).

## Requirements

Spirit requires the following software to be installed:

* Python 2.7, 3.3 or 3.4 (recommended)
* Django 1.8
* PostgreSQL or MySQL or Oracle Database

## Dependencies

Check out the [requirements](https://github.com/nitely/Spirit/blob/master/requirements.txt) provided.

## Installing (Advanced)

Check out the [example](https://github.com/nitely/Spirit/tree/master/example) provided.

In short:

Add `url(r'^', include('spirit.urls')),` to your *urls.py*

Add `from spirit.settings import *` to the top of your *settings.py* file,
otherwise you will have to setup all django's related constants (Installed_apps, Middlewares, Login_url, etc)

Run:

    pip install -r requirements.txt
    python manage.py migrate
    python manage.py createcachetable spirit_cache
    python manage.py collectstatic

> **Note:**
>
> You will need to setup a search engine,
> Spirit is configured to work with [Woosh](https://bitbucket.org/mchaput/whoosh/wiki/Home) by default.
>
> An email server is required, you can host your own (ie: [exim](http://www.exim.org/)),
> or hire an external service provider (ie: [Mandrill](http://mandrill.com/)).

Start a development server:

    python manage.py runserver

Visit (http://127.0.0.1:8000/)

> **Note:** On production, you would rather run Spirit on a real web server. ie: gunicorn + Nginx.
> Running Spirit on a [virtualenv](http://www.virtualenv.org) is adviced.

## Updating

> *Note:* If you are *upgrading* from any release *previous to v0.3*:
> * Add `AUTH_USER_MODEL = 'spirit.User'` (or your custom user model) to your `settings.py`.
> * Remove the `AbstractForumUser` from your custom user model (if you have one).
> * Change `spirit.models.AbstractUser` to `django.contrib.auth.models.AbstractUser` in your custom user model (if you have one).

Run:

    pip install -r requirements.txt
    python manage.py makemigrations
    python manage.py migrate
    python manage.py collectstatic
    python manage.py rebuild_index --noinput

## Contributing

Feel free to check out the source code and submit pull requests.

You may also report any bug or propose new features in the [issues tracker](https://github.com/nitely/Spirit/issues)

## Testing

The `runtests.py` script enable you to run the test suite of spirit.

- Type `./runtests.py` to run the test suite using the settings from the `tests` folder.
- Type `./runtests.py example` to run the test suite using the settings from the `example` folder.

## Copyright / License

Copyright 2014 [Esteban Castro Borsani](https://github.com/nitely).

Licensed under the [MIT License](https://github.com/nitely/Spirit/blob/master/LICENSE).

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
