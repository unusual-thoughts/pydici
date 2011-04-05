# coding: utf-8
"""
Test cases
@author: Sébastien Renard (sebastien.renard@digitalfox.org)
@license: GPL v3 or newer
"""

# Python/Django test modules
from django.test import TestCase
from django.core import urlresolvers

# Pydici modules
from pydici.leads.models import Consultant, Client, Lead
import pydici.settings

# Python modules used by tests
from urllib2 import urlparse
from datetime import date

TEST_USERNAME = "fox"
TEST_PASSWORD = "rototo"
PREFIX = "/" + pydici.settings.PYDICI_PREFIX

class SimpleTest(TestCase):
    fixtures = ["auth.json", "core.json", "people.json", "crm.json",
                "leads.json", "staffing.json"]


    def test_basic_page(self):
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)
        for page in ("/",
                     "/search",
                     "/search?q=lala",
                     "/search?q=a",
                     "/search?q=a+e",
                     "/leads/1/",
                     "/leads/2/",
                     "/leads/3/",
                     "/admin/",
                     "/leads/csv/all",
                     "/leads/csv/active",
                     "/leads/sendmail/2/",
                     "/leads/mail/text",
                     "/leads/mail/html",
                     "/leads/review",
                     "/feeds/latest/",
                     "/feeds/mine/",
                     "/feeds/new/",
                     "/feeds/won/",
                     "/feeds/latestStaffing/",
                     "/feeds/myLatestStaffing/",
                     "/staffing/pdcreview/",
                     "/staffing/pdcreview/2009/07",
                     "/staffing/mission/",
                     "/staffing/mission/all",
                     "/staffing/forecast/mission/1/",
                     "/staffing/forecast/mission/2/",
                     "/staffing/forecast/mission/3/",
                     "/staffing/forecast/consultant/1/",
                     "/staffing/timesheet/mission/1/",
                     "/staffing/timesheet/mission/2/",
                     "/staffing/timesheet/mission/3/",
                     "/staffing/timesheet/consultant/1/",
                     "/staffing/timesheet/consultant/1/?csv",
                     "/staffing/timesheet/consultant/1/2010/10",
                     "/staffing/timesheet/all",
                     "/staffing/timesheet/all/?csv",
                     "/staffing/timesheet/all/2010/11",
                     "/leads/graph/pie",
                     "/leads/graph/bar",
                     "/people/consultant/1/",
                     "/people/consultant/2/",
                     "/people/consultant/3/",
                     "/crm/company/1/",
                     "/crm/company/",
                     "/billing/graph/bar",
                     "/billing/bill_review",
                     "/billing/bill_delay",
                     "/forbiden",
                     ):
            response = self.client.get(PREFIX + page)
            self.failUnlessEqual(response.status_code, 200,
                                 "Failed to test url %s (got %s instead of 200" % (page, response.status_code))

    def test_redirect(self):
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)
        response = self.client.get(PREFIX + "/help")
        self.failUnlessEqual(response.status_code, 301)
        for page in ("/staffing/mission/newfromdeal/1/",
                     "/staffing/mission/newfromdeal/2/",
                     "/staffing/mission/1/deactivate",
                     "/staffing/rate/mission/1/consultant/1/"):
            response = self.client.get(PREFIX + page)
            self.failUnlessEqual(response.status_code, 302)

    def test_not_found_page(self):
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)
        for page in (PREFIX + "/leads/234/",
                     PREFIX + "/leads/sendmail/434/"):
            response = self.client.get(page)
            self.failUnlessEqual(response.status_code, 404,
                                 "Failed to test url %s (got %s instead of 404" % (page, response.status_code))

    def test_create_lead(self):
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)
        lead = create_lead()
        self.failUnlessEqual(lead.staffing.count(), 0)
        lead.staffing.add(Consultant.objects.get(pk=1))
        self.failUnlessEqual(lead.staffing.count(), 1)
        # Add staffing here lead.add...
        self.failUnlessEqual(len(lead.update_date_strf()), 14)
        self.failUnlessEqual(lead.staffing_list(), "SRE, (JCF)")
        self.failUnlessEqual(lead.short_description(), "A wonderfull lead th...")
        self.failUnlessEqual(urlresolvers.reverse(pydici.leads.views.detail, args=[4]), PREFIX + "/leads/4/")

        url = "".join(urlparse.urlsplit(urlresolvers.reverse(pydici.leads.views.detail, args=[4]))[2:])
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        context = response.context[-1]
        self.failUnlessEqual(unicode(context["lead"]), u"World company : DSI  - laala")
        self.failUnlessEqual(unicode(context["user"]), "fox")

    def test_pdc_review(self):
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)
        url = PREFIX + "/staffing/pdcreview/2009/07"
        for arg in ({}, {"projected":None}, {"groupby": "manager"}, {"groupby": "position"}):
            response = self.client.get(url, arg)
            self.failUnlessEqual(response.status_code, 200,
                "Failed to test pdc_review with arg %s (got %s instead of 200" % (arg, response.status_code))

class UtilsTest(TestCase):
    def test_monthWeekNumber(self):
        from pydici.staffing.utils import monthWeekNumber
        # Week number, date
        dates = ((1, date(2011, 4, 1)),
                 (1, date(2011, 4, 3)),
                 (2, date(2011, 4, 4)),
                 (2, date(2011, 4, 10)),
                 (5, date(2011, 4, 30)))
        for weekNum, weekDate in dates:
            self.assertEqual(weekNum, monthWeekNumber(weekDate))

    def test_previousWeek(self):
        from pydici.staffing.utils import previousWeek
        # Previous week first day, week day
        dates = ((date(2011, 3, 28), date(2011, 4, 1)),
                 (date(2011, 3, 28), date(2011, 4, 2)),
                 (date(2011, 3, 28), date(2011, 4, 3)),
                 (date(2011, 4, 1), date(2011, 4, 4)),
                 (date(2011, 4, 1), date(2011, 4, 10)),
                 (date(2011, 4, 18), date(2011, 4, 30)),
                 (date(2010, 12, 27), date(2011, 1, 1)),
                 (date(2010, 12, 27), date(2011, 1, 2)),
                 (date(2011, 1, 1), date(2011, 1, 3)),
                 )
        for firstDay, weekDay in dates:
            self.assertEqual(firstDay, previousWeek(weekDay))

    def test_nextWeek(self):
        from pydici.staffing.utils import nextWeek
        # Previous week first day, week day
        dates = ((date(2011, 4, 4), date(2011, 4, 1)),
                 (date(2011, 4, 4), date(2011, 4, 2)),
                 (date(2011, 4, 4), date(2011, 4, 3)),
                 (date(2011, 4, 11), date(2011, 4, 4)),
                 (date(2011, 4, 11), date(2011, 4, 10)),
                 (date(2011, 5, 1), date(2011, 4, 30)),
                 (date(2011, 5, 2), date(2011, 5, 1)),
                 (date(2011, 1, 1), date(2010, 12, 31)),
                 (date(2011, 1, 3), date(2011, 1, 1)),
                 (date(2011, 1, 3), date(2011, 1, 2)),
                 (date(2011, 1, 10), date(2011, 1, 3)),
                 )
        for firstDay, weekDay in dates:
            self.assertEqual(firstDay, nextWeek(weekDay))


#######
def create_lead():
    """Create test lead
    @return: lead object"""
    lead = Lead(name="laala",
          due_date="2008-11-01",
          update_date="2008-11-01 16:14:16",
          creation_date="2008-11-01 15:43:43",
          start_date="2008-11-01",
          responsible=None,
          sales=None,
          external_staffing="JCF",
          state="QUALIF",
          deal_id="123456",
          client=Client.objects.get(pk=1),
          salesman=None,
          description="A wonderfull lead that as a so so long description")

    lead.save()
    return lead
