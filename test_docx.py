from doc import DocTemplate

d = DocTemplate('1.docx')


# {{ LastName:Имя }} {{ FirstName:Фамилия }}

path = d.fill_template({"LastName": "Мое имя", "FirstName": "Фамилия типо"})

print(f"{path=}")

# print(d.get_patterns_from_template())
