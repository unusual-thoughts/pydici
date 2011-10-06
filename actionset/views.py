# coding: utf-8
"""
Pydici action set views. Http request are processed here.
@author: Sébastien Renard (sebastien.renard@digitalfox.org)
@license: AGPL v3 or newer (http://www.gnu.org/licenses/agpl-3.0.html)
"""

import json

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.template import RequestContext
from django.contrib.auth.models import User

from pydici.actionset.models import ActionSet, Action, ActionState
from pydici.core.decorator import pydici_non_public

@pydici_non_public
def update_action_state(request, action_state_id, state):
    """Update action status.
    This view is designed to be called in ajax only
    @return: 0 on success, 1 on error/permission limitation"""
    error = HttpResponse(json.dumps({"error":True}), mimetype="application/json")
    try:
        actionState = ActionState.objects.get(id=action_state_id)
    except ActionState.DoesNotExist:
        return error
    if request.user != actionState.user:
        return error
    if state == "DELEGUATE" and "username" in request.GET:
        try:
            user = User.objects.get(username=request.GET["username"])
        except User.DoesNotExist:
            return error
        actionState.user = user
        actionState.save()
        return HttpResponse(json.dumps({"error":False, "id":action_state_id}), mimetype="application/json")
    elif state in (i[0] for i in ActionState.ACTION_STATES):
        actionState.state = state
        actionState.save()
        return HttpResponse(json.dumps({"error":False, "id":action_state_id}), mimetype="application/json")
    else:
        return error


@pydici_non_public
def actionset_catalog(request):
    """Catalog of all action set"""
    if request.user.has_perm("actionset.change_action") and request.user.has_perm("actionset.change_actionset"):
        can_change = True
    else:
        can_change = False
    return render_to_response("actionset/actionset_catalog.html",
                              {"actionsets": ActionSet.objects.all(),
                               "can_change" : can_change },
                               RequestContext(request))


@pydici_non_public
def launch_actionset(request, actionset_id):
    """Manually launch an actionset for given user (username GET parameter) with ajax query"""
    #TODO: add optional target object (content and id)
    data = {"error": False, "id": actionset_id}
    try:
        actionset = ActionSet.objects.get(id=actionset_id)
    except ActionSet.DoesNotExist:
        data["error"] = True
        data["errormsg"] = _("Action set %s does not exist" % actionset_id)
    try:
        user = User.objects.get(username=request.GET["username"])
    except User.DoesNotExist:
        data["error"] = True
        data["errormsg"] = _("User %s does not exist" % request.GET["username"])
    except KeyError:
        data["error"] = True
        data["errormsg"] = _("Username parameter is missing")

    if not data["error"]:
        actionset.start(user)

    return HttpResponse(json.dumps(data), mimetype="application/json")
