import os
import io
import zipfile
import re
from PIL import Image
import pytesseract
from wand.image import Image as wi
import gc
#import PyPDF2
import PyPDF4 as PyPDF2
from django.shortcuts import render
from start.forms import UploadFileForm
from start.models import UserResumes


try:
    from xml.etree.cElementTree import XML
except ImportError:
    from xml.etree.ElementTree import XML

WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
PARA = WORD_NAMESPACE + 'p'
TEXT = WORD_NAMESPACE + 't'

relevtags=['Hobbies','HOBBIES','ExtraCurricularActivities','Activites','ACTIVITIES','Projects','PROJECTS','WORK','Work','ACHIEVEMENTS','Achievements','SKILLS','Skills','Experience','EXPERIENCE','Qualification','QUALIFICATION','Education','EDUCATION','EDUCATIONAL','Educational']






def get_docx_text(path):
    """
    Take the path of a docx file as argument, return the text in unicode.
    """
    document = zipfile.ZipFile(path)
    xml_content = document.read('word/document.xml')
    document.close()
    tree = XML(xml_content)

    paragraphs = []
    for paragraph in tree.getiterator(PARA):
        texts = [node.text
                 for node in paragraph.getiterator(TEXT)
                 if node.text]
        if texts:
            paragraphs.append(''.join(texts))

    return '\n\n'.join(paragraphs)


def convertpdf(name):
    #print("hiiii")
    my_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(my_path, "../UploadedResumes/")
    pdfobj=open(path+str(name), 'rb')
    pdfreader=PyPDF2.PdfFileReader(pdfobj)
    #print(pdfreader.numPages)
    x = name[0:len(name)-3]
    desturl =str(x)+"txt"
    fob = open(path+desturl, "w", encoding="utf-8")
    for page in pdfreader.pages:
        s = page.extractText()
        #print(s)
        lines=s.split("\n")
        #print(lines)
        for line in lines:
            fob.write((line + "\n"))

    fob.close()
    pdfobj.close()

    final_path=path+desturl
    if file_is_empty(final_path):
        convertpdf1(name)

def file_is_empty(path):
    content = open(path, 'r').read()
    if re.search(r'^\s*$', content):
        return True
    else:
        return os.stat(path).st_size == 0

def convertpdf1(name):
    my_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(my_path, "../UploadedResumes/")
    pdf_path=path+str(name)
    pdf = wi(filename=pdf_path, resolution=300)
    pdfImg = pdf.convert('jpeg')
    imgBlobs = []
    extracted_text = []
    x = name[0:len(name) - 3]
    desturl = str(x) + "txt"
    fob = open(path+ desturl, "w", encoding="utf-8")
    for img in pdfImg.sequence:
        page=wi(image=img)
        imgBlobs.append(page.make_blob('jpeg'))

    for imgBlob in imgBlobs:
        im = Image.open(io.BytesIO(imgBlob))
        text = pytesseract.image_to_string(im, lang='eng')
        lines = text.split("\n")
        # print(lines)
        for line in lines:
            fob.write((line + "\n"))
    fob.close()

def handle_uploaded_file(file, name, content):
    my_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(my_path, "../UploadedResumes/")
    fo = open(path + str(name), "wb+")
    for chunk in file.chunks():
        fo.write(chunk)
    fo.close()
    if content.endswith("pdf"):
        convertpdf(name)
    if content.endswith("document"):
        text = get_docx_text(path+str(name))
        text = os.linesep.join([s for s in text.splitlines() if s])
        s=str(name)
        fo = open(path+s[:s.rfind('.')]+".txt", "w",encoding="utf-8")
        fo.write(text)
        fo.close()


def index(request):
    if request.method=="POST":
        uploadform=UploadFileForm(request.POST, request.FILES)
        if uploadform.is_valid():
            print("its in normal")
            file = request.FILES['file']
            print(file.name)
            print(file.content_type)
            handle_uploaded_file(file, file.name, file.content_type)
            s=str(file.name)
            if s.__contains__('docx'):
                x = file.name[0:len(file.name) - 4]
            elif s.__contains__('doc'):
                    x = file.name[0:len(file.name) - 3]
            else:
                x = file.name[0:len(file.name) - 3]
            desturl = str(x) + "txt"
            my_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
            path = os.path.join(my_path, "../UploadedResumes/")
            fo = open(path + desturl, "r", encoding="utf-8")
            text = fo.read()
            fo.close()
            fo = open(path + desturl, "r", encoding="utf-8")
            s = fo.readlines()
            fo.close()
            print(text)
            print(s)
            # num = re.sub(r'[\n][\n]', "", text)
            num2 = re.sub(r'[\n]', "", text)
            slist = num2.split()
            mobno=extractmobile(text)
            cgpa=extractcgpa(text)
            email=extractemail(num2)
            perc=extractperc(num2)
            pinfo=extractpersonalinfo(slist)
            obj=extractobjective(slist)
            edu=extracteducation(slist)
            skill=extractskills(slist)
            achieve=extractachievements(slist)
            projects=extractprojects(slist)
            hobb=extracthobbies(slist)
            if cgpa==None:
                cgpa = 0.0
            if mobno == None:
                    mobno = 0
            if email == None:
                    email = ''

            user=UserResumes(pinfo=pinfo,cgpa=cgpa,mobile=mobno,email=email,objective=obj,education=edu,skill=skill,achievements=achieve,projects=projects,hobbies=hobb)
            user.save()
            for i in UserResumes.objects.all():
                print(i.mobile)
            return render(request, 'success.html', {'mobno':mobno,'email':email,'pinfo':pinfo,'obj':obj,'edu':edu,'skills':skill,'achieve':achieve,'projects':projects,'hobbies':hobb})
    else:
        print("default form created")
        form=UploadFileForm()
        #book = UserResumes(name="ujjwal", address="vfdv", mobile="9760017250", email="uj00007@gmail.com")
        #book.save()
    return render(request,'index.html',{'fileform':form})


def extractmobile(s):
    m = re.search('[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]', s)
    if m:
        #print("hello")
        found = m.group(0)
        return found

def extractcgpa(s):
    m = re.findall('[0-9][.][0-9]', s)
    if m:
        #print("hello")
        found = m
        return found[0]

def extractemail(s):
    #print("vsdf")
    m = re.findall('[ ][a-z|0-9.]+[@][a-z]+[.][a-z]+[ ]', s)
    if m:
        #print("hello")
        found = m
        return found[0]

def extractperc(s):
    m = re.findall('[0-9][0-9][.][0-9][0-9]', s)
    if m:
        #print("hello")
        found = m
        return found

def extractpersonalinfo(s):
    text=""
    for i in s:
        i=str(i).strip()
        #print(i)
        if i!="CAREER" and i!="Objective" and i!="Career" and i!="OBJECTIVE":
            text=text+str(i)+" "
        else:
            #print("gaya")
            break
    return text
    #print(ne_chunk(pos_tag(text.strip().split('.'))))

def extractobjective(s):
    global relevtags
    text=""
    for i in range(0,len(s)):
        temp=str(s[i]).strip()
        #print(i)

        if not temp.find("OBJECTIVE"):
            #print(temp)
            #print("found")
            for j in range(i+1,len(s)):
                if str(s[j]).strip() not in relevtags:
                    text=text+str(s[j]).strip()+" "
                else:
                    break
        else:

            continue
    return text
    #print(ne_chunk(pos_tag(text.strip().split('.'))))

def extracteducation(s):
    global relevtags
    text=""
    for i in range(0,len(s)):
        temp=str(s[i]).strip()
        #print(i)

        if not temp.find("EDUCATION") or not temp.find("EDUCATIONAL") or not temp.find("Education") or not temp.find("Educational") or not temp.find("QUALIFICATION"):
            #print(temp)
            #print("found")
            for j in range(i+1,len(s)):
                if str(s[j]).strip() not in relevtags:
                    text=text+str(s[j]).strip()+" "
                else:
                    break
        else:

            continue
    return text


def extractskills(s):
    global relevtags
    text=""
    for i in range(0,len(s)):
        temp=str(s[i]).strip()
        #print(i)

        if not temp.find("SKILLS") or not temp.find("Skills"):
            #print(temp)
            #print("found")
            for j in range(i+1,len(s)):
                if str(s[j]).strip() not in relevtags:
                    text=text+str(s[j]).strip()+" "
                else:
                    break
        else:

            continue
    return text

def extractachievements(s):
    global relevtags
    text=""
    for i in range(0,len(s)):
        temp=str(s[i]).strip()
        #print(i)

        if not temp.find("Achievements") or not temp.find("ACHIEVEMENTS"):
            #print(temp)
            #print("found")
            for j in range(i+1,len(s)):
                if str(s[j]).strip() not in relevtags:
                    text=text+str(s[j]).strip()+" "
                else:
                    break
        else:

            continue
    return text

def extractprojects(s):
    global relevtags
    text=""
    for i in range(0,len(s)):
        temp=str(s[i]).strip()
        #print(i)

        if not temp.find("Projects") or not temp.find("PROJECTS"):
            #print(temp)
            #print("found")
            for j in range(i+1,len(s)):
                if str(s[j]).strip() not in relevtags:
                    text=text+str(s[j]).strip()+" "
                else:
                    break
        else:

            continue
    return text

def extracthobbies(s):
    global relevtags
    text=""
    for i in range(0,len(s)):
        temp=str(s[i]).strip()
        #print(i)

        if not temp.find("Activities") or not temp.find("ACTIVITIES"):
            #print(temp)
            #print("found")
            for j in range(i+1,len(s)):
                if str(s[j]).strip() not in relevtags:
                    text=text+str(s[j]).strip()+" "
                else:
                    break
        else:

            continue
    return text
