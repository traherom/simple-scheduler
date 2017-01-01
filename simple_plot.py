#!/usr/bin/env python3
import csv
import sys
from gantt import Chart, Project, Task, Resource

# Create resources and tasks from CSV
chart = Chart('Xylok')
project = Project('Xylok Scanner')
chart.add_project(project)

resources = {}
tasks = {}
with open('data.csv') as csvfile:
    csv = csv.DictReader(csvfile)

    for row in csv:
        # Add new resources as encountered
        task_resources = []
        for r in row['Resource'].split('/'):
            if r not in resources:
                resources[r] = Resource(r)
                chart.add_resource(resources[r])

            task_resources.append(resources[r])

        dependencies = [tasks[row['Dependency']]] if row['Dependency'] else []

        tasks[row['Task']] = Task(
            name=row['Task'],
            duration=int(row['Duration']),
            resources=task_resources,
            dependencies=dependencies,
            project=project,
        )

# Draw
chart.calculate_schedule()
print(chart)
