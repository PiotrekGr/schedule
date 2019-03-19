from datetime import datetime

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.http import request, HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from django.urls import reverse_lazy
from django.views import generic, View
from django.views.generic import DeleteView

from functions import create_schedule, time_recalc_rounded, basic_time_recalc
from main.forms import AddPlan, AddActivity, AddAvailability
from main.models import Plan, Activities, Availability, Schedule


class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


class CheckUser(View):
    def get(self, request):
        users = User.objects.all()
        session = ' | '.join("{}={}".format(key, val) for (key, val) in request.session.items())
        cookies = ' | '.join('{}: {}'.format(key, value) for key, value in request.COOKIES.items())
        return render(request, "users_list.html", {"users": users, "session": session, "cookies": cookies})


class UserView(View):
    def get(self, request, id):
        plans = Plan.objects.filter(user_id=id) # todo wyjaśnić
        form = AddPlan()
        return render(request, 'user_summary.html', {'plans': plans,
                                                     'user':User.objects.get(id=id).username,
                                                     'form': form})

    def post(self,request, id):
        form = AddPlan(request.POST)
        user = User.objects.get(id=id)
        if form.is_valid():
            start_date = form.cleaned_data['starting_date']
            Plan.objects.create(user=user, start_date=start_date)
            return HttpResponseRedirect("/rotw/{}".format(id))
        else:
            return HttpResponse(form.non_field_errors, form.starting_date.errors)


class PlanView(View):
    def get(self, request, u_id, p_id):
        plan_act = Activities.objects.filter(plan_id=p_id)
        plan_ava = Availability.objects.filter(plan_id=p_id)
        form_act = AddActivity()
        form_ava = AddAvailability()
        user = User.objects.get(id=u_id)
        plan = Plan.objects.get(id=p_id)

        sum_act = 0
        for a in plan_act:
            sum_act += a.assumed_time

        sum_ava =0
        for a in plan_ava:
            sum_ava += a.duration

        return render(request, 'plan_view.html', {'plan_act': plan_act,
                                                  'plan_ava': plan_ava,
                                                  'form_act': form_act,
                                                  'form_ava': form_ava,
                                                  'sum_act': sum_act,
                                                  'sum_ava': sum_ava,
                                                  'plan': plan,
                                                  'user': user})

    def post(self,request, u_id, p_id):
        plan_act = Activities.objects.filter(plan_id=p_id)
        plan_ava = Availability.objects.filter(plan_id=p_id)
        # activities
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
                                            duration=(int(end_time)-int(start_time))/2
                                            )
                form_ava_status = 'valid'
            else:
                form_ava_status = 'not valid'
        else:
            form_ava = AddAvailability()

        sum_act = 0
        for a in plan_act:
            sum_act += a.assumed_time

        sum_ava =0
        for a in plan_ava:
            sum_ava += a.duration

        return render(request, 'plan_view.html', {'plan_act': plan_act,
                                                  'form_act': form_act,
                                                  'sum_act': sum_act,
                                                  'sum_ava': sum_ava,
                                                  'plan_ava': plan_ava,
                                                  'form_ava': form_ava,
                                                  'plan': plan,
                                                  'user': user})



class ActivityView(View):
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
            activity.description= description
            activity.priority= priority
            activity.assumed_time= assumed_time
            activity.color= color
            activity.save()
        return HttpResponseRedirect("/rotw/{}/{}".format(user_id, plan_id))


class AvailabilityView(View):
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
            availability.day= day
            availability.start_time= start_time
            availability.end_time= end_time
            availability.duration =(int(end_time)-int(start_time))/2
            availability.save()
        return HttpResponseRedirect("/rotw/{}/{}".format(user_id, plan_id))


class RemoveActivityView(DeleteView):
    model = Activities

    def get_success_url(self):
        return '/rotw/{}/{}'.format(self.object.user.id, self.object.plan.id)


class RemoveAvailabilityView(DeleteView):
    model = Availability

    def get_success_url(self):
        return '/rotw/{}/{}'.format(self.object.user.id, self.object.plan.id)


class PlanDetailsView(View):
    def get(self, request, u_id, p_id):
        schedule = Schedule.objects.get(plan_id=p_id)
        return render(request, 'schedule.html', {'schedule': schedule})


class ScheduleRecalculation(View):
    def get(self, request, u_id, p_id):
        activities = Activities.objects.filter(plan_id=p_id)
        availability= Availability.objects.filter(plan_id=p_id)
        user = User.objects.get(id=u_id)
        plan = Plan.objects.get(id=p_id)

        sum_ava = 0
        for slot in availability:
            sum_ava += slot.duration
        act_sequence = create_schedule(activities, sum_ava)

        for a in activities:
            a.applied_time = 0
            a.save()

        # usuń poprzedni schedule - do uzupełnienia

        to_delete = Schedule.objects.filter(plan_id=p_id)
        to_delete.delete()


        # wypełnij schedule
        j = 0
        for slot in availability:
            for i in range(int(slot.duration*2)):
                act = Activities.objects.get(id=act_sequence[j])
                j += 1
                Schedule.objects.create(user=user,
                                        plan=plan,
                                        slot=slot,
                                        order=i,
                                        activity=act,
                                        duration=0.5)
                act.applied_time = act.applied_time + 0.5
                act.save()

        schedule = Schedule.objects.filter(plan_id=p_id)
        activities = Activities.objects.filter(plan_id=p_id)

        return render(request, "schedule_recalculation.html", {'act_sequence': act_sequence,
                                                               'schedule': schedule,
                                                               'activities': activities,
                                                               'user': user})
