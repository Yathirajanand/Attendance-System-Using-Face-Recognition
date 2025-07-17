from attendance.forms import StudentForm, FacultyForm, LoginForm
from attendance.models import FacultyModel

import smtplib
import random

from attendance.service1 import recognize_faces, register_face
from django.shortcuts import render
from datetime import datetime
from .models import StudentModel, AttendanceModel

def send_otp(email,otp):

    try:
        s = smtplib.SMTP("smtp.gmail.com", 587)  # 587 is a port number
        s.starttls()
        s.login("yathirajananda@gmail.com", "kxtbjznevzcvgquh")

        s.sendmail("yathirajananda@gmail.com", email, otp)
        s.quit()
        print("mail sent successfully")

    except Exception as e:
        print(e)
        print("Send OTP via Email","Please enter the valid email address OR check an internet connection")

def sendemail_notification(email,message):

    try:
        s = smtplib.SMTP("smtp.gmail.com", 587)  # 587 is a port number
        s.starttls()
        s.login("srivanitadaka24@gmail.com", "rytzkvbpfcztfuge")

        s.sendmail("srivanitadaka24@gmail.com", email, message)
        s.quit()
        print("mail sent successfully")

    except Exception as e:
        print(e)
        print("Send Message via Email","Please enter the valid email address OR check an internet connection")


def sendemail(request):

    for student in StudentModel.objects.all():

        if student is not None:

            td = datetime.now()
            cd = str(td.day) + "-" + str(td.month) + "-" + str(td.year)

            for attendance in AttendanceModel.objects.filter(studentid=student.rno):
                if str(attendance.date) == cd:
                    if attendance.isattended=="no":
                        sendemail_notification(student.email,"Your Child is Not Attended today")

    branch = request.session['branch']
    return render(request, "viewstudentes.html", {"students": StudentModel.objects.filter(branch=branch)})

def registration(request):

    # Get the posted form
    registrationForm = StudentForm(request.POST)

    print("in function")
    if registrationForm.is_valid():
        print("in if")
        regModel = StudentModel()

        otp = random.randint(1000, 9999)
        otp = str(otp)

        regModel.name = registrationForm.cleaned_data["name"]
        regModel.email = registrationForm.cleaned_data["email"]
        regModel.mobile = registrationForm.cleaned_data["mobile"]
        regModel.rno = registrationForm.cleaned_data["rno"]
        regModel.password = registrationForm.cleaned_data["password"]
        regModel.year = registrationForm.cleaned_data["year"]
        regModel.section = registrationForm.cleaned_data["section"]
        regModel.branch = registrationForm.cleaned_data["branch"]
        regModel.isverified = "no"
        regModel.otp = otp
        regModel.status = "no"

        user = StudentModel.objects.filter(rno=regModel.rno).first()

        if user is not None:
            return render(request, 'registration.html', {"message": "User All Ready Exist"})
        else:
            regModel.save()
            print("after save")
            send_otp(regModel.email, otp)
            register_face(regModel.rno)
            print("Done123")
            #train_recognizer()
            return render(request, 'registration.html', {"message": "Registred Sucessfully"})
    else:
        print("in else")
        return render(request, 'registration.html', {"message": "Invalid Form"})

def loginpage(request):
    return render(request,'login.html', {"usertype":request.GET['usertype']})

def login(request):

    if request.method == "GET":
        # Get the posted form
        loginForm = LoginForm(request.GET)

        if loginForm.is_valid():

            uname = loginForm.cleaned_data["username"]
            upass = loginForm.cleaned_data["password"]
            usertype = loginForm.cleaned_data["usertype"]

            if usertype=="admin":
                if uname == "admin" and upass == "admin":
                    request.session['role'] = "admin"
                else:
                    return render(request, 'index.html', {"message": "Invalid Credentials"})
            elif usertype=="student":
                user = StudentModel.objects.filter(rno=uname, password=upass, isverified="yes",status='yes').first()
                if user is not None:
                    request.session['role'] = "student"
                else:
                    return render(request, 'index.html', {"message": "Invalid Credentials"})
            elif usertype=="faculty":
                faculty = FacultyModel.objects.filter(username=uname, password=upass).first()
                if faculty is not None:
                    request.session['role'] = "faculty"
                    request.session['branch']=faculty.branch
                else:
                    return render(request, 'index.html', {"message": "Invalid Credentials"})

            request.session['username'] = uname

            if request.session['role'] in "admin":
                return render(request, "viewfacultyes.html", {"facultys": FacultyModel.objects.all()})
            elif request.session['role'] in "student":

                count = AttendanceModel.objects.values('date').distinct().count()
                username = request.session['username']

                attended = 0

                for attendance in AttendanceModel.objects.filter(studentid=uname):
                    if attendance.isattended == 'yes':
                        attended = attended + 1

                percentage = 0
                if count != 0 and attended != 0:
                    percentage = count / attended

                return render(request, "viewattendances.html", {"attendances": {username: percentage * 100}})

            elif request.session['role'] in "faculty":
                branch = request.session['branch']
                return render(request, "viewstudentes.html", {"students":StudentModel.objects.filter(branch=branch)})
            else:
                return render(request, 'index.html', {"message": "Invalid Credentials"})

        return render(request, 'index.html', {"message": "Invalid From"})

    return render(request, 'index.html', {"message": "Invalid Request"})

def logout(request):
    try:
        del request.session['username']
    except:
        pass
    return render(request, 'index.html', {})

def activate_account(request):

    username=request.GET['username']
    otp=request.GET['otp']

    model=StudentModel.objects.filter(rno=username).first()

    if model is not None:
        if model.otp in otp:
            StudentModel.objects.filter(rno=username).update(isverified="yes")
            return render(request, 'index.html', {"message": "your account is activated"})
        else:
            return render(request, 'activate.html', {"message":"invalid otp"})
    else:
        return render(request, 'activate.html', {"message":"invalid username"})

def getstudents(request):
    branch = request.session['branch']
    return render(request, "viewstudentes.html", {"students": StudentModel.objects.filter(branch=branch)})

def deletestudent(request):

    studentid= request.GET['studentid']
    StudentModel.objects.get(id=studentid).delete()

    return render(request, "viewstudentes.html", {"students": StudentModel.objects.all()})

def activateAccount(request):

    username=request.GET['username']
    status=request.GET['status']
    print("RNO",username,"status",status)
    StudentModel.objects.filter(id=username).update(status=status)
    #trainimg()
    return render(request, 'viewstudentes.html', {"message":"status updated","students": StudentModel.objects.all()})

#====================================================================================================
def addfaculty(request):

    facultyForm = FacultyForm(request.POST)

    if facultyForm.is_valid():

        name = facultyForm.cleaned_data["name"]
        email = facultyForm.cleaned_data["email"]
        mobile = facultyForm.cleaned_data["mobile"]
        username = facultyForm.cleaned_data["username"]
        password = facultyForm.cleaned_data["password"]
        branch = facultyForm.cleaned_data["branch"]

        FacultyModel(name=name,email=email,mobile=mobile,username=username,password=password,branch=branch).save()

        return render(request, 'addfaculty.html', {"message": "Faculty Posted SuccessFully"})

    return render(request, 'addfaculty.html', {"message": "Faculty Request Failed"})

def getfacultys(request):
    return render(request, "viewfacultyes.html", {"facultys":FacultyModel.objects.all()})

def deletefaculty(request):

    facultyid= request.GET['facultyid']
    FacultyModel.objects.get(id=facultyid).delete()

    return render(request, "viewfacultyes.html", {"facultys": FacultyModel.objects.all()})


def addinattendance(request):

    rnos = recognize_faces()  # List of recognized student IDs

    td = datetime.now()
    cd = f"{td.day}-{td.month}-{td.year}"  # Formatted date string
    cr = td.hour  # Current hour

    for rno in rnos:
        student = StudentModel.objects.filter(rno=rno).first()

        if student:
            # Check if the morning attendance is already recorded
            isInserted = AttendanceModel.objects.filter(studentid=rno, date=cd, intime=cr).exists()

            if not isInserted:
                AttendanceModel.objects.create(
                    studentid=rno,
                    date=cd,
                    intime=cr,
                    outtime="",  # Outtime will be updated later
                    branch=student.branch,
                    isattended="no"
                )

    return render(request, "viewattendances.html", {
        "attendances": AttendanceModel.objects.filter(branch=request.session['branch'])
    })


def addoutattendance(request):

    rnos = recognize_faces()  # List of recognized student IDs

    td = datetime.now()
    cd = f"{td.day}-{td.month}-{td.year}"  # Formatted date string
    cr = td.hour  # Current hour

    for rno in rnos:

        attendance = AttendanceModel.objects.filter(studentid=rno, date=cd).first()

        print
        if attendance and attendance.outtime is "":
            # Update outtime and mark attendance as "yes" if both sessions exist
            print("attendence is updating")
            attendance.outtime = cr
            attendance.isattended = "yes"
            attendance.save()

    role = request.session['role']
    count = AttendanceModel.objects.values('date').distinct().count()
    username = request.session['username']

    if role == "faculty":

        attendancemap = dict()

        for student in StudentModel.objects.filter(branch=request.session['branch']):

            attended = 0
            for attendance in AttendanceModel.objects.filter(studentid=student.rno):
                if attendance.isattended == 'yes':
                    attended = attended + 1

            percentage = 0
            if count != 0 and attended != 0:
                percentage = count / attended

            attendancemap.update({student.rno: percentage * 100})

        return render(request, "viewattendances.html", {"attendances": attendancemap})

    elif role == "student":

        attended = 0

        for attendance in AttendanceModel.objects.filter(studentid=username):
            if attendance.isattended == 'yes':
                attended = attended + 1

        percentage = 0
        if count != 0 and attended != 0:
            percentage = count / attended

        return render(request, "viewattendances.html", {"attendances": {username: percentage * 100}})

def getattendance(request):

    role=request.session['role']
    count = AttendanceModel.objects.values('date').distinct().count()
    username=request.session['username']

    if role=="faculty":

        attendancemap=dict()

        for student in StudentModel.objects.filter(branch=request.session['branch']):

            attended = 0
            for attendance in AttendanceModel.objects.filter(studentid=student.rno):
                if attendance.isattended == 'yes':
                    attended = attended + 1

            percentage = 0
            if count != 0 and attended != 0:
                percentage = count / attended

            attendancemap.update({student.rno:percentage*100})


        return render(request, "viewattendances.html", {"attendances": attendancemap})

    elif role=="student":

        attended=0

        for attendance in AttendanceModel.objects.filter(studentid=username):
            if attendance.isattended=='yes':
                attended=attended+1

        percentage=0
        if count!=0 and attended!=0:
            percentage=count/attended

        return render(request, "viewattendances.html", {"attendances":{username:percentage*100}})