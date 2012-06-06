import urllib, urllib2
from django.utils import simplejson

class Xpenser:
    BASE_URL    = 'https://www.xpenser.com/api/v1.0/'
    RECEIPT_BASE_URL = 'https://www.xpenser.com/static/xpenser/media/Receipts/'

    def __init__(self, username, passwd):
        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, self.BASE_URL, username, passwd)
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        opener = urllib2.build_opener(handler)
        urllib2.install_opener(opener)

    def _request(self, request, params=None):
        print "Hello: _request", request, params
        try:
            req = urllib2.Request(self.BASE_URL + request, params)
            conn  = urllib2.urlopen(req)
            print "Response ", conn.code, conn.msg
            response = conn.read()
        except Exception, e:
            print "Unable to make request: [%s]: [%s]" % (str(e), e.read())
            raise
        try:
            result = simplejson.loads(response)
        except Exception, e:
            print "Unable to process response: [%s]" % (str(e), )
            print response
            raise
        return result

    def _receipt(self, request):
        print "Hello: _request", request

        try:
            req = urllib2.Request(self.RECEIPT_BASE_URL + request)
            conn  = urllib2.urlopen(req)
            print "Response ", conn.code, conn.msg
            response = conn.read()
        except Exception, e:
            print "Unable to make request: [%s]: [%s]" % (str(e), e.read())
            raise
        return response

    def save_receipt(self, request, filename):
        response = self._receipt(request)
        with open(filename, 'w') as rfile:
            rfile.write(response)

    def get_expenses(self, params=""):
        ''' '''
        try:
            result = self._request('expenses/?' + params)
        except Exception, e:
            print "Unable to get expenses:", str(e)
            return False
        return result

    def update_expense(self, expense_id, values):
        '''
        expense_id should be an int
        values should be a dictionary suitable for urllib.urlencode()
        '''
        return self._request('expense/%i' % expense_id, urllib.urlencode(values))

    def get_report(self, report_name, status='U'):
        reports = self._request('reports/?status=%s'%status)
        for report in reports:
            if report['name'] == report_name:
                return report

        return None

    def create_report(self, report_name, status=None):
        report = self._request('report/', urllib.urlencode({'name':report_name}))
        if status:
            report = self._request('report/%i' % report['id'], urllib.urlencode({'status':status}))
        return report


if __name__ == "__main__":
    xp = Xpenser('username@something.com', 'password')
    expenses = xp.get_expenses()
    print "Here are your expenses:"
    for expense in expenses:
        print expense['type'], expense['amount'], expense['date']
    
    print "Expenses modified since 2010-09-28 in any report"
    new_expenses = xp.get_expenses('modified=2010-09-28+00:00:00&modified_op=gt&report=*')
    for expense in new_expenses:
        print expense['type'], expense['amount'], expense['date']
