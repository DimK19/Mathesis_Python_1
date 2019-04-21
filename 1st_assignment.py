from random import randint as r

flag = True # Boolean μεταβλητή για τον έλεγχο διακοπής του προγράμματος

# Είσοδος αριθμού από τον παίκτη
def read():
    while(True):
        print("Μάντεψε αριθμό (1, 100): ", end = "")
        x = input()
        if(x.isdigit() and int(x) in range(1, 101)): return x
        elif(x == "stop"): return -1

# Είσοδος απάντησης για νέο παιχνίδι
def prompt():
    while(True):
        p = input("Να ξαναπαίξουμε;(yes/no) ")
        if(p.lower() == "no"): return False
        elif(p.lower() == "yes"): return True

# Το παιχνίδι
def play():
    global flag
    ans = r(1, 100)

    guess = read()
    counter = 0

    while(True):
        if(guess == -1):
            flag = False
            return
        elif(int(guess) == ans):
            print("Το βρήκες με την %dη προσπάθεια" % (counter + 1))
            score = max(0, 10 - counter)
            print("Κέρδισες", score, "πόντους")
            return
        else:
            print("Ο κρυμμένος αριθμός είναι", "μικρότερος" if int(guess) > ans else "μεγαλύτερος")
            counter += 1
            guess = read()

# Κυρίως Πρόγραμμα
def main():
    global flag
    print("Οποιαδήποτε στιγμή μπορείτε να τερματίσετε το πρόγραμμα γράφοντας \"stop\"")
    
    while(flag):
        play()
        if(flag): flag = prompt() # πρώτα ελέγχεται αν flag == false για την περίπτωση που έχει εισαχθεί "stop"
     
main()
