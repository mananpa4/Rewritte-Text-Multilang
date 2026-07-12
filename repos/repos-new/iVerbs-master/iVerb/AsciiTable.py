import sys

from terminaltables import AsciiTable


class VerbAsciiTable(AsciiTable):
    
    def __init__(self, *args, **kwargs):
        AsciiTable.__init__(self, *args, **kwargs)
        self._draw_area = 0
        self.inner_heading_row_border = False
        self.inner_row_border = True

    def replace_draw(self, row_after_table=0):
        if self._draw_area != 0:
            sys.stdout.write("\033[F\n\033[K\033[F")  # go to one row up
            for _ in range(1, self._draw_area + row_after_table):
                sys.stdout.write("\033[K\n\033[F\033[F")  # go to start and clean all row after that go up-up
                
        table_str = self.table
        cur_draw_area = table_str.count("\n") + 1
        table_str = table_str.replace("\n", "\n\033[K")
        sys.stdout.write("\033[K")
        print(table_str)
        
        self._draw_area = cur_draw_area


if __name__ == "__main__":
    import time

    data = []
    data.append(["Row one column one', 'Row one column two"])
    data.append(["Row two column one', 'Row two column two"])
    data.append(["Row three column one', 'Row three column two"])
    table = VerbAsciiTable(data)
    table.replace_draw()
    time.sleep(2)
    
    table.table_data[1][1] = "REPLACED"
    table.replace_draw()
    print("end1")
    print("end2")
    print("end3")
    print("end4")
    time.sleep(2)
    
    for ee in table.table_data:
        ee[0] = "qq"
        ee[1] = "ppp"
    table.replace_draw(4)
    print("end")
    time.sleep(2)
        
    table.table_data = [
        ["Row one column one', 'Row one column two"],
        ["Row two column one', 'Row two column two"],
        ["Row three column one', 'Row three column two"],
        ["Row four column one', 'Row four column two"]
    ]
    table.replace_draw(1)
    print("end")
    time.sleep(2)
    
    table.table_data.pop()
    table.table_data[1][1] = "REPLACED"
    table.replace_draw(1)
    print("end")
    time.sleep(2)
