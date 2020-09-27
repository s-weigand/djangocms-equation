# taken from
# https://github.com/divio/djangocms-attributes-field/blob/master/tests/test_migrations.py
# original from
# http://tech.octopus.energy/news/2016/01/21/testing-for-missing-migrations-in-django.html


from django.core.management import call_command
from django.test import TestCase
from django.test import override_settings
from django.utils.six import StringIO
from django.utils.six import text_type


class TestMigrations(TestCase):
    @override_settings(MIGRATION_MODULES={})
    def test_for_missing_migrations(self):
        output = StringIO()
        options = {
            "interactive": False,
            "dry_run": True,
            "stdout": output,
            "check_changes": True,
        }

        try:
            call_command("makemigrations", **options)
        except SystemExit as e:
            status_code = text_type(e)
        else:
            # the "no changes" exit code is 0
            status_code = "0"

        if status_code == "1":
            self.fail("There are missing migrations:\n {}".format(output.getvalue()))
