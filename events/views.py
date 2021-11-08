from .utils import (
    Calendar,
    # Table,
    # Quickview,
    DivLayout,
    DivSailors,
)
import calendar
from .models import Event
# from sailors.models import Sailor
from django.views import generic
from django.shortcuts import (
    render,
    redirect,
)
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.safestring import mark_safe
from datetime import (
    datetime,
    timedelta,
    date,
)


def index(request):
    # print(request)
    return render(request, 'calendar.html', {})


def login_user(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You have successfully logged in')
            return redirect("quickview")
        else:
            messages.success(request, 'Error logging in')
            return redirect('login')
    else:
        return render(request, 'login.html', {})


def logout_user(request):
    logout(request)
    messages.success(request, 'You have been logged out!')
    print('logout function working')
    return redirect('login')


def recall(request, queryset):
    return render(request, 'sailors/detail.html', queryset)


class CalendarView(generic.ListView):
    model = Event
    template_name = 'calendar.html'

    def __init__(self, *args, **kwargs):
        print(*args)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # use today's date for the calendar
        d = get_date(self.request.GET.get('month', None))
        # Instantiate our calendar class with today's year and date
        auth = self.request.user.is_authenticated
        cal = Calendar(d.year, d.month, auth=auth)

        # Call the formatmonth method, which returns our calendar as a table
        html_cal = cal.formatmonth(withyear=True)
        context['prev_month'] = prev_month(d)
        context['curr_month'] = d.strftime("%B %Y")
        context['next_month'] = next_month(d)
        context['calendar'] = mark_safe(html_cal)
        context['view'] = 'calendar'
        return context


class QuickView(generic.ListView):
    model = Event
    template_name = 'calendar.html'

    def __init__(self, *args, **kwargs):
        print(*args)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        auth = self.request.user.is_authenticated

        li = DivSailors(auth=auth)
        sailors = li.get_sailors()

        # use today's date for the calendar unless it's after the last Duty day this month
        d = get_date(self.request.GET.get('month', None))
        print(d)
        try:
            last_dutyday = Event.objects.filter(day__year=d.year,day__month=d.month).last().day
            if (date.today() > last_dutyday):
                d += timedelta(days=7)
        except AttributeError:
            pass    
        print(d)

        quickview = DivLayout(d.year, d.month, auth)
        table = quickview.formatmonth()
        # context['slack_url'] = 'https://join.slack.com/t/csa63dutysection/shared_invite/zt-rlq6ddgn-XoEPYV6ub0h_FSAqxcGXSw'
        context['prev_month'] = prev_month(d)
        context['curr_month'] = d.strftime("%B %Y")
        context['next_month'] = next_month(d)
        context['sailors'] = mark_safe(sailors)
        context['calendar'] = mark_safe(table)
        context['view'] = 'quickview'
        return context


def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    # print(f'prev: {month}')
    return month


def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    # print(f'next: {month}')
    return month


def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))

        return date(year, month, day=1)
    return date.today()
