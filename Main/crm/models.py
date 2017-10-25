from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
DEFAULT = 'logos/anonymous.png'
class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact_no = models.CharField(max_length=10)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(null=True,blank=True,default=DEFAULT)


    def __str__(self):
        return '{0}'.format(self.user.username)

@receiver(post_save, sender=User)
def create_user_agent(sender, instance, created, **kwargs):
    if created:
        Agent.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_agent(sender, instance, **kwargs):
    instance.agent.save()


class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.TextField()
    avatar = models.ImageField(null=True,blank=True,default=DEFAULT)
    phone = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    dj = models.DateTimeField(null=True,blank=True)
    dtc = models.DateTimeField(null=True,blank=True)
    dta = models.DateTimeField(null=True,blank=True)
    added_by = models.CharField(max_length=40,null=True,blank=True)

    def save(self, *args, **kwargs):
        self.phone = int(self.phone)
        if self.avatar == None or self.avatar == "":
            self.avatar = DEFAULT
            super(Customer, self).save(*args, **kwargs)

        if self.dta != None:
            if self.dtc > self.dta:
                self.dtc = self.dta + timezone.timedelta(days=7,hours=0,minutes=0,seconds=0)
                super(Customer, self).save(*args, **kwargs)

        if self.dtc == timezone.now():
            if self.dta == None:
                self.dtc = timezone.now()+ timezone.timedelta(days=7,hours=0,minutes=0,seconds=0)
                super(Customer, self).save(*args, **kwargs)

            else:
                self.dtc = self.dta + timezone.timedelta(days=7,hours=0,minutes=0,seconds=0)
                super(Customer, self).save(*args, **kwargs)

        super(Customer, self).save(*args, **kwargs)

    def __str__(self):
        return '{0}'.format(self.first_name)


class log(models.Model):

    cust = models.ForeignKey(Customer,blank=True,null=True)
    date = models.DateField(null=True,blank=True)

    agent = models.ForeignKey(Agent,blank=True,null=True)
    data = models.TextField(null=True,blank=True)


    def __str__(self):
        return 'Agent: {0},Customer: {1}'.format(self.agent.user.first_name,self.cust.first_name)



class Relation(models.Model):
    cust = models.ForeignKey(Customer,null=True,blank=True)
    agen = models.ForeignKey(Agent,null=True,blank=True)
    ag_nm = models.CharField(max_length=40,blank=True,null=True)
    date = models.DateTimeField(null=True,blank=True)


    def save(self, *args,**kwargs):
        if self.cust != None:
            if self.agen != None:
                self.ag_nm = self.agen.user.first_name

                super(Relation, self).save(*args, **kwargs)
            else:
                self.ag_nm = None

                super(Relation, self).save(*args, **kwargs)


    def __str__(self):
        return '{0} {1}'.format(self.cust,self.ag_nm)




class RelationLogHistory(models.Model):
    cus = models.OneToOneField(Customer, on_delete=models.CASCADE)
    log = models.TextField(blank=True,null=True)


    def __str__(self):
        return '{0} {1}'.format(self.cus.first_name,self.id)

@receiver(post_save, sender=Customer)
def create_customer_log(sender, instance, created, **kwargs):
    if created:
        RelationLogHistory.objects.create(cus=instance)

@receiver(post_save, sender=Customer)
def save_customer_log(sender, instance, **kwargs):
    instance.relationloghistory.save()

class Company(models.Model):
    Company_Image = models.ImageField(default=DEFAULT)
    Company_Name = models.CharField(max_length=40,unique=True)

    def __str__(self):
        return self.Company_Name

class CompanyAgentRelation(models.Model):
    company = models.ForeignKey(Company)
    Agents = models.ForeignKey(Agent)

    def __str__(self):
        return "{0} {1}".format(self.company,self.Agents)

class CompanyCustomerRelation(models.Model):
    company = models.ForeignKey(Company)
    customer = models.ForeignKey(Customer)

    def __str__(self):
        return "{0} {1}".format(self.company,self.customer)