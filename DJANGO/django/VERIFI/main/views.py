from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.db import connection
from collections import namedtuple
#from .forms import UploadFileForm 
from django.shortcuts import render
#from django.conf import settings
#from django.core.files.storage import FileSystemStorage
from .models import Document
from django.contrib import messages


import bcrypt 



def namedtuplefetchall(cursor):
    """
    Return all rows from a cursor as a namedtuple.
    Assume the column names are unique.
    """
    desc = cursor.description
    nt_result = namedtuple("Result", [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

def dictfetchall(cursor):
    """
    Return all rows from a cursor as a dict.
    Assume the column names are unique.
    """
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def convertToBinaryData(filename):

    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData


# *****************************************************************************************************************


def login(request):
    
    context = {}
    return render(request, "main/login.html", context)
    
def authenticate(request):

    if request.method == 'POST':
        # Get the forms credentials
        username = request.POST['username']
        password = request.POST['password']
        failure_message ="username and/or password is invalid"
        # authenticate the user creds against the DB.

        # see https://www.makeuseof.com/encrypt-password-in-python-bcrypt/ to employ bcrypt encryption validation. 
        # note: the password field in the users table may need the datatype to be changed to accomodate utf-8

        
        with connection.cursor() as cursor:
            cursor.execute("select uid, first_name, last_name from users where user_name = %s and password = %s", (username, password))

            if cursor.rowcount > 0:

                # get the user uuid (created when the user was created) to pass to the next page
                # as it is used for permissions
                # uid = cursor.fetchone()[0]
                allvals = cursor.fetchall()

                uid = allvals[0][0]
                firstname = allvals[0][1]
                lastname = allvals[0][2]

                if uid > '':
                    # ****************************************
                    # get user permissions, user roles, etc and pass into context
                    # depending on the user type, navigate to the appropriate page (i.e. admin page, dashboard, etc)
                    # log activity and page navigations
                    request.session['uid'] = uid
                    args = [uid]
                    cursor.callproc("sp_User_Get_MainPermissions", args)
                    menu_items = dictfetchall(cursor)

                    context = {'uid' : uid, 'firstname' : firstname, 'lastname' : lastname, 'menu_items' : menu_items, 'menu_items_count' : len(menu_items) }
                    return render(request, "main/maindashboard.html", context)
                    # ****************************************
                else:
                    return HttpResponse("username and/or password is invalid")
            else:
                context = {'failure_message' : failure_message}

                messages.info(request, failure_message)
                url = reverse("main:login")
                return HttpResponseRedirect(url, context)

    else:
        raise Http404("invalid address, page not found")


def administration(request):
    # query the database, get all the widgets for this uid  
    context = {}
    return render(request, "main/administrationcontents.html", context)

def dashboard(request):
    # query the database, get all the widgets for this uid  
    context = {}
    return render(request, "main/dashboardcontents.html", context)

def settings(request):
    # query the database, load all the permissions for settings for this uid

    with connection.cursor() as cursor:
        # request.session['uid'] = uid
        cursor.callproc("sp_Get_SurveyQuestions",)    
        questions_list = dictfetchall(cursor)

    with connection.cursor() as cursor:
        cursor.callproc("sp_Get_SurveyHeader")
        header_list = dictfetchall(cursor)


    context = {'questions_list' : questions_list, 'header_list' : header_list}

    return render(request, "main/settingscontents.html", context)    

def reports(request):
    # query the database and load all the reports for this uid
    context = {}
    return render(request, "main/reportscontents.html", context)    

def transactions(request):
    # query the database and load all the statuses for this uid
    context = {}
    return render(request, "main/transactionscontents.html", context)    

def data(request):

    uid = request.session.get('uid')
    #context= {'uid' : uid}  

    if request.method == 'POST' and request.FILES['myfile']:

        myfile = request.FILES['myfile']

        #myFileConverted = convertToBinaryData(myfile)
        # Document.objects.create(name=myfile.name, file=myfile)

        # create file listed in DB table named "main_document" and save to local filesystem
        newEntry = Document(file=myfile)
        newEntry.save()

        # read local filesystem for file just added and upload full file to db table uploaded_documents
        readablefile = convertToBinaryData(newEntry.file.path)


        # need to change to procedure to upload file as blob (arg to proc) and returns list of files uploaded to pass
        # back to the page... note: this proc needs to consider a blob arg that is null, if so... then just return list.
        with connection.cursor() as cursor:
                # request.session['uid'] = uid
                args = [uid, myfile.name, newEntry.file.path, readablefile]
                cursor.callproc("sp_User_Insert_Get_FilesUploaded", args)

        # cursor = connection.cursor()
            #cursor.execute("insert into uploaded_documents (file_name, file_path, document, uploaded_by_uid) values (%s, %s, %s, %s)", (myfile.name, newEntry.file.path, readablefile, uid))
                uploaded_file = myfile.name
                files_list = dictfetchall(cursor)

        # get list of files already uploaded and pass to the context object to load back on the page.
        return render(request, 'main/uploadcontents.html', {'uploaded_file': uploaded_file, 'uid' : uid, 'files_list' : files_list })
  
    with connection.cursor() as cursor:
        args = [uid, None, None, None]
        cursor.callproc("sp_User_Insert_Get_FilesUploaded", args)
        files_list = dictfetchall(cursor)
        context = {'uid' : uid, 'files_list' : files_list}
        return render(request, 'main/uploadcontents.html', context)
    

