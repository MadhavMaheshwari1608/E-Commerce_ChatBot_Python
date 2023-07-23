# -*- coding: utf-8 -*-
"""ChatBot_updated.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16c_QHlcB5z--8LN6lBwASLghiwRPL9mF

##Importing the libraries
"""

import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import Input, Embedding, LSTM, Dense, Flatten, GlobalMaxPooling1D

"""##Importing our pre-cleaned dataset"""

dataset = pd.read_csv('Customer_Queries_1.csv')
X = dataset.iloc[:,:-1].values
y = dataset.iloc[:,-1].values

"""Encoding our dependent variable"""

from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
y_train = le.fit_transform(y)

"""## Data Cleaning"""

import re
def clean_text(text):
    text = text.lower()
    text = re.sub(r"i'm", "i am", text)
    text = re.sub(r"he's", "he is", text)
    text = re.sub(r"she's", "she is", text)
    text = re.sub(r"that's", "that is", text)
    text = re.sub(r"what's", "what is", text)
    text = re.sub(r"where's", "where is", text)
    text = re.sub(r"\'ll", " will", text)
    text = re.sub(r"\'ve", " have", text)
    text = re.sub(r"\'re", " are", text)
    text = re.sub(r"\'d", " would", text)
    text = re.sub(r"won't", "will not", text)
    text = re.sub(r"can't", "can not", text)
    text = re.sub(r"\'bout", " about", text)
    text = re.sub(r"[-()\'|/<>,`~!#$%^&*:;.?{}]", "", text)
    return text

for i in range(len(X)):
    X[i][0] = clean_text(X[i][0]).replace('"','')

import nltk
from nltk.stem.porter import PorterStemmer
corpus = []
for i in range(len(X)):
    query = X[i][0].split()
    ps = PorterStemmer()
    query = [ps.stem(word) for word in query]
    query = " ".join(query)
    corpus.append(query)

print(corpus)

"""Tokenizing our inputs"""

tokenizer = Tokenizer(num_words = 2000)
tokenizer.fit_on_texts(corpus)
train = tokenizer.texts_to_sequences(corpus)

"""Padding our input to make the training easy"""

x_train = pad_sequences(train)

input_shape = x_train.shape[1]
unique_words = len(tokenizer.word_index)
output_length = le.classes_.shape[0]

print(output_length)

"""## Training our ChatBot"""

model = tf.keras.Sequential()
model.add(Input(shape=(input_shape,)))
model.add(Embedding(unique_words+1, 10, input_length= (input_shape,)))
model.add(LSTM(10, return_sequences=True))
model.add(Flatten())
model.add(Dense(units= 19, activation='relu'))
model.add(Dense(units= 19, activation='relu'))
model.add(Dense(units= 19, activation='relu'))
model.add(Dense(units= output_length, activation='softmax'))

model.compile(loss = "sparse_categorical_crossentropy", optimizer ='adam', metrics=['accuracy'])
model.fit(x_train, y_train, epochs=500)

"""Dictionary of possible replies by ChatBot based on FAQs"""

Query_reply = {"return":"Returns can only be issued within 7 days of delivery."
                        "Electronics can only be replaced,"
                        "Visit my orders page to check for more details as return period may vary for different products."
               ,"payments": "We accept all UPIs and card payments including Visa,MasterCard and Rupay,"
                            "Cash on delivery option is available only for specific products,"
                            "For checking your payments, you can visit transactions section"
               ,"track": "Visit the order page, click on the your order, select 'TRACK MY ORDER', and check the status"
               ,"delivery":"Delivery and shipping takes around 7 days for non-prime users and 2 days for prime users"
                           "If your order has not been delivered for more than above mentioned days, then click on 'URGENT QUERY' in orders section and our team will contact you shortly afterwards."
               ,"items":"We have great range of products, click on CATEGORY drop-down menu to see all our products."
               ,"confirm": "It takes upto 24 hours for confirmation,"
                           "If your order has not been confirmed for more than above mentioned time, then click on 'URGENT QUERY' in orders section and our team will contact you shortly afterwards."
               ,"delay":"We are really sorry if there has been a delay more than the specified period,"
                        "If your order has not been delivered for more than above mentioned days, then click on 'URGENT QUERY' in orders section and our team will contact you shortly afterwards."
               ,"return_status":"It generally takes about 3 days to pickup an order, and around 7 days to initialise the refund after verification and checking of the product."
                                "If you have not received refund even after 10 days, check your wallet balance,due to some bank issues, we sometimes pay into your wallet."
                                 "If there also you have not received the payment,please contact our Customer Care Call support."
               ,"voucher": "You can add a voucher by clicking on VOUCHERS > ADD VOUCHER "
                           "To avail a voucher, click on 'AVAIL VOUCHER' option at the time of payment."
               ,"mobile_app": "You can download the our Mobile App from IOS App Store, or Google Play Store for a better experience."
               ,"cancel": "Order can only be cancelled within 24 hours of the placement of the order."
                          "To cancel an order, go to ORDERS > Cancel An Order "
               ,"goodbye":"Have a nice day. Hope I was able to help!,If your query has not been resolved, please contact our Customer Care Call Centre."
               ,"thanks":"Happy to help!,Anything else in which I can be of assistance?"
               ,"reasons":"Reasons include Courier Issues, Cross Border shipment delay, Non-timely delivery by seller to us."
               ,"profile": "You can add or change your account details by following the steps: "
                           "Account > Click on 'Manage my account' from the icon, You change or edit your name, address, email address, mobile number > click on Update Details."
               ,"more":"Contact our Customer Call Support Centre: Phone: 051-111-128929. Timings are from 09:00 AM to 05:00 PM from Monday to Saturday."
               ,"greeting":"Hello!, How can I help?"
               ,"personal":"I'm good"
               ,"refund_status": "It generally takes upto 14 days to receive into bank."
                                 "If you have not received refund even after 14 days, check your wallet balance,due to some bank issues, we sometimes pay into your wallet."
                                 "If there also you have not received the payment,please contact our Customer Care Call support."}

"""## ChatBot Implementation via Terminal

## For better results and experience, use Google Colab or Jupyter Notebook

### Run only below cell instead of whole code when using repeatedly as that would result in updating our model with more and more use.

## Improving the Bot after every 20 successful predictions

### Also, updating these new values to our dataset
"""

user_has_query = True
corpus_update = 0
corpus_new = []
y_new = []
userInput_list = []

while user_has_query:
    textList = []
    prediction_input = []
    response_tag = ""
    print("Greetings!, how can I help?")
    print("To end a conversation, type 'goodbye'.")
    userInput = input("You: ")
    user_input = clean_text(userInput).replace('"','')
    user_input = user_input.split()
    user_input = [ps.stem(word) for word in user_input]
    user_input = " ".join(user_input)
    for i in range(len(corpus_new)):
        if user_input == corpus_new[i]:
            response_tag = y_new[i]

    if response_tag != "":
        print("Chatbot: ",Query_reply[response_tag])
    else:
        textList.append(user_input)
        prediction_input = tokenizer.texts_to_sequences(textList)
        prediction_input = np.array(prediction_input).reshape(-1)
        prediction_input = pad_sequences([prediction_input], input_shape)

        output = model.predict(prediction_input)
        import math
        probability = []
        sum_exp = 0
        for i in range(19):
            sum_exp += math.exp(output[0][i])
        for i in range(19):
            prob = math.exp(output[0][i])/sum_exp
            probability.append(prob)
# Minimum confidence = 10%.
        if max(probability)>0.1:
            arg = output.argmax()
            response_tag = le.inverse_transform([arg])[0]
#             print(max(probability)*100,'%')
        else:
            response_tag = 'more'
        print("Chatbot: ",Query_reply[response_tag])

    if response_tag == "goodbye":
            user_has_query = False
    else:
# Updating our chatbot to remember the current reply if that was correct for future.
        ask_user = input('Was my response helpful?: ')
        if ask_user == "yes":
            corpus_update += 1
            corpus_new.append(user_input)
            y_new.append(response_tag)
            userInput_list.append(userInput)
        else:
            valid_categories = ['return', 'payments', 'track', 'delivery', 'items', 'confirm', 'delay', 'return_status', 'voucher', 'mobile_app', 'cancel', 'reasons', 'profile', 'refund status']
            ask_user_again = input('Your query is related to which category? ' + str(valid_categories) + ': ')
            if ask_user_again in valid_categories:
              for query in valid_categories:
                if ask_user_again == query:
                  user_input_new = ask_user_again
                  response_tag_new = query
            else:
              user_input_new = clean_text(ask_user_again).replace('"','')
              user_input_new = user_input_new.split()
              user_input_new = [ps.stem(word) for word in user_input_new]
              user_input_new = " ".join(user_input_new)
              prediction_input_new = tokenizer.texts_to_sequences([user_input_new])
              prediction_input_new = np.array(prediction_input_new).reshape(-1)
              prediction_input_new = pad_sequences([prediction_input_new], input_shape)
              output_new = model.predict(prediction_input_new)
              arg_new = output_new.argmax()
              response_tag_new = le.inverse_transform([arg_new])[0]
            print("Chatbot: ",Query_reply[response_tag_new])
            ask_user_new = input('Was my response helpful now?: ')
            if ask_user_new == "yes":
              corpus_update += 1
              corpus_new.append(user_input_new)
              y_new.append(response_tag_new)
              userInput_list.append(ask_user_again)
              y_new.append(response_tag_new)
              userInput_list.append(userInput)
            else:
              print('I am sorry')
              print('Please contact our costumer service call centre')

# Bot Upgradation after 25 successful predictions.

if corpus_update >=25:
    corpus += corpus_new
    y += y_new
    model.fit(pad_sequences(tokenizer.texts_to_sequences(corpus)), le.fit_transform(y), epochs=500)
    for i in range(corpus_update):
      new_data = []
      new_data.append({'Queries':userInput_list[i], 'Type':y_new[i]})
      dataset = dataset.append(new_data,ignore_index=True)

    userInput_list = []
    corpus_update = 0
    corpus = corpus_new
    y = y_new
    y_new = []
    corpus_new = []

    dataset.to_csv('Customer_Queries_1.csv',index=False)

