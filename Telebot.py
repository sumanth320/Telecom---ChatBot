# all packages:
from tkinter import *
import time
import datetime
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer  # wordNet is a collection of nouns and verbs and adjectives and their synonyms
import pickle
from keras.models import load_model
import json
import random
import numpy as np
import sqlite3
from fuzzywuzzy import fuzz
from PIL import Image
from PIL import ImageTk

lemmatizer = WordNetLemmatizer()
model = load_model('chatbot_model.h5')
intents = json.loads(open('intents.json').read())
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))


# Take the input sentence  from the customer - lemmatize it and change to lower case.
def clean_up_sentence(sentence):
    # tokenize the pattern - split words into array
    sentence_words =word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words


# Return bag of words array: 0 or 1 for each word in the bag that exists in the sentence
def bow(sentence, words, show_details=True):
    # print("/t bow executed called by predict_class")
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0] * len(words)
    for sen in sentence_words:
        for i, word in enumerate(words):
            if word == sen:
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % word)
    return (np.array(bag))


# Using the model "chatbot_model.h5" predicting the tag for the inout sentence
def predict_class(sentence, model):
    p = bow(sentence, words, show_details=TRUE)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    # filter out predictions below a threshold
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    print("\n\tReturn_list passed to chatbot_response is ", return_list)
    return return_list


# To insert the plan type - prepaid or postpaid in 'plan_type' table
def db_insertplantype(plan):
    try:
        db_connect = sqlite3.connect("Telebot.db")
        db_cur = db_connect.cursor()
        time_stamp = time.time()
        date = str(datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S'))
        db_cur.execute("Insert into plan_type(plan_type,load_date) VALUES(:plantype,:load_date)",
                       {
                           'plantype': plan,
                           'load_date': date
                       })
        db_connect.commit()
        db_cur.close()
        db_connect.close()
        print("PlanType Inserted Successfully")
    except Exception as e:
        print(f"DB exception: {e}")


# To insert customer budget in the "budget" table
def db_insertbudget(msg):
    money = 0
    print("\tThe message received for budget insertion is: ", msg)
    for word in msg.split():
        print(word)
        num = ''.join([n for n in word if n.isdigit()])
        if num.isdigit():
            money = num
        elif num.isalpha():
            money = 100

    print(f"message received is {msg} and money calculated is {money}")
    time_stamp = time.time()
    date = str(datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S'))
    try:
        db_connect = sqlite3.connect("Telebot.db")
        db_cur = db_connect.cursor()
        print("db_insertbudget() --> connection and cursor created successfully")
        db_cur.execute("insert into budget (budget,load_date) VALUES(:cost,:load_date)",
                       {
                           'cost': money,
                           'load_date': date
                       })
        print("\nBudget Inserted Successfully")
        db_connect.commit()
        db_cur.close()
        db_connect.close()
        print("db_insertbudget() --> connection and cursor closed successfully")
    except Exception as e:
        print(f"DB exception: {e}")


# To insert customer data requirement in the "data" table
def db_insertdata(msg):
    data_limit = ""
    num = re.findall('\d*\.?\d+', msg)
    print("num is", num)
    if fuzz.ratio(msg.lower(), 'unlimited data') > 70:
        data_limit += 'unlimited'
    elif num:
        data_limit += num[0]
    else:
        data_limit += '1' #default value

    time_stamp = time.time()
    date = str(datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S'))
    try:
        db_connect = sqlite3.connect("Telebot.db")
        db_cur = db_connect.cursor()
        print("db_insertdata --> connection and cursor created successfully")
        db_cur.execute("insert into data (data,load_date) VALUES(:data,:load_date)",
                       {
                           'data': data_limit,
                           'load_date': date
                       })
        print("data Inserted Successfully")
        db_connect.commit()
        db_cur.close()
        db_connect.close()
        print("db_insertdata --> connection and cursor closed successfully")
    except Exception as e:
        print(f"DB exception: {e}")


# To  fetch result based on the plan type, budget and data requirement.
def fetchresult():
    print("fetchresult function called:")

    try:
        db_connect = sqlite3.connect("Telebot.db")
        db_cur = db_connect.cursor()
        print("fetchresult() --> connection and cursor created successfully")
        db_cur.execute(""" 
                         with Quest as ( 
                 select Data.id, plan_type.plan_type,
                 trim(data.data) data,
                 trim(budget.budget) cost
                  from data, budget, plan_type 
                 where data.id=(select max(id) from data)
                 and plan_type.id=(select max(id) from plan_type)
                 and budget.id=(select max(id) from budget) 
                 and data.id in (select max(id) from data))

Select Rate_Plan_Options  from (
        Select case when RATEPLAN_TYPE is null then 
'Sorry, for the given budget of € '||COST||' and data requirement of '||DATA||' units, I could not find a suitable Tariff.
'||char(10)||'If you would like to continue with '||PLAN_TYPE||', you have to either increase your budget or decrease your data requirement.
'||char(10)||'To change the Plan type please type "Prepaid" or "Postpaid/Contract".
'||char(10)||'To change the search criteria please enter new budget.
'||char(10)||'Thank you! '
else
'This rate plan is from '||Upper(vendor)||' which is a '||upper(RATEPLAN_TYPE)||' plan and is known as '||Upper(rateplan_name)||'. The monthly charges would be € '||RECURRING_FEE||' and one time fee is € '||ONEOFF_FEE||' and you will be eligible for a '||DATA_LIMIT||' data pack for the month.
'||char(10)||'More details could be found about the plan at the following link : '||char(10)||''||coalesce(URL_LINK,'NA')||'. ' END Rate_Plan_Options--,'1' as counter

from (
     Select distinct case when Upper(rateplan_type)='CONTRACT' then 'POSTPAID' else Upper(rateplan_type) end RATEPLAN_TYPE,RP.VENDOR,RP.RATEPLAN_NAME,RP.RECURRING_FEE,CASE WHEN RP.ONEOFF_FEE GLOB '*[0-9]*'=1 then RP.ONEOFF_FEE else '0' end ONEOFF_FEE,
                RP.DATA_LIMIT,RP.RECOMMENDATION,RP.INTERNET_INFO,RP.EU_ROAMING_INFO,RP.TELEPHONY_SMS_MMS_INFO,RP.RUNNING_TIME_INFO,RP.NOTICE_PERIOD_INFO,RP.AUTO_RENEWAL_INFO,RP.URL_LINK, Q.DATA,Q.COST,Q.PLAN_TYPE,RP.RECURRING_FEE 
                from Quest Q left join (select case when instr(data_limit,' ')=0 then data_limit else substr(data_limit,1,instr(data_limit,' ')-1) end DATA,
                case when trim(upper(RATEPLAN_TYPE))='PREPAID' then RATEPLAN_TYPE else 'POSTPAID' end RATEPLAN_TYPE, * from rate_plans) RP 
                on trim(UPPER(Q.Data)) = trim(Upper(RP.Data))
                and cast(replace(RP.Recurring_Fee,',','.') as real) <= cast(replace(Q.COST,',','.') as real) +5
                and upper(rp.RATEPLAN_TYPE)=upper(q.plan_type)
                and 1<=(select count(*)  from rate_plans where Recurring_Fee<=Q.cost)
              )order by RECURRING_FEE
                )
                order by rate_plan_options asc LIMIT 5
        ;
""")
        print("result extracted Successfully")
        rateplan_result = db_cur.fetchmany(2)
        print(len(rateplan_result))
        db_cur.close()
        db_connect.close()
        print("fetchresult() --> connection and cursor closed successfully")
    except Exception as e:
        print(f"DB exception: {e}")
    return rateplan_result


# Choosing a random response for the tag predicted.
def getResponse(ints, intents_json):
    result = ""
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if (i['tag'] == tag):
            result = random.choice(i['responses'])
            break
    print("get_Response ", result)
    return result


#
def chatbot_response(msg):
    ints = predict_class(msg, model)
    # identifying the tag- to insert plan_type in the database
    if (ints[0]['intent'] == "prepaid" or ints[0]['intent'] == "postpaid"):
        db_insertplantype(ints[0]['intent'])

    # identifying the tag- to insert budget in the database
    if (ints[0]['intent'] == 'budget'):
        db_insertbudget(msg)

    # identifying the tag- to insert data in the database and call fetchresult() to retrieve the matching tariff.
    if (ints[0]['intent'] == 'data_limit'):
        db_insertdata(msg)
        sql_res = fetchresult()
        print(sql_res)
        sep = "-" * 90
        result = ""
        result1 = "Option 1: "
        result2 = sep+"\n"+"Option 2: "
        init_txt = "\nThank you!, Please find the top result  for your search criteria.\n"
        initial_text = "\nThank you!, Please find the top 2 options for your search criteria.\n"
        ending_text = "\nI hope, you are happy with the results. Have a Nice Day!"

        # Checking the context retrieved from the database and adding specific content to the start and enc
        if len(sql_res) == 2:
            result1 += sql_res[0][0]
            print("result1", result1)
            result2 += sql_res[1][0]
            print("result2", result2)
            result = initial_text + result1 + '\n\n' + result2 + ending_text

        elif len(sql_res) == 1:

            if "Sorry" not in sql_res[0][0]:
                result = init_txt + sql_res[0][0] + ending_text
            else:
                result = sql_res[0][0]

    else:
        result = getResponse(ints, intents)
        print("Result in chatbot_response() -->", result)
    return result

def clear_label_image():
    logo.destroy()


# Retrieving the messaged entered by the customer in the entrybox and calling the chatbot_response()
def send(*args):
    # extracting the text from the entrybox
    clear_label_image()
    msg = EntryBox.get("1.0", 'end-1c').strip()
    EntryBox.delete("0.0", END)

    ChatLog.config(state=NORMAL)
    ChatLog.insert(END, "You" + " " + " : " + msg + '\n', 'start1')
    # ChatLog.tag_add("start1",1.0,'end')
    ChatLog.tag_config('start1', foreground="#faa21f", font=("Courier New", 14))
    res = chatbot_response(msg)
    if res == "":
        res = "Sorry for the inconvenience, looks like i missed something. Please type again!"
        ChatLog.insert(END, "Bot" + " " + " : " + res + '\n\n', 'start')

        ChatLog.tag_config("start", foreground="green", font=("Courier New", 14))

    else:
        ChatLog.insert(END, "Bot" + " " + " : " + res + '\n\n', 'start')

        ChatLog.tag_config("start", foreground="green", font=("Courier New", 14))

    ChatLog.config(state=DISABLED)
    ChatLog.yview(END)
    return 'break'


base = Tk()
base.title("Tele-Bot "+ " "+"Hi There!!")
base.resizable(width=FALSE, height=FALSE)

# Create date and time:
# ****************************************************************

def date():
    todays_date = time.strftime("%d %B , 20%y")
    label_date['text'] = todays_date
    label_date.after(86400000, date)


date_txt = Label(base, text="Date: ", font='TimesNewRoman 15 bold', fg="Black")
label_date = Label(base, bd=5, height=1, width=12, font="Ariel 11 bold", fg="#faa21f", bg="black",
                   relief='groove')
date()


def clock():
    current = time.strftime("%H:%M:%S")
    label_time['text'] = current
    label_time.after(1000, clock)

time_txt = Label(base, text="Time: ", font=('TimesNewRoman 15 bold'), fg="black")
label_time = Label(base, bd=5, height=1, width=8, font='Ariel 11 bold', fg="#faa21f", bg="Black",
                   relief='groove')
clock()

# Create Chat window :ChatLog:
ChatLog = Text(base, bd=0, bg="black", fg='white', height="5", width="50", font="TimesNewRoman", wrap=WORD, padx=10,
               pady=5)

ChatLog.config(state=DISABLED)

# Bind scrollbar to Chat window: scrollbar
scrollbar = Scrollbar(base, command=ChatLog.yview, cursor="heart")
ChatLog['yscrollcommand'] = scrollbar.set

# Create Button to send message :SendButton
SendButton = Button(base, font=("Lucida Calligraphy", 14, 'bold'), text="Send", width="6", height=5,
                    bd=0, bg="black", fg='#faa21f',
                    command=send)


# Create the box to enter message: EntryBox
EntryBox = Text(base, bd=0, bg="white", width="29", height="5", font="TimesNewRoman", borderwidth=10, wrap=WORD, padx=5,
                pady=5)
EntryBox.bind("<Return>", send)
EntryBox.focus()


# Place all components on the screen

global logo
img = Image.open('image_1.png')
tkimage = ImageTk.PhotoImage(img)

logo=Label(base,image = tkimage)
logo.place(x=6, y=40, height=550, width=520)


base.geometry("550x700+20+20")
base.iconbitmap("tele_bot_2.ico")
date_txt.place(x=62, y=10)
label_date.place(x=120, y=10)
time_txt.place(x=280, y=11)
label_time.place(x=340, y=10)
ChatLog.place(x=6, y=40, height=550, width=520)
scrollbar.place(x=525, y=40, height=570)
EntryBox.place(x=6, y=600, height=90, width=435)
SendButton.place(x=445, y=600, height=90)

# Window loop
base.mainloop()


# Window loop
base.mainloop()
