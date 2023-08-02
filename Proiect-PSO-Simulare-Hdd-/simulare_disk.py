import re
import os


class Disk:
    def __init__(self):
        self.alloc_unit_size = 16  # UA
        self.total_units = 4096  # nr total de UA

        # reprezinta nr de unitati de alocare
        self.dimfat = (self.total_units * 2) // self.alloc_unit_size  # dim fat in cadrul harddisk
        self.dimroot = 64  # nr fisiere
        self.index_fis = self.dimfat + self.dimroot  # index start pt fisiere

        # disk matrix
        self.data = [[0] * (self.alloc_unit_size) for i in range(self.total_units)]
        # fat table ,1 pt fat 2 pt root 0 pt spataiu liber pentru fisiere
        self.fat_vector = [1] * self.dimfat + [2] * self.dimroot + [0] * (self.total_units - (self.dimfat + self.dimroot))

        self.root = [[0] * self.alloc_unit_size for i in range(self.dimroot)]

        # initfat, root
        self.write_fat_in_data()
        self.write_root_in_data()

    # count 0 in fatvector
    def avail_space(self):
        return self.fat_vector.count(0) * 16

    # writes fat on disk , pentru a reprezenta numarul (ultima unitate de pe disc) 4096 => avem nevoie de maxim 2 bytes
    # pentru a stoca numerele int din fat pe disk ele trebuie transformate in binar si impartite in bucati de cate doua
    # deoarece o unitate de aloc de pe disk are 16 "bits" (simuleaza) daca am pune direct valoare reprezentata in intreg
    # din fat in matricea care simuleaza discul , am consuma numai 8 "bits", pt a consuma toata unitatea trebuie sa impartim
    # acel int in doua bucati
    def write_fat_in_data(self, start_index=0):
        index_col = 0
        for row, val in enumerate(self.fat_vector):
            val = bin(val)[2:].zfill(16)  # transf in binar si impartim in doi bytes
            val_split1, val_split2 = val[:8], val[8:]

            # punem pe disk ,
            self.data[row // (self.alloc_unit_size // 2)][index_col % self.alloc_unit_size] = val_split1  # row // 16 rezulta mereu partea intreaga
            index_col += 1
            self.data[row // (self.alloc_unit_size // 2)][index_col % self.alloc_unit_size] = val_split2
            index_col += 1
            # acum pe disc doua intrari adiacente reprezinta un int din fat table
        #     print(row)
        # print(index_col)

    # writes root on disk
    def write_root_in_data(self):
        for i in range(self.dimfat, self.dimfat + self.dimroot):
            self.data[i] = self.root[i % self.dimroot]

    # create file
    def create_file(self, inp, mod=1):  # inp [nume, ext, dim] #mod = 1 num(implicit) 2 alfa 3 hex
        # find prima_ua
        prima_ua = -1
        for i in range(self.index_fis, self.total_units):  # cautam o unitate de aloc libera
            if self.fat_vector[i] == 0:
                prima_ua = i
                break

        root_unit_index = -1  # for file
        for i in range(self.dimroot):  # cautam o intrare in root libera
            if self.root[i][0] == 0 or self.root[i][0] == "?":
                root_unit_index = i
                break
        # if no space avail
        if prima_ua == -1 or root_unit_index == -1:
            print("failed! free memory not found")
            return -1
        else:
            unit_to_fill = prima_ua  # index unitate de aloc pentru fisier
            # nume,   ext,     dim,      prim_ua,   flag
            nume = [i for i in inp[0].ljust(8, "0")]  # deoarece nume trebuie sa consume 8 "bits" ljust adauga in dreapta 0 pana la lungime 8
            ext = [i for i in inp[1].ljust(3, "0")]

            dim = bin(int(inp[2]))[2:].zfill(16)
            dim_split1, dim_split2 = dim[:8], dim[8:]

            prima_ua = bin(prima_ua)[2:].zfill(16)
            prima_ua_split1, prima_ua_split2 = prima_ua[:8], prima_ua[8:]

            # nume 8,  ext 3, dim(impreuna 2), prima_ua(impreuna 2), flag 1
            self.root[root_unit_index] = nume + ext + [dim_split1] + [dim_split2] + [prima_ua_split1] + [prima_ua_split2] + [mod]  # adaugam in root

            dim_fisier = int(inp[2])
            # momentan trecem unitatea curenta ca fiind folosita
            self.fat_vector[unit_to_fill] = 3
            counter_ua_full = 0  # indica cand ua este plin
            alfacounter = 0  # for alpha fill

            while dim_fisier:  # scriem pe disc pana cand dimensiune fisier ajunge 0
                if counter_ua_full == self.alloc_unit_size:  # daca unitatea curenta este umpluta maxim
                    self.fat_vector[unit_to_fill] = 3  # momentan trecem unitatea curenta ca fiind folosita
                    for i in range(self.index_fis, self.total_units):  # cautam o unitate libera in fat
                        if self.fat_vector[i] == 0:  # daca am gasita una libera
                            self.fat_vector[unit_to_fill] = i  # unitatea curenta indica catre noua unitatate de alocare
                            unit_to_fill = i  # unitatea curenta
                            break
                    counter_ua_full = 0  # reset counter

                # numeric fill
                if mod == 1:
                    self.data[unit_to_fill][counter_ua_full] = counter_ua_full % 10  # num size
                # alfa fill
                elif mod == 2:
                    self.data[unit_to_fill][counter_ua_full] = chr(ord("A") + alfacounter)
                    alfacounter = (alfacounter + 1) % 26  # alfabet size
                # hex fill
                elif mod == 3:
                    self.data[unit_to_fill][counter_ua_full] = hex(counter_ua_full % 16)  # hex size

                counter_ua_full += 1
                dim_fisier -= 1

            #
            self.fat_vector[unit_to_fill] = 3  # ultima unitate de aloc a fisier
            self.write_fat_in_data()  # update fat, root
            self.write_root_in_data()
            print(f"{inp[0]}.{inp[1]} created succesfuly!")
            return True

    # readfile
    def read_file(self, name):
        # daca nume este de forma nume.txt
        if "." in name:
            name = name.split(".")[0]  # pastram doar nume

        # cautam fisier in root
        reading_ua_index = -1
        root_index = -1
        name_pentru_cautare = [i for i in name.ljust(8, "0")]
        for i in range(self.dimroot):
            if self.root[i][:8] == name_pentru_cautare:
                dim_fisier = int(self.root[i][11] + self.root[i][12], 2)  # transf in int
                reading_ua_index = int(self.root[i][13] + self.root[i][14], 2)  # transf in int
                break

        # daca nu a fost gasit
        if reading_ua_index == -1:
            print("file not found!")
            return -1

        print("-------- printing file --------")
        counter = 0  # index byte curent care trebuie citit
        while dim_fisier:  # cat timp nu am printat tot
            if counter == self.alloc_unit_size:  # daca counter == 16
                if self.fat_vector[reading_ua_index] != 3:  # daca cumva unitatea curenta nu este ultima
                    reading_ua_index = self.fat_vector[reading_ua_index]  # indexul de la care citim
                    counter = 0  # reset counter

            print(self.data[reading_ua_index][counter], end=" ")
            counter += 1
            dim_fisier -= 1
        print()

    # list files in root
    def dir_list(self, mod=0):
        print("listing files----")
        # normal print
        if mod == 0:
            for i in range(self.dimroot):
                if self.root[i][0] not in [0, "?"]:
                    nume = "".join([i for i in self.root[i][:8] if i != "0"])
                    ext = "".join([i for i in self.root[i][8:11] if i != "0"])
                    print(f"{nume}.{ext}")
        else:
            # detaliat
            for i in range(self.dimroot):
                if self.root[i][0] not in [0, "?"]:
                    nume = "".join([i for i in self.root[i][:8] if i != "0"])
                    ext = "".join([i for i in self.root[i][8:11] if i != "0"])
                    dim_fisier = int(self.root[i][11] + self.root[i][12], 2)
                    prima_ua = int(self.root[i][13] + self.root[i][14], 2)
                    flag = {1: "-num", 2: "-alfa", 3: "-hex"}.get(self.root[i][15])
                    print(f"{nume}.{ext}    size:{dim_fisier}, first_ua={prima_ua} tip_fisier: {flag}")  # tip fisier in sensul ce info contine, alfa num sau hex

            print(f"disk space in-use = {self.print_fat_in_use() * self.alloc_unit_size}")

    # check if filename exista deja
    def check_name_exists(self, name):
        if "." in name:
            name = name.split(".")[0]
        # cauta in root
        for i in range(self.dimroot):
            if self.root[i][0] not in [0, "?"]:  # daca nu e empty
                if "".join([i for i in self.root[i][:8] if i != "0"]) == name:  # daca nume fisier == nume dat de user
                    return True
        return False

    # delete a file
    def del_file(self, name):
        ext = None
        if "." in name:
            name, ext = name.split(".")[0], name.split(".")[1]
        current_ua = -1
        # cauta prima unitate de aloc folosita de fisier
        for i in range(self.dimroot):
            if self.root[i][0] not in [0, "?"]:
                if "".join([i for i in self.root[i][:8] if i != "0"]) == name:
                    if ext != None and ext == "".join([i for i in self.root[i][8:11] if i != "0"]):
                        current_ua = int(self.root[i][13] + self.root[i][14], 2)
                        self.root[i][0] = "?"  # marcam in root ca fisierul a fost sters
                        break
                    if ext == None:
                        current_ua = int(self.root[i][13] + self.root[i][14], 2)
                        self.root[i][0] = "?"  # marcam in root ca fisierul a fost sters
                        break
        if current_ua == -1:  # daca nu a fost gasit
            print(f"file '{name}' not found")
            return -1

        while current_ua != 3:  # cat timp current_ua nu este final de fisier
            next = self.fat_vector[current_ua]  # arata catre noua unitate folosita de fisier
            self.fat_vector[current_ua] = 0  # marcam ca fiind o unitate libera
            current_ua = next  #

        self.write_fat_in_data()
        self.write_root_in_data()
        print(f"file '{name}' deleted!")

    # formatare
    def format_disk(self):
        # confirmare pentru formatare
        confirm_overwrite = ""
        while confirm_overwrite not in ["y", "n"]:
            confirm_overwrite = input(f"Warning! All files will be lost, confirm? (y/n)").lower()
        if confirm_overwrite == "n":
            print("formatting canceled!")
            return -1

        # initializeaza disk ca la inceput
        self.data = [[0] * (self.alloc_unit_size) for i in range(self.total_units)]
        self.fat_vector = [1] * self.dimfat + [2] * self.dimroot + [0] * (self.total_units - (self.dimfat + self.dimroot))
        self.root = [[0] * self.alloc_unit_size for i in range(self.dimroot)]

        self.write_fat_in_data()
        self.write_root_in_data()
        print("disk formatted!")

    # copiere
    def copy_file(self, name, new_name):
        if "." in name:  # daca user a scris nume fisier ca nume.ext
            name = name.split(".")[0]  # nume devine doar nume , fara ext
        if "." in new_name:
            new_name = new_name.split(".")[0]  # la fel si numele copiei

        if self.check_name_exists(new_name):  # daca nume copie exista
            print(f"file '{new_name}' already exists!")
            return -1

        found = False
        # cauta fisier initial in root
        for i in range(self.dimroot):
            if self.root[i][0] not in [0, "?"]:
                if "".join([i for i in self.root[i][:8] if i != "0"]) == name:  # daca este gasit
                    ext = [x for x in "".join([i for i in self.root[i][8:11] if i != "0"]).ljust(3, "0")]  # extensia
                    dim_split1, dim_split2 = self.root[i][11], self.root[i][12]
                    of_prima_ua = int(self.root[i][13] + self.root[i][14], 2)
                    mod = self.root[i][15]
                    found = True

        if found:
            nf_prima_ua = -1
            for i in range(self.index_fis, self.total_units):
                if self.fat_vector[i] == 0:
                    nf_prima_ua = i
                    break

            root_unit_index = -1  # for file
            for i in range(self.dimroot):
                if self.root[i][0] == 0 or self.root[i][0] == "?":
                    root_unit_index = i
                    break
            # if no space avail
            if nf_prima_ua == -1 or root_unit_index == -1:
                print("failed! free memory not found")
                return -1

            unit_to_fill = nf_prima_ua  # index unitate de aloc pentru fisier
            new_name = [i for i in new_name.ljust(8, "0")]
            nf_prima_ua = bin(nf_prima_ua)[2:].zfill(16)
            nf_prima_ua_split1, nf_prima_ua_split2 = nf_prima_ua[:8], nf_prima_ua[8:]

            # nume 8,  ext 3, dim(impreuna 2), prima_ua(impreuna 2), flag 1
            self.root[root_unit_index] = new_name + ext + [dim_split1] + [dim_split2] + [nf_prima_ua_split1] + [nf_prima_ua_split2] + [mod]

            dim_fisier = int(self.root[root_unit_index][11] + self.root[root_unit_index][12], 2)

            counter_ua_full = 0
            while dim_fisier:
                # bucata de cod copiata de la create_file
                if counter_ua_full == self.alloc_unit_size:  # daca unitatea curenta este umpluta maxim
                    self.fat_vector[unit_to_fill] = 3  # momentan trecem unitatea curenta ca fiind folosita
                    for i in range(self.index_fis, self.total_units):  # cautam o unitate libera in fat
                        if self.fat_vector[i] == 0:  # daca am gasita una libera
                            self.fat_vector[unit_to_fill] = i  # unitatea curenta indica catre noua unitatate de alocare
                            unit_to_fill = i  # unitatea curenta
                            break
                    of_prima_ua = self.fat_vector[of_prima_ua]  # next ua from old file
                    counter_ua_full = 0  # reset counter

                # din fisier vechi in cel nou
                self.data[unit_to_fill][counter_ua_full] = self.data[of_prima_ua][counter_ua_full]

                counter_ua_full += 1
                dim_fisier -= 1

            self.fat_vector[unit_to_fill] = 3
            self.write_fat_in_data()
            self.write_root_in_data()
            print(f"file copied successfuly!")
            return 1

        # daca copierea nu s-a finalizat cu succes
        print(f"Warning: copying failed!")
        return -1

    def rename_file(self, name, new_name):
        if "." in name:  # daca user a scris nume fisier ca nume.ext
            name = name.split(".")[0]  # nume devine doar nume , fara ext
        if "." in new_name:
            new_name = new_name.split(".")[0]  # la fel si numele pt rename

        if self.check_name_exists(new_name):  # daca nume copie exista
            print(f"file '{new_name}' already exists!")
            return -1

        # cauta fisier initial in root
        for i in range(self.dimroot):
            if self.root[i][0] not in [0, "?"]:
                if "".join([i for i in self.root[i][:8] if i != "0"]) == name:  # daca este gasit
                    new_name = [i for i in new_name.ljust(8, "0")]
                    self.root[i][:8] = new_name
                    self.write_root_in_data()
                    print("file was renamed!")
                    return True

        # daca copierea nu s-a finalizat cu succes
        print(f"Warning! file: '{name}' was not renamed")
        return -1

    def defrag_disk(self):
        pass

    # print index al unitatilor de alocare folosite de fisiere
    def print_fat_in_use(self, afisare=0):
        empty = 0
        for i in range(self.dimfat + self.dimroot, self.total_units):
            if self.fat_vector[i] != 0:
                if afisare:
                    print(f"{i}", end=" ")
                empty += 1  # counter pentru nr de unitati
        if afisare:
            print(f"\ntotal units in use = {empty}")
        return empty

    # comanda de help cu lista comenzilor
    def help_cmd(self):
        print("create <filename> <size> <type> - create a file (type = alfa/num/hex)")
        print("read <filename> - read a file")
        print("del <filename> - delete a file")
        print("dir - list files")
        print("format - format disk")
        print("copy <filename> <newfilename> - copy a file")
        print("space - available disk space")
        print("fat state - prints the index of allocation units that are in-use by files")
        print("exit - exit program")

    # print disk matrix
    def print_data(self):
        for index, unit in enumerate(self.data):
            print(f"{index} {unit}")

    # pentru o simplificare a codului vom utiliza doar un fisier pentru a salva diskul
    # apelata de comanda "save" salveaza diskul in fisierul disk.txt
    def save_disk(self):
        if os.path.exists("disk.txt"):
            confirm_overwrite = ""
            while confirm_overwrite not in ["y", "n"]:
                confirm_overwrite = input("disk.txt already exists. Overwrite? (y/n): ")
            if confirm_overwrite == "n":
                return -1

        with open("disk.txt", "w") as f:
            f.write(str(self.data))

        print("disk saved successfully!")

    # functie load disk commanda pentru apelare este "load" incarca din fisierul curent daca exista disk.txt
    def load_disk(self):
        if not os.path.exists("disk.txt"):
            print("Warning! no disk to load!")
            return -1

        if self.print_fat_in_use() > 0:
            confirm_overwrite = ""
            while confirm_overwrite not in ["y", "n"]:
                confirm_overwrite = input("Warning!current disk is not empty all files will be lost confirm? (y/n): ")
            if confirm_overwrite == "n":
                return -1

        with open("disk.txt", "r") as f:
            self.data = eval(f.read())  #

        # scriem in fat de pe disk
        c_unit = 0
        for index, unitate in enumerate(self.data[: self.dimfat]):
            unitate = [int("".join(unitate[i] + unitate[i + 1]), 2) for i in range(0, len(unitate), 2)]
            self.fat_vector[c_unit : c_unit + 8] = unitate
            c_unit += 8
        c_root = 0
        # scriem in root de pe disk
        for root_unit in self.data[self.dimfat : self.dimfat + self.dimroot]:
            self.root[c_root] = root_unit
            c_root += 1

        print("disk loaded successfully!")


d = Disk()
# expresii regulate pentru comenzi
# create_pattern = r"^create \S+\.\S+ \d+|^create \S+\.\S+ \d+ -alfa|^create \S+\.\S+ \d+ -num|^create \S+\.\S+ \d+ -hex"
create_pattern = r"^create \S+\.\S+ \d+(?: -(?:alfa|num|hex))?$"  # create asd.txt 20 -alfa
read_pattern = r"^read \S+.\S+|^read \S+"  # read a.txt | read a
del_pattern = r"^del.+|^delete.+"  # del sau delete
copy_pattern = r"^copy \S+ \S+"
ren_pattern = r"^rename \S+ \S+"


print("Welcome! 💫💫💫")
while True:
    inp = input("$> ").lower()

    # devin true cand este gasit un pattern in input
    create_match = re.match(create_pattern, inp)
    read_match = re.match(read_pattern, inp)
    del_match = re.match(del_pattern, inp)
    copy_match = re.match(copy_pattern, inp)
    ren_match = re.match(ren_pattern, inp)

    if inp == "exit":
        break

    if create_match:
        inp = inp.lower().split()
        inp = inp[1].split(".") + inp[2:]  # scoate create din input [nume, ext, dim, flag]
        if len(inp[0]) > 8:
            print(f"Warning: filname too long! filename must be at most 8 chars!")
            continue
        if len(inp[1]) > 3:
            print(f"Warning: extension too long! ext must be at most 3 chars!")
            continue
        if len(inp) == 4:
            inp[3] = {"-num": 1, "-alfa": 2, "-hex": 3}.get(inp[3])  # transf flag in numar
        if d.check_name_exists(inp[0]):  # daca exista nume
            confirm_overwrite = ""
            while confirm_overwrite not in ["y", "n"]:
                confirm_overwrite = input(f"File {inp[0]}.{inp[1]} already exists, overwrite? (y/n)").lower()
            if confirm_overwrite == "n":
                continue
            d.del_file(name=inp[0])  # stergem fisier initial

        avail_space = d.avail_space()  # calc spatiu
        if int(inp[2]) <= avail_space:
            if len(inp) == 4:
                d.create_file(inp, mod=inp[3])  # daca avea flag -alfa num sau hex
            else:
                d.create_file(inp)  # fisier cu numere , default
            continue
        else:
            print(
                f"""Error Not Enough diskspace available
diskspace = {avail_space}
try deleting some files or creating a smaller file"""
            )
            continue

    if read_match:  # read
        inp = inp.lower().split()
        d.read_file(inp[1])
        continue
    if del_match:  # delete
        inp = inp.lower().split()
        d.del_file(inp[1])
        continue
    if copy_match:  # copiere
        inp = inp.lower().split()
        if len(inp[2]) <= 8:
            if d.check_name_exists(inp[1]):
                d.copy_file(inp[1], inp[2])
            else:
                print(f"file '{inp[1]}' not found")
        else:
            print(f"Warning: filname too long! filename must be at most 8 chars!")
        continue
    if inp == "dir":  # list files
        d.dir_list()
        continue
    if inp == "dir -a":  # list files detaliat
        d.dir_list(mod=1)
        continue
    if inp == "space":
        print(f"free space available = {d.avail_space()}")
        continue
    if inp == "format":  # formatare fara a schimba formatul discului , doar stergere
        d.format_disk()
        continue
    if inp == "fat state":  # unitati de alocare folosite de fisiere
        d.print_fat_in_use(afisare=1)
        continue
    if ren_match:  # rename
        inp = inp.lower().split()
        if d.check_name_exists(inp[1]):
            if len(inp[2]) > 8:
                print(f"Warning NEWFILENAME too long! filename must be at most 8 chars!")
                continue
            d.rename_file(inp[1], inp[2])
        else:
            print(f"file '{inp[1]}' not found")
        continue
    if inp in ["-help", "help"]:
        d.help_cmd()
        continue
    if inp == "data":
        d.print_data()
        continue
    if inp == "save":
        d.save_disk()
        continue
    if inp == "load":
        d.load_disk()
        continue

    print("invalid cmd try -help cmd for available commands")
