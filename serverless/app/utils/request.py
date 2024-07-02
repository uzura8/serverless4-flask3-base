import os
from app.utils.error import InvalidUsage
from app.validators import ValidatorExtended


def validate_req_params(schema, params=None, accept_keys=None):
    target_schema = {}
    target_vals = {}
    if params:
        for key, val in params.items():
            if accept_keys and key not in accept_keys:
                raise InvalidUsage('Field {} is not accepted'.format(key), 400)

            if key in schema:
                target_schema[key] = schema[key]
                target_vals[key] = val
            elif key not in schema and schema.get(key, {}).get('default') is not None:
                target_vals[key] = schema[key]['default']

    # スキーマに存在するがparamsに含まれていない場合、default値を設定する
    for key, details in schema.items():
        if key not in target_vals and 'default' in details:
            target_vals[key] = details['default']

    v = ValidatorExtended(target_schema, allow_unknown=True)
    if not v.validate(target_vals):
        msg = 'Validation Failed'
        field_errs = []
        err_dict = v.errors
        for key, errs in err_dict.items():
            for err in errs:
                field_errs.append({
                    'field': key,
                    'message': err,
                })

        raise InvalidUsage(msg, 400, {'errors': field_errs})

    return v.document


def validate_params(schema, req_params, add_params=None):
    req_params = req_params if req_params else {}
    # req_params = req_params.to_dict()
    params = {**req_params, **add_params} if add_params else req_params
    vals = validate_req_params(schema, params)
    return vals


def get_uploaded_file_size(req_file):
    req_file.seek(0, os.SEEK_END)
    file_size = req_file.tell()
    req_file.seek(0)  # reset file pointer
    return file_size
