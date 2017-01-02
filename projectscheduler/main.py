#!/usr/bin/env python3
import csv
import sys
import argparse
from gantt import Chart, Project, Task, Resource

def main():
    # Where we reading from?
    parser = argparse.ArgumentParser(description='Create a Gantt chart from a CSV.')
    parser.add_argument('input', help='''CSV to read data from. CSV must have the headers "Resource",
                                    "Dependency", "Task", and "Duration".''')
    parser.add_argument('output', help='''Name of SVG file to write to''')
    args = parser.parse_args()

    # Create resources and tasks from CSV
    chart = Chart(args.input)
    project = Project(args.input)
    chart.add_project(project)

    resources = {}
    tasks = {}
    with open(args.input) as csvfile:
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
    chart.save_svg(args.output)

if __name__ == '__main__':
    sys.exit(main())
