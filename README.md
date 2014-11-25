# Spirit [![Build Status](https://travis-ci.org/nitely/Spirit.png)](https://travis-ci.org/nitely/Spirit) [![Coverage Status](https://coveralls.io/repos/nitely/Spirit/badge.png)](https://coveralls.io/r/nitely/Spirit)

Spirit is a Python based forum built using the Django framework.

To see it in action, please visit [The Spirit Project](http://spirit-project.com/).

## Requirements

Spirit requires the following software to be installed:

* Python 2.7, 3.3 or 3.4 (recommended)
* Django 1.7
* PostgreSQL or MySQL or Oracle Database

## Dependencies

Check out the [requirements](https://github.com/nitely/Spirit/blob/master/requirements.txt) provided.

## Integration

Spirit can be integrated with any other Django application without much of a hassle.

The only thing to notice is that Spirit uses its own *AUTH_USER_MODEL*.

If you want to roll your own user app, your user model must inherit from `spirit.models.user.AbstractForumUser`.

If you want to extend the Spirit user model (adding new fields or methods),
your model must inherit from `spirit.models.user.AbstractUser`.

If you just want to integrate Spirit's user profile to your *existing* project
and you are using the default Django's user model, check out the [Spirit-User-Profile](https://github.com/nitely/Spirit-User-Profile) app.

## Installing (Advanced)

Check out the [example](https://github.com/nitely/Spirit/tree/master/example) provided.

In short:

Add `url(r'^', include('spirit.urls', namespace="spirit", app_name="spirit")),` to your *urls.py*

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

Run:

    pip install -r requirements.txt
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
