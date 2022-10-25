import xlsxwriter


def writer(list_cars):
    book = xlsxwriter.Workbook(r'autoria_cars.xlsx')
    page = book.add_worksheet('skoda')

    row = 0
    column = 0

    page.set_column("A:A", 21)
    page.set_column("B:B", 30)
    page.set_column("C:C", 20)
    page.set_column("D:D", 8)
    page.set_column("E:E", 15)
    page.set_column("F:F", 60)
    page.set_column("G:G", 100)

    for item in list_cars:
        page.write(row, column, item[0])
        page.write(row, column+1, item[1])
        page.write(row, column+2, item[2])
        page.write(row, column+3, item[3])
        page.write(row, column+4, item[4])
        page.write(row, column+5, item[5])
        page.write(row, column+6, item[6])
        row += 1
    book.close()

