import croniter
from time import sleep, time
import time
import logging
import threading
import datetime


class ScheduleThread(threading.Thread):
    """
    Класс потока
    """
    def __init__(self, cronlike_time, destroy_event, target, target_args=(), target_kwargs={}, scheduler_name="noname"):
        """
        Опции потока
        """
        threading.Thread.__init__(self)
        self.cronlike_time = cronlike_time
        self._destroyEvent = destroy_event
        self.daemon = True
        self.scheduler_name = scheduler_name
        self.target = target
        self.target_args = target_args
        self.target_kwargs = target_kwargs

        self._logger = logging.getLogger('Scheduler [{}]'.format(self.scheduler_name))


    def run(self):
        try:
            cron = croniter.croniter(self.cronlike_time)
        except croniter.CroniterBadCronError:
            default_cron_time = '0 */1 * * *'
            self._logger.warning('Cronlike time format error. Use default "{}"'.format(default_cron_time))
            cron = croniter.croniter(default_cron_time)

        next_job_time = None

        while True:
            """Нужно убивать поток только в нужный момент (чтобы все ок было)"""
            if self._destroyEvent.is_set():
                return

            if next_job_time is None:
                next_job_time = self._get_next_time(cron)

            await_time = next_job_time - float(round(time.time()))
            if await_time == 0:
                self._logger.info('Run schedule')
                self.target(*self.target_args, **self.target_kwargs)
                self._logger.info('Ready schedule')
                next_job_time = self._get_next_time(cron)

            while await_time < 0:
                next_job_time = self._get_next_time(cron)
                await_time = next_job_time - float(round(time.time()))

            time.sleep(1)

    def _get_next_time(self, croniter_obj):
        next_job_time = croniter_obj.get_next()
        self._log_next_time(next_job_time)
        return next_job_time

    def _log_next_time(self, next_job_time):
        next_job_time_str = datetime.datetime.fromtimestamp(int(next_job_time)).strftime('%d.%m.%Y %H:%M:%S')
        self._logger.debug("Next job: {}".format(next_job_time_str))
