# from loader import variants_db, users_db
# import openpyxl
#
# book = openpyxl.open(r'C:\Users\Wolfram\Downloads\ОГЭ ответы ФИПИ 2022.xlsx', read_only=True, data_only=True)
# sheet = book.active
#
# # # sheet[номер строки][индекс столбца].value
#
# # добавить варианты ОГЭ:
# for line in range(2, 21+1):
#     _line = []
#     for task in range(1, 12+1):
#         _line.append(sheet[line][task])
#     variants_db.add_variant(
#         title=f'Вариант #{line-1} ФИПИ 2022 ОГЭ',
#         answers={str(number): str(element.value).lower() for number, element in zip(range(1, 12+1), _line)},
#         type='OGE',
#         status='VIP',
#         source='Сборник ФИПИ 2022',
#     )
# # for i in variants_db.select_all_variants():
# #     if 20 <= i[0] <= 40:
# #         variants_db.delete_variant(variant_id=i[0])
#
# book_1 = openpyxl.open(r'C:\Users\Wolfram\Downloads\ЕГЭ ответы ФИПИ 2022.xlsx', read_only=True, data_only=True)
# sheet_1 = book_1.active
#
# # добавить варианты ЕГЭ:
# for line in range(2, 21+1):
#     _line = []
#     for task in range(1, 27+1):
#         _line.append(sheet_1[line][task])
#     variants_db.add_variant(
#         title=f'Вариант #{line-1} ФИПИ 2022 ЕГЭ',
#         answers={str(number): str(element.value).lower() for number, element in zip(range(1, 27+1), _line)},
#         type='EGE',
#         status='VIP',
#         source='Сборник ФИПИ 2022',
#     )
#
# for i in variants_db.select_all_variants():
#     print(i)
