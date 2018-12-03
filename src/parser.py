from flask import Markup

parse_dict = {
    'b[bold]': '<b>',
    'e[bold]': '</b>',

    'b[italic]': '<i>',
    'e[italic]': '</i>',

    'b[center]': '<span align=center>',
    'e[center]': '</span>',

    'b[small]': '<font size=8>',
    'e[small]': '</font>',

    'b[middle]': '<font size=12>',
    'e[middle]': '</font>',

    'b[large]': '<font size=16>',
    'e[large]': '</font>',

    'b[red]': '<font color=red>',
    'e[red]': '</font>',

    'u[nl]': '<br/>'
}

def parse_to_markup(s):
    for (key, val) in parse_dict.items():
        s = s.replace(key, val)

    return Markup(s)
