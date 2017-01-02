Simple Scheduler
================
I occasionally do freelancing work and needed a simple way to build
out a notional schedule based on estimated task length. There are many
Gantt chart builders out there, but they typically require choosing
start dates for each individual task. In addition, all the online builders
make you enter the tasks in their own interface (clunky), cost money after
some short trial (too much overhead), or don't offer an easy way to share
the schedule with someone else.

Simple Scheduler asks for just a CSV of tasks, how long they'll take,
who is going to work on each task, and any dependencies of each task.
From there it spits out an SVG with each task scheduled based on the rules:

- Tasks are scheduled in the order they are in the CSV.
- A resource (person) can only perform one task at a time.
- A task's dependencies must be complete before it can begin.
- (by default) No work is done on weekends.

Installation
============

.. code:: shell

   pip install projectscheduler

Usage
=====

Create a CSV with your tasks in the format:
.. table:: Example CSV

   ===================  ======== ========== =========================
   Task                 Duration Resources  Dependency
   ===================  ======== ========== =========================
   Name of task 1       6        Person 1
   Some other task      3        Person 1
   Some other task 3    12       Person 2   Name of task 1
   ===================  ======== ========== =========================

Where duration is given in days. Multiple resources can be separated by a "/". (I.E, "Person1/Person2").

.. code:: shell

   schedule input.csv output.svg

TODO
====
1. Command line arguments
2. `pip install`
3. Multiple dependencies for a task?

Credits
=======
Python-gantt_ was the original inspiration for this project. I originally built the scheduler around it,
but didn't like certain aspects of the API. This tool uses the rendering
code from that project.

.. _Python-gantt: http://xael.org/pages/python-gantt-en.html
