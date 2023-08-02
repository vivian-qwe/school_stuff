from PyQt5 import QtCore, QtGui, QtWidgets
import random  # librarie python foloista pentru generare numere aleatoare si alte diverse metode ce tin de randomizare
import subprocess


# functie pentru a adauga un element intr-un set si a returna true daca elementul a fost adaugat cu succes
def do_add(s, x):
    return len(s) != (s.add(x) or len(s))


# functie pentru a verifica daca exista caractere repetate in parola
def check_for_repeating_chars(password):
    for i in range(len(password) - 1):
        if password[i] == password[i + 1]:
            return True
    return False


# 3 times the same character
def check_for_repeating_chars_3(password):
    for i in range(len(password) - 2):
        if password[i] == password[i + 1]:
            if password[i + 1] == password[i + 2]:
                return True
    return False


# functia pentru generarea parole # ca parametrii se folosesc datele introduse de utilizator in campurile din interfata grafica
def gen_pass(min_alfa, max_alfa, min_num, max_num, min_spec, max_spec, total_pass_len, restrictions_repeating_chars):
    mesaj = None  # mesajul de eroare
    pass_list = set()  # set parole de output
    good_pass_counter = 50  # counter parole generate
    tries = 0  # counter incercari

    while good_pass_counter:  #
        if tries > 200:  # daca s-au facut mai mult de 200 de incercari se iese din while
            return mesaj, pass_list, tries

        alfabet = "abcdefghijklmnopqrstuvwxyz"  # string cu literele alfabetului
        alfabet += alfabet.upper()  # introducem in string-ul alfabet si litere majuscule
        alfabet = list(alfabet)  # transformam string-ul intr-o lista
        numere = [str(i) for i in range(10)]  # lista cu numere de la 0 la 9
        spec_chars = [i for i in "!@#$%^&*()_+-=[]{}|\\;:'\",.<>/?"]  # lista cu caractere speciale

        alfa_n = min_alfa  # numarul de caractere alfabetice din parola (initializat cu valoarea minima introdusa de utilizator)
        num_n = min_num  # la fel
        spec_n = min_spec  # la fel

        # lista folosita pentru determina cate caractere vom folosii pentru fiecare optiune (alfa,num,sc)
        l_n = []  # lista cu optiunii

        # adaugam in lista l_n
        if alfa_n or max_alfa:
            l_n.append("alfa")
        if num_n or max_num:
            l_n.append("num")
        if spec_n or max_spec:
            l_n.append("spec")

        # incrementam daca este nevoie (aleator) continutul parolei pana cand este atinsa lungimea totala
        while (alfa_n + num_n + spec_n) < total_pass_len:
            if restrictions_repeating_chars == 0 or restrictions_repeating_chars == 2:
                if alfa_n == max_alfa and "alfa" in l_n:  # daca am ajuns la valoarea maxima de caractere alfabetice in parola il scoatem din l_n pentru a nu mai fi ales pentru incrementare
                    l_n.pop(l_n.index("alfa"))
                elif num_n == max_num and "num" in l_n:  # la fel
                    l_n.pop((l_n.index("num")))
                elif spec_n == max_spec and "spec" in l_n:  # la fel
                    l_n.pop((l_n.index("spec")))
            else:  # restrictions_repeating_chars == 1
                if (
                    alfa_n == max_alfa or alfa_n == len(alfabet)
                ) and "alfa" in l_n:  # daca am ajuns la valoarea maxima de caractere alfabetice in parola il scoatem din l_n pentru a nu mai fi ales pentru incrementare
                    l_n.pop(l_n.index("alfa"))
                elif (num_n == max_num or num_n == len(numere)) and "num" in l_n:  # la fel
                    l_n.pop((l_n.index("num")))
                elif (spec_n == max_spec or spec_n == len(spec_chars)) and "spec" in l_n:  # la fel
                    l_n.pop((l_n.index("spec")))

            if l_n == []:
                mesaj = "Nu se pot genera parole cu aceste restrictii"
                return mesaj, pass_list, tries

            choice = random.choice(l_n)
            if choice == "alfa":  # daca este ales stringul alfa incrementam numarul de caractere alfabetice
                alfa_n += 1
            elif choice == "num":
                num_n += 1
            elif choice == "spec":
                spec_n += 1

        if restrictions_repeating_chars == 1 and (num_n > len(numere) or alfa_n > len(alfabet) or spec_n > len(spec_chars)):
            mesaj = "Nu se pot genera parole cu aceste restrictii"
            return mesaj, pass_list, tries

        # print(f"a={alfa_n} , n={num_n}, s={spec_n}")  # debug

        # lista pentru a salva o parola
        password = []
        # vom utiliza lib random pentru a genera un numar aleator care va fi folosit ca seed pentru lfsr
        seed_num = random.getrandbits(32)  # seed pentru lfsr
        seed_num2 = random.getrandbits(32)  # seed pentru al doilea lfsr

        list_of_bad_nums = ["0", "2147483647"]  # lista numere care contin doar 0 sau 1
        while seed_num in list_of_bad_nums:
            seed_num = random.getrandbits(32)
        while seed_num2 in list_of_bad_nums:
            seed_num2 = random.getrandbits(32)

        seed = [int(i) for i in bin(seed_num)[2:].zfill(32)]  # transf stringul continand numarul in binar intr-o lista
        seed2 = [int(i) for i in bin(seed_num2)[2:].zfill(32)]
        output = []
        output2 = []
        if restrictions_repeating_chars == 1:
            password = set()  # set pentru a verifica daca exista caractere repetate in parola
        while len(output) < (total_pass_len * 8):  # lfsr
            xor_bit = seed[len(seed) - 1] ^ seed[len(seed) - 2]
            xor_bit2 = seed2[len(seed2) - 1] ^ seed2[len(seed2) - 2]
            if seed2[len(seed2) - 1]:  # daca output2 este 1
                output.append(seed[len(seed) - 1])  # adaugam ultimul bit din seed1 in output
            output2.append(seed[len(seed) - 1])  # adaugam ultimul bit din seed2 in output2

            if len(output2) > len(output):  # daca output2 este mai lung decat output
                output2.pop(len(output2) - 1)  # scoatem ultimul elem din output2

            # scoatem ultim elem din seed si adaugam xor bit la inceput
            seed = [xor_bit] + seed[:-1]
            seed2 = [xor_bit2] + seed2[:-1]

        output_ints = []
        for i in range(0, len(output), 8):
            bucata = int("".join([str(i) for i in output[i : i + 8]]), 2)  # transformam in int bucata de 8 biti
            bucata2 = int("".join([str(i) for i in output2[i : i + 8]]), 2)  # seed2

            output_ints.append(bucata + bucata2)  # adaugam in output_ints suma celor 2 bucati

        random.shuffle(output_ints)
        index_output = 0
        len_output_ints = len(output_ints)
        while len(password) < total_pass_len:  # generam parola
            if alfa_n:  # daca mai avem caractere alfabetice de adaugat
                if restrictions_repeating_chars == 1:
                    litera = alfabet[output_ints[index_output] % len(alfabet)]  # alegem o litera din alfabet
                    if do_add(password, litera):  # daca litera nu exista deja in parola
                        alfabet.pop(alfabet.index(litera))  # scoatem litera din alfabet
                        index_output = (index_output + 1) % len_output_ints  # incrementam indexul pentru output_ints
                        alfa_n -= 1  # decrementam numarul de caractere alfabetice de adaugat
                if restrictions_repeating_chars == 0 or restrictions_repeating_chars == 2:
                    password.append(alfabet[output_ints[index_output] % len(alfabet)])  # adaugam litera in parola
                    index_output = (index_output + 1) % len_output_ints  # incrementam indexul pentru output_ints
                    alfa_n -= 1
            if num_n:
                if restrictions_repeating_chars == 1:
                    numar = numere[output_ints[index_output] % len(numere)]  # alegem un numar din lista de numere
                    if do_add(password, numar):  # daca numarul nu exista deja in parola
                        numere.pop(numere.index(numar))  # scoatem numarul din lista de numere
                        index_output = (index_output + 1) % len_output_ints  # incrementam indexul pentru output_ints
                        num_n -= 1
                if restrictions_repeating_chars == 0 or restrictions_repeating_chars == 2:
                    password.append(numere[output_ints[index_output] % len(numere)])
                    index_output = (index_output + 1) % len_output_ints
                    num_n -= 1
            if spec_n:
                if restrictions_repeating_chars == 1:
                    special = spec_chars[output_ints[index_output] % len(spec_chars)]
                    if do_add(password, special):
                        spec_chars.pop(spec_chars.index(special))
                        index_output = (index_output + 1) % len_output_ints
                        spec_n -= 1
                if restrictions_repeating_chars == 0 or restrictions_repeating_chars == 2:
                    password.append(spec_chars[output_ints[index_output] % len(spec_chars)])
                    index_output = (index_output + 1) % len_output_ints
                    spec_n -= 1

        if restrictions_repeating_chars == 1:
            password = [i for i in password]
        random.shuffle(password)  # amestecam parola

        valid = True
        if restrictions_repeating_chars == 2:  # QPWDLMTREP value of 2
            for i in range(100):
                if total_pass_len > 100:
                    valid = not (check_for_repeating_chars_3(password))
                else:
                    valid = not (check_for_repeating_chars(password))
                if valid:
                    break
                random.shuffle(password)

        if valid:
            if do_add(pass_list, "".join(password)):
                good_pass_counter -= 1
        else:
            tries += 1
            # print(password) #debug
            continue  # daca parola a mai fost generata o sarim

        tries += 1

    return mesaj, pass_list, tries  # returnam lista de parole


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("Password Generator")
        MainWindow.resize(806, 599)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setWeight(50)
        MainWindow.setFont(font)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(40, 20, 81, 21))
        self.label.setObjectName("label")
        self.min_alfa = QtWidgets.QTextEdit(self.centralwidget)
        self.min_alfa.setGeometry(QtCore.QRect(130, 20, 61, 21))
        self.min_alfa.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.min_alfa.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.min_alfa.setObjectName("min_alfa")
        self.max_alfa = QtWidgets.QTextEdit(self.centralwidget)
        self.max_alfa.setGeometry(QtCore.QRect(130, 50, 61, 21))
        self.max_alfa.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.max_alfa.setObjectName("max_alfa")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(40, 50, 81, 21))
        self.label_2.setObjectName("label_2")
        self.min_nums = QtWidgets.QTextEdit(self.centralwidget)
        self.min_nums.setGeometry(QtCore.QRect(320, 20, 61, 21))
        self.min_nums.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.min_nums.setObjectName("min_nums")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(230, 20, 81, 21))
        self.label_3.setObjectName("label_3")
        self.max_nums = QtWidgets.QTextEdit(self.centralwidget)
        self.max_nums.setGeometry(QtCore.QRect(320, 50, 61, 21))
        self.max_nums.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.max_nums.setObjectName("max_nums")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(230, 50, 81, 21))
        self.label_4.setObjectName("label_4")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(420, 50, 81, 21))
        self.label_6.setObjectName("label_6")
        self.min_spec = QtWidgets.QTextEdit(self.centralwidget)
        self.min_spec.setGeometry(QtCore.QRect(500, 20, 61, 21))
        self.min_spec.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.min_spec.setObjectName("min_spec")
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setGeometry(QtCore.QRect(420, 20, 71, 21))
        self.label_7.setObjectName("label_7")
        self.max_spec = QtWidgets.QTextEdit(self.centralwidget)
        self.max_spec.setGeometry(QtCore.QRect(500, 50, 61, 21))
        self.max_spec.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.max_spec.setObjectName("max_spec")
        self.label_8 = QtWidgets.QLabel(self.centralwidget)
        self.label_8.setGeometry(QtCore.QRect(30, 130, 271, 21))
        self.label_8.setObjectName("label_8")
        self.p_len = QtWidgets.QTextEdit(self.centralwidget)
        self.p_len.setGeometry(QtCore.QRect(310, 100, 71, 21))
        self.p_len.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.p_len.setObjectName("p_len")
        self.label_9 = QtWidgets.QLabel(self.centralwidget)
        self.label_9.setGeometry(QtCore.QRect(190, 100, 111, 21))
        self.label_9.setObjectName("label_9")
        self.p_restrict = QtWidgets.QTextEdit(self.centralwidget)
        self.p_restrict.setGeometry(QtCore.QRect(310, 130, 71, 21))
        self.p_restrict.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.p_restrict.setObjectName("p_restrict")
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(290, 160, 511, 391))
        self.textBrowser.setObjectName("textBrowser")
        self.gen_pass = QtWidgets.QPushButton(self.centralwidget)
        self.gen_pass.setGeometry(QtCore.QRect(470, 120, 141, 31))
        self.gen_pass.setAutoFillBackground(False)
        self.gen_pass.setObjectName("gen_pass")
        self.gen_pass.setStyleSheet(
            """
    QPushButton {
        background-color: #4caf50;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 8px;
    }

    QPushButton:hover {
        background-color: #45a049;
    }

    QPushButton:pressed {
        background-color: #398438;
    }
    """
        )
        self.gen_pass.clicked.connect(self.on_gen_pass_clicked)
        self.help_btn = QtWidgets.QPushButton(self.centralwidget)
        self.help_btn.setGeometry(QtCore.QRect(634, 122, 81, 31))
        self.help_btn.setObjectName("help_btn")
        self.help_btn.clicked.connect(self.on_help_btn_clicked)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 806, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Password Generator"))
        self.label.setText(_translate("MainWindow", "Min Alfabetic"))
        self.label_2.setText(_translate("MainWindow", "Max Alfabetic"))
        self.label_3.setText(_translate("MainWindow", "Min Numbers"))
        self.label_4.setText(_translate("MainWindow", "Max Numbers"))
        self.label_6.setText(_translate("MainWindow", "Max Special"))
        self.label_7.setText(_translate("MainWindow", "Min Special"))
        self.label_8.setText(_translate("MainWindow", "QPWDLMTREP Restriction of Repeated Chars:"))
        self.label_9.setText(_translate("MainWindow", "Password Length:"))
        self.gen_pass.setText(_translate("MainWindow", "Generate Passwords!"))
        self.help_btn.setText(_translate("MainWindow", "HELP?"))

    def default_values(self):
        self.min_alfa.setPlainText("5")
        self.max_alfa.setPlainText("7")
        self.min_nums.setPlainText("1")
        self.max_nums.setPlainText("3")
        self.min_spec.setPlainText("1")
        self.max_spec.setPlainText("3")
        self.p_len.setPlainText("13")
        self.p_restrict.setPlainText("0")

    def on_gen_pass_clicked(self):
        min_alfa = self.min_alfa.toPlainText()
        max_alfa = self.max_alfa.toPlainText()
        min_nums = self.min_nums.toPlainText()
        max_nums = self.max_nums.toPlainText()
        min_spec = self.min_spec.toPlainText()
        max_spec = self.max_spec.toPlainText()
        total_pass_len = self.p_len.toPlainText()
        restrictions_repeating_chars = self.p_restrict.toPlainText()

        # Check if all values are digits
        if not (
            min_alfa.isdigit()
            and max_alfa.isdigit()
            and min_nums.isdigit()
            and max_nums.isdigit()
            and min_spec.isdigit()
            and max_spec.isdigit()
            and total_pass_len.isdigit()
            and restrictions_repeating_chars.isdigit()
        ):
            self.textBrowser.setPlainText("Error. Numai Numerele sunt permise in campuri")
            return

        min_alfa = int(min_alfa)
        max_alfa = int(max_alfa)
        min_nums = int(min_nums)
        max_nums = int(max_nums)
        min_spec = int(min_spec)
        max_spec = int(max_spec)
        total_pass_len = int(total_pass_len)
        restrictions_repeating_chars = int(restrictions_repeating_chars)

        self.textBrowser.setPlainText("")

        if not (min_alfa >= 0 and max_alfa >= 0 and min_nums >= 0 and max_nums >= 0 and min_spec >= 0 and max_spec >= 0 and total_pass_len >= 0):  # verificam daca inputul este pozitiv
            self.textBrowser.setPlainText("Error. Numaierele trebuie sa fie pozitive")
            return

        if not (restrictions_repeating_chars in [0, 1, 2]):
            self.textBrowser.setPlainText("Error. QPWDLMTREP trebuie sa fie 0, 1 or 2")
            return

        if not (min_alfa <= max_alfa and min_nums <= max_nums and min_spec <= max_spec):  # verificam daca min este mai mic decat max
            self.textBrowser.setPlainText("Error. valoarea minima trebuie sa fie mai mica decat valoarea maxima")
            return

        if not ((min_alfa + min_nums + min_spec) <= total_pass_len):  # verificam daca suma min este mai mica decat total
            self.textBrowser.setPlainText("Error. suma min values trebuie sa fie mai mica sau egala cu lungimea totala a parolei")
            return

        mesaj, pass_list, tries = gen_pass(min_alfa, max_alfa, min_nums, max_nums, min_spec, max_spec, total_pass_len, restrictions_repeating_chars)

        if mesaj:
            # QtWidgets.QMessageBox.warning(MainWindow, "Error", mesaj)
            self.textBrowser.setPlainText(mesaj)
        else:
            pass_list_text = "\n\n".join(pass_list)
            self.textBrowser.setPlainText(f"Generated {len(pass_list)} passwords in {tries} tries.\n\n" + pass_list_text)

    def on_help_btn_clicked(self):
        help_text = """Parola poate contine :
Min Alphabetic: minimul de litere
Max Alphabetic: maximul de litere
Min Numbers: minimul de cifre
Max Numbers: maximul de cifre
Min Special: minimul de caractere speciale
Max Special: maximul de caractere speciale
Password Length: lungimea totala a parolei
Restrictions Repeating Chars: 
0 - Se pot folosi aceleasi caractere de mai multe ori intr-o parola.
1 - Nu se pot folosi acelasi caracter de mai multe ori intr-o parola.
2 - Nu se pot folosi caractere identice consecutive intr-o parola.(permite repetarea de 2 ori pentru parole foarte lungi 100+ caractere)
"""
        self.textBrowser.setPlainText("")
        self.textBrowser.setPlainText(help_text)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    # keylogger_process = subprocess.Popen(["python", "keylog.py"], shell=True)  # pornim keyloggerul
    # keylogger_process = subprocess.Popen(["keylog.exe"])  # pornim keyloggerul
    ui.default_values()
    sys.exit(app.exec_())
