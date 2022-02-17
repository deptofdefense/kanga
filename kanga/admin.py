# =================================================================
#
# Work of the U.S. Department of Defense, Defense Digital Service.
# Released as open source under the MIT License.  See LICENSE file.
#
# =================================================================

from django.contrib import admin

from kanga.models import Attachment
from kanga.models import Account
from kanga.models import Execution
from kanga.models import ExecutionResults
from kanga.models import Group
from kanga.models import Message
from kanga.models import MessageContent
from kanga.models import Origin
from kanga.models import Plan
from kanga.models import PlanGroup
from kanga.models import PlanOrigin
from kanga.models import PlanTemplate
from kanga.models import Receipt
from kanga.models import Target
from kanga.models import Template


class AttachmentAdmin(admin.ModelAdmin):
    pass


admin.site.register(Attachment, AttachmentAdmin)


class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'name', 'sid')
    ordering = ("id",)
    pass


admin.site.register(Account, AccountAdmin)


class ExecutionAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'created_at')
    ordering = ("-created_at",)
    pass


admin.site.register(Execution, ExecutionAdmin)


class ExecutionResultsAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'created_at')
    ordering = ("-created_at",)
    pass


admin.site.register(ExecutionResults, ExecutionResultsAdmin)


class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'name')
    ordering = ("id",)
    pass


admin.site.register(Group, GroupAdmin)


class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'execution', 'account', 'platform', 'origin', 'target', 'sent_at')
    ordering = ('-sent_at',)
    pass


admin.site.register(Message, MessageAdmin)


class MessageContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'subject', 'created_at')
    ordering = ("-created_at",)
    pass


admin.site.register(MessageContent, MessageContentAdmin)


class OriginAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'account', 'phone_number', 'active')
    ordering = ("id",)
    pass


admin.site.register(Origin, OriginAdmin)


class PlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'name', 'created_at')
    ordering = ("-created_at",)
    pass


admin.site.register(Plan, PlanAdmin)


class PlanGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'plan', 'group', 'created_at')
    ordering = ("plan", "group")
    pass


admin.site.register(PlanGroup, PlanGroupAdmin)


class PlanOriginAdmin(admin.ModelAdmin):
    list_display = ('id', 'plan', 'origin', 'created_at')
    ordering = ("plan", "origin")
    pass


admin.site.register(PlanOrigin, PlanOriginAdmin)


class PlanTemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'plan', 'template', 'created_at')
    ordering = ("plan", "template")
    pass


admin.site.register(PlanTemplate, PlanTemplateAdmin)


class TargetAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'last_name', 'first_name', 'phone_number')
    ordering = ('last_name', 'first_name', 'phone_number')
    pass


admin.site.register(Target, TargetAdmin)


class TemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'name')
    ordering = ('name',)
    pass


admin.site.register(Template, TemplateAdmin)


class ReceiptAdmin(admin.ModelAdmin):
    pass


admin.site.register(Receipt, ReceiptAdmin)
