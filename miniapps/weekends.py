# Вывод выходных дней
import calendar

def get_year_month():
    year = int(input("Введите год \n"))
    month = int(input("Введите месяц (1-12) \n"))
    return year, month

def get_weekend(year, month):
    cal = calendar.monthcalendar(year, month)
    weekends = []

    for week in cal:
        if week[calendar.SATURDAY] != 0:
            weekends.append((week[calendar.SATURDAY], month, year, "Суббота"))
        if week[calendar.SUNDAY] != 0:
            weekends.append((week[calendar.SUNDAY], month, year, "Воскресенье"))
    return weekends

def display_weekends(weekends, month, year):
    print(f"Выходные дни в {calendar.month_name[month], year}")
    for weekend in weekends:
        print(f"{weekend[0]:02d}.{weekend[1]:02d}.{weekend[2]} - {weekend[3]}")

def main():
    year, month = get_year_month()
    weekend = get_weekend(year, month)
    display_weekends(weekend, month, year)

main()