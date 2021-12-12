"""This python file contains the shared scheduler amongst all other files."""

import time
import sched

# Schedule instance initialization
sched_instance = sched.scheduler(time.time, time.sleep)
