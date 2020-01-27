# djangocms-equation

[![Test Status](https://github.com/s-weigand/djangocms-equation/workflows/Tests/badge.svg)](https://github.com/s-weigand/djangocms-equation/actions)
[![Documentation Status](https://readthedocs.org/projects/djangocms-equation/badge/?version=latest)](https://djangocms-equation.readthedocs.io/en/latest/?badge=latest)
[![Code Coverage](https://codecov.io/gh/s-weigand/djangocms-equation/branch/master/graph/badge.svg)](https://codecov.io/gh/s-weigand/djangocms-equation)
[![This project is using Percy.io for visual regression testing.](https://percy.io/static/images/percy-badge.svg)](https://percy.io/s-weigand/djangocms-equation)

[![Dependabot Status](https://api.dependabot.com/badges/status?host=github&repo=s-weigand/djangocms-equation)](https://dependabot.com)
[![Codacy code quality](https://api.codacy.com/project/badge/Grade/f3c0be01f67b43b082810a0d86a79b4d)](https://www.codacy.com/manual/s.weigand.phy/djangocms-equation?utm_source=github.com&utm_medium=referral&utm_content=s-weigand/djangocms-equation&utm_campaign=Badge_Grade)
[![Code style Python: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Code style TypeScript: prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg)](https://prettier.io/)

DjangoCMS plugin to write equations, utilizing KaTeX

![](./demo.gif)

- Free software: Apache Software License 2.0
- Documentation: <https://djangocms-equation.readthedocs.io>.

## Features

- Enables the use of LaTeX for equations with django-cms
- Live editing of LaTeX Code, via KaTeX

## Installation

Install the plugin from PyPi

```bash
$ pip install djangocms_equation
```

Add it to the installed apps in the `settings.py` of your django-cms
project.

```python
"INSTALLED_APPS": [..., "djangocms_equation"]
```

For the Equations to be properly displayed in `djangocms-text-ckeditor`,
while edit it, you need to add the css file to the allowed of ckeditor.
To do this simply add the following lines to the
`settings.py` of your django-cms project.

```python
CKEDITOR_SETTINGS = {
    "contentsCss": ["/static/djangocms_equation/css/change_form_template.css"]
}
```

**Note:**

The equations might be rendered properly in ckeditor-windows,when they
are added the first time. This can be fixed by saving the text plugin or
having another equation on the page.

## Credits

This package was created with
[Cookiecutter](https://github.com/cookiecutter/cookiecutter) and the
[audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage)
project template.
