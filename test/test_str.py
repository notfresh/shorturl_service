a = '124{}'
a= a.format(123)
print(a)

mode_mapping = {
    "jj": "https://juejin.cn/search?query=%22{}%22",
    "cls": "https://dict.youdao.com/search?q={}&keyfrom=new-fanyi.smartResult",
    "gh": "https://github.com/{}?tab=repositories"
}

def comma_mode(input_string):
    if ':' not in input_string:
        return input_string
    segments = input_string.split(':')    
    key = segments[0]
    if key in mode_mapping:
        template = mode_mapping[key]
        value = segments[1]
        if " " in value:
            value = value.replace(" ", "%20")
        formatted = template.format(value)
        return formatted
    else:
        print("The string does not contain a colon.")
        return input_string        

print(comma_mode("jj:xxx"))
print(comma_mode("jj:spring admin"))
print(comma_mode("cls:acurate"))
print(comma_mode("cls:ad hoc"))
print(comma_mode("gh:iefnaf"))
