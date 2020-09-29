.. _templates:

Templates
=========

Spirit templates can be overridden the regular
`Django way <https://docs.djangoproject.com/en/stable/howto/overriding-templates/>`_.
The issue with overriding is keeping up with all the changes a new Spirit
version may introduce to those templates. To avoid this, Spirit has some specific
templates that can be safely overridden.

.. _extend_the_html_head_section:

Extend the HTML head section
----------------------------

Extending the head section is the best way to override the CSS style,
add JS scripts, add some font, etc.

Let's override the theme colors to make it green-ish::

    {# templates/spirit/_base.html #}

    {% extends "spirit/_base.html" %}
    {% block custom_head_extra %}
      <style>
        :root {
          --st-text-prim: #e7e7e7;
          --st-text-sec: #c9c9c9;
          --st-bg-prim: #010e00;
          --st-bg-sec: #012700;
          --st-bg-ter: #012100;
          --st-bg-qua: #011a00;
          --st-bg-qui: #011500;
          --st-text-selected-prim: #5cba58;
          --st-highlight-prim: #830000;
          --st-text-button: var(--st-text-sec);
          --st-bg-input: var(--st-bg-qui);
          --st-bg-checkbox: #black;
          --st-bg-comment-user-admin: #979733;
          --st-bg-comment-user-mod: #2e8f38;
          --st-bg-comment-user-topic-owner: #2e658f;
          --st-bg-message-info: var(--st-bg-qui);
          --st-text-message-info: #023800;
          --st-bg-message-error: #5e0000;
          --st-bg-selection: white;
          --st-text-selection: black;
          --st-bg-unread: #13232f;
          --st-bg-comment-diff-ins: #979733;
          --st-bg-comment-diff-del: #5e0000;
        }
      </style>
    {% endblock %}

The ``templates`` folder must be next to the ``static`` and ``media``
folders.

There is a bunch more of CSS color variables in the
`Sass colors file <https://github.com/nitely/Spirit/blob/master/spirit/core/static/spirit/stylesheets/src/modules/_colors.scss>`_.
There is also a dark-mode that is active when the OS is in dark-mode, but
it can be set as the default or as the only theme the same way.

Extend other sections
---------------------

The HTML body can be extended as well, before and after
the Spirit layout section. This is useful to add an extra nav-bar
at the top, or to add some JS snippet or footer at the bottom.

Let's just add some minimal text this time::

    {# templates/spirit/_base.html #}

    {% extends "spirit/_base.html" %}
    {% block custom_before_spirit_body %}
      <div style="background-color:yellow;color:black;text-align:center;">
        My extra nav bar
      </div>
    {% endblock %}
    {% block custom_after_spirit_body %}
      <div style="background-color:yellow;color:black;text-align:center;">
        My extra footer
      </div>
    {% endblock %}

I've inlined the ``style`` in the elements, but a better way is to style things
in the head section, see :ref:`extend_the_html_head_section`.

Customize the site name/logo
----------------------------

The forum name can be set without overriding any template,
go to ``http://127.0.0.1:8000/st/admin/config/``, and change
the ``site name`` field.

The template can be overridden to include custom HTML,
such as an image::

    {# templates/spirit/_header.html #}

    {% extends "spirit/_header.html" %}
    {% block custom_header_logo %}
      <a
        style="line-height: 3rem;font-size: 1.75rem;color: var(--st-header-logo);"
        href="{% url "spirit:index" %}"
      >MyForum</a>
    {% endblock %}
