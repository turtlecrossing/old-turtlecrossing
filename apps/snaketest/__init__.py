# -*- coding: utf-8 -*-
"""
snaketest
=========
Make your Django test cases use underscores, the way Guido intended!
Also some more featureful asserts.

:copyright: (C) 2013 Matthew Frazier
:license:   MIT/X11, see package's LICENSE for details
"""
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
try:
    import six
except ImportError:
    from django.utils import six

class SnakeTestMixin(object):
    """
    This grants a collection of `assert_*` methods corresponding to everything
    in unittest in Pythons before 2.7, as well as some Django-specific
    helper methods.

    It doesn't touch the `setUp`/`tearDown` problem with a ten-foot pole.
    """
    # Aliases.
    def assert_equal(self, a, b, msg=None):
        return self.assertEqual(a, b, msg)

    def assert_not_equal(self, a, b, msg=None):
        return self.assertNotEqual(a, b, msg)

    def assert_is(self, a, b, msg=None):
        return self.assertIs(a, b, msg)

    def assert_is_not(self, a, b, msg=None):
        return self.assertIsNot(a, b, msg)

    def assert_raises(self, *args, **kwargs):
        return self.assertRaises(*args, **kwargs)

    def assert_true(self, x, msg=None):
        return self.assertTrue(x, msg)

    def assert_false(self, x, msg=None):
        return self.assertFalse(x, msg)

    def assert_none(self, x, msg=None):
        return self.assertIsNone(x, msg)

    def assert_not_none(self, x, msg=None):
        return self.assertIsNotNone(x, msg)

    def assert_in(self, x, y):
        return self.assertIn(x, y)

    def assert_not_in(self, x, y):
        return self.assertNotIn(x, y)

    def assert_isinstance(self, inst, cls, msg=None):
        return self.assertIsInstance(inst, cls, msg)

    def assert_not_isinstance(self, inst, cls, msg=None):
        return self.assertIsInstance(inst, cls, msg)

    def assert_instance(self, inst, cls, msg=None):
        return self.assertIsInstance(inst, cls, msg)

    def assert_not_instance(self, inst, cls, msg=None):
        return self.assertIsInstance(inst, cls, msg)

    def assert_almost_equal(self, a, b, msg=None):
        return self.assertAlmostEqual(a, b, msg)

    def assert_not_almost_equal(self, a, b, msg=None):
        return self.assertNotAlmostEqual(a, b, msg)

    # Object-related asserts!
    def assert_instances(self, iterable, cls, msg=None):
        for idx, obj in enumerate(iterable):
            self.assertIsInstance(obj, cls, msg or "object %d is wrong type" % idx)

    def assert_str(self, obj, rep, msg=None):
        self.assertEquals(six.text_type(obj), rep,
                          msg or "string representation incorrect")

    def assert_fields_equal(self, obj, **fields):
        """
        Checks that all of the fields of `obj` have the values listed
        in `fields`.
        """
        for attr, value in fields.items():
            self.assertEquals(getattr(obj, attr), value,
                              attr + "'s value does not match")

    # Validation-related asserts!
    def assert_model_validates(self, model):
        """
        Checks that a model validates. It does this by just calling
        `full_clean` and letting exceptions happen.
        """
        model.full_clean()

    def assert_not_model_validates(self, model, *all_codes, **field_codes):
        """
        Checks that a model does not validate. Pass error codes which should
        apply to the entire model as positional arguments, and error codes for
        specific fields as keyword arguments -- the key being the name of the
        field, and the value being a code or iterable thereof.
        """
        with self.assertRaises(ValidationError) as caught:
            model.full_clean()

        errors = caught.exception.error_dict
        if all_codes:
            self.assertEquals(set(errors.keys()),
                              set(field_codes.keys()) | set([NON_FIELD_ERRORS]))
            self.assertEquals(
                set(error.code for error in errors[NON_FIELD_ERRORS]),
                set(all_codes)
            )
        else:
            self.assertEquals(set(errors.keys()), set(field_codes.keys()))

        for field, codes in field_codes.items():
            self.assertIn(field, errors)

            if isinstance(codes, six.string_types):
                codes = set([codes])
            else:
                codes = set(codes)

            self.assertEquals(
                set(error.code for error in errors[field]),
                codes
            )

