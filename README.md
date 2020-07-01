# resumeparser - 
A python/django based web app to upload a resume file whether in text format or in docx or in pdf ., the relevant  tags will be crawled through and displayed as well as stored in mysql database..

link-resumeparser.pythonanywhere.com

# direct deploy 

python manage.py runserver

#connection to database -mysql

default database name taken - resumeparser 

table made in models.py called UserResumes

uploads document to folder UploadedResumes

#Algorithm:
non ML Approach

firstly to create a text file by converting the pdf file if uploaded to normal text format using PyPDF2

pip install PyPDF2

then extractings things we can get through regular Expressions like-

Mobile No,
Email,
CGPA, GRADES , 10TH AND 12TH %

then to extract relevant tags  like -

objective,
personal info including name and address,
education info, 
skill set,
projects,
experience,
hobbies, etc

Now the relevant tags are stored in a list firstly,
the crawled text from the text file of the resume is converted to tokens,
which is then iterated lets say for 
extract objective function()
iterateing whole list of tokens(words):
    if objective or aim tag is found:
          then further iterating from the list after the aim token 
		        if token is not in relevant gtags list:
				    added to temporary string 
				else:
                     break
       therefore if another relevant tag comes we iterate till that point 
and then break, the temporary string will now give the aim or objective,

same is done with functions for extracting other relevant tags.

This is a another not so accurate approach , but yeah worthwile ,
for detailed and more accurate results , use of machine learning, via neural nets should be done..

#requirements 

PyPDF2 package
Django 1.10
and other corresponding packages..	   







