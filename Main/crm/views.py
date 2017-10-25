from django.shortcuts import render,HttpResponseRedirect,HttpResponse,get_object_or_404,render_to_response
from django.contrib.auth.views import logout
from .forms import UserForm,AgentForm,User_Form,CustForm,updatem,updatea,updateagc,LogF,import_csv,Validate_Admin,pass_form,Company_Form
from django.views.generic import View
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.utils.translation import gettext as _
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import datetime
from .models import Customer,Agent,Relation,log,RelationLogHistory,Company,CompanyAgentRelation,CompanyCustomerRelation
from django.contrib.auth.models import User
from rest_framework import viewsets
import csv,xlwt,io,xlrd
from.serializers import AgentSerializer,CustomerSerializer
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4,cm,A3
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import Paragraph,Table,TableStyle
from django.core.mail import send_mail
from django.conf import settings


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/main/')


class UserFormView(View):
    form_class=UserForm
    form_class1 = Company_Form
    template_name = "register.html"

    def get(self, request):
        form = self.form_class(None)
        form1 = self.form_class1(None)
        return render(request, self.template_name, {'form':form,'form1':form1})

    def post(self, request):
        form = self.form_class(request.POST or None)
        form1 = self.form_class1(request.POST or None,request.FILES)

        if form.is_valid() and form1.is_valid():

            user = form.save(commit=False)
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user.set_password(password)
            user.is_active = False
            user.save()
            user1 = form.cleaned_data['username']
            print(user1)
            user2 = User.objects.get(username=user1)

            user = authenticate(username=username, password=password)

            form1.save()

            com = CompanyAgentRelation()
            com.company = Company.objects.get(Company_Name=form1.cleaned_data['Company_Name'])
            com.Agents = Agent.objects.get(user=user2)
            com.save()

            messages.success(request,"Your details have been submitted.A confirmation mail will be sent to you on validation of your account")
            return HttpResponseRedirect('/main/')


        return render(request, self.template_name, {'form': form,'form1':form1})


def update_profile(request):
    if request.method == 'POST':
        user_form = User_Form(request.POST, instance=request.user)
        agent_form = AgentForm(request.POST,request.FILES, instance=request.user.agent)
        if user_form.is_valid() and agent_form.is_valid():
            user_form.save()

            agent_form.save()

            messages.success(request, ('Profile Updated'))
            return HttpResponseRedirect('/home/')
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        user_form = User_Form(instance=request.user)
        agent_form = AgentForm(instance=request.user.agent)
        a = Agent.objects.get(user=request.user)
        com = CompanyAgentRelation.objects.filter(Agents=a)
        return render(request, 'profile.html', {
            'user_form': user_form,
            'agent_form': agent_form,
            'b':com,
        })





def update_cust(request):
   if request.user.is_superuser or request.user.is_staff:
       if request.method == 'POST':
           form = CustForm(request.POST, request.FILES)

           if form.is_valid():
               b = form.save()
               a=b.id
               b.dj = timezone.now()
               b.dtc = timezone.now() + timezone.timedelta(days=7, hours=0, minutes=0, seconds=0)
               b.added_by = request.user.username
               b.save()
               user = Agent.objects.get(user=request.user)
               comp = CompanyAgentRelation.objects.get(Agents=user)
               com = CompanyCustomerRelation()
               com.customer = Customer.objects.get(id=a)
               com.company = comp.company
               com.save()
               messages.success(request, _('Your profile was successfully updated!'))
               return HttpResponseRedirect('/home')
           else:
               messages.error(request, _('Please correct the error below.'))
       else:
           form = CustForm()
           a = Agent.objects.get(user=request.user)
           com = CompanyAgentRelation.objects.filter(Agents=a)
           return render(request, 'cust.html', {'form': form,'b':com})

   elif request.user.is_authenticated:
       if request.method == 'POST':
           form = CustForm(request.POST, request.FILES)

           if form.is_valid():
               b = form.save()

               b.dj = timezone.now()
               b.dtc = timezone.now() + timezone.timedelta(days=7, hours=0, minutes=0, seconds=0)
               b.added_by = request.user.username
               a = b.id
               b.save()
               rel=Relation()
               rel.cust = b
               rel.agen = Agent.objects.get(user=request.user)
               rel.date = timezone.now()
               rel.save()
               rell = RelationLogHistory.objects.all()
               for r in rell:
                   if r.cus == rel.cust:
                       r.log = "Agent: {0} was assigned to {1} on {2}".format(rel.ag_nm, rel.cust,
                                                                              datetime.now().date())
                       r.save()

               user = Agent.objects.get(user=request.user)
               comp = CompanyAgentRelation.objects.get(Agents=user)
               com = CompanyCustomerRelation()
               com.customer = Customer.objects.get(id=a)
               com.company = comp.company
               com.save()

               messages.success(request, _('Your profile was successfully updated!'))
               return HttpResponseRedirect('/home')
           else:
               messages.error(request, _('Please correct the error below.'))
       else:
           form = CustForm()
           a = Agent.objects.get(user=request.user)
           com = CompanyAgentRelation.objects.filter(Agents=a)
           return render(request, 'cust.html', {'form': form,'b':com})

def updatema(request, pk):
    a = Relation.objects.filter(cust=pk).exists()
    if a:
        a= Relation.objects.get(cust=pk)
        p = get_object_or_404(Relation, pk=a.id)
        n = get_object_or_404(Customer, pk=pk)
        if request.method == 'POST':
            if request.user.is_staff or request.user.is_superuser:
                form_m = updatem(request.POST or None, instance=p)
                form_a = updatea(request.POST ,request.FILES, instance=n)
                if form_m.is_valid() and form_a.is_valid():
                    form_a.save()
                    b = form_m.save()
                    b.date = timezone.now()
                    b.cust = Customer.objects.get(id=pk)
                    b.save()

                    rell = RelationLogHistory.objects.all()
                    for r in rell:
                        if r.cus == b.cust:
                            if b.agen != None:
                                if r.log!= None:
                                    r.log = r.log + "\nAgent: {0} was assigned to {1} on {2}".format(b.agen.user.first_name, b.cust,datetime.now().date())
                                    r.save()
                                else:
                                    r.log ="Agent: {0} was assigned to {1} on {2}".format(b.agen.user.first_name, b.cust, datetime.now().date())
                                    r.save()
                                messages.success(request,"{0} is the assigned agent for {1}".format(b.agen.user.first_name,b.cust))
                            else:
                                if r.log!= None:
                                    r.log = r.log + "\nNo agent is assigned to customer {0} on {1}".format(b.cust,datetime.now().date())
                                    r.save()
                                    messages.success(request,"No agent assigned to {0}".format(b.cust))
                                else:
                                    r.log = "No agent is assigned to customer {0} on {1}".format(b.cust,
                                                                                                           datetime.now().date())
                                    r.save()
                                    messages.success(request, "No agent assigned to {0}".format(b.cust))


                    return HttpResponseRedirect('/home/')

            else:
                return HttpResponse("You are not the valid user")


        else:
            form_a = updatea(instance=n)
            form_m = updatem(instance=p)

            a = Agent.objects.all()
            user = Agent.objects.get(user=request.user)
            b = CompanyAgentRelation.objects.get(Agents=user)
            c = CompanyAgentRelation.objects.all().filter(company=b.company)
            print(c)
            return render(request, "updatea.html", {'form': form_a,'form_m':form_m, 'c': c, 'a': a})
    else:

        n = get_object_or_404(Customer, pk=pk)
        if request.method == 'POST':
            if request.user.is_staff or request.user.is_superuser:
                form_m = updatem(request.POST or None)
                form_a = updatea(request.POST, request.FILES, instance=n)
                if form_m.is_valid() and form_a.is_valid():
                    form_a.save()
                    b = form_m.save()
                    b.date = timezone.now()
                    b.cust = Customer.objects.get(id=pk)
                    b.save()

                    rell = RelationLogHistory.objects.all()
                    for r in rell:
                        if r.cus == b.cust:
                            if b.agen != None:
                                if r.log!= None:
                                    r.log = r.log + "\nAgent: {0} was assigned to {1} on {2}".format(b.agen.user.first_name, b.cust,datetime.now().date())
                                    r.save()
                                else:
                                    r.log ="Agent: {0} was assigned to {1} on {2}".format(b.agen.user.first_name, b.cust, datetime.now().date())
                                    r.save()
                                messages.success(request,"{0} is the assigned agent for {1}".format(b.agen.user.first_name,b.cust))
                            else:
                                if r.log!= None:
                                    r.log = r.log + "\nNo agent is assigned to customer {0} on {1}".format(b.cust,datetime.now().date())
                                    r.save()
                                    messages.success(request,"No agent assigned to {0}".format(b.cust))
                                else:
                                    r.log = "No agent is assigned to customer {0} on {1}".format(b.cust,
                                                                                                           datetime.now().date())
                                    r.save()
                                    messages.success(request, "No agent assigned to {0}".format(b.cust))

                    return HttpResponseRedirect('/home/')

            else:
                return HttpResponse("You are not the valid user")


        else:
            form_a = updatea(instance=n)
            form_m = updatem()

            a = Agent.objects.all()
            user = Agent.objects.get(user=request.user)
            b = CompanyAgentRelation.objects.get(Agents=user)
            c = CompanyAgentRelation.objects.all().filter(company=b.company)
            print(c)
            return render(request, "updatea.html", {'form': form_a, 'form_m': form_m, 'c': c, 'a': a})


# def updatead(request, pk):
#     a = Relation.objects.filter(cust=pk).exists()
#     if a :
#         a=Relation.objects.get(cust=pk)
#         p = get_object_or_404(Relation, pk=a.id)
#         n = get_object_or_404(Customer, pk=pk)
#
#         if request.method == 'POST':
#             if request.user.is_staff:
#                 form_m = updatem(request.POST or None, instance=p)
#                 form_a = updatea(request.POST or None, instance=n)
#                 if form_a.is_valid() and form_m.is_valid:
#                     form_a.save()
#                     b = form_m.save()
#                     b.date = timezone.now()
#                     b.cust = Customer.objects.get(id=pk)
#                     b.save()
#                     rell = RelationLogHistory.objects.all()
#                     for r in rell:
#                         if r.cus == b.cust:
#                             r.log = r.log + "\nAgent: {0} was assigned to {1} on {2}".format(b.ag_nm, b.cust,datetime.now().date())
#                             r.save()
#
#                     messages.success(request, "{0} is the assigned agent for {1}".format(b.ag_nm, b.cust))
#                     return HttpResponseRedirect('/home/')
#
#             else:
#                 return HttpResponse("You are not the valid user")
#
#
#         else:
#             form_a = updatea(instance=n)
#             form_m = updatem(instance=p)
#             return render(request, "updatea.html", {'form_a': form_a, 'form_m': form_m})
#
#     else:
#         n = get_object_or_404(Customer, pk=pk)
#         if request.method == 'POST':
#             if request.user.is_staff:
#                 form_m = updatem(request.POST or None)
#                 form_a = updatea(request.POST or None, instance=n)
#                 if form_a.is_valid() and form_m.is_valid:
#                     form_a.save()
#                     b = form_m.save()
#                     b.cust = Customer.objects.get(id=pk)
#                     b.date = timezone.now()
#                     b.save()
#                     rell = RelationLogHistory.objects.all()
#                     for r in rell:
#                         if r.cus == b.cust:
#                             r.log ="Agent: {0} was assigned to {1} on {2}".format(b.ag_nm, b.cust,datetime.now().date())
#                             r.save()
#
#                     messages.success(request, "{0} is the assigned agent for {1}".format(b.ag_nm, b.cust))
#                     return HttpResponseRedirect('/home/')
#
#             else:
#                 return HttpResponse("You are not the valid user")
#
#
#         else:
#             form_a = updatea(instance=n)
#             form_m = updatem()
#             return render(request, "updatea.html", {'form_a': form_a, 'form_m': form_m})


def AgentInfo(request):
    lists = Agent.objects.all()
    users = User.objects.all().order_by("date_joined")
    comp = CompanyAgentRelation.objects.all().order_by("Agents")
    zipped = zip(lists, users)
    return render(request,'agentinfo.html',{'comp':comp,'zip':zipped})

def Ass(request):
    cus = Customer.objects.all()
    rel = Relation.objects.all()
    rel = rel.order_by("-date")
    d = {'zip': zip(cus, rel)}
    return render(request,'unas.html',{'cus':cus,'rel':rel})


def updateag(request, pk):
    p = get_object_or_404(Customer, pk=pk)
    n = Relation.objects.get(cust = pk)
    if request.method == 'POST':
        if request.user.is_authenticated and request.user.first_name==n.ag_nm:
            form = updateagc(request.POST or None, instance=p)
            if form.is_valid():
                form.save()

                return HttpResponseRedirect('/home/')

        else:
            return HttpResponse("You are not the valid user")


    else:
        form = updateagc(instance=p)
        return render(request, "updateag.html", {'form': form})






def CusDet(request):
    if request.user.is_authenticated and not request.user.is_superuser:
        a=Agent.objects.get(user=request.user)
        com = CompanyAgentRelation.objects.filter(Agents=a)
        co=CompanyAgentRelation.objects.get(Agents=a)
        o=CompanyCustomerRelation.objects.all().filter(company=co.company).values("customer")
        cus=Customer.objects.all().filter(id__in=o)
        rel =Relation.objects.all().filter(cust__in=cus)
        return render(request,'cusa.html',{'object_list':cus,'rel':rel,'b':com})





def AddL(request,pk):

    if request.method == 'POST':
        form = LogF(request.POST)
        if form.is_valid():
            b=form.save()
            b.cust = Customer.objects.get(id=pk)
            b.agent=Agent.objects.get(user=request.user)
            b.date = timezone.now()
            b.save()

            return HttpResponseRedirect('/home/')

        else:
            return HttpResponse("You are not the valid user")


    else:
        form = LogF()
        cus=Customer.objects.get(id=pk)
        logs = log.objects.all()
        rel= Relation.objects.all()
        loghis = RelationLogHistory.objects.all()
        return render(request, "log.html", {'form': form,'logs':logs,'rel':rel,'loghis':loghis,'object':cus})



class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class AgentViewSet(viewsets.ModelViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer


def xml1(request):
    response = render_to_response('agents.xml', {'ag': Agent.objects.all(), })
    response['Content-Type'] = 'application/xml;'
    return response

def export_users_csv(request):
    if request.user.is_staff:

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="customers.csv"'

        writer = csv.writer(response)
        writer.writerow(['First name', 'Last name','Address','Avatar','Phone', 'Email address'])
        a = Agent.objects.get(user=request.user)
        co = CompanyAgentRelation.objects.get(Agents=a)
        o = CompanyCustomerRelation.objects.all().filter(company=co.company).values("customer")

        cust = Customer.objects.all().filter(id__in=o).values_list('first_name', 'last_name', 'address','avatar','phone','email')

        for c in cust:
            writer.writerow(c)

        return response

    elif request.user.is_authenticated:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="customers.csv"'

        writer = csv.writer(response)
        writer.writerow(['First name', 'Last name','Address','Avatar','Phone', 'Email address'])
        rel = Relation.objects.all().filter(agen=Agent.objects.filter(user=request.user))

        cu=Customer.objects.all()
        for cus in cu:
            for r in rel:
                if r.cust.id == cus.id:
                    c=Customer.objects.filter(id=cus.id).values_list('first_name', 'last_name', 'address','avatar','phone','email')
                    for r in c:
                        writer.writerow(r)


        return response



def export_users_xls(request):
    if request.user.is_staff:
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="users.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Users')

        # Sheet header, first row
        row_num = 0

        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        columns = ['first_name', 'last_name', 'address', 'avatar', 'phone', 'email']

        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        # Sheet body, remaining rows
        font_style = xlwt.XFStyle()
        a = Agent.objects.get(user=request.user)
        co = CompanyAgentRelation.objects.get(Agents=a)
        o = CompanyCustomerRelation.objects.all().filter(company=co.company).values("customer")

        rows = Customer.objects.all().filter(id__in=o).values_list('first_name', 'last_name', 'address', 'avatar', 'phone', 'email')
        # rows = Customer.objects.all().values_list('first_name', 'last_name', 'address', 'avatar', 'phone', 'email')
        for row in rows:
            row_num += 1
            for col_num in range(len(row)):
                ws.write(row_num, col_num, row[col_num], font_style)

        wb.save(response)
        return response
    if request.user.is_authenticated:
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="users.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Users')

        # Sheet header, first row
        row_num = 0

        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        columns = ['first_name', 'last_name', 'address', 'avatar', 'phone', 'email']

        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        # Sheet body, remaining rows
        font_style = xlwt.XFStyle()

        rel = Relation.objects.all().filter(agen=Agent.objects.filter(user=request.user))

        cu = Customer.objects.all()


        for cus in cu:
            for r in rel:
                if r.cust.id == cus.id:
                    c=Customer.objects.filter(id=cus.id).values_list('first_name', 'last_name', 'address','avatar','phone','email')
                    for row in c:
                        row_num += 1
                        for col_num in range(len(row)):
                            ws.write(row_num, col_num, row[col_num], font_style)


        wb.save(response)
        return response

def import_cus_csv(request):
    if request.method == 'POST':
        if request.user.is_staff or request.user.is_superuser:
            form = import_csv(request.POST, request.FILES)
            if form.is_valid():
                file = form.cleaned_data['file']
                csvf = io.StringIO(file.read().decode())
                data = csv.reader(csvf, delimiter=',')

                r = 0
                for col in data:
                    i = 0
                    a = len(col)
                    if a<=5 or a>=7:
                        messages.error(request,"error at row {0} number of columns must be 6 not {1}".format(r,a))
                        return HttpResponseRedirect("/home/")
                    for d in col:
                        if d=="" and i!=3:
                            messages.error(request, "error at row {0} cell {1}".format(r, i))
                            return HttpResponseRedirect("/home/")
                        i = i + 1
                    r = r + 1
                    if col[0] != 'First name':
                        cust = Customer()
                        cust.first_name = col[0]
                        cust.last_name = col[1]
                        cust.address = col[2]
                        cust.avatar = col[3]
                        cust.phone = col[4]
                        cust.email = col[5]
                        cust.dj = timezone.now()
                        cust.dtc = timezone.now() + timezone.timedelta(days=7, hours=0, minutes=0, seconds=0)
                        cust.added_by = request.user.username

                        cust.save()
                        a = cust.id
                        user = Agent.objects.get(user=request.user)
                        comp = CompanyAgentRelation.objects.get(Agents=user)
                        com = CompanyCustomerRelation()
                        com.customer = Customer.objects.get(id=a)
                        com.company = comp.company
                        com.save()

                messages.success(request,"{0} records successfully added".format(r-1))
                return HttpResponseRedirect('/home/')
            else:
                return HttpResponse('invalid')


        elif request.user.is_authenticated:
            form = import_csv(request.POST, request.FILES)
            if form.is_valid():
                file = form.cleaned_data['file']
                csvf = io.StringIO(file.read().decode())
                data = csv.reader(csvf, delimiter=',')
                r = 0
                for col in data:
                    i = 0
                    a = len(col)
                    if a <= 5 or a >= 7:
                        messages.error(request, "error at row {0} number of columns must be 6 not {1}".format(r, a))
                        return HttpResponseRedirect("/home/")
                    for d in col:
                        if d == "" and i != 3:
                            messages.error(request, "error at row {0} cell {1}".format(r, i))
                            return HttpResponseRedirect("/home/")
                        i = i + 1
                    r = r + 1
                    if col[0] != 'First name':
                        cust = Customer()
                        rel=Relation()
                        cust.first_name = col[0]
                        cust.last_name = col[1]
                        cust.address = col[2]
                        cust.avatar = col[3]
                        cust.phone = col[4]
                        cust.email = col[5]
                        cust.dj = timezone.now()
                        cust.dtc = timezone.now() + timezone.timedelta(days=7, hours=0, minutes=0, seconds=0)
                        cust.added_by = request.user.username

                        cust.save()
                        a=cust.id
                        rel.agen = Agent.objects.get(user=request.user)
                        rel.cust = cust
                        rel.save()
                        rell = RelationLogHistory.objects.all()
                        for d in rell:
                            if d.cus == rel.cust:
                                d.log = "Agent: {0} was assigned to {1} on {2}".format(rel.ag_nm, rel.cust,
                                                                                       datetime.now().date())
                                d.save()
                        user = Agent.objects.get(user=request.user)
                        comp = CompanyAgentRelation.objects.get(Agents=user)
                        com = CompanyCustomerRelation()
                        com.customer = Customer.objects.get(id=a)
                        com.company = comp.company
                        com.save()

                messages.success(request,"{0} records successfully added".format(r-1))
                return HttpResponseRedirect('/home/')
            else:
                return HttpResponse('invalid')

    else:
        form=import_csv()
        user = Agent.objects.filter(user=request.user)
        com = CompanyAgentRelation.objects.filter(Agents=user)
        return render(request,'import.html',{'form':form,'title':'Import CSV','b':com})


def import_data(request):

    if request.method == "POST":
        if request.user.is_staff:
            form = import_csv(request.POST, request.FILES)
            if form.is_valid():
                file = form.cleaned_data['file']
                book = xlrd.open_workbook(filename=None,file_contents=file.read())

                sh = book.sheet_by_index(0)
                if int(sh.ncols) <=5 or int(sh.ncols) >=7 :
                    messages.error(request, "No. of columns at each row must be 6 not {0}".format(sh.ncols))
                    return HttpResponseRedirect("/home/")



                for i in range(sh.nrows-1):
                    i=i+1
                    cust = Customer()
                    cust.first_name = sh.cell(i, 0).value
                    cust.last_name = sh.cell(i, 1).value
                    cust.address = sh.cell(i, 2).value
                    cust.avatar = sh.cell(i, 3).value
                    cust.phone = sh.cell(i, 4).value
                    cust.email = sh.cell(i,5).value
                    cust.dj = timezone.now()
                    cust.dtc = timezone.now() + timezone.timedelta(days=7, hours=0, minutes=0, seconds=0)
                    cust.added_by = request.user.username

                    cust.save()
                    a = cust.id
                    user = Agent.objects.get(user=request.user)
                    comp = CompanyAgentRelation.objects.get(Agents=user)
                    com = CompanyCustomerRelation()
                    com.customer = Customer.objects.get(id=a)
                    com.company = comp.company
                    com.save()

                messages.success(request, "{0} records were added".format(sh.nrows-1))
                return HttpResponseRedirect("/home/")

        elif request.user.is_authenticated:
            form = import_csv(request.POST, request.FILES)
            if form.is_valid():
                file = form.cleaned_data['file']
                book = xlrd.open_workbook(filename=None, file_contents=file.read())

                sh = book.sheet_by_index(0)
                if int(sh.ncols) <= 5 or int(sh.ncols) >= 7:
                    messages.error(request, "No. of columns at each row must be 6 not {0}".format(sh.ncols))
                    return HttpResponseRedirect("/home/")

                for i in range(sh.nrows - 1):
                    i = i + 1
                    cust = Customer()
                    rel = Relation()
                    cust.first_name = sh.cell(i, 0).value
                    cust.last_name = sh.cell(i, 1).value
                    cust.address = sh.cell(i, 2).value
                    cust.avatar = sh.cell(i, 3).value
                    cust.phone = sh.cell(i, 4).value
                    cust.email = sh.cell(i, 5).value
                    cust.dj = timezone.now()
                    cust.dtc = timezone.now() + timezone.timedelta(days=7, hours=0, minutes=0, seconds=0)
                    cust.added_by = request.user.username

                    cust.save()
                    a = cust.id
                    rel.agen = Agent.objects.get(user=request.user)
                    rel.cust = cust
                    rel.date = timezone.now()
                    rel.save()
                    rell = RelationLogHistory.objects.all()
                    for r in rell:
                        if r.cus == rel.cust:
                            r.log = "Agent: {0} was assigned to {1} on {2}".format(rel.ag_nm, rel.cust,
                                                                                   datetime.now().date())
                            r.save()
                    user = Agent.objects.get(user=request.user)
                    comp = CompanyAgentRelation.objects.get(Agents=user)
                    com = CompanyCustomerRelation()
                    com.customer = Customer.objects.get(id=a)
                    com.company = comp.company
                    com.save()
                messages.success(request, "{0} records were added and relations were created with {1}".format(sh.nrows-1,request.user.username))
                return HttpResponseRedirect("/home/")



    else:
        form = import_csv()
        user = Agent.objects.filter(user=request.user)
        com = CompanyAgentRelation.objects.filter(Agents=user)
        return render(request, 'import.html', {'form': form,'title':'Import XLS','b':com})



def pdf(request):
    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = 'attachment; filename=customer.pdf'
    buffer =BytesIO()
    c= canvas.Canvas(buffer,pagesize=A4)

    c.setFont('Courier',22)
    c.drawString(30,750,'Customers:')

    styles = getSampleStyleSheet()
    styleBH = styles['Normal']
    styleBH.alignment = TA_CENTER
    styleBH.fontsize = 10
    first_name = Paragraph('First Name',styleBH)
    last_name = Paragraph('Last Name', styleBH)
    address = Paragraph('Address', styleBH)
    avatar = Paragraph('Avatar', styleBH)
    phone = Paragraph('Phone', styleBH)
    email = Paragraph('Email', styleBH)

    data = []
    data.append([first_name,last_name,address,avatar,phone,email])
    styleN = styles["BodyText"]
    styleN.alignment = TA_CENTER
    styleN.fontsize = 7
    if request.user.is_staff:
        a = Agent.objects.get(user=request.user)
        co = CompanyAgentRelation.objects.get(Agents=a)
        o = CompanyCustomerRelation.objects.all().filter(company=co.company).values("customer")

        cus = Customer.objects.all().filter(id__in=o)
        high = 650
        for d in cus:
            a = [d.first_name, d.last_name, d.address, d.avatar, d.phone, d.email]
            data.append(a)
            high = high - 18

        width, height = A3
        table = Table(data, colWidths=[3.0 * cm, 3.0 * cm, 3.0 * cm, 4.0 * cm, 3.0 * cm, 3.5 * cm])
        table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), .25, colors.black), ('BOX', (0, 0), (-1, -1), .25, colors.black), ]))
        table.wrapOn(c, width, height)
        table.drawOn(c, 30, high)

        c.save()
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response

    elif request.user.is_authenticated:
        rel = Relation.objects.all().filter(agen=Agent.objects.filter(user=request.user))

        cus = Customer.objects.all()
        high = 650
        for cu in cus:
            for r in rel:
                if r.cust.id == cu.id:
                    d=Customer.objects.get(id=cu.id)
                    a = [d.first_name, d.last_name, d.address, d.avatar, d.phone, d.email]
                    data.append(a)
                    high = high - 18

        width, height = A3
        table = Table(data, colWidths=[3.0 * cm, 3.0 * cm, 3.0 * cm, 4.0 * cm, 3.0 * cm, 3.5 * cm])
        table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), .25, colors.black), ('BOX', (0, 0), (-1, -1), .25, colors.black), ]))
        table.wrapOn(c, width, height)
        table.drawOn(c, 30, high)

        c.save()
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response

def home(request):
    return render(request,"main.html")

def requests(request):
    a = User.objects.all().filter(is_active=False)
    user = Agent.objects.all().filter(user__in=a)
    comp = CompanyAgentRelation.objects.all().order_by("Agents")
    return render(request,"NewAdmins.html",{'user':user,'comp':comp})

def validate(request,pk):
    p = get_object_or_404(Agent, pk=pk)
    n = get_object_or_404(User,id=p.user.id)
    if request.method == 'POST':
        form = Validate_Admin(request.POST, instance=n)

        if form.is_valid():
            n.is_active = True
            form.save()
            subject = "Registration"
            message = "Validated"
            fromem = settings.EMAIL_HOST_USER
            to = [n.email]

            send_mail(subject,message,fromem,to,fail_silently=False)

            return HttpResponseRedirect('/home/')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = Validate_Admin(instance=n)

        return render(request, 'validate.html', {
            'form': form,
        })

def AddAgent(request):
    if request.user.is_staff:
        if request.method == "POST":
            form = UserForm(request.POST or None)
            if form.is_valid():
                b=form.save(commit=False)
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                b.set_password(password)
                b.save()
                user1=User.objects.get(username=username)
                agen=Agent.objects.get(user=request.user)
                comp = CompanyAgentRelation.objects.get(Agents=agen)
                com = CompanyAgentRelation()
                com.company = Company.objects.get(Company_Name=comp.company.Company_Name)
                com.Agents = Agent.objects.get(user=user1)
                com.save()
                return HttpResponseRedirect("/home/")

        else:
            form = UserForm()
            a = Agent.objects.get(user=request.user)
            com = CompanyAgentRelation.objects.filter(Agents=a)
            return render(request,"register.html", {'form': form,'b':com})


def home(request):
    object_list = Agent.objects.all()
    user = Agent.objects.filter(user=request.user)
    com = CompanyAgentRelation.objects.filter(Agents=user)
    return render(request,'home.html',{'objects_list':object_list,'com':com,'b':com})

def main(request):
    return render(request,"main.html")

def UpdateAgent(request,pk):
    a=User.objects.get(id=pk)
    if request.user.is_superuser:
        if request.method=="POST":
            form=Validate_Admin(request.POST,instance=a)
            if form.is_valid():
                b=form.save()
                if not b.is_staff:
                    b.is_active = False
                    user=Agent.objects.get(user=a)
                    com = CompanyAgentRelation.objects.get(Agents=user)
                    comp = CompanyAgentRelation.objects.all().filter(company=com.company)
                    print(comp)
                    for c in comp:
                        c.Agents.user.is_active= False
                        c.Agents.user.save()

                else:
                    b.is_active = True
                    user = Agent.objects.get(user=a)
                    com = CompanyAgentRelation.objects.get(Agents=user)
                    comp = CompanyAgentRelation.objects.all().filter(company=com.company)
                    print(comp)
                    for c in comp:
                        c.Agents.user.is_active = True
                        c.Agents.user.save()


                b.save()
                return HttpResponseRedirect("/aginfo/")

        else:
            form = Validate_Admin(instance=a)
            return render(request, 'validate.html', {'form': form})


def ChangePassword(request):
    if request.method == 'POST':
        form = pass_form(request.POST or None,instance=request.user)

        if form.is_valid():
            old = form.cleaned_data['old_password']
            user = User.objects.get(id=request.user.id)
            if user.check_password(old):
                user=form.save(commit=False)
                password = form.cleaned_data['password']
                user.set_password(password)
                update_session_auth_hash(request,user)
                user.save()
                messages.success(request,"Password changed successfully.")
                return HttpResponseRedirect('/agent/')
            else:
                messages.error(request, "Enter the correct the old password.")
                return HttpResponseRedirect("/changepass/")
        else:
            messages.error(request,"Passwords Must Match.")
            return HttpResponseRedirect("/changepass/")


    else:
        form = pass_form(instance=request.user)
        user = Agent.objects.filter(user=request.user)
        com = CompanyAgentRelation.objects.filter(Agents=user)
        return render(request, 'change.html', {'form':form,'b': com})


def CompanyEdit(request):
    a = Agent.objects.get(user=request.user)
    b = CompanyAgentRelation.objects.filter(Agents=a).values("company")
    n = Company.objects.get(id=b)
    if request.method=="POST":
        if request.user.is_staff:
            form=Company_Form(request.POST or None,request.FILES, instance = n)
            if form.is_valid():

                form.save()
                messages.success(request,"Company information has been updated")

                return HttpResponseRedirect("/home/")
        else:
            messages.error(request, "You are not authorized")

            return HttpResponseRedirect("/home/")

    else:
        form=Company_Form(instance=n)
        user = Agent.objects.filter(user=request.user)
        com = CompanyAgentRelation.objects.filter(Agents=user)
        return render(request,"company.html",{'form':form,'b':com})