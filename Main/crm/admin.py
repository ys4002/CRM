from django.contrib import admin
from .models import Agent,Customer,log,Relation,RelationLogHistory,Company,CompanyAgentRelation,CompanyCustomerRelation
# Register your models here.
admin.site.register(Agent)
admin.site.register(Customer)
admin.site.register(log)
admin.site.register(Relation)
admin.site.register(RelationLogHistory)
admin.site.register(Company)
admin.site.register(CompanyAgentRelation)
admin.site.register(CompanyCustomerRelation)
