from flask import Flask, render_template, request, redirect
from tkinter import Tk, filedialog
import os
import pythontrial
import summarization
from textblob import TextBlob
app = Flask(__name__)
files = []


class Variables:
    path = ""
    files = []
    files_scores = []
    summary = ""
    corrected_query = ""
    query = ""

    def getDirectory():
        root = Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        Variables.path = filedialog.askdirectory()
        root.destroy()
        root.mainloop()
        return Variables.path


def spellChecker(text):
    textblb = TextBlob(text)
    textCorrected = textblb.correct()
    return textCorrected


@app.route("/", methods=['GET', 'POST'])
def hello_world():

    if "select" in request.form:
        path = Variables.getDirectory()
        print(path)
        return redirect('/')

    if "search" in request.form:
        Variables.files = []
        query = request.form["search"]
        try:
            table = pythontrial.Table(Variables.path)
            Variables.query = query
            Variables.corrected_query = spellChecker(query)

            #Variables.phrase_table = invrt_idx2

            invrt_idx = table.createTable()
            file_score_dict = pythontrial.process_query(
                query, invrt_idx, Variables.path, table)
            res = list(file_score_dict.keys())
            # vals = [v for k,v in file_score_dict]
            vals = []
            for k in file_score_dict:
                vals.append(file_score_dict[k])
                Variables.files_scores.append(file_score_dict[k])

                # handle the phrase query here
            print(res, "this is our result with files")
            if res is not None:
                #     res = list(set(res))
                for file in res:
                    files.append(file)
                    Variables.files.append(file)

            print(Variables.files)
            Variables.files.reverse()
            Variables.files_scores.reverse()
            return redirect('/')
        except:
            pass
    return render_template('index.html', files=Variables.files, files_score=Variables.files_scores, query=Variables.query, corrected_query=Variables.corrected_query)


@app.route('/delete/<file>/<index>')
def delete(file, index):
    if(os.path.exists(Variables.path+"/"+file)):
        os.remove(Variables.path+"/"+file)
        Variables.files.remove(file)
        Variables.files_scores.pop(int(index))

    else:
        print("The path does not exist")
    # return redirect('/')
    return render_template('index.html', files=Variables.files, files_score=Variables.files_scores)


@app.route('/update/<file>', methods=['GET', 'POST'])
def update(file):
    file_path = Variables.path+"/"+file
    file_open = open(file_path)
    summary = summarization.generate_summary(file_path, 2)
    Variables.summary = summary
    if Variables.summary == "":
        Variables.summary = "No summary available"
    content = ""
    for each_line in file_open:

         content += each_line.strip()
    #content += file_open.read()

    if request.method == 'POST':
        title = request.form["title"]

        file_w = open(file_path, 'w')
        file_w.writelines(title)
        file_w.close()
        return render_template('index.html', files=Variables.files, files_score=Variables.files_scores)
    file_open.close()
    return render_template('update.html', file=file,  content=content, summary=Variables.summary)


if __name__ == '__main__':
    app.run(debug=True)
    # HOST = os.environ.get('SERVER_HOST', 'localhost')
    # try:
    #     PORT = int(os.environ.get('SERVER_PORT', '5555'))
    # except ValueError:
    #     PORT = 5555
    # app.run(HOST, PORT,debug = False)
