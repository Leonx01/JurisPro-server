from datetime import datetime, timedelta


def datetime_format(utc_time_str, utc_offset=8, format="%Y-%m-%d %H:%M:%S"):
    """
    将 UTC 时间字符串转换为指定时区时间，并格式化输出。

    :param utc_time_str: UTC 时间字符串 (格式: "2025-03-19T15:24:48.000Z")
    :param utc_offset: 时区偏移量 (默认 UTC+8)
    :param format: 输出时间格式 (默认 "%Y-%m-%d %H:%M:%S")
    :return: 格式化后的时间字符串
    """
    # 解析 UTC 时间字符串
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%S.%fZ")

    # 转换到指定时区
    local_time = utc_time + timedelta(hours=utc_offset)

    # 格式化输出
    return local_time.strftime(format)
