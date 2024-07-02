import re
import json
from datetime import datetime
from cerberus import Validator
from app.utils.string import validate_url, validate_email, validate_uuid, validate_slug
from app.utils.date import validate_iso8601


class ValidatorExtended(Validator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _validate_valid_email(self, email, field, value):
        """
        The rule's arguments are validated against this schema: {'type': 'boolean'}
        """
        if (email and value and not validate_email(value)):
            self._error(field, 'email is invalid')

    def _validate_valid_tel(self, tel, field, value):
        """
        The rule's arguments are validated against this schema: {'type': 'boolean'}
        """
        if (tel and value and not re.match('^\d{10,11}$', value)):
            self._error(field, 'tel is invalid')

    def _validate_valid_url(self, url, field, value):
        """
        The rule's arguments are validated against this schema: {'type': 'boolean'}
        """
        if (url and value and not validate_url(value)):
            self._error(field, 'url is invalid')

    def _validate_valid_slug(self, slug, field, value):
        """
        The rule's arguments are validated against this schema: {'type': 'boolean'}
        """
        if (slug and value and not validate_slug(value)):
            self._error(field, 'slug is invalid')

    def _validate_valid_random_generated_slug(self, slug, field, value):
        """
        The rule's arguments are validated against this schema: {'type': 'boolean'}
        """
        if (slug and value and not validate_slug(value, True)):
            self._error(field, 'slug is invalid')

    def _validate_valid_iso8601(self, constraint, field, value):
        """
        The rule's arguments are validated against this schema: {'type': 'boolean'}
        """
        if value:
            if constraint is True:
                if not validate_iso8601(value):
                    self._error(field, 'Must be a iso8601 format')
            else:
                if validate_iso8601(value):
                    self._error(field, 'Must not be a iso8601 format')

    def _validate_valid_ulid(self, constraint, field, value):
        """
        The rule's arguments are validated against this schema: {'type': 'boolean'}
        """
        if value:
            if constraint is True:
                if not validate_uuid(value, 'ulid'):
                    self._error(field, 'Must be a ulid format')
            else:
                if validate_uuid(value, 'ulid'):
                    self._error(field, 'Must not be a ulid format')

    def _validate_valid_uuid(self, constraint, field, value):
        """
        The rule's arguments are validated against this schema: {'type': 'boolean'}
        """
        if value:
            if constraint is True:
                if not validate_uuid(value, 'uuidv4'):
                    self._error(field, 'Must be a uuidv4 format')
            else:
                if validate_uuid(value, 'uuidv4'):
                    self._error(field, 'Must not be a uuidv4 format')

    def _validate_not_future_month(self, not_future_month, field, value):
        """ Test if the value is a future month.
            The rule's arguments are validated against this schema:
            {'type': 'boolean'}
        """
        if not_future_month and self._is_future_month(value):
            self._error(field, "Must not be a future month")

    def _is_future_month(self, value):
        """ Helper function to check if the provided month is in the future """
        try:
            input_year, input_month = map(int, value.split('-'))
            current_year, current_month = datetime.now().year, datetime.now().month
            # Check if the year-month is in the future
            return (input_year > current_year) or (input_year == current_year and input_month > current_month)
        except ValueError:
            return False  # In case of ValueError, it's not a valid year-month string


class NormalizerExtended(Validator):
    pass


class NormalizerUtils():
    def to_bool(v): return v.lower() in ('true', '1')
    def to_bool_int(v): return 1 if v.lower() in ('true', '1') else 0
    def trim(v): return v.strip(' \u3000') if type(v) is str else v
    def rtrim(v): return v.rstrip(' \u3000') if type(v) is str else v
    split = lambda v, dlt=',': v.split(dlt) if v else []
    def json2dict(v): return json.loads(v) if type(v) is str else None
    def zero_2pad(v): return str(v).zfill(2)
