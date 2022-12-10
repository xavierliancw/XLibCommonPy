from time import time


class TimeoutTimerPassive:
    """Use this class to keep track of when things time out.
    For example, if you want to determine if some function has taken more than 5
    seconds, you'd keep polling an instance of this class. The appropriate function
    below will tell you if it's been more than 5 seconds.

    IMPORTANT:
    You have to poll the instance of this class to determine if a time out has occured.
    For example, keep asking the instance of this class every 1 second if a time out
    has occurred.
    In other words, this implementation does not automatically notify you in any way
    that your time out has occurred. Like, it doesn't use multithreading and/or an
    active timing mechanism."""

    def __init__(self, timeout_time_sec: int) -> None:
        if timeout_time_sec <= 0:
            raise RuntimeError(
                "Timeout limit cannot be "
                f"{'negative' if timeout_time_sec < 0 else 'zero'}."
            )
        self._timeout_time_sec = timeout_time_sec
        self._timestart_unixts = None

    def get_timeout_time_sec(self) -> int:
        return self._timeout_time_sec

    def is_active(self) -> bool:
        self._update_state()
        return self._timestart_unixts is not None

    def start_timer(self) -> None:
        if self.is_active():
            raise RuntimeError(
                "Can't start a timer that has already started. If you want to start ov"
                "er, reset this timer and start it after that."
            )
        self._timestart_unixts = time()

    def reset(self) -> None:
        self._timestart_unixts = None

    def timed_out(self, raise_on_timeout: bool = False) -> bool:
        if self._timestart_unixts is None:
            # Technically a timeout never occured if just initialized or reset
            return False
        # Calculate and remember here just in case state update wipes the starting time
        time_since_timeout = time() - self._calculate_timeout_time(
            self._timestart_unixts
        )
        self._update_state()
        if not self.is_active():
            if raise_on_timeout:
                raise RuntimeError(
                    f"Time out occurred {time_since_timeout} second(s) ago."
                )
            return True
        return False

    def _calculate_timeout_time(self, time_started_unixts: float) -> float:
        # Passing in parameter because the member variable can possibly be None (i.e
        # I'm shoving responsibility of None handling to the caller which is fine
        # because this is a private function)
        return time_started_unixts + self._timeout_time_sec

    def _update_state(self) -> None:
        if self._timestart_unixts is None or time() > self._calculate_timeout_time(
            self._timestart_unixts
        ):
            self.reset()
