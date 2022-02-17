# =================================================================
#
# Work of the U.S. Department of Defense, Defense Digital Service.
# Released as open source under the MIT License.  See LICENSE file.
#
# =================================================================

import uuid
import json
import math

from twilio.rest import Client as TwilioClient

from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.db.models import Count
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from kanga import settings
from kanga.encoder import KangaEncoder
from kanga.utils import normalize_phone_number, decode_data, format_string, split_string, flatten

from kanga.models import Account
from kanga.models import Asset
from kanga.models import Execution
from kanga.models import ExecutionResults
from kanga.models import Group
from kanga.models import Message
from kanga.models import MessageContent
from kanga.models import Origin
from kanga.models import Plan
from kanga.models import PlanGroup
from kanga.models import PlanOrigin
from kanga.models import PlanPlatform
from kanga.models import PlanTemplate
from kanga.models import Target
from kanga.models import Template

from kanga.models import UpdateOrCreateTargetForGroup
from kanga.models import SyncOriginsForAccount
from kanga.models import SyncOrigins

from kanga.forms import NewAccountForm
from kanga.forms import EditAccountForm
from kanga.forms import PlanAccountForm
from kanga.forms import AssetForm
from kanga.forms import NewGroupForm
from kanga.forms import EditGroupForm
from kanga.forms import NewTargetForm
from kanga.forms import EditTargetForm
from kanga.forms import ImportTargetsForm
from kanga.forms import NewTemplateForm
from kanga.forms import EditTemplateForm
from kanga.forms import DeleteObjectForm
from kanga.forms import NewPlanForm
from kanga.forms import EditPlanForm


def home(request):
    template = loader.get_template('index.html')
    #
    executions = []
    for e in Execution.objects.all().order_by("-created_at"):
        executions += [{
            "uuid": e.uuid,
            "plan": json.loads(e.plan),
            "created_at": e.created_at
        }]

    plans = []
    for p in Plan.objects.all():
        planPlatforms = PlanPlatform.objects.filter(plan__id=p.id)
        planGroups = PlanGroup.objects.filter(plan__id=p.id)
        plans += [{
            "uuid": p.uuid,
            "name": p.name,
            "platform_names": [p.platform for p in planPlatforms],
            "group_names": [g.group.name for g in planGroups],
            "created_at": p.created_at
        }]
    #
    context = {
        "title": settings.TITLE,
        "accounts": Account.objects.all(),
        "plans": plans,
        "executions": executions
    }
    return HttpResponse(template.render(context, request))


@login_required
def account_plan(request, u):
    if request.method == 'POST':
        items = [item for item in request.POST.items()]
        print(items)
        #
        plan = {
            "account_sid": None,
            "account_name": None,
            "account_auth_token": None,
            "name": None,
            "platforms": [],
            "groups": [],
            "origins": [],
            "templates": [],
        }
        #
        available_platforms = {p["id"]: p["title"] for p in settings.AVAILABLE_PLATFORMS}
        #
        for item in request.POST.items():
            k, v = item
            if k == "plan_name":
                plan["name"] = v
            elif k == "account":
                a = Account.objects.get(uuid=v)
                plan['account_sid'] = a.sid
                plan['account_name'] = a.name
                plan['account_auth_token'] = a.auth_token
            elif k.startswith("group-"):
                plan['groups'] += [Group.objects.get(uuid=v).name]
            elif k.startswith("origin-"):
                plan['origins'] += [Origin.objects.get(uuid=v).phone_number]
            elif k.startswith("template-"):
                plan['templates'] += [Template.objects.get(uuid=v).body]
            elif k.startswith("platform-"):
                if v in available_platforms:
                    plan['platforms'] += [v]
        print(plan)
        p = Plan.objects.create(
            uuid=uuid.uuid4(),
            data=json.dumps(plan, cls=KangaEncoder, ensure_ascii=False, allow_nan=False))
        return HttpResponseRedirect(reverse("plan_view", args=[p.uuid]))
    else:
        template = loader.get_template('account_plan.html')

        a = Account.objects.get(uuid=u)

        origins = Origin.objects.filter(account__id=a.id)

        context = {
            "title": settings.TITLE,
            "a": a,
            "groups": Group.objects.all(),
            "origins": origins,
            "templates": Template.objects.all(),
            "platforms": settings.AVAILABLE_PLATFORMS,
        }
        return HttpResponse(template.render(context, request))


@login_required
def assets(request):
    template = loader.get_template('assets.html')

    assets = Asset.objects.values()

    context = {
        "title": settings.TITLE,
        "assets": assets
    }
    return HttpResponse(template.render(context, request))


@login_required
def asset_detail(request, uuid):
    template = loader.get_template('asset.html')

    a = Asset.objects.get(uuid=uuid)

    context = {
        "title": settings.TITLE,
        "asset": a,
    }
    return HttpResponse(template.render(context, request))


@login_required
def asset_import(request, uuid):
    template = loader.get_template('asset_import.html')

    if request.method == 'POST':
        form = AssetForm(request.POST, request.FILES)
        form.uuid = uuid.uuid4()
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/assets')
    else:
        context = {
            "title": settings.TITLE,
        }
        return HttpResponse(template.render(context, request))


#
# Accounts
#


@login_required
def accounts(request):
    template = loader.get_template('accounts.html')

    accounts = Account.objects.values()

    context = {
        "title": settings.TITLE,
        "accounts": accounts
    }
    return HttpResponse(template.render(context, request))


@login_required
def account_view(request, u):
    template = loader.get_template('account_view.html')
    if request.method == 'POST':
        f = PlanAccountForm(request.POST)
        if f.is_valid() and u == f.cleaned_data['uuid']:
            a = Account.objects.get(uuid=u)
            return HttpResponseRedirect("{}?account={}".format(reverse('plan_new'), u))
        else:
            return HttpResponseRedirect(reverse('accounts'))
    else:
        a = Account.objects.get(uuid=u)
        SyncOriginsForAccount(a)
        origins = Origin.objects.filter(account=a).order_by("phone_number")
        message_counts = Message.objects.only("origin_id").filter(origin_id__in=[x.id for x in origins]).values("origin_id").annotate(total=Count("origin_id")).order_by()  # noqa
        total_counts = {x["origin_id"]: x["total"] for x in message_counts}
        context = {
            "title": settings.TITLE,
            "a": a,
            "active_origins": [{
                "phone_number": x.phone_number,
                "capabilities": x.capabilities,
                "total_messages": total_counts.get(x.id, 0)
            } for x in origins if x.active],
            "inactive_origins": [{
                "phone_number": x.phone_number,
                "capabilities": x.capabilities,
                "total_messages": total_counts.get(x.id, 0)
            } for x in origins if not x.active],
        }
        return HttpResponse(template.render(context, request))


@login_required
def account_new(request):
    template = loader.get_template('account_new.html')
    if request.method == 'POST':
        f = NewAccountForm(request.POST)
        if f.is_valid():
            d = f.cleaned_data
            Account.objects.create(
                name=d['name'].strip(),
                sid=d['sid'].strip(),
                auth_token=d['auth_token'].strip(),
                active=(d['active'] == "yes"))
            return HttpResponseRedirect(reverse('accounts'))
        else:
            print(f)
            return HttpResponseRedirect(reverse('accounts'))
    else:
        context = {
            "title": settings.TITLE,
        }
        return HttpResponse(template.render(context, request))


@login_required
def account_edit(request, u):
    template = loader.get_template('account_edit.html')
    if request.method == 'POST':
        f = EditAccountForm(request.POST)
        if f.is_valid() and u == f.cleaned_data['uuid']:
            d = f.cleaned_data
            a = Account.objects.get(uuid=u)
            a.name = d['name'].strip()
            a.sid = d['sid'].strip()
            a.auth_token = d['auth_token'].strip()
            a.save()
            return HttpResponseRedirect(reverse('accounts'))
        else:
            print(f)
            return HttpResponseRedirect(reverse('accounts'))
    else:
        a = Account.objects.get(uuid=u)
        context = {
            "title": settings.TITLE,
            "a": a,
        }
        return HttpResponse(template.render(context, request))


@login_required
def account_delete(request, u):
    template = loader.get_template('account_delete.html')
    if request.method == 'POST':
        f = DeleteObjectForm(request.POST)
        if f.is_valid() and u == f.cleaned_data['uuid']:
            Account.objects.filter(uuid=u).delete()
            return HttpResponseRedirect(reverse('accounts'))
        else:
            a = Account.objects.get(uuid=u)
            context = {
                "title": settings.TITLE,
                "a": a,
                "form": f,
            }
            return HttpResponse(template.render(context, request))
    else:
        a = Account.objects.get(uuid=u)
        context = {
            "title": settings.TITLE,
            "a": a,
        }
        return HttpResponse(template.render(context, request))


#
# Groups
#


@login_required
def groups(request):
    template = loader.get_template('groups.html')

    context = {
        "title": settings.TITLE,
        "groups": Group.objects.all().order_by("name")
    }
    return HttpResponse(template.render(context, request))


@login_required
def group_new(request):
    template = loader.get_template('group_new.html')
    if request.method == 'POST':
        f = NewGroupForm(request.POST)
        if f.is_valid():
            d = f.cleaned_data
            Group.objects.create(
                uuid=uuid.uuid4(),
                name=d['name'].strip())
            return HttpResponseRedirect(reverse('groups'))
        else:
            print(f)
            return HttpResponseRedirect(reverse('groups'))
    else:
        context = {
            "title": settings.TITLE,
        }
        return HttpResponse(template.render(context, request))


@login_required
def group_edit(request, u):
    template = loader.get_template('group_edit.html')
    if request.method == 'POST':
        f = EditGroupForm(request.POST)
        if f.is_valid() and u == f.cleaned_data['uuid']:
            d = f.cleaned_data
            t = Group.objects.get(uuid=u)
            t.name = d['name'].strip()
            t.save()
            return HttpResponseRedirect(reverse('groups'))
        else:
            print(f)
            return HttpResponseRedirect(reverse('groups'))
    else:
        g = Group.objects.get(uuid=u)
        context = {
            "title": settings.TITLE,
            "g": g,
        }
        return HttpResponse(template.render(context, request))


@login_required
def group_delete(request, u):
    template = loader.get_template('group_delete.html')
    if request.method == 'POST':
        f = DeleteObjectForm(request.POST)
        if f.is_valid() and u == f.cleaned_data['uuid']:
            Group.objects.filter(uuid=u).delete()
            return HttpResponseRedirect(reverse('groups'))
        else:
            g = Group.objects.get(uuid=u)
            context = {
                "title": settings.TITLE,
                "g": g,
                "form": f,
            }
            return HttpResponse(template.render(context, request))
    else:
        g = Group.objects.get(uuid=u)
        context = {
            "title": settings.TITLE,
            "g": g,
        }
        return HttpResponse(template.render(context, request))


@login_required
def group_view(request, u):
    template = loader.get_template('group_view.html')
    g = Group.objects.get(uuid=u)
    context = {
        "title": settings.TITLE,
        "g": g,
        "targets": Target.objects.filter(group=g)
    }
    return HttpResponse(template.render(context, request))

#
# Targets
#


@login_required
def targets(request):
    template = loader.get_template('targets.html')

    groups = {g["id"]: g for g in Group.objects.values()}
    targets = Target.objects.values()
    for t in targets:
        t["group"] = groups[t["group_id"]]

    print(targets)

    context = {
        "title": settings.TITLE,
        "targets": targets
    }
    return HttpResponse(template.render(context, request))


@login_required
def target_new(request):
    template = loader.get_template('target_new.html')
    if request.method == 'POST':
        f = NewTargetForm(request.POST)
        if f.is_valid():
            d = f.cleaned_data
            g = Group.objects.get(uuid=d["group"])
            Target.objects.create(
                uuid=uuid.uuid4(),
                first_name=d['first_name'].strip(),
                last_name=d['last_name'].strip(),
                group=g,
                phone_number=normalize_phone_number(d['phone_number']))
            return HttpResponseRedirect(reverse('targets'))
        else:
            print(f)
            return HttpResponseRedirect(reverse('targets'))
    else:
        g = None
        try:
            g = Group.objects.get(uuid=request.GET.get('group'))
        except Exception:
            pass
        context = {
            "title": settings.TITLE,
            "group_uuid": g.uuid if g is not None else None,
            "groups": Group.objects.all().order_by('name'),
        }
        return HttpResponse(template.render(context, request))


@login_required
def target_edit(request, u):
    template = loader.get_template('target_edit.html')
    if request.method == 'POST':
        f = EditTargetForm(request.POST)
        if f.is_valid() and u == f.cleaned_data['uuid']:
            d = f.cleaned_data
            g = Group.objects.get(uuid=d["group"])
            t = Target.objects.get(uuid=u)
            t.first_name = d['first_name'].strip()
            t.last_name = d['last_name'].strip()
            t.group = g
            t.phone_number = normalize_phone_number(d['phone_number'])
            t.save()
            return HttpResponseRedirect(reverse('targets'))
        else:
            print(f)
            return HttpResponseRedirect(reverse('targets'))
    else:
        t = Target.objects.get(uuid=u)
        context = {
            "title": settings.TITLE,
            "t": t,
            "groups": Group.objects.all().order_by('name'),
        }
        return HttpResponse(template.render(context, request))


@login_required
def target_view(request, u):
    template = loader.get_template('target_view.html')
    if request.method == 'POST':
        pass
    else:
        t = Target.objects.get(uuid=u)
        context = {
            "title": settings.TITLE,
            "t": t,
            "groups": Group.objects.all().order_by('name'),
            "messages": Message.objects.filter(target=t).order_by("-sent_at"),
        }
        return HttpResponse(template.render(context, request))


@login_required
def target_delete(request, u):
    template = loader.get_template('target_delete.html')
    if request.method == 'POST':
        f = DeleteObjectForm(request.POST)
        if f.is_valid() and u == f.cleaned_data['uuid']:
            Target.objects.filter(uuid=u).delete()
            return HttpResponseRedirect(reverse('targets'))
        else:
            t = Template.objects.get(uuid=u)
            context = {
                "title": settings.TITLE,
                "t": t,
                "form": f,
                "groups": Group.objects.all().order_by('name'),
            }
            return HttpResponse(template.render(context, request))
    else:
        t = Target.objects.get(uuid=u)
        context = {
            "title": settings.TITLE,
            "t": t,
            "groups": Group.objects.all().order_by('name'),
        }
        return HttpResponse(template.render(context, request))


@login_required
def targets_import(request):
    template = loader.get_template('targets_import.html')
    if request.method == 'POST':
        f = ImportTargetsForm(request.POST, request.FILES)
        if f.is_valid():
            d = f.cleaned_data
            sheet_name = d['sheet_name']
            first_name_field = d['first_name_field']
            last_name_field = d['last_name_field']
            phone_number_field = d['phone_number_field']
            g = Group.objects.get(uuid=d["group"])
            data_reader = decode_data(
                data=request.FILES['file'].read(),
                file_format=d['file_format'],
                sheet_name=sheet_name,
            )
            errored_phone_numbers = []
            errored_objects = []
            for obj in data_reader:
                raw_phone_number = obj[phone_number_field]
                if isinstance(raw_phone_number, str):
                    if len(raw_phone_number) == 0:
                        continue
                elif isinstance(raw_phone_number, float):
                    if math.isnan(raw_phone_number):
                        continue
                # split the string twice and then flatten
                split_phone_numbers = flatten([split_string(x) for x in split_string(format_string(raw_phone_number))])
                if len(split_phone_numbers) == 0:
                    print("Object errored:", obj)
                    raise Exception("Phone number is missing")
                for phone_number in split_phone_numbers:
                    normalized_phone_number = None
                    try:
                        normalized_phone_number = normalize_phone_number(phone_number)
                    except Exception as e:
                        print(e)
                        errored_phone_numbers += [phone_number]
                    else:
                        try:
                            # if first name is not present, then can be a nan float
                            first_name_raw = obj.get(first_name_field, "")
                            first_name = first_name_raw.strip() if isinstance(first_name_raw, str) else "-"
                            # if last name is not present, then can be a nan float
                            last_name_raw = obj.get(last_name_field, "")
                            last_name = last_name_raw.strip() if isinstance(last_name_raw, str) else "-"
                            UpdateOrCreateTargetForGroup(
                                group=g,
                                first_name=first_name,
                                last_name=last_name,
                                phone_number=normalized_phone_number
                            )
                        except Exception as ee:
                            print("WTF", obj, ee)
            print(json.dumps({"errored_phone_numbers": errored_phone_numbers}))
            print({"errored_objects": [errored_objects]})
            return HttpResponseRedirect(reverse('targets'))
        else:
            print(f)
            context = {
                "title": settings.TITLE,
                "groups": Group.objects.all().order_by('name'),
                "errors_by_field": f.errors
            }
            return HttpResponse(template.render(context, request))
    else:
        g = None
        try:
            g = Group.objects.get(uuid=request.GET.get('group'))
        except Exception:
            pass
        context = {
            "title": settings.TITLE,
            "group_uuid": g.uuid if g is not None else None,
            "groups": Group.objects.all().order_by('name'),
            "file_formats": ["csv", "excel"],
        }
        return HttpResponse(template.render(context, request))


#
# Templates
#


@login_required
def templates(request):
    template = loader.get_template('templates.html')

    templates = Template.objects.values().order_by('name')

    context = {
        "title": settings.TITLE,
        "templates": templates
    }
    return HttpResponse(template.render(context, request))


@login_required
def template_new(request):
    template = loader.get_template('template_new.html')
    if request.method == 'POST':
        f = NewTemplateForm(request.POST)
        if f.is_valid():
            d = f.cleaned_data
            Template.objects.create(
                uuid=uuid.uuid4(),
                name=d['name'].strip(),
                body=d['body'].strip())
            return HttpResponseRedirect(reverse('templates'))
        else:
            return HttpResponseRedirect(reverse('templates')+"?errors")
    else:
        context = {
            "title": settings.TITLE,
        }
        return HttpResponse(template.render(context, request))


@login_required
def template_edit(request, u):
    template = loader.get_template('template_edit.html')
    if request.method == 'POST':
        f = EditTemplateForm(request.POST)
        if f.is_valid() and u == f.cleaned_data['uuid']:
            d = f.cleaned_data
            t = Template.objects.get(uuid=u)
            t.name = d['name'].strip()
            t.body = d['body'].strip()
            t.save()
            return HttpResponseRedirect(reverse('templates'))
        else:
            print(f)
            return HttpResponseRedirect(reverse('templates'))
    else:
        t = Template.objects.get(uuid=u)
        context = {
            "title": settings.TITLE,
            "t": t,
        }
        return HttpResponse(template.render(context, request))


@login_required
def template_delete(request, u):
    template = loader.get_template('template_delete.html')
    if request.method == 'POST':
        f = DeleteObjectForm(request.POST)
        if f.is_valid() and u == f.cleaned_data['uuid']:
            Template.objects.filter(uuid=u).delete()
            return HttpResponseRedirect(reverse('templates'))
        else:
            t = Template.objects.get(uuid=u)
            context = {
                "title": settings.TITLE,
                "t": t,
                "form": f
            }
            return HttpResponse(template.render(context, request))
    else:
        t = Template.objects.get(uuid=u)
        context = {
            "title": settings.TITLE,
            "t": t,
        }
        return HttpResponse(template.render(context, request))

#
# Plans
#


@login_required
def plans(request):
    template = loader.get_template('plans.html')

    plans = []
    for p in Plan.objects.all():
        planPlatforms = PlanPlatform.objects.filter(plan__id=p.id)
        planGroups = PlanGroup.objects.filter(plan__id=p.id)
        plans += [{
            "uuid": p.uuid,
            "name": p.name,
            "platform_names": [p.platform for p in planPlatforms],
            "group_names": [g.group.name for g in planGroups],
            "created_at": p.created_at
        }]

    context = {
        "title": settings.TITLE,
        "plans": plans
    }
    return HttpResponse(template.render(context, request))


@login_required
def plan_new(request):
    template = loader.get_template('plan_new.html')
    if request.method == 'POST':
        f = NewPlanForm(request.POST)
        if f.is_valid():
            d = f.cleaned_data
            a = Account.objects.get(uuid=d['account'])
            p = Plan.objects.create(
                uuid=uuid.uuid4(),
                name=d['name'].strip(),
                account=a)
            for platform in d["platforms"]:
                PlanPlatform.objects.create(plan=p, platform=platform)
            for g in d["groups"]:
                PlanGroup.objects.create(plan=p, group=g)
            for o in d["origins"]:
                PlanOrigin.objects.create(plan=p, origin=o)
            for t in d["templates"]:
                PlanTemplate.objects.create(plan=p, template=t)
            return HttpResponseRedirect(reverse("plan_view", args=[p.uuid]))
        else:
            print(f)
            return HttpResponseRedirect(reverse('plans'))
    else:
        SyncOrigins()
        accounts = {a["id"]: a for a in Account.objects.all().values()}
        origins = Origin.objects.filter(active=True).order_by("phone_number").values()
        for o in origins:
            o["account_uuid"] = accounts[o["account_id"]]["uuid"]
        context = {
            "title": settings.TITLE,
            "account_uuid": request.GET.get('account', None),
            "accounts": Account.objects.filter(active=True).order_by("name"),
            "groups": Group.objects.all().order_by('name'),
            "origins": origins,
            "templates": Template.objects.all().order_by("name"),
            "platforms": settings.AVAILABLE_PLATFORMS,
        }
        return HttpResponse(template.render(context, request))


@login_required
def plan_edit(request, u):
    template = loader.get_template('plan_edit.html')
    if request.method == 'POST':
        f = EditPlanForm(request.POST)
        if f.is_valid() and u == f.cleaned_data['uuid']:
            d = f.cleaned_data
            print("Cleaned Data:", d)
            plan = Plan.objects.get(uuid=u)
            plan.name = d['name'].strip()
            plan.account = Account.objects.get(uuid=d['account'].strip())
            PlanPlatform.objects.filter(plan__id=plan.id).delete()
            for platform in d["platforms"]:
                PlanPlatform.objects.create(plan=plan, platform=platform)
            PlanGroup.objects.filter(plan__id=plan.id).delete()
            for g in d["groups"]:
                PlanGroup.objects.create(plan=plan, group=g)
            PlanOrigin.objects.filter(plan__id=plan.id).delete()
            for o in d["origins"]:
                PlanOrigin.objects.create(plan=plan, origin=o)
            PlanTemplate.objects.filter(plan__id=plan.id).delete()
            for t in d["templates"]:
                PlanTemplate.objects.create(plan=plan, template=t)
            plan.save()
            return HttpResponseRedirect(reverse('plans'))
        else:
            print(f)
            return HttpResponseRedirect(reverse('plans'))
    else:
        accounts_set = {x["id"]: x for x in Account.objects.values()}
        groups_set = {x["id"]: x for x in Group.objects.values()}
        origins = Origin.objects.values().order_by("phone_number")
        for o in origins:
            o["account_uuid"] = accounts_set[o["account_id"]]["uuid"]
        origins_set = {x["id"]: x for x in Origin.objects.values()}
        templates_set = {x["id"]: x for x in Template.objects.values()}

        plan = Plan.objects.get(uuid=u)
        context = {
            "title": settings.TITLE,
            "plan": plan,
            "accounts": Account.objects.all().order_by("name"),

            "groups": Group.objects.all().order_by('name'),
            "selected_groups": [
                groups_set[x[0]]["uuid"]
                for x
                in PlanGroup.objects.filter(plan__id=plan.id).values_list("group")
            ],

            "origins": origins,
            "selected_origins": [
                origins_set[x[0]]["uuid"]
                for x
                in PlanOrigin.objects.filter(plan__id=plan.id).values_list("origin")
            ],

            "templates": Template.objects.all().order_by("name"),
            "selected_templates": [
                templates_set[x[0]]["uuid"]
                for x
                in PlanTemplate.objects.filter(plan__id=plan.id).values_list("template")
            ],

            "platforms": settings.AVAILABLE_PLATFORMS,
            "selected_platforms": [
                x[0]
                for x
                in PlanPlatform.objects.filter(plan__id=plan.id).values_list("platform")
            ],
        }
        return HttpResponse(template.render(context, request))


@login_required
def plan_delete(request, u):
    template = loader.get_template('plan_delete.html')
    if request.method == 'POST':
        f = DeleteObjectForm(request.POST)
        if f.is_valid() and u == f.cleaned_data['uuid']:
            Plan.objects.filter(uuid=u).delete()
            return HttpResponseRedirect(reverse('plans'))
        else:
            print(f)
            p = Plan.objects.get(uuid=u)
            context = {
                "title": settings.TITLE,
                "p": p,
                "form": f
            }
            return HttpResponse(template.render(context, request))
    else:
        p = Plan.objects.get(uuid=u)
        context = {
            "title": settings.TITLE,
            "p": p,
        }
        return HttpResponse(template.render(context, request))


@login_required
def plan_view(request, u):
    if request.method == 'POST':

        groups_set = {x.id: x for x in Group.objects.all()}
        origins_set = {x.id: x for x in Origin.objects.all()}
        templates_set = {x.id: x for x in Template.objects.all()}

        plan = Plan.objects.get(uuid=u)

        platforms = [x[0] for x in PlanPlatform.objects.filter(plan__id=plan.id).values_list("platform")]
        groups = [groups_set[x[0]] for x in PlanGroup.objects.filter(plan__id=plan.id).values_list("group")]
        origins = [origins_set[x[0]] for x in PlanOrigin.objects.filter(plan__id=plan.id).values_list("origin")]
        templates = [templates_set[x[0]] for x in PlanTemplate.objects.filter(plan__id=plan.id).values_list("template")]

        results = []

        c = TwilioClient(
            plan.account.sid,
            plan.account.auth_token,
            edge=settings.TWILIO_EDGE)

        e = Execution.objects.create(plan=json.dumps({
            "account": {
                "sid": plan.account.sid,
                "uuid": plan.account.uuid,
                "name": plan.account.name
            },
            "uuid": plan.uuid,
            "name": plan.name,
            "platforms": platforms,
            "origins": [x.phone_number for x in origins],
            "groups": [x.name for x in groups],
            "templates": [x.body for x in templates],
        },  cls=KangaEncoder, ensure_ascii=False, allow_nan=False))
        i = 0
        for template in templates:
            # Log the message here, since not actually using templating
            content, created = MessageContent.objects.update_or_create(subject=template.body[0:20], body=template.body)
            #
            for group in groups:
                targets = Target.objects.filter(group__id=group.id)
                for target in targets:
                    origin = origins[i % len(origins)]
                    from_phone_number = origin.phone_number.as_e164
                    to_phone_number = target.phone_number.as_e164
                    for platform in platforms:
                        if platform == "sms":
                            try:
                                # Send message via Twilio
                                m = c.messages.create(
                                    body=content.body,
                                    from_=from_phone_number,
                                    to=to_phone_number)
                                # Log into results
                                results += [{
                                    "group": group.name,
                                    'platform': platform,
                                    'sid': m.sid,
                                    'from_phone_number': from_phone_number,
                                    'to_phone_number': to_phone_number,
                                    "num_media": m.num_media,
                                    "uri": m.uri,
                                    "date_created": m.date_created,
                                }]
                                # Add to database log
                                Message.objects.create(
                                    sid=m.sid,
                                    execution=e,
                                    account=plan.account,
                                    platform=platform,
                                    origin=origin,
                                    target=target,
                                    content=content,
                                    sent_at=m.date_created,
                                )
                                # increment counter
                                i += 1
                            except Exception as err:
                                print("error sending message via {} to {}".format(platform, to_phone_number))
                                print(err)
                        elif platform == "whatsapp":
                            # Send message via Twilio
                            try:
                                m = c.messages.create(
                                    body=content.body,
                                    from_="whatsapp:{}".format(from_phone_number),
                                    to="whatsapp:{}".format(to_phone_number))
                                # Log into results
                                results += [{
                                    "group": group.name,
                                    'platform': platform,
                                    'sid': m.sid,
                                    'from_phone_number': from_phone_number,
                                    'to_phone_number': to_phone_number,
                                    "num_media": m.num_media,
                                    "uri": m.uri,
                                    "date_created": m.date_created,
                                }]
                                # Add to database log
                                Message.objects.create(
                                    sid=m.sid,
                                    execution=e,
                                    account=plan.account,
                                    platform=platform,
                                    origin=origin,
                                    target=target,
                                    content=content,
                                    sent_at=m.date_created,
                                )
                                # increment counter
                                i += 1
                            except Exception as err:
                                print("error sending message via {} to {}".format(platform, to_phone_number))
                                print(err)
                        else:
                            raise Exception("unkown platform {}".format(platform))
        ExecutionResults.objects.create(
            execution=e,
            results=json.dumps(
                results,
                cls=KangaEncoder,
                ensure_ascii=False,
                allow_nan=False
            )
        )
        return HttpResponseRedirect(reverse("execution_view", args=[e.uuid]))
    else:
        plan = Plan.objects.get(uuid=u)

        plan_group_ids = [x[0] for x in PlanGroup.objects.filter(plan__id=plan.id).values_list("group")]

        accounts_set = {x["id"]: x for x in Account.objects.values()}
        groups_set = {x["id"]: x for x in Group.objects.values()}
        origins = Origin.objects.values().order_by("phone_number")
        for o in origins:
            o["account_uuid"] = accounts_set[o["account_id"]]["uuid"]
        origins_set = {x["id"]: x for x in Origin.objects.values()}
        templates_set = {x["id"]: x for x in Template.objects.values()}

        targets_by_group = {
            x['group']: x['total']
            for x
            in Target.objects.all().values('group').annotate(total=Count('group')).order_by('total')
        }

        plan_groups = [
            {
                "name": groups_set[x[0]]["name"],
                "total": targets_by_group[x[0]]
            }
            for x
            in PlanGroup.objects.filter(plan__id=plan.id).values_list("group")
        ]

        targets = Target.objects.filter(group__in=plan_group_ids).count()

        context = {
            "title": settings.TITLE,
            "plan": plan,
            "groups": plan_groups,
            "origins": [
                origins_set[x[0]]["phone_number"]
                for x
                in PlanOrigin.objects.filter(plan__id=plan.id).values_list("origin")
            ],
            "templates": [
                templates_set[x[0]]
                for x
                in PlanTemplate.objects.filter(plan__id=plan.id).values_list("template")
            ],
            "platforms": [
                x[0]
                for x
                in PlanPlatform.objects.filter(plan__id=plan.id).values_list("platform")
            ],
            "total": targets,
        }
        return HttpResponse(loader.get_template('plan_view.html').render(context, request))


#
# Execution Results
#

@login_required
def executions(request):
    template = loader.get_template('executions.html')

    executions = []
    for e in Execution.objects.all().order_by("-created_at"):
        executions += [{
            "uuid": e.uuid,
            "plan": json.loads(e.plan),
            "created_at": e.created_at
        }]

    context = {
        "title": settings.TITLE,
        "executions": executions,
    }
    return HttpResponse(template.render(context, request))


@login_required
def execution_view(request, u):
    template = loader.get_template('execution_view.html')

    e = Execution.objects.get(uuid=u)

    origins_set = {x.id: x for x in Origin.objects.all().order_by("phone_number")}
    metrics = {
        "platforms": [
            {
                "platform": x["id"],
                "count": Message.objects.filter(execution=e, platform=x["id"]).count()
            }
            for x in settings.AVAILABLE_PLATFORMS
        ],
        "origins": [
            {
                "origin": origins_set[x['origin']].phone_number,
                "count": x['count']
            }
            for x
            in Message.objects.filter(execution=e).values('origin').annotate(count=Count('origin')).order_by('count')
        ]
    }

    context = {
        "title": settings.TITLE,
        "execution": e,
        "plan": json.loads(e.plan),
        "messages": Message.objects.filter(execution=e).order_by("sent_at"),
        "metrics": metrics
    }
    return HttpResponse(template.render(context, request))


#
# Messages
#

@login_required
def messages(request):
    template = loader.get_template('messages.html')

    context = {
        "title": settings.TITLE,
        "messages": Message.objects.values()
    }
    return HttpResponse(template.render(context, request))
