# mathesis.cup.gr
# N. Αβούρης: Εισαγωγή στην Python
# Μάθημα 22. Τελική εργασία
# bbcnews
'''
Ο βρετανικός ειδησεογραφικός οργανισμός BBC διαθέτει το μεγαλύτερο δίκτυο οπτικοακουστικών και
διαδικτυακών μεταδόσεων ανά τον κόσμο και παρέχει ιδιαίτερα πλούσια κάλυψη όλου του πλανήτη.
Μεταξύ των άλλων το BBC διαθέτει υπηρεσία απευθείας αναφοράς ειδήσεων για διάφορες κατηγορίες
με μορφή rss (really simple syndication).
Στην άσκηση αυτή ζητείται να κατασκευαστεί μια εφαρμογή που ενημερώνει τον χρήστη για ειδήσεις
για διάφορες περιοχές του κόσμου, με βάση τα ενδιαφέροντά του.
1. Κάθε χρήστης ορίζει την περιοχή που τον ενδιαφέρει και για κάθε κατηγορία αν το επιθυμεί
ορίζει συγκεκριμένους όρους αναζήτησης (πχ χώρες).
2. Οι επιθυμίες των χρηστών αποθηκεύονται σε αρχείο user_profiles.csv
3. Κάθε φορά που ξεκινάει η εφαρμογή αναζητάει για τον συγκεκριμένο χρήστη τρέχουσες ειδήσεις
με βάση τα ενδιαφέροντά του.
4. Η εφαρμογή θα πρέπει να υποστηρίζει τη διαχείριση χρηστών και των προφίλ τους.
'''

import os.path
import urllib.request
import urllib.error
import re
import datetime
import utilities

# τα ονόματα αρχείων και φακέλων
dirname = '.'
data_dir = os.path.join(os.getcwd(), dirname) # φάκελος για αποθήκευση δεδομένων εφαρμογής
feeds_file = os.path.join(data_dir, "bbcfeeds.csv") # αρχείο με κατηγορίες από rss feeds
users_file = os.path.join(data_dir, "user_profiles.csv") # αρχείο με προφιλ χρηστών
WIDTH = 70  #πλάτος κειμένου είδησης

# καθολική μεταβλητή
user = {} # καθολική μεταβλητή τύπου λεξικού που περιέχει τα στοιχεία του συνδεδεμένου χρήστη
          # στη μορφή: user = {"user": "nikos", "areas": {"Africa": ["Kenya"], "Latin America": ["Brazil"]}

def login_user():
    '''
    ΕΡΩΤΗΜΑ 1
    H συνάρτηση ζητάει από τον χρήστη το username
    Αν ο χρήστης δεν δώσει όνομα επιστρέφει την τιμή False.
    Aν δώσει όνομα, ελέγχει αν αυτός υπάρχει ήδη καλώντας τη συνάρτηση retrieve_user(username)
        Αν η retrieve_user() επιστρέψει True (βρέθηκε χρήστης) τότε τυπώνει ένα μήνυμα καλωσορίσματος και
        επιστρέφει την τιμή True.
        Αν η retrieve_user() επιστρέψει False (δεν βρέθηκε χρήστης) τότε ρωτάει τον χρήστη αν θέλει να
        δημιουργήσει προφίλ,
            Aν απαντήσει θετικά, το όνομα αποθηκεύεται στην καθολική μεταβλητή user με κενή λίστα,
            καλείται η συνάρτηση update_user() η οποία αποθηκεύει το προφίλ του χρήστη
            στο αρχείο users_file, και επιστρέφει True.
            Αν απαντήσει αρνητικά επιστρέφει False.
    '''

    global user

    un = input("Εισάγετε όνομα χρήστη: ")
    if(un == ''):
        print("Αντίο")
        return False

    if(retrieve_user(un)): # Το όνομα χρήστη βρέθηκε
        print("Χαίρετε,", un)
        return True
    else: # Το όνομα χρήστη δεν βρέθηκε
        new_user = input("Δεν βρέθηκε χρήστης. Επιθυμείτε να δημιουργήσετε νέο προφίλ; (yes/no) ")
        while(True): # Επανάληψη μέχρι να δοθεί έγκυρη είσοδος
            if(new_user.lower() == "yes"): # Δημιουργία νέου χρήστη
                user = {"user" : un, "areas" : {}}
                update_user()
                return True
            elif(new_user.lower() == "no"): return False
            else: new_user = input("Επιθυμείτε να δημιουργήσετε νέο προφίλ; (yes/no) ")
            

def retrieve_user(username):
    '''
    ΕΡΩΤΗΜΑ 2
    :param username: το όνομα χρήστη που έδωσε ο χρήστης
    :return: True αν ο χρήστης βρέθηκε στο αρχείο users_file. Στην περίπτωση αυτή στην καθολική μεταβλητή
    user φορτώνεται το λεξικό που περιέχει τα στοιχεία του χρήστη, για παράδειγμα:
    {'user': 'nikos', 'areas': {'Europe': ['Greece', 'Brexit'], 'Africa': ['Egypt']}
    Προσοχή: αν ένα θέμα περιέχει πολλούς όρους, αυτοί έχουν αποθηκευτεί ως μια συμβολοσειρά με το $ ως
    διαχωριστικό. Συνεπώς πρέπει εδώ να τους διαχωρίσουμε και να τους εισάγουμε στη σχετική λίστα όρων.
    Η συνάρτηση επιστρέφει False αν δεν υπάρχει ο χρήστης ήδη στο αρχείο users_file
    '''

    global user

    temp = {}
    found = False # Λογική μεταβλητή, παίρνει αληθή τιμή αν υπάρχουν παλιότερες καταχωρίσεις του δοθέντος username

    if(not os.path.isfile(users_file)): open(users_file, 'w', encoding = "utf-8").close() # Δημιουργούμε το αρχείο, αν δεν υπάρχει ήδη, και το αφήνουμε άδειο
    with open(users_file, 'r', encoding = "utf-8") as uf: # Βρίσκουμε όλες τις καταχωρίσεις για τον τρέχοντα user, αναζητώντας μια-μια όλες τις
        for line in uf: # καταχωρίσεις του αρχείου. Η μέθοδος αυτή δεν είναι ιδιαίτερα αποδοτική, αλλά απαιτεί τη λιγότερη επεξεργασία
            if(line.split(';')[0].lower() == username.lower()): # Εδώ γίνεται η υπόθεση ότι τα ονόματα χρηστών είναι ανεξάρτητα από τη διάκριση των γραμμάτων
                found = True # σε κεφαλαία - πεζά, δηλαδή τα ονόματα "nikos" και "NiKoS"(με λατινικούς χαρακτήρες) αναφέρονται στον ίδιο χρήστη 
                user.update({"user" : username})
                
                countries = line.split(';')[2].split('$') # Χωρίζει τους όρους αναζήτησης με $
                countries[-1] = countries[-1].rstrip() # Aφαιρεί τον χαρακτήρα '\n' από το τελευταίο στοιχείο
                temp.update({line.split(';')[1] : countries}) # Κάθε καταχώριση προστίθεται στο προσωρινό λεξικό temp

    if(found): user.update({"areas" : temp}) # Η συνάρτηση update προσθέτει ένα ζεύγος {"key" : "value"} στο λεξικό

    return found


def update_user():
    '''
    ΕΡΩΤΗΜΑ 3
    H συνάρτηση αυτή αποθηκεύει το περιεχόμενο της καθολικής μεταβλητής user στο αρχείο users_file
    Προσέχουμε ώστε αν στο αρχείο users_file υπάρχουν ήδη άλλοι χρήστες, να ανακτώνται αυτοί πρώτα,
    να προστίθεται στη συνέχεια ο χρήστης user και να αποθηκεύονται τέλος όλοι οι χρήστες ξανά στο users_file.
    Επίσης προσέχουμε ώστε οι όροι αναζήτησης που υπάρχουν για κάποιο θέμα να αποθηκευτούν ως μια
    συμβολοσειρά με το χαρακτήρα $ ως διαχωριστικό.
    Η συνάρτηση επιστρέφει None
    '''

    global user
    
    un = user["user"]
    continents = list(user["areas"].keys()) # Λίστα με όλα τα λήμματα του λεξικού (με όλες, δηλαδή, τις επιλεγμένες περιοχές του χρήστη)
    states = []
    for c in continents: states.append(user["areas"][c]) # Λίστα από λίστες: η ν-οστή λίστα περιέχει τους όρους αναζήτησης για τη ν-οστή περιοχή
    
    all_entries = utilities.csv_to_dict(users_file) # Αποθηκεύουμε τη λίστα με όλες τις υπάρχουσες καταχωρίσεις
    
    all_entries = [dic for dic in all_entries if(dic["user"].lower() != un.lower())] # Αφαιρεί από τη λίστα όλα τα λεξικά που αφορούν τον τρέχοντα user

    open(users_file, 'w', encoding = "utf-8").close() # Καθαρίζει το περιεχόμενο του αρχείου
    if(not continents): all_entries.append({"user" : un, "area" : '', "keywords" : ''}) # Αν το λεξικό user["areas"] είναι κενό
    else:
        for c, s in zip(continents, states): all_entries.append({"user" : un, "area" : c, "keywords" : '$'.join(s)}) # Η συνάρτηση zip αντιστοιχίζει ένα
                                                                                                                 # προς ένα τα στοιχεία των δύο λιστών

    utilities.dict_to_csv(all_entries, users_file) # Αποθηκεύει στο αρχείο την τροποποιημένη λίστα
    
    return None

def load_newsfeeds():
    '''
    Η συνάρτηση φορτώνει τις διευθύνσεις των rss feed urls στο λεξικό feeds από το σχετικό αρχείο
    επιστρέφει το λεξικό που ανακτάται ή επιστρέφει False αν το αρχείο feeds_file δεν υπάρχει
    '''
    if(not os.path.isdir(data_dir)): os.makedirs(data_dir)
    if(os.path.isfile(feeds_file)): return utilities.csv_to_dict(feeds_file)
    else:
        print("Δεν υπάρχει αρχείο {} στον φάκελο {}".format(feeds_file, data_dir))
        return False

def load_news_to_temp(feeds):
    '''
    Άνοιγμα του rss feed,
    :param feeds οι θεματικές περιοχές ειδήσεων με τις αντίστοιχες διευθύνσεις των rss feeds
    φορτώνει τα άρθρα και τα αποθηκεύει σε προσωρινό αρχείο
    '''
    news_items = []
    for area in user["areas"]:
        print(area, " ....", end='')
        url = [x["rss"] for x in feeds if x["title"] == area]
        if url:
            url = url[0]
            req = urllib.request.Request(url)
        try:
            with urllib.request.urlopen(req) as response:
                html = response.read().decode()
            filename = "tempfile.rss"
            with open(filename, 'w', encoding="utf-8") as p:
                p.write(html)
        except urllib.error.HTTPError as e:
            print(e.code)
            print(e.readline())
        except urllib.error.URLError as e:
            print(e)
            if hasattr(e, "reason"):  # χωρίς σύνδεση ιντερνετ
                print("Αποτυχία σύνδεσης στον server")
                print("Αιτία: ", e.reason)
        else:
            
            '''
            ΕΡΩΤΗΜΑ 4 Συμπληρώστε τον κώδικα της συνάρτησης load_news_to_temp()
            Συμπληρώστε τον κώδικα που λείπει στην συνάρτηση load_news_to_temp(feeds)
            Η συνάρτηση αυτή που παίρνει ως όρισμα το λεξικό feeds με τις θεματικές κατηγορίες ειδήσεων και τις
            αντίστοιχες διευθύνσεις των rss feeds, φορτώνει τα άρθρα και τα αποθηκεύει σε προσωρινό αρχείο
            tempfile.rss για κάθε θεματική περιοχή ενδιαφέροντος του χρήστη.
            Στο σημείο που ζητείται να συμπληρωθεί ο κώδικας, για το αρχείο που περιέχει τις ειδήσεις για τη θεματική
            περιοχή ειδήσεων area ζητείται να επιλέξουμε τις ειδήσεις εκείνες στις οποίες υπάρχει κάποιος από τους
            όρους που έχει ορίσει ο χρήστης στο προφίλ του. Αν δεν έχουν οριστεί στο προφιλ όροι αναζήτησης, θα
            πρέπει να περιληφθούν όλες οι ειδήσεις της θεματικής περιοχής.
            Τις ειδήσεις που επιλέγουμε τις προσθέτουμε ως λεξικά {'no': ..., 'date':...,'title': ..., 'content': ...} 
            στη λίστα news_items, όπου το στοιχείο ‘no’ είναι ένας ακέραιος αριθμός που δίνει ταυτότητα στην είδηση.
            Για τον έλεγχο ύπαρξης ενός όρου χρησιμοποιούμε τη βοηθητική συνάρτηση check_keyword(key, text)
            '''

            # Κάθε είδηση περιέχεται μέσε σε ένα item
            # Ο τίτλος είναι εντός των brackets <title></title>,
            # η περιγραφή εντός των brackets <description></description>,
            # και η ημερομηνία δημοσίευσης αναλόγως στο <pubDate>
            with open(filename, 'r', encoding = "utf-8") as f:
                rss = f.read().replace('\n', ' ')
                items = re.findall(r"<item>(.*?)</item>", rss, re.MULTILINE | re.IGNORECASE) # Όλο το περιεχόμενο όλων των items
                for item in items: # Για κάθε ένα item ξεχωριστά
                    title = re.findall(r"<title>(.*?)</title>", item, re.MULTILINE | re.IGNORECASE)
                    title = clear_format(title[0])
                    description = re.findall(r"<description>(.*?)</description>", item, re.MULTILINE | re.IGNORECASE)
                    description = clear_format(description[0])
                    story_date = re.findall(r"<pubDate>(.*?)</pubDate>", item, re.MULTILINE | re.IGNORECASE)
                    if(not user["areas"][area]): # Αν ο χρήστης δεν έχει θέσει ειδικούς όρους αναζήτησης, συμπεριλαμβάνονται όλες οι ειδήσεις από την περιοχή
                        news_items.append({"no" : len(news_items) + 1, "date" : story_date, "title" : title, "content" : description})
                    for kw in user["areas"][area]: # Έλεγχος όλων των θεμάτων - keywords για τη συγκεκριμένη περιοχή
                        if(check_keyword(kw, title) or check_keyword(kw, description)): # Τα keywords αναζητώνται και στον τίτλο, και στην περιγραφή
                            news_items.append({"no" : len(news_items) + 1, "date" : story_date, "title" : title, "content" : description})
                            break # Αρκεί να βρεθεί ένα keyword για να συμπεριληφθεί η είδηση

    utilities.dict_to_csv(news_items, "mytemp.csv")
    return len(news_items)

def clear_format(t):
    # βοηθητική συνάρτηση καθαρισμού των κειμένων <title> και <description>
    return t.replace("<![CDATA[", '').replace("]]>", '')

def print_news():
    '''
    Η συνάρτηση αυτή τυπώνει τις ειδήσεις που υπάρχουν στο αρχείο mytemp.csv
    :return:
    '''
    try:
        news_items = utilities.csv_to_dict("mytemp.csv")
        print('\n')
        for item in news_items:
            print(' [' + format_date(item["date"]) + "]\t" + item["title"])
            formatted_print(item["content"]+"\n")
        return True
    except FileNotFoundError:
        return False

def format_date(date):
    # βοηθητική συνάρτηση για διαμόρφωση της ημερομηνίας της είδησης
    m_gr = "Ιαν Φεβ Μαρ Απρ Μαϊ Ιουν Ιουλ Αυγ Σεπ Οκτ Νοε ∆εκ".split()
    m_en = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
    d = re.findall(r"([0-9]{2}\s[A-Z][a-z]{2}\s[0-9]{4})",date, re.I)
    if(d): date = d[0].split()
    #if d: date = d.group(0).split()
    if(date[1] in m_en): date[1] = m_gr[m_en.index(date[1])]
    return ' '.join(date)

def check_keyword(keyword, text):
    # βοηθητική συνάρτηση που αναζητάει το keyword σε μια συμβολοσειρά text. Επιστρέφει True/False αν βρεθεί ή όχι.
    tonoi = ("αά", "εέ", "ηή", "ιί", "οό", "υύ", "ωώ") # για αναζήτηση Ελληνικών όρων
    if(keyword == '*'): return True
    n_phrase = ""
    for c in keyword:
        char = c
        for t in tonoi:
            if c in t: char = '[' + t + ']'
        n_phrase += char
    pattern = r".*" + n_phrase + r".*"
    w = re.findall(pattern, text, re.I)
    if(w): return True
    else: return False

def formatted_print(st, width=WIDTH):
    # συνάρτηση που τυπώνει συμβολοσειρά st με πλάτος width χαρακτήρων
    para = st.split('\n')
    for p in para:
        st = p.split()
        out = ""
        while(True):
            while(len(st) > 0 and len(out + st[0]) < width): out = ' '.join([out, st.pop(0)])
            print('\t', out)
            out = ''
            if(len(st) == 0): break

def manage_profile(feeds):
    global user
    modify = False
    while(True):
        print_user_profile()
        print(WIDTH * '_')
        reply = input("Θέλετε να αλλάξετε το προφίλ σας; ('Ναι' για αλλαγές):")
        if(not reply or reply[0].lower() not in 'nν'): break
        print("Αρχικά θα μπορείτε να επιλέξετε περιοχές ειδήσεων, και στη συνέχεια να θέσετε όρους αναζήτησης σε καθένα από αυτά")
        main_feeds = [x["title"] for x in feeds]
        '''
        ΕΡΩΤΗΜΑ 5
        Επαναληπτικά ζητήστε από τον χρήστη να ορίσει τις περιοχές ειδήσεων που τον ενδιαφέρουν 
        και στη συνέχεια για κάθε περιοχή τους ειδικούς όρους αναζήτησης.
        (δέστε παράδειγμα στο βίντεο) 
        '''
                                                                            
        while(True):
            print_user_profile()
            display_all_areas(main_feeds)
            print("Μπορείτε να προσθέσετε ή να αφαιρέσετε περιοχή γράφοντας + ή - αντιστοίχως, και αριθμό περιοχής (ENTER για συνέχεια): ", end = "")
            choice = input()
            if(choice == ''): break
            choice = ''.join(choice.split()) # Αφαιρεί όλα τα πιθανά κενά
            if(len(choice) == 2 and choice[0] in "+-" and choice[1].isdigit() and int(choice[1]) in range(1, 7)): # Επιβεβαίωση έγκυρης εισόδου
                modify = True
                sign = choice[0]
                choice = choice[1:] # Αφαιρεί τον πρώτο χαρακτήρα (+/-)
                choice = main_feeds[int(choice) - 1] # Παίρνει την αντίστοιχη ήπειρο από τη λίστα
                if(sign == '+'):
                    if(choice in list(user["areas"].keys())): print("Έχετε ήδη επιλέξει την περιοχή", choice, '\n')
                    else:
                        user["areas"].update({choice : []})
                        print("Η περιοχή", choice, "προστέθηκε\n")
                else: # sign = '-'
                    if(choice not in list(user["areas"].keys())): print("Η περιοχή", choice, "δεν έχει επιλεχθεί\n")
                    else:
                        user["areas"].pop(choice, None) # Αφαιρεί το λήμμα από το λεξικό. Η παράμετρος None αποτρέπει KeyErrors
                        print("Η περιοχή", choice, "αφαιρέθηκε\n")
            else: print("Μη έγκυρη εισοδος!\n")

        print(WIDTH * '_')
        print("Τώρα μπορείτε να επιλέξετε όρους αναζήτησης για κάθε θέμα ειδήσεων. Επιτρέπονται μόνο γράμματα, αριθμοί και κενά.\n")
        for area in list(user["areas"].keys()):
            print("Θέμα: ",  area, "\tΌροι αναζήτησης: ", ", ".join(user["areas"][area]))
            while(True):
                print("Μπορείτε να προσθέσετε ή να αφαιρέσετε έναν όρο με + ή - αντιστοίχως, και τον όρο (ENTER για συνέχεια): ", end = "")
                choice = input()
                if(choice == ""): break
                choice = choice.lstrip() # Αφαιρεί όλα τα ηγούμενα κενά, ούτως ώστε ο πρώτος χαρακτήρας να είναι + ή -
                choice = choice.rstrip() # Αφαιρεί τα πιθανά κενά στο τέλος, που είναι άχρηστα
                sign = choice[0]
                choice = choice[1:] # Αφαιρεί τον πρώτο χαρακτήρα (+/-)
                choice = choice.title() # Πρώτο γράμμα κάθε λέξης κεφαλαίο, τα υπόλοιπα πεζά
                # Έλεγχος εγκυρότητας. Αν στον όρο αναζήτησης περιέχονται σημεία στίξης προκαλούνται σφάλματα
                # στην αναζήτηση ειδήσεων, λόγω ασάφειας με τα regex. Για αυτό επιτρέπουμε στον χρήστη μόνο γράμματα και/ή αριθμούς, και κενά
                if(sign in "+-" and len(choice) > 1 and bool(re.match(r"[a-zA-Z0-9 ]+$", choice))):
                    modify = True
                    if(sign == '+'):
                        if(choice in user["areas"][area]): print("Έχετε ήδη επιλέξει τον όρο", choice, '\n')
                        else:
                            user["areas"][area].append(choice)
                            print("Ο όρος αναζήτησης '", choice, "' προστέθηκε στην περιοχή", area, '\n')
                    else: # sign = '-'
                        if(choice not in user["areas"][area]): print("Η περιοχή", choice, "δεν έχει επιλεχθεί\n")
                        else:
                            user["areas"][area].remove(choice)
                            print("Ο όρος αναζήτησης '", choice, "' αφαιρέθηκε απο την περιοχή", area, '\n')
                else: print("Μη έγκυρη είσοδος!\n")
            print() # Κενή σειρά

        # εκτυπώστε το νέο προφίλ του χρήστη και ερωτήστε τον για έξοδο
        print_user_profile()
        reply = input("\nΈχετε ολοκληρώσει την επεξεργασία του προφίλ; ('Ναι' για περαιτέρω αλλαγές) ")
        if(not reply or reply[0].lower() not in 'nν'): break
    if(modify): update_user() # χρησιμοποιήστε μια λογική μεταβλητή η οποία γίνεται True αν έγιναν αλλαγές στο προφίλ του χρήστη

def print_user_areas(li):
    print("\nΤα ενδιαφέροντά σας είναι ...", end='')
    items = False
    for item in li:
        if(item in user["areas"].keys()):
            print(item, end = ", ")
            items = True
    if(not items): print('ΚΑΝΕΝΑ ΕΝΔΙΑΦΕΡΟΝ', end='')
    print()

def display_all_areas(main_areas):
    # Βοηθητική συνάρτηση, παίρνει ως παράμετρο τις διαθέσιμες κύριες περιοχές, και τις εκτυπώνει με αύξουσα αρίθμηση, μία σε κάθε σειρά
    print(WIDTH * '_')
    print("Οι διαθέσιμες περιοχές ειδήσεων ειναι (με *** οι επιλεγμένες):")
    for index, ar in enumerate(main_areas, start = 1): # Με τη συνάρτηση enumerate η μεταβλητή index παίρνει τον αύξοντα αριθμό κάθε στοιχείου της λίστας
        stars = ""
        if(ar in list(user["areas"].keys())): stars = "***" # Αν η περιοχή έχει ήδη επιλεγεί
        print(index, ar, stars)

    print() # Κενή σειρά

def print_user_profile():
    if(not user["areas"]): print("ΚΕΝΟ ΠΡΟΦΙΛ ΧΡΗΣΤΗ")
    else: print("\nΤα θέματα ειδήσεων που σας ενδιαφέρουν είναι:")
    for area in user["areas"]:
        print(area)
        for keyword in user["areas"][area]:
            print("\t\t", keyword)

def main():
    print("Σήμερα είναι :", str(datetime.datetime.today()).split()[0])
    username = login_user()
    if(username):
        feeds = load_newsfeeds()
        if(feeds):
            print("To bbcnews πρoσφέρει προσωποποιημένες ειδήσεις από το BBC")
            while(True): # main menu
                print(WIDTH * '=')
                user_selected = input("(Π)ροφίλ ενδιαφέροντα, (Τ)ίτλοι ειδήσεων, (enter)Εξοδος:\n")
                if(user_selected == ''): break # έξοδος
                elif(user_selected.upper() in "ΠP"): manage_profile(feeds) # διαχείριση του προφίλ χρήστη
                elif(user_selected.upper() in "ΤT"): # παρουσίαση τίτλων ειδήσεων
                    if("areas" in user.keys() and len(user["areas"]) > 0): # αν ο χρήστης έχει ορίσει areas
                        print_user_profile()
                        print("\nΤΕΛΕΥΤΑΙΕΣ ΕΙΔΗΣΕΙΣ ΠΟΥ ΣΑΣ ΕΝΔΙΑΦΕΡΟΥΝ...")
                        items_count = load_news_to_temp(feeds)  # φόρτωσε τις ειδήσεις που ενδιαφέρουν τον χρήστη
                        if(items_count): print_news() # εαν υπάρχουν ειδήσεις σύμφωνα με το προφιλ του χρήστη, τύπωσε τους τίτλους των ειδήσεων αυτών
                        else: print("Δεν υπάρχουν ειδήσεις με βάση το προφίλ ενδιαφερόντων σας ...")
                    else: print("Πρέπει πρώτα να δημιουργήσετε το προφίλ σας")
    print("\nΕυχαριστούμε")

if __name__ == "__main__": main()
