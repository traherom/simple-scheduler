"""
Core of simple-gantt
"""
from datetime import date, timedelta
import logging
from collections import defaultdict

ONE_DAY = timedelta(days=1)

# Don't work weekends (Sat/Sun)
WEEKEND_DAYS = [5, 6]

logger = logging.getLogger(__name__)

class Chart:
    """
    Builds extremely SIMPLE gantt charts.

    This is designed to be a basic utility to help estimate schedules and provide a projected
    timeline for a project. As such, not all features like exact start and end dates are supported;
    instead, tasks ask for duration and follow these rules:
        - A resource (person) can never be doing two things at once
        - All dependencies must be complete before a task can begin
        - All tasks are measurable in days
        - Tasks are ordered on the chart top-to-bottom in the order they were added to projects

    Currently, vacations/unavailability for resources is not supported and only a single project
    may be added to a chart.
    """
    def __init__(self, name):
        self.name = name
        self.projects = []
        self.resources = []
        self.start_date = date.today()

        self.work_weekends = False

    def add_project(self, project):
        """
        Adds the given project to the chart
        """
        if project not in self.projects:
            if len(self.projects) >= 1:
                raise ValueError('Simple Gantt can only handle a single project at a time currently')

            self.projects.append(project)
            project.set_chart(self)

    def add_resource(self, resource):
        """
        Adds the given resource to the gantt chart
        """
        if resource not in self.resources:
            self.resources.append(resource)
            resource.set_chart(self)

    @property
    def skipped_days(self):
        if self.work_weekends:
            return []
        else:
            return WEEKEND_DAYS

    def calculate_schedule(self):
        """
        Calculates the start and end dates of each task
        """
        for proj in self.projects:
            for t in proj.tasks:
                t.schedule()

    def __str__(self):
        """
        Display info on all projects under us
        """
        s = 'Chart {} starts {}, {} resources\nProjects:'.format(self.name, self.start_date, len(self.resources))
        for p in self.projects:
            s += '\n' + str(p)
        return s


class Project:
    """
    Collects tasks
    """
    def __init__(self, name, chart=None):
        self.name = name
        self.tasks = []

        self.chart = None
        self.set_chart(chart)

    def set_chart(self, chart):
        """
        Assigns task to given chart. Ensures chart has us included in their list.
        """
        old_chart = self.chart
        self.chart = chart
        if old_chart != chart and self.chart is not None:
            self.chart.add_project(self)

    def add_task(self, task):
        """
        Adds the given task project
        """
        if task not in self.tasks:
            self.tasks.append(task)
            task.set_project(self)

    def __str__(self):
        """
        Displays info on all tasks
        """
        s = 'Project {} with {} tasks:'.format(self.name, len(self.tasks))
        for t in self.tasks:
            s += '\n' + str(t)
        return s


class Resource:
    """
    Resource for the gantt chart. I.E., a person.
    """
    def __init__(self, name, chart=None):
        """
        Configure required resource attributes
        """
        self.name = name
        self.tasks = []

        self.chart = None
        self.set_chart(chart)

    def set_chart(self, chart):
        """
        Assigns task to given chart. Ensures chart has us included in their list.
        """
        old_chart = self.chart
        self.chart = chart
        if old_chart != chart and self.chart is not None:
            self.chart.add_resource(self)

    def add_task(self, task):
        """
        Adds the given task to this resource so it knows what it's working on.
        """
        if task not in self.tasks:
            self.tasks.append(task)
            task.add_resource(self)

    def is_free(self, date):
        """
        Determines if the resource is available to work on the given day
        """
        for task in self.tasks:
            # If a task isn't scheduled, then we don't need to worry about it
            if task.is_scheduled and task.start_date <= date and task.end_date >= date:
                return False

        return True

    def __str__(self):
        """
        Basic resource info
        """
        return '{} with {} tasks'.format(self.name, len(self.tasks))


class Task:
    """
    Task in project
    """
    def __init__(self, name, duration, resources=[], dependencies=[], project=None):
        """
        Sets the basic attributes of a task
        """
        self.name = name
        self.duration = duration
        self.dependencies = dependencies

        self.resources = []
        for r in resources:
            self.add_resource(r)

        self.project = None
        self.set_project(project)

        self._start_date = None

    def set_project(self, project):
        """
        Assigns task to given project. Ensures project has us included in their list.
        """
        old_proj = self.project
        self.project = project
        if old_proj != project and self.project is not None:
            self.project.add_task(self)

    def add_resource(self, resource):
        """
        Assigns task to given project. Ensures project has us included in their list.
        """
        if resource not in self.resources:
            self.resources.append(resource)
            resource.add_task(self)

    def schedule(self):
        """
        Schedule ourselves based on other tasks and resource availability

        General algorithm:
            1. Try first date immediately after dependency
                1a. If no dependency, use chart start date
            2. Keep advancing date until first free date
        """
        self.clear_schedule()

        chart = self.project.chart

        # Dependencies
        start_date = chart.start_date
        for task in self.dependencies:
            # Must already be scheduled. While they would automatically schedule when we ask them to,
            # we enforce this to require tasks to be added in date order
            if not task.is_scheduled:
                raise SchedulingError('Task {} is a dependency of {} but has not been scheduled. Please place task prior to {} in project'.format(
                    task.name,
                    self.name,
                    self.name)
                    )

            if task.end_date > start_date:
                start_date = task.end_date + ONE_DAY

        # Resource deconfliction
        date_is_free = False
        while not date_is_free:
            date_is_free = True
            for resc in self.resources:
                if not resc.is_free(start_date):
                    start_date += ONE_DAY
                    date_is_free = False

        self._start_date = start_date

    def clear_schedule(self):
        """
        Clears any cached scheduling information
        """
        self._start_date = None

    @property
    def is_scheduled(self):
        """
        Returns if this task has had a start date set
        """
        return self._start_date is not None

    @property
    def start_date(self):
        """
        Returns start date of task, calculating if not already cached
        """
        if self._start_date is not None:
            return self._start_date

        self.schedule()
        return self._start_date

    @property
    def end_date(self):
        """
        End date of task based on start and duration.

        Marks the final day work is actually performed.

        If chart is set to not work weekends, schedule will be extended to
        include extra days to compensate for Saturday and Sunday.
        """
        work_done = 0
        end_date = self.start_date
        while work_done < self.duration:
            end_date += ONE_DAY

            if end_date.weekday() not in self.project.chart.skipped_days:
                work_done += 1

        return end_date

    def __str__(self):
        """
        All dates and resources for task
        """
        return '\tTask {} ({} resources, {} dependencies): {} days, {} through {}'.format(
            self.name,
            len(self.resources),
            len(self.dependencies),
            self.duration,
            self.start_date,
            self.end_date,
            )


class SchedulingError(Exception):
    """
    Exceptions related to improperly configured or impossible scheduling
    """
    pass
