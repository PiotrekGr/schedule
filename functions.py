import random

import django
django.setup()

from main.models import Activities

activities = Activities.objects.filter(plan_id=1)


def basic_time_recalc(activities, available_time, min_priority=1):
    # aim:  reducing time assigned to specific activities (assumed_time) due to overall
    #       lack of time (available_time) proportionally to priority, e.g. 5% time reduction for priority 9,
    #       10% for priority 8, 15% for priority 7 and so on - in order to eventually match available time and
    #       sum of recalculated time assigned for individual activities
    #
    #       ! if substantial amount of time is missing, the reduction ratio for lowest priority
    #       may be higher than 100% and assigned time goes negative
    #
    # input: activities (priority, assumed time)
    # input: available time
    # input: filter for minimum priority included in the calculation

    weighted_sum = 0
    assumed_sum = 0
    for a in activities:
        if a.priority >= min_priority:
            weighted_sum += (10 - a.priority)*a.assumed_time
            assumed_sum += a.assumed_time
        else:
            a.recalculated_time = 0

    missing_time = assumed_sum - available_time
    ratio = missing_time / weighted_sum
    for a in activities:
        if a.priority >= min_priority:
            a.diff = ratio * (10 - a.priority)*a.assumed_time
            a.recalculated_time = a.assumed_time - a.diff
    return activities


def time_recalc(tab, available_time):
    # separate path in case time assigned for priority 10 activities surpasses available time
    #     checking if priority 10 alone exceeds time limit
    sum_10 = 0
    for row in tab:
        if row.priority == 10:
            sum_10 += row.assumed_time

    #   if yes, time assigned for priority 10 gets reduced,
    #   whereas time assigned for remaining activities goes down to zero
    if sum_10 > available_time:
        reduction_ratio = available_time/sum_10
        for row in tab:
            if row.priority == 10:
                row.recalculated_time = row.assumed_time*reduction_ratio
                row.diff = row.assumed_time-row.recalculated_time
            else:
                row.recalculated_time = 0
                row.diff = 0
        return activities
# if there is still space for activities with lower priorities
    else:
        finished = False
        i = 0
        while not finished:
            i += 1
            # print('iteration', i)
            iter_result = basic_time_recalc(tab, available_time, i)
            any_neg = 0
            for activity in iter_result:
                if activity.recalculated_time < 0:
                    any_neg += 1
            if any_neg == 0:
                finished = True
        # for activity in activities:
        #     print(activity.priority, activity.assumed_time, round(activity.recalculated_time,1))
        return iter_result


# print(basic_time_recalc(activities, 20, 2))
# print(time_recalc(activities, 120))
#
# for a in time_recalc(activities, 120):
#     print(a.priority, a.assumed_time, a.diff, a.recalculated_time)


def time_recalc_rounded(tab, available_time):
    initial_result = time_recalc(tab, available_time)
    sum_time_rounded = 0
    for a in initial_result:
        a.recalculated_time_rounded = round((a.recalculated_time*2),0)/2
        a.round_diff = a.recalculated_time_rounded - a.recalculated_time
        sum_time_rounded += a.recalculated_time_rounded
    # checking sum after rounding
    # print('initial', available_time)
    # print('rounded', sum_time_rounded)

    while available_time != sum_time_rounded:
        diff_max = 0
        diff_min = 0

        # max and min is corrected by assigned priority - in order to adjust in accorh activities' importance in case of
        # equal difference resulting from rounding
        for a in initial_result:
            diff_max = max(diff_max, a.round_diff - a.priority/10000)
            diff_min = min(diff_min, a.round_diff - a.priority/10000)

        if sum_time_rounded > available_time:
            for a in initial_result:
                if (a.round_diff - a.priority/10000) == diff_max:
                    a.recalculated_time_rounded -= 0.5
                    a.round_diff = a.recalculated_time_rounded - a.recalculated_time
                    sum_time_rounded -= 0.5
                    break

        if sum_time_rounded < available_time:
            for a in initial_result:
                if (a.round_diff - a.priority/10000) == diff_min:
                    a.recalculated_time_rounded += 0.5
                    a.round_diff = a.recalculated_time_rounded - a.recalculated_time
                    sum_time_rounded += 0.5
                    break
    return initial_result


def create_schedule(tab, available_time):
    result = time_recalc_rounded(tab, available_time)
    schedule = []
    for a in result:
        repeat = int(a.recalculated_time_rounded*2)
        for i in range(repeat):
            schedule.append(a.id)
    random.shuffle(schedule)
    return schedule
#
# time_recalc_rounded(activities, 131)

# for a in create_schedule(activities, 45):
#     print(a.activity_id)


print(create_schedule(activities, 9))
print(len(create_schedule(activities, 9)))
