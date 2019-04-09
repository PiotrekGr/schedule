import random
import django
django.setup()

from main.models import Activities

# activities = Activities.objects.filter(plan_id=2)

MAX_PRIORITY = 10
VALUE_FOR_EXCLUDED_ELEMENTS = 0
ANY_LARGE_NUMBER = 10000
HALF_HOUR_BLOCK_DURATION = 0.5
HALF_HOUR_BLOCKS_IN_ONE_HOUR = 2


def reverse_priority(priority):
    return MAX_PRIORITY - priority


def base_time_reduction(activities, available_time, minimum_included_priority=1):
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

    assumed_time_sum = sum(activity.assumed_time
                           if activity.priority >= minimum_included_priority
                           else VALUE_FOR_EXCLUDED_ELEMENTS for activity in activities)

    assumed_time_weighted_sum = sum(reverse_priority(activity.priority) * activity.assumed_time
                                    if activity.priority >= minimum_included_priority 
                                    else VALUE_FOR_EXCLUDED_ELEMENTS for activity in activities)

    missing_time = assumed_time_sum - available_time
    base_reduction_ratio = missing_time / assumed_time_weighted_sum

    for activity in activities:
        if activity.priority >= minimum_included_priority:
            activity.time_reduction = base_reduction_ratio * reverse_priority(activity.priority) * activity.assumed_time
            activity.recalculated_time = activity.assumed_time - activity.time_reduction

    return activities


def no_time_reduction(activities):
    for activity in activities:
        activity.recalculated_time = activity.assumed_time
    return activities


def max_priority_time_reduction(activities, available_time, assumed_time_sum_max_priority):
    reduction_ratio = available_time / assumed_time_sum_max_priority
    for activity in activities:
        if activity.priority == MAX_PRIORITY:
            activity.recalculated_time = activity.assumed_time * reduction_ratio
            activity.diff = activity.assumed_time - activity.recalculated_time
        else:
            activity.recalculated_time = VALUE_FOR_EXCLUDED_ELEMENTS
            activity.diff = VALUE_FOR_EXCLUDED_ELEMENTS
    return activities


def time_reduction_positive_outcomes(activities, available_time):
    outcome_with_positive_figures = False
    priority_threshold = 0
    while not outcome_with_positive_figures:
        priority_threshold += 1
        activities_recalculated = base_time_reduction(activities, available_time, priority_threshold)
        any_negative_figures = 0
        for activity in activities_recalculated:
            if activity.recalculated_time < 0:
                any_negative_figures += 1
        if any_negative_figures == 0:
            outcome_with_positive_figures = True
    return activities_recalculated


def time_recalculation(activities, available_time):
    # separate path in case time assigned for priority 10 activities surpasses available time
    #     checking if priority 10 alone exceeds time limit

    assumed_time_sum_all_priorities = sum(activity.assumed_time for activity in activities)
    assumed_time_sum_max_priority = sum(activity.assumed_time if activity.priority == MAX_PRIORITY
                                        else VALUE_FOR_EXCLUDED_ELEMENTS
                                        for activity in activities)

    #   if yes, time assigned for priority 10 gets reduced,
    #   whereas time assigned for remaining activities goes down to zero
    if assumed_time_sum_max_priority > available_time:
        return max_priority_time_reduction(activities, available_time, assumed_time_sum_max_priority)

    elif assumed_time_sum_all_priorities < available_time:
        return no_time_reduction(activities)

    else:
        return time_reduction_positive_outcomes(activities, available_time)


def round_time(activities):
    sum_time_rounded = 0
    for activity in activities:
        activity.recalculated_time_rounded = round((activity.recalculated_time * 2), 0) / 2
        activity.round_diff = activity.recalculated_time_rounded - activity.recalculated_time
        sum_time_rounded += activity.recalculated_time_rounded
    return activities, sum_time_rounded


def rounding_subtract_half_hour(activities, diff_max, sum_time_rounded):
    for activity in activities:
        if (activity.round_diff - activity.priority / ANY_LARGE_NUMBER) == diff_max:
            activity.recalculated_time_rounded -= HALF_HOUR_BLOCK_DURATION
            activity.round_diff = activity.recalculated_time_rounded - activity.recalculated_time
            sum_time_rounded -= HALF_HOUR_BLOCK_DURATION
            break
    return activities, sum_time_rounded


def rounding_add_half_hour(activities, diff_min, sum_time_rounded):
    for activity in activities:
        if (activity.round_diff - activity.priority / ANY_LARGE_NUMBER) == diff_min:
            activity.recalculated_time_rounded += HALF_HOUR_BLOCK_DURATION
            activity.round_diff = activity.recalculated_time_rounded - activity.recalculated_time
            sum_time_rounded += HALF_HOUR_BLOCK_DURATION
            break
    return activities, sum_time_rounded


def time_recalculation_rounded(activities, available_time):
    assumed_time_sum_all_priorities = sum(activity.assumed_time for activity in activities)
    if assumed_time_sum_all_priorities <= available_time:
        for activity in activities:
            activity.recalculated_time_rounded = activity.recalculated_time
        return activities
    else:
        activities_recalculated = time_recalculation(activities, available_time)
        activities_recalculated, sum_time_rounded = round_time(activities_recalculated)

        while available_time != sum_time_rounded:
            diff_max = 0
            diff_min = 0
            # max and min is corrected by assigned priority - in order to adjust in accordance with
            # activities' importance in case of equal difference resulting from rounding
            for activity in activities_recalculated:
                diff_max = max(diff_max, activity.round_diff - activity.priority / ANY_LARGE_NUMBER)
                diff_min = min(diff_min, activity.round_diff - activity.priority / ANY_LARGE_NUMBER)

            if sum_time_rounded > available_time:
                activities_recalculated, sum_time_rounded = \
                    rounding_subtract_half_hour(activities_recalculated, diff_max, sum_time_rounded)

            if sum_time_rounded < available_time:
                activities_recalculated, sum_time_rounded = \
                    rounding_add_half_hour(activities_recalculated, diff_min, sum_time_rounded)

        return activities_recalculated


def create_schedule(activities, available_time):
    result = time_recalculation_rounded(activities, available_time)
    schedule = []
    for activity in result:
        number_of_half_hour_blocks = int(activity.recalculated_time_rounded * HALF_HOUR_BLOCKS_IN_ONE_HOUR)
        for i in range(number_of_half_hour_blocks):
            schedule.append(activity.id)
    random.shuffle(schedule)
    return schedule


def time_format(a):
    split = str(a).split(':')
    return split[0]+":"+split[1]
