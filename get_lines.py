def get_lines(txt_file, expr):

    """
    get_lines(txt_file, expr)

    returns a list of lines of txt_file that match expr
    replaces grep -i expr txt_file
    """

    found_lines = []
    with open(txt_file, 'r') as infile:
        for line in infile:
            if not (line.find(expr) == -1):
                found_lines.append(line)
    return found_lines
