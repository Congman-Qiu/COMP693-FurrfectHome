import datetime
from app.models.common_model import Season

# get the current year and month which 6MR form belong to
def get_current_season():
    now = datetime.datetime.now()
    year = now.year
    month = now.month

    if month > 6 and month <= 12:
        season_month = "December"       
    else:
        season_month = "June"

    return Season(year, season_month)

