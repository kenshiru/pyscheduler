from croniter import croniter
from time import sleep, time
import logging


def schedule(cronlike_time, target, args=(), kwargs={}):
    logger = logging.getLogger('Scheduler')

    cron = croniter(cronlike_time)
    next_job_time = None

    while True:
        if next_job_time is None:
            next_job_time = cron.get_next()

        print(next_job_time)
        logger.info("Stayed time: {}".format(next_job_time - float(round(time()))))
        if next_job_time - float(round(time())) == 0:
            logger.info("Run target {}".format(str(target)))
            target(*args, **kwargs)
            next_job_time = None
        sleep(1)