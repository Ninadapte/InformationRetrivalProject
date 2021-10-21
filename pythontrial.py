from tkinter import Tk, filedialog
import glob
import os
from nltk.stem import PorterStemmer
import math


# use set instead of list


def getFiles(path):
    os.chdir(path)
    myFiles = glob.glob('*.txt')

    return myFiles


# opens the directory menu


def selectDirectory():
    root = Tk()  # pointing root to Tk() to use it as Tk() in program.
    root.withdraw()  # Hides small tkinter window.
    open_file = filedialog.askdirectory()  # Returns opened path as str
    return open_file


def postfix(infix_query):
    # precedance initialization
    precedence = {}
    precedence['NOT'] = 3
    precedence['AND'] = 2
    precedence['OR'] = 1
    precedence['('] = 0
    precedence[')'] = 0

    output = []
    operator_stack = []
    for token in infix_query:
        if token == '(':
            operator_stack.append(token)
        elif token == ')':
            operator = operator_stack.pop()
            while operator != '(':
                output.append(operator)
                operator = operator_stack.pop()

        elif token in precedence:
            if (operator_stack):
                current_operator = operator_stack[-1]
                while operator_stack and precedence[current_operator] > precedence[token]:
                    output.append(operator_stack.pop())
                    if operator_stack:
                        current_operator = operator_stack[-1]

            operator_stack.append(token)
            # output.append(operator_stack.pop())
        else:
            output.append(token.lower())

    while operator_stack:
        output.append(operator_stack.pop())
    return output


def AND_op(word1, word2):
    if (word1) and (word2):
        return list(set(word1).intersection(word2))
    else:
        return list(set())


def OR_op(word1, word2):
    return list(set(word1).union(word2))


def NOT_op(a, tot_docs):
    return list(set(tot_docs).symmetric_difference(a))


def finder(last_word_list, new_word_list):
    for y in last_word_list:
        for w in new_word_list:

            if w == y + 1:
                return True
    return False


def process_query_phrase(q, invrt_idx, path):
    tot_docs = getFiles(path)

    q = q.split(" ")
    found_files = []
    files_hold = []
    last_word = ""
    hold = 0
    for word in q:

        if word not in invrt_idx.keys():
            return []
        if len(files_hold) == 0:

            for x in invrt_idx[word].keys():
                files_hold.append(x)
                found_files.append(x)

            last_word = word

        else:

            if hold == 0:
                found_files.clear()
                hold = 1
            for file in files_hold:

                if file not in invrt_idx[word]:
                    files_hold.remove(file)
                    try:
                        found_files.remove(file)
                    except:
                        pass
                else:
                    try:
                        last_word_list = invrt_idx[last_word][file]
                        new_word_list = invrt_idx[word][file]

                        if finder(last_word_list, new_word_list):
                            found_files.append(file)
                        else:
                            files_hold.remove(file)
                    except:
                    #     files_hold.remove(file)
                          try:
                             found_files.remove(file)
                             files_hold.remove(file)
                          except:
                              pass
                         #return [found_files[0]]


            last_word = word

    return found_files


def formatterForPhrase(q):
    first = 0

    x = 0

    while x < len(q):

        if q[x] == "\"":
            x += 1
            while q[x] != "\"" and x < len(q):

                if q[x] == ' ':
                    q = q[:x] + '$' + q[x + 1:]

                x += 1
        x += 1

    return q


def getTermFrequency(total_files, table, table2, words):
    tf = {}
    # {
    # word1 : {file1 : 12 , file2 : 24},
    ##  word2 : {file3 : 11 , file4  : 4}
    # }

    for word in words:

        if '$' in word and "\"" in word:
            word = word.replace("$", " ")
            word = word.replace("\"", "")

            tf[word] = {}

            for file in total_files:
                count = table2.getCount(file, word)

                tf[word].update({file: count+1})

        else:

            tf[word] = {}
            for file in total_files:
                count = table.getCount(file, word)
                tf[word].update({file: count+1})

    return tf


def process_query(q, invrt_idx, path, table):
    table2 = TablePhrase(path)
    invrt_idx2 = table2.createTable()
    total_docs = 0
    q = formatterForPhrase(q)

    tf_dict = {}
    word_dict = {}
    word_list = []
    for holder in q.split(' '):
        if holder != 'and' and holder != 'AND' and holder != 'OR' and holder != 'or' and holder != 'not' and holder != 'NOT':
            word_list.append(holder)

    tot_docs = getFiles(path)
    total_docs = len(tot_docs)
    ps = PorterStemmer()
    q = q.replace('(', '( ')
    q = q.replace(')', ') ')
    q = q.split(' ')
    query = []

    for i in q:
        query.append(ps.stem(i))

    for i in range(0, len(query)):
        if query[i] == 'and' or query[i] == 'or' or query[i] == 'not':
            query[i] = query[i].upper()

    result_stack = []
    postfix_queue = postfix(query)
    # print(postfix_queue)
    # evaluate postfix query expression
    for i in postfix_queue:
        if (i != 'AND' and i != 'OR' and i != 'NOT'):

            if '$' not in i and "\"" not in i:
                i = i.replace('(', ' ')
                i = i.replace(')', ' ')
                i = i.lower()

                rec = invrt_idx.get(i)
                if (rec is not None and len(rec) != 0):
                    rec = set(rec)
                    rec = list(rec)
                    word_dict.update({i: len(rec)})

                    result_stack.append(rec)

                    result_stack[0] = set(result_stack[0])
                    result_stack[0] = list(result_stack[0])
                else:
                    word_dict.update({i: 0})

            else:

                i = i.replace("$", " ")
                i = i.replace("\"", "")

                rec = process_query_phrase(i, invrt_idx2, path)

                if (rec is not None and len(rec) != 0):
                    rec = set(rec)
                    rec = list(rec)
                    word_dict.update({i: len(rec)})

                    result_stack.append(rec)
                    result_stack[0] = set(result_stack[0])
                    result_stack[0] = list(result_stack[0])
                else:
                    word_dict.update({i: 0})

        elif (i == 'AND'):
            try:
                a = result_stack.pop()
                b = result_stack.pop()
                result_stack.append(AND_op(a, b))
            except:
                return {}

        elif (i == 'OR'):
            try:
                a = result_stack.pop()
            except:
                return {}
            try:
                b = result_stack.pop()
                result_stack.append(OR_op(a, b))
            except:
                result_stack.append(a)

        elif (i == 'NOT'):
            try:
                a = result_stack.pop()
            except:
                return {}
            if (a == None):
                result_stack.append(tot_docs)

            else:
                result_stack.append(NOT_op(a, tot_docs))
        if len(result_stack) != 0:
            result_stack[0] = set(result_stack[0])
            result_stack[0] = list(result_stack[0])

    if len(result_stack) != 0:
        total_files = result_stack.pop()
        tf_dict = getTermFrequency(total_files, table, table2, word_list)

        filels = []
        for file in total_files:
            c = 0

            mainls = []

            for word in word_dict:
                mainls.append(math.log((total_docs + 1) /
                              (int(word_dict[word])+1), 10))

            hld = []
            for x in word_list:
                if '$' in x and "\"" in x:
                    x = x.replace("$", " ")
                    x = x.replace("\"", "")
                    hld.append(x)
                else:
                    hld.append(x)
            # changed word_list to  word_dict
            for num in range(len(word_dict)):
                tf_word = 0
                if file not in tf_dict[hld[num]]:
                    tf_word = 0
                else:
                    tf_word = tf_dict[hld[num]][file]
                mainls[num] *= int(tf_word)

            filels.append(sum(mainls))

        ret = {}
        for x in range(len(filels)):
            ret.update({total_files[x]: filels[x]})

        ret = {k: v for k, v in sorted(ret.items(), key=lambda item: item[1])}

        print(ret)

        return ret
    else:
        return {}


class TablePhrase:
    myFiles = None

    def __init__(self, path):
        self.invrt_idx = {}
        self.directory = path

        self.common_stack = []
        self.query_result = set()
        # not has priority 3 , and has priority 2 , or has priority 1
        self.bool_stack = []

    def getFiles(self, path):
        os.chdir(path)
        myFiles = glob.glob('*.txt')
        Table.myFiles = myFiles
        return myFiles

    def getCount(self, file, word):

        with open(self.directory + "//" + file, 'r') as open_file:

            internal = ""
            for each in open_file:
                internal += each
                #each = each.split(" ")
                #for x in each:
                #    internal += " " + str(x)

        # open_file.close()

        return internal.count(word)+1

    def createTable(self):

        file_names = self.getFiles(self.directory)
        file = None
        for name in file_names:
            with open(self.directory + "//" + name, 'r') as file:

                line_hold = 0
                for each in file:

                    each = each.split(" ")
                    word_hold = 0
                    for word in each:
                        word = word.strip()

                        if word in self.invrt_idx:

                            # self.invrt_idx[word].append(name)
                            if name in self.invrt_idx[word]:
                                if word_hold + line_hold not in self.invrt_idx[word][name]:
                                    self.invrt_idx[word][name].append(
                                        word_hold + line_hold)
                            else:
                                self.invrt_idx[word].update(
                                    {name: [word_hold + line_hold]})

                        else:

                            self.invrt_idx[word] = {
                                name: [word_hold + line_hold]}
                        word_hold += 1

                    line_hold += 1

                # file.close()
        self.sortDict()

        return self.invrt_idx

    def removeDuplicates(self, l):
        res = []
        [res.append(x) for x in l if x not in res]
        return res

    def sortDict(self):
        # for x in sorted(dict["word1"]):
        # print({x : dict["word1"][x]})

        keys = self.invrt_idx.keys()
        for key in keys:
            hold = {}

            for x in sorted(self.invrt_idx[key]):
                hold.update({x: self.invrt_idx[key][x]})

            self.invrt_idx[key] = hold


class Table:
    myFiles = None

    def __init__(self, path):
        self.invrt_idx = {}
        self.directory = path

        self.common_stack = []
        self.query_result = set()
        # not has priority 3 , and has priority 2 , or has priority 1
        self.bool_stack = []

    def getFiles(self, path):
        os.chdir(path)
        myFiles = glob.glob('*.txt')
        Table.myFiles = myFiles
        return myFiles

    def getCount(self, file, word):
        with open(self.directory + "//" + file, 'r') as open_file:
            #open_file = open(self.directory + "//" + file, 'r')

            internal = ""
            for each in open_file:

                each = each.split(" ")
                for x in each:
                    internal += " " + str(x)
            #print("closed " + file)
            # open_file.close()
        return internal.count(word)

    def createTable(self):
        ps = PorterStemmer()
        file_names = self.getFiles(self.directory)
        for name in file_names:
            with open(self.directory + "//" + name, 'r') as file:
                #file = open(self.directory + "//" + name, 'r')

                for each in file:
                    each = each.split(" ")
                    for word in each:
                        word = word.strip()
                        word = ps.stem(word)
                        if word in self.invrt_idx:
                            self.invrt_idx[word].append(name)
                        else:
                            self.invrt_idx[word] = [name]
                # file.close()

        self.sortDict()

        return self.invrt_idx

    def removeDuplicates(self, l):
        res = []
        [res.append(x) for x in l if x not in res]
        return res

    def sortDict(self):
        keys = self.invrt_idx.keys()
        for key in keys:
            values = self.invrt_idx[key]
            values.sort()
            self.invrt_idx[key] = values

# def main():
#     path = selectDirectory()

#     table =  Table(path)
#     invrt_idx = table.createTable()
#     res = process_query("computer and science not apple", invrt_idx, path)
#     # print("The result is ")
#     # print(table.query_result)
#     print(res, "this is result")


# main()
