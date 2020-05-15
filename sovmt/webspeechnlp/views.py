from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from googletrans import Translator
import os,sys
from subprocess import Popen
import pyautogui
import psutil
import os
import platform
from PIL import Image
import webbrowser
from nltk import pos_tag
from PyDictionary import PyDictionary
from nltk.stem import PorterStemmer 
from nltk.tokenize import word_tokenize 
from nltk.corpus import wordnet
import time
import pyttsx3
import requests
import paralleldots

engine = pyttsx3.init()



def index(request):
    return render(request,'index.html',{})
# Create your views here.

def vrdata(request):
    if request.method == "POST":
        data = {}
        str1 = ""
        ostype = ""
        desktopdir = ""
        desktopdir = os.path.expanduser("~\\Desktop")

        ostype = platform.system()
        if(ostype=="Windows"):
            desktopdir = desktopdir.replace('\\','/')

        translator = Translator()
        uservoicetext = request.POST['voicedata']
        

        dt1=translator.translate(uservoicetext)        
        str1=dt1.text

        if uservoicetext.startswith('code505'):
            uservoicetext=uservoicetext.replace('code505','')

            dt1=translator.translate(uservoicetext)        
            str1=dt1.text

            print(str1)
            ps = PorterStemmer() 

            str2=""

            words = word_tokenize(str1) 
               
            for w in words: 
                print(w, " : ", ps.stem(w)) 
                str2+=ps.stem(w)
                str2+=" "

            word1=pos_tag(str2.split())

            wordsearch=[]
            wordsearchblock=[]
            meaninglist=[]
            pofspeechandmeaning=[]

            for i in range(len(word1)):
                if(word1[i][1]=='VB' or word1[i][1]=='NN'):
                    if(len(word1)==1):
                        wordsearch.append(str1+" "+word1[i][1]) 
                    else:
                        wordsearch.append(word1[i][0]+" "+word1[i][1])

            for x in range(len(wordsearch)):
                wordsearchblock.append(wordsearch[x].split(" "))

            print(wordsearchblock)
            dictionary=PyDictionary()

            for x in range(len(wordsearchblock)):
                if(wordsearchblock[x][1]=="VB"):
                    meaningword=(dictionary.meaning(wordsearchblock[x][0])['Verb'][0:2])
                    meaninglist.append("Verb"+"#"+str(meaningword))
                else:
                    try:
                        meaningword=(dictionary.meaning(wordsearchblock[x][0])['Noun'][0:2])
                        meaninglist.append("Noun"+"#"+str(meaningword))
                    except:
                        meaningword=(dictionary.meaning(wordsearchblock[x][0]))
                        meaninglist.append(" "+"#"+str(meaningword))

            if(len(meaninglist)>0):
                pofspeechandmeaning.append(meaninglist[0].split("#"))
                data["wordmeaningclass"]=pofspeechandmeaning[0][0]
                data["wordmeaning"]=pofspeechandmeaning[0][1][1:-1]
            else:
                data["wordmeaningclass"]="Currently not available"
                data["wordmeaning"]="Currently not available"


            languagedetect=translator.detect(uservoicetext)
            data["languagedetect"]=languagedetect.lang

            synonyms = []
            antonyms = []
            synlist=[]
            anotolist=[]

            for syn in wordnet.synsets(str1):
                for l in syn.lemmas():
                    synonyms.append(l.name())
                    if l.antonyms():
                         antonyms.append(l.antonyms()[0].name())

            synlist.append(list(set(synonyms)))
            anotolist.append(list(set(antonyms)))

            data['synonyms']=synlist[0]
            data['antonyms']=anotolist[0]
            data['rootword']=str2
            data["True"]=str1

            return JsonResponse(data)

        elif uservoicetext.startswith('codesentiment'):
            uservoicetext=uservoicetext.replace('codesentiment','')

            dt1=translator.translate(uservoicetext)        
            str1=dt1.text

            paralleldots.set_api_key("s9OZqpcehQAN1KFRz2Yo9uV2eIaCdP64QflDkwDoFRo")

            print(str1)

            temp=paralleldots.sentiment(str1)
            #temp={'sentiment': {'negative': 0.004, 'neutral': 0.03, 'positive': 0.967}}
            temp=temp['sentiment']

            prob=(max(temp['positive'],temp['negative'],temp['neutral']))

            sentimentclass = [key  for (key, value) in temp.items() if value == prob]

            data["sentiment"]=sentimentclass
            data["True"]=str1

            return JsonResponse(data)
        elif uservoicetext.startswith('codetrans'):
            uservoicetext=uservoicetext.replace('codetrans','')

            dt1=translator.translate(uservoicetext)        
            str1=dt1.text

            print(str1)
            data["True"]=str1

            return JsonResponse(data)
        else:
            notepadstatus  = "notepad.exe" in (p.name() for p in psutil.process_iter())

            if(notepadstatus==True):
                if("stop writing" in str1.lower()):
                    pyautogui.hotkey('ctrl', 's')
                elif('enter' in str1.lower()):
                    pyautogui.press('enter')
                elif('close' in str1.lower()):
                    pyautogui.hotkey('alt', 'f4')
                    notepadstatus  = "notepad.exe" in (p.name() for p in psutil.process_iter())
                    if(notepadstatus==True):
                        pyautogui.press('right')
                        pyautogui.press('enter')
                    engine.say("File saved successfully on your Desktop!!!")
                    engine.runAndWait()
                    data['True']='writeFlag1'
                    return JsonResponse(data)
                elif('copy' in str1.lower()):
                    pyautogui.hotkey('shift','ctrl','left')
                    time.sleep(0.2)
                    pyautogui.hotkey('ctrl','c')
                    time.sleep(0.2)
                    pyautogui.hotkey('ctrl','v')
                    pyautogui.hotkey('ctrl','v')
                elif('remove' in str1.lower()):
                    pyautogui.hotkey('shift','ctrl','left')
                    pyautogui.press('backspace')
                elif('space' in str1.lower()):
                    pyautogui.press('space') 
                else:
                    pyautogui.write(str1, interval=0.25)
            else:
                if("start" and "writing"  in str1.lower()):
                    Popen(["start", "/MAX", "notepad"], shell=True)
                    data['True']=str1
                    return JsonResponse(data)


            if("sentiment"  in str1.lower()):
                data['True']='sentiFlag0'
                return JsonResponse(data)
            

            if("screenshot"  in str1.lower()):
                myScreenshot = pyautogui.screenshot()
                myScreenshot.save(desktopdir+"/file1.png")
                image=Image.open(desktopdir+"/file1.png") 
                image.show()
                time.sleep(0.1)
                engine.say("Heres the preview, Screenshot saved successfully on your Desktop!!!")
                engine.runAndWait()
                data['True']="screenshotFlag1"
                return JsonResponse(data)

            if("translation" in str1.lower()):
                data['True']="translateFlag1"
                return JsonResponse(data)

            if("morphology" in str1.lower()):
                data['True']="translateFlag0"
                return JsonResponse(data)

            if('close' in str1.lower()):
                pyautogui.hotkey('alt', 'f4')

            if('browser' in str1.lower()):
                webbrowser.get("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s").open_new_tab("")

            if('youtube' in str1.lower()):
                webbrowser.get("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s").open_new_tab("youtube.com")
            
            if('stop' or 'continue' in str1.lower()):
                pyautogui.press('space')  

            if('down' in str1.lower()):
                pyautogui.press('down')

            if('top' in str1.lower()):
                pyautogui.press('up')

            if('left' in str1.lower()):
                pyautogui.press('left')

            if('right' in str1.lower()):
                pyautogui.press('right')
            
            if('menu' in str1.lower()):
                pyautogui.press('win')

            if('select' in str1.lower()):
                pyautogui.press('enter')

            if('music' in str1.lower()):
                webbrowser.get("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s").open_new_tab("https://www.youtube.com/watch?v=Htaj3o3JD8I")

            if('mute' in str1.lower()):
                pyautogui.press('m')

            if('escape' in str1.lower()):
                pyautogui.press('escape')

            if('volume up' in str1.lower()):
                pyautogui.hotkey('fn','volumeup')

            if('volume down' in str1.lower()):
                pyautogui.hotkey('fn','volumedown')

            if('home screen' in str1.lower()): 
                pyautogui.hotkey('win','d')

            if('maximum' in str1.lower()): 
                pyautogui.hotkey('win','up')

            if('minimum' in str1.lower()):
                pyautogui.hotkey('win','down')

            if('back' in str1.lower()):
                pyautogui.hotkey('backspace')

            if uservoicetext.startswith('write'):
                str1=str1.replace('write ','')
                pyautogui.write(str1, interval=0.25)


            print(str1)
            data["True"]=str1

            return JsonResponse(data)
             

        
        
def vrdatatxt(request):
    if request.method == "POST":
        data={}
        str1=""
        translator = Translator()
        uservoicetext = request.POST['voicedata']
        
        dt1=translator.translate(uservoicetext)        
        str1=dt1.text

        #notepadpath = "C:/Users/shaik/Desktop/batch.bat"
        file1= open("C:/Users/shaik/Desktop/batch.txt",'w')
        file1.write(str1)
        file1.close()
        Popen(["start", "/MAX", "C:/Users/shaik/Desktop/batch.txt"], shell=True)

        data['True']=str1
        return JsonResponse(data)
        

