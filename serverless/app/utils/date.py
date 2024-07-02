from dateutil import parser, tz
from datetime import datetime, timezone, timedelta


def utc_iso(dt=None, use_zulu_format=True, scale='millisec'):
    if not dt:
        dt = datetime.utcnow()

    if scale == 'millisec':
        dt = dt.replace(tzinfo=timezone.utc)
        res = dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + '+00:00'

    elif scale == 'sec':
        res = dt.replace(tzinfo=timezone.utc, microsecond=0).isoformat()

    else:
        res = dt.replace(tzinfo=timezone.utc).isoformat()

    if use_zulu_format:
        res = res.replace('+00:00', 'Z')

    return res


def locale_iso_to_utc_iso(locale_iso_date_str):
    """
    Convert the given ISO date string to UTC ISO date string.
    ローカルのISO8601形式の日時文字列をUTCのISO8601形式の日時文字列に変換

    :param locale_iso_date_str: ISO formatted date string, e.g. "2020-01-01T00:00:00+09:00"
    :return: UTC ISO formatted date string, e.g. "2020-01-01T00:00:00Z"
    """
    dt = parser.isoparse(locale_iso_date_str)
    dt = dt.astimezone(timezone.utc)
    return utc_iso(dt)


def utc_iso_to_locale_date_str(utc_iso_date_str, timezone_str=None, format='%Y-%m-%d'):
    """
    指定されたUTCのISO8601形式の日時文字列を、指定されたタイムゾーン（もしくはシステムのローカルタイムゾーン）のフォーマットされた日付文字列に変換します。

    :param utc_iso_date_str: UTCのISO8601形式の日時文字列（例: "2020-01-01T00:00:00Z"）
    :param timezone_str: 変換する日時のタイムゾーン。指定されていない場合はシステムのタイムゾーンを使用します。
    :param format: 出力される日付文字列のフォーマット。デフォルトは '%Y-%m-%d' です。
    :return: 指定されたタイムゾーンのフォーマットされた日付文字列。
    """
    # ISO8601形式の文字列をdatetimeオブジェクトに変換
    dt_utc = parser.isoparse(utc_iso_date_str)

    # タイムゾーンが指定されていない場合はシステムのローカルタイムゾーンを取得
    tz_to_use = tz.gettz(timezone_str) if timezone_str else tz.tzlocal()

    # UTC datetimeを指定されたタイムゾーンに変換
    dt_local = dt_utc.astimezone(tz_to_use)

    # datetimeオブジェクトを指定されたフォーマットの文字列に変換
    return dt_local.strftime(format)


def date_str_by_local_iso(locale_iso_date_str, format='%Y-%m-%d'):
    """
    Convert the given ISO date string to a formatted date string in its original timezone.

    :param locale_iso_date_str: ISO formatted date string, e.g. "2020-01-01T00:00:00+09:00"
    :param format: Format for the output date string. Default is '%Y-%m-%d'.
    :return: Formatted date string in the original timezone.
    """
    dt = parser.isoparse(locale_iso_date_str)
    # dt_local = dt.astimezone()
    # return dt_local.strftime(format)
    return dt.strftime(format)


def calc_date_str(base_date_str, **timedelta_args):
    if base_date_str:
        base_dt = parser.parse(base_date_str)
    else:
        base_dt = datetime.now(timezone.utc)

    calculated_datetime = base_dt + timedelta(**timedelta_args)
    return utc_iso(False, True, calculated_datetime)


def validate_iso8601(value):
    if isinstance(value, str):
        try:
            parsed_date = parser.isoparse(value)
            return parsed_date is not None
        except (ValueError, TypeError):
            return False
    return False
