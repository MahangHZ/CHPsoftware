

class RemoveTheSame:
    def __init__(self, list_a):  # a是某二维数组
        self.after_removing = []
        self.after_removing.append(list_a[0])
        for compare in range(1, len(list_a)):
            duplicate_or_not = DuplicateOrNot(list_a[compare], self.after_removing)
            if duplicate_or_not.leave == 1:
                self.after_removing.append(list_a[compare])


class DuplicateOrNot:
    def __init__(self, component, the_list):  # component是元素(一维数组),the list是二位数组
        self.status = []  # 0 不留下 1 留下
        for l in range(0, len(the_list), 1):
            self.status.append(1)
            for q in range(0, len(component), 1):
                if component[q] != the_list[l][q]:
                    self.status[l] = 0
                    break
        if sum(self.status) == 0:
            self.leave = 1
        else:
            self.leave = 0


a = [[1, 2, 3, 4, 5], [2, 2, 3, 4, 5], [1, 2, 3, 4, 5], [1, 2, 3, 4, 5], [3, 3, 3, 3, 3]]
b = RemoveTheSame(a)
print(b.after_removing)
