import datetime

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import request, HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from django.urls import reverse_lazy
from django.views import generic, View
from django.views.generic import DeleteView

from functions import create_schedule, time_recalculation_rounded, base_time_reduction, time_format
from main.forms import AddPlan, AddActivity, AddAvailability
from main.models import Plan, Activities, Availability, Schedule


class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


class CheckUser(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request):
        users = User.objects.all()
        session = ' | '.join("{}={}".format(key, val) for (key, val) in request.session.items())
        cookies = ' | '.join('{}: {}'.format(key, value) for key, value in request.COOKIES.items())
        return render(request, "users_list.html", {"users": users, "session": session, "cookies": cookies})


class UserView(UserPassesTestMixin, View):
    def test_func(self):
        u_id = self.kwargs['id']
        user_url = User.objects.get(id=u_id)
        return user_url == self.request.user

    def get(self, request, id):
        plans = Plan.objects.filter(user_id=id)
        today = datetime.date.today()
        today_min6 = today - datetime.timedelta(days=7)
        form = AddPlan()
        return render(request, 'user_summary.html', {'plans': plans,
                                                     'user': User.objects.get(id=id),
                                                     'form': form,
                                                     'today': today,
                                                     'today_min6': today_min6})

    def post(self,request, id):
        form = AddPlan(request.POST)
        user = User.objects.get(id=id)
        if form.is_valid():
            start_date = form.cleaned_data['starting_date']
            Plan.objects.create(user=user, start_date=start_date)
            return HttpResponseRedirect("/rotw/{}".format(id))
        else:
            return HttpResponse(form.non_field_errors, form.starting_date.errors)


class PlanView(UserPassesTestMixin, View):

    def test_func(self):
        p_id = self.kwargs['p_id']
        user_url = Plan.objects.get(id=p_id).user
        return user_url == self.request.user

    def get(self, request, u_id, p_id):
        val = request.GET.get('val')
        if val == "time":
            m = "Available time is higher than time assigned to all activities, please modify the assumptions"
        else:
            m = ""
        plan_act = Activities.objects.filter(plan_id=p_id)
        plan_ava = Availability.objects.filter(plan_id=p_id)
        form_act = AddActivity()
        form_ava = AddAvailability()
        user = User.objects.get(id=u_id)
        plan = Plan.objects.get(id=p_id)
        today = datetime.date.today()

        for a in plan_ava:
            a.day_date = a.plan.start_date + datetime.timedelta(days=(a.day-1))
            a.weekday = a.day_date.strftime('%A')
            a.day_label = a.weekday + " (" + str(a.day_date) + ")"
            # print(a.day_date, a.weekday, a.day_label)

        sum_act = 0
        for a in plan_act:
            sum_act += a.assumed_time

        sum_ava = 0
        for a in plan_ava:
            sum_ava += a.duration

        f_weekday = plan.start_date.strftime('%A')
        first_day = f_weekday + " (" + str(plan.start_date) + ")"

        return render(request, 'plan_view.html', {'plan_act': plan_act,
                                                  'plan_ava': plan_ava,
                                                  'form_act': form_act,
                                                  'form_ava': form_ava,
                                                  'sum_act': sum_act,
                                                  'sum_ava': sum_ava,
                                                  'plan': plan,
                                                  'user': user,
                                                  'm': m,
                                                  'today': today,
                                                  'first_day': first_day})

    def post(self,request, u_id, p_id):
        plan_act = Activities.objects.filter(plan_id=p_id)
        plan_ava = Availability.objects.filter(plan_id=p_id)
        today = datetime.date.today()

        user = User.objects.get(id=u_id)
        plan = Plan.objects.get(id=p_id)
        submit = request.POST.get('submit')

        if submit == "add activity":
            form_act = AddActivity(request.POST)

            if form_act.is_valid():
                name = form_act.cleaned_data['name']
                description = form_act.cleaned_data['description']
                priority = form_act.cleaned_data['priority']
                assumed_time = form_act.cleaned_data['assumed_time']
                color = form_act.cleaned_data['color']
                Activities.objects.create(user=user,
                                          plan=plan,
                                          name=name,
                                          description=description,
                                          priority=priority,
                                          assumed_time=assumed_time,
                                          color=color)
                form_act_status = 'valid'
            else:
                form_act_status = 'not valid'
        else:
            form_act = AddActivity()

        if submit == "add time slot":
            form_ava = AddAvailability(request.POST)

            if form_ava.is_valid():
                day = form_ava.cleaned_data['day']
                start_time = form_ava.cleaned_data['start_time']
                end_time = form_ava.cleaned_data['end_time']

                Availability.objects.create(user=user,
                                            plan=plan,
                                            day=day,
                                            start_time=start_time,
                                            end_time=end_time,
                                            duration=(int(end_time) - int(start_time)) / 2
                                            )
                form_ava_status = 'valid'
            else:
                form_ava_status = 'not valid'
        else:
            form_ava = AddAvailability()

        sum_act = 0
        for a in plan_act:
            sum_act += a.assumed_time

        sum_ava = 0
        for a in plan_ava:
            sum_ava += a.duration

        f_weekday = plan.start_date.strftime('%A')
        first_day = f_weekday + " (" + str(plan.start_date) + ")"

        return render(request, 'plan_view.html', {'plan_act': plan_act,
                                                  'form_act': form_act,
                                                  'sum_act': sum_act,
                                                  'sum_ava': sum_ava,
                                                  'plan_ava': plan_ava,
                                                  'form_ava': form_ava,
                                                  'plan': plan,
                                                  'user': user,
                                                  'today': today,
                                                  'first_day': first_day})


class ActivityView(UserPassesTestMixin, View):
    def test_func(self):
        u_id = self.kwargs['id']
        user_url = Activities.objects.get(id=u_id).user
        return user_url == self.request.user

    def get(self, request, id):
        activity = Activities.objects.get(id=id)
        form = AddActivity(initial={"name": activity.name,
                                    "description": activity.description,
                                    "priority": activity.priority,
                                    "assumed_time": activity.assumed_time,
                                    "color": activity.color})
        return render(request, 'edit_activity.html', {'activity': activity,
                                                      'form': form})

    def post(self,request, id):
        form = AddActivity(request.POST)
        activity = Activities.objects.get(id=id)
        user_id = activity.user_id
        plan_id = activity.plan_id
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            priority = form.cleaned_data['priority']
            assumed_time = form.cleaned_data['assumed_time']
            color = form.cleaned_data['color']
            activity.name = name
            activity.description = description
            activity.priority = priority
            activity.assumed_time = assumed_time
            activity.color = color
            activity.save()
        return HttpResponseRedirect("/rotw/{}/{}".format(user_id, plan_id))


class AvailabilityView(UserPassesTestMixin, View):
    def test_func(self):
        u_id = self.kwargs['id']
        user_url = Availability.objects.get(id=u_id).user
        return user_url == self.request.user

    def get(self, request, id):
        availability = Availability.objects.get(id=id)
        form = AddAvailability(initial={"day": availability.day,
                                        "start_time": availability.start_time,
                                        "end_time": availability.end_time,
                                        "duration": availability.duration})

        return render(request, 'edit_availability.html', {'availability': availability,
                                                          'form': form})

    def post(self,request, id):
        form = AddAvailability(request.POST)
        availability = Availability.objects.get(id=id)
        user_id = availability.user_id
        plan_id = availability.plan_id
        if form.is_valid():
            day = form.cleaned_data['day']
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']
            availability.day = day
            availability.start_time = start_time
            availability.end_time = end_time
            availability.duration = (int(end_time) - int(start_time)) / 2
            availability.save()
        return HttpResponseRedirect("/rotw/{}/{}".format(user_id, plan_id))


class RemovePlanView(UserPassesTestMixin, DeleteView):
    def test_func(self):
        u_id = self.kwargs['pk']
        user_url = Plan.objects.get(id=u_id).user
        return user_url == self.request.user

    model = Plan

    def get_success_url(self):
        return '/rotw/{}'.format(self.object.user.id)


class RemoveActivityView(UserPassesTestMixin, DeleteView):
    def test_func(self):
        u_id = self.kwargs['pk']
        user_url = Activities.objects.get(id=u_id).user
        return user_url == self.request.user

    model = Activities

    def get_success_url(self):
        return '/rotw/{}/{}'.format(self.object.user.id, self.object.plan.id)


class RemoveAvailabilityView(UserPassesTestMixin, DeleteView):
    def test_func(self):
        u_id = self.kwargs['pk']
        user_url = Availability.objects.get(id=u_id).user
        return user_url == self.request.user

    model = Availability

    def get_success_url(self):
        return '/rotw/{}/{}'.format(self.object.user.id, self.object.plan.id)


class PlanDetailsView(UserPassesTestMixin, View):

    def test_func(self):
        p_id = self.kwargs['p_id']
        user_url = Plan.objects.get(id=p_id).user
        return user_url == self.request.user

    def get(self, request, u_id, p_id):
        val = request.GET.get('val')
        if val == "true":
            activities = Activities.objects.filter(plan_id=p_id)
            availability = Availability.objects.filter(plan_id=p_id)
            user = User.objects.get(id=u_id)
            plan = Plan.objects.get(id=p_id)

            sum_ava = 0
            for slot in availability:
                sum_ava += slot.duration
            act_sequence = create_schedule(activities, sum_ava)

            if sum_ava > len(act_sequence) / 2:
                return HttpResponseRedirect('/rotw/{}/{}?val=time'.format(user.id, plan.id))

            for a in activities:
                a.applied_time = 0
                a.save()

            # usuń poprzedni schedule - do uzupełnienia

            to_delete = Schedule.objects.filter(plan_id=p_id)
            to_delete.delete()

            # wypełnij schedule
            j = 0
            for slot in availability:
                for i in range(int(slot.duration * 2)):
                    act = Activities.objects.get(id=act_sequence[j])
                    j += 1
                    Schedule.objects.create(user=user,
                                            plan=plan,
                                            slot=slot,
                                            order=i,
                                            activity=act,
                                            start_time=slot.start_time + i,
                                            duration=0.5)
                    act.applied_time = act.applied_time + 0.5
                    act.save()

            schedule = Schedule.objects.filter(plan_id=p_id)

        activities = Activities.objects.filter(plan_id=p_id)
        schedule = Schedule.objects.filter(plan_id=p_id)
        user = User.objects.get(id=u_id)
        plan = Plan.objects.get(id=p_id)
        day = plan.start_date

        graph = []
        for d in range(1,8):
            day = plan.start_date+datetime.timedelta(days=(d-1))
            day_weekday = day.strftime('%A')
            day_label = day_weekday+" ("+str(day)+")"
            graph_day = []
            for slot in range(14,44):
                try:
                    a = Schedule.objects.get(plan__id=p_id, slot__day=d, start_time=slot)
                    graph_day.append((
                        day_label,
                        time_format(datetime.timedelta(minutes=slot*30)),
                        a.activity.name,
                        a.activity.get_color_display()
                    ))
                except ObjectDoesNotExist:
                    graph_day.append((
                        day_label,
                        time_format(datetime.timedelta(minutes=slot*30)),
                        '',
                        'whitesmoke'
                    ))
            graph.append(graph_day)

        return render(request, 'schedule.html', {'schedule': schedule,
                                                 'user': user,
                                                 'plan': plan,
                                                 'graph': graph,
                                                 'activities': activities})


# class ScheduleRecalculation(UserPassesTestMixin, View):
#     def test_func(self):
#         u_id = self.kwargs['u_id']
#         user_url = User.objects.get(id=u_id)
#         return user_url == self.request.user
#
#     def get(self, request, u_id, p_id):
#         activities = Activities.objects.filter(plan_id=p_id)
#         availability= Availability.objects.filter(plan_id=p_id)
#         user = User.objects.get(id=u_id)
#         plan = Plan.objects.get(id=p_id)
#
#         sum_ava = 0
#         for slot in availability:
#             sum_ava += slot.duration
#         act_sequence = create_schedule(activities, sum_ava)
#
#         for a in activities:
#             a.applied_time = 0
#             a.save()
#
#         # usuń poprzedni schedule - do uzupełnienia
#
#         to_delete = Schedule.objects.filter(plan_id=p_id)
#         to_delete.delete()
#
#
#         # wypełnij schedule
#         j = 0
#         for slot in availability:
#             for i in range(int(slot.duration*2)):
#                 act = Activities.objects.get(id=act_sequence[j])
#                 j += 1
#                 Schedule.objects.create(user=user,
#                                         plan=plan,
#                                         slot=slot,
#                                         order=i,
#                                         activity=act,
#                                         start_time=slot.start_time+i,
#                                         duration=0.5)
#                 act.applied_time = act.applied_time + 0.5
#                 act.save()
#
#         schedule = Schedule.objects.filter(plan_id=p_id)
#         activities = Activities.objects.filter(plan_id=p_id)
#
#         return render(request, "schedule_recalculation.html", {'act_sequence': act_sequence,
#                                                                'schedule': schedule,
#                                                                'activities': activities,
#                                                                'user': user,
#                                                                'plan': plan})
