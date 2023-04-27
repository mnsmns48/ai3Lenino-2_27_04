from datetime import datetime
import pytz


def date_out(date):
    m_date = datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S%z")
    tz = pytz.timezone("Etc/GMT-3")
    m_date_utc3 = tz.normalize(m_date.astimezone(tz))
    out_date = m_date_utc3.strftime("%d-%m-%Y %H:%M")
    return out_date
