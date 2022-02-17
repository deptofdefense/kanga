# =================================================================
#
# Work of the U.S. Department of Defense, Defense Digital Service.
# Released as open source under the MIT License.  See LICENSE file.
#
# =================================================================

from django import forms

from kanga import settings

from kanga.models import Group, Origin, Template


class NewAccountForm(forms.Form):
    name = forms.CharField(max_length=255)
    sid = forms.CharField(max_length=255)
    auth_token = forms.CharField(max_length=255)
    active = forms.CharField(max_length=255)


class EditAccountForm(forms.Form):
    uuid = forms.CharField(max_length=36)
    name = forms.CharField(max_length=255)
    sid = forms.CharField(max_length=255)
    auth_token = forms.CharField(max_length=255)
    active = forms.CharField(max_length=255)


class PlanAccountForm(forms.Form):
    pass


class AssetForm(forms.Form):
    uuid = forms.CharField(max_length=36)
    name = forms.CharField(max_length=255)
    file = forms.FileField()


class NewGroupForm(forms.Form):
    name = forms.CharField(max_length=255)


class EditGroupForm(forms.Form):
    uuid = forms.CharField(max_length=36)
    name = forms.CharField(max_length=255)


class NewPlanForm(forms.Form):
    name = forms.CharField(max_length=255)
    account = forms.CharField(max_length=255)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for p in settings.AVAILABLE_PLATFORMS:
            self.fields["platform-{}".format(p["id"])] = forms.CharField(max_length=255, required=False)
        for g in Group.objects.all():
            self.fields["group-{}".format(g.id)] = forms.CharField(max_length=255, required=False)
        for o in Origin.objects.all():
            self.fields["origin-{}".format(o.id)] = forms.CharField(max_length=255, required=False)
        for t in Template.objects.all():
            self.fields["template-{}".format(t.id)] = forms.CharField(max_length=255, required=False)

    def clean(self):
        platforms = set()
        for p in settings.AVAILABLE_PLATFORMS:
            if self.cleaned_data.get("platform-{}".format(p["id"])) == p["id"]:
                platforms.add(p["id"])
        self.cleaned_data["platforms"] = platforms

        groups = set()
        for g in Group.objects.all():
            if self.cleaned_data.get("group-{}".format(g.id)) == str(g.uuid):
                groups.add(g)
        self.cleaned_data["groups"] = groups

        origins = set()
        for o in Origin.objects.all():
            if self.cleaned_data.get("origin-{}".format(o.id)) == str(o.uuid):
                origins.add(o)
        self.cleaned_data["origins"] = origins

        templates = set()
        for t in Template.objects.all():
            if self.cleaned_data.get("template-{}".format(t.id)) == str(t.uuid):
                templates.add(t)
        self.cleaned_data["templates"] = templates


class EditPlanForm(forms.Form):
    uuid = forms.CharField(max_length=36)
    name = forms.CharField(max_length=255)
    account = forms.CharField(max_length=255)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for p in settings.AVAILABLE_PLATFORMS:
            self.fields["platform-{}".format(p["id"])] = forms.CharField(max_length=255, required=False)
        for g in Group.objects.all():
            self.fields["group-{}".format(g.id)] = forms.CharField(max_length=255, required=False)
        for o in Origin.objects.all():
            self.fields["origin-{}".format(o.id)] = forms.CharField(max_length=255, required=False)
        for t in Template.objects.all():
            self.fields["template-{}".format(t.id)] = forms.CharField(max_length=255, required=False)

    def clean(self):
        platforms = set()
        for p in settings.AVAILABLE_PLATFORMS:
            if self.cleaned_data.get("platform-{}".format(p["id"])) == p["id"]:
                platforms.add(p["id"])
        self.cleaned_data["platforms"] = platforms

        groups = set()
        for g in Group.objects.all():
            if self.cleaned_data.get("group-{}".format(g.id)) == str(g.uuid):
                groups.add(g)
        self.cleaned_data["groups"] = groups

        origins = set()
        for o in Origin.objects.all():
            if self.cleaned_data.get("origin-{}".format(o.id)) == str(o.uuid):
                origins.add(o)
        self.cleaned_data["origins"] = origins

        templates = set()
        for t in Template.objects.all():
            if self.cleaned_data.get("template-{}".format(t.id)) == str(t.uuid):
                templates.add(t)
        self.cleaned_data["templates"] = templates

        print(self.cleaned_data)


class NewTargetForm(forms.Form):
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)
    group = forms.CharField(max_length=36)
    phone_number = forms.CharField(max_length=20)


class EditTargetForm(forms.Form):
    uuid = forms.CharField(max_length=36)
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)
    group = forms.CharField(max_length=36)
    phone_number = forms.CharField(max_length=20)


class ImportTargetsForm(forms.Form):
    group = forms.CharField(max_length=255)
    file_format = forms.CharField(max_length=255)
    sheet_name = forms.CharField(max_length=255)
    first_name_field = forms.CharField(max_length=255)
    last_name_field = forms.CharField(max_length=255)
    phone_number_field = forms.CharField(max_length=255)
    file = forms.FileField()


class NewTemplateForm(forms.Form):
    name = forms.CharField(max_length=255)
    body = forms.CharField()


class EditTemplateForm(forms.Form):
    uuid = forms.CharField(max_length=36)
    name = forms.CharField(max_length=255)
    body = forms.CharField()


class DeleteObjectForm(forms.Form):
    uuid = forms.CharField(max_length=36)
