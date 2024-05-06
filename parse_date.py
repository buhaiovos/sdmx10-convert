from datetime import datetime
from dataclasses import dataclass

@dataclass 
class ParsedDate:
    year:int
    quarter:int
    month:int
    weekYear:int
    week:int
    dayOfYear:int

def parse(dateStr:str) -> ParsedDate:
    date = datetime.strptime(dateStr, '%Y-%m-%d').date()
    
    year = date.year
    month = date.month

    weekYear, week, _ = date.isocalendar()

    quarter = (month - 1) // 3 + 1
    
    dayOfYear = datetime.fromisoformat(dateStr).timetuple().tm_yday

    return ParsedDate(year, quarter, month, weekYear, week, dayOfYear)