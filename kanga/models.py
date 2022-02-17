# =================================================================
#
# Work of the U.S. Department of Defense, Defense Digital Service.
# Released as open source under the MIT License.  See LICENSE file.
#
# =================================================================

import uuid
from slugify import slugify

from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber

from twilio.rest import Client as TwilioClient

from kanga import settings


class Base(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Account(Base):
    name = models.CharField(max_length=255, db_index=True)
    sid = models.CharField(max_length=255, db_index=True)
    auth_token = models.CharField(max_length=255, db_index=True)
    active = models.BooleanField()

    def __str__(self):
        return str(self.id)

    def __unicode__(self):
        return str(self.id)


class Origin(Base):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    phone_number = PhoneNumberField()
    voice = models.BooleanField()
    sms = models.BooleanField()
    mms = models.BooleanField()
    fax = models.BooleanField()
    active = models.BooleanField()

    @property
    def capabilities(self):
        capabilities = []
        if self.voice:
            capabilities += ["voice"]
        if self.sms:
            capabilities += ["sms"]
        if self.mms:
            capabilities += ["mms"]
        if self.fax:
            capabilities += ["fax"]
        return capabilities

    def __str__(self):
        return str(self.id)

    def __unicode__(self):
        return str(self.id)


class Group(Base):
    name = models.CharField(max_length=255, db_index=True)

    @property
    def slug(self):
        return slugify(str(self.name))

    def __str__(self):
        return str(self.id)

    def __unicode__(self):
        return str(self.id)


class Target(Base):
    first_name = models.CharField(max_length=255, db_index=True)
    last_name = models.CharField(max_length=255, db_index=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    phone_number = PhoneNumberField()

    def __str__(self):
        return str(self.id)

    def __unicode__(self):
        return str(self.id)


class Template(Base):
    name = models.CharField(max_length=255, db_index=True)
    body = models.TextField()

    def __str__(self):
        return str(self.id)

    def __unicode__(self):
        return str(self.id)


class Asset(Base):
    id = models.AutoField(primary_key=True)
    uuid = models.CharField(max_length=36, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    file = models.FileField(upload_to='assets/')

    def __str__(self):
        return str(self.id)

    def __unicode__(self):
        return str(self.id)


class Attachment(models.Model):
    id = models.AutoField(primary_key=True)
    template = models.ForeignKey(Template, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)

    def __unicode__(self):
        return str(self.id)


class Plan(Base):
    name = models.CharField(max_length=36, db_index=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)

    def __unicode__(self):
        return str(self.id)


class PlanPlatform(models.Model):
    id = models.AutoField(primary_key=True)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    platform = models.CharField(max_length=24, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    def __unicode__(self):
        return str(self.id)


class PlanGroup(models.Model):
    id = models.AutoField(primary_key=True)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    def __unicode__(self):
        return str(self.id)


class PlanOrigin(models.Model):
    id = models.AutoField(primary_key=True)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    origin = models.ForeignKey(Origin, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    def __unicode__(self):
        return str(self.id)


class PlanTemplate(models.Model):
    id = models.AutoField(primary_key=True)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    template = models.ForeignKey(Template, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    def __unicode__(self):
        return str(self.id)


class Execution(Base):
    plan = models.TextField()

    def __str__(self):
        return str(self.id)

    def __unicode__(self):
        return str(self.id)


class ExecutionResults(Base):
    execution = models.ForeignKey(Execution, on_delete=models.CASCADE)
    results = models.TextField()

    def __str__(self):
        return str(self.id)

    def __unicode__(self):
        return str(self.id)


class MessageContent(Base):
    """MessageContent is used to store the raw message content.
    """
    subject = models.TextField()
    body = models.TextField()

    def __str__(self):
        return str(self.id)

    def __unicode__(self):
        return str(self.id)


class Message(Base):
    sid = models.CharField(max_length=255, db_index=True)
    execution = models.ForeignKey(Execution, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    platform = models.CharField(max_length=255, db_index=True)
    origin = models.ForeignKey(Origin, on_delete=models.CASCADE)
    target = models.ForeignKey(Target, on_delete=models.CASCADE)
    content = models.ForeignKey(MessageContent, on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    def __unicode__(self):
        return str(self.id)


class Receipt(Base):
    data = models.TextField()

    def __str__(self):
        return str(self.id)

    def __unicode__(self):
        return str(self.id)


def UpdateOrCreateTargetForGroup(group=None, phone_number=None, first_name=None, last_name=None):
    try:
        obj = Target.objects.get(group=group, phone_number=PhoneNumber.from_string(phone_number))
        obj.first_name = first_name
        obj.last_name = last_name
        obj.save()
    except Target.DoesNotExist:
        Target.objects.create(
            uuid=uuid.uuid4(),
            group=group,
            first_name=first_name,
            last_name=last_name,
            phone_number=PhoneNumber.from_string(phone_number),
        )


def SyncOriginsForAccount(a):
    c = TwilioClient(
        a.sid,
        a.auth_token,
        edge=settings.TWILIO_EDGE)
    existing_origins = {x.phone_number.as_e164: x for x in Origin.objects.filter(account=a)}
    new_phone_numbers = {x.phone_number: x for x in c.incoming_phone_numbers.list()}
    for x in new_phone_numbers.keys() - existing_origins.keys():
        Origin.objects.create(
            account=a,
            phone_number=x,
            voice=new_phone_numbers[x].capabilities.get('voice', False),
            sms=new_phone_numbers[x].capabilities.get('sms', False),
            mms=new_phone_numbers[x].capabilities.get('mms', False),
            fax=new_phone_numbers[x].capabilities.get('fax', False),
            active=True,
        )
    for x in existing_origins.keys() - new_phone_numbers.keys():
        Origin.objects.filter(account=a, phone_number=x).update(active=False)


def SyncOrigins():
    for a in Account.objects.filter(active=True):
        SyncOriginsForAccount(a)
