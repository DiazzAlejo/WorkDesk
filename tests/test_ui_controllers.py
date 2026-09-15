import unittest

from app.ui.hooks import PomodoroHook


class FakeScheduler:
    def __init__(self):
        self.next_id = 0
        self.callbacks = {}
        self.cancelled = []

    def after(self, _delay, callback):
        self.next_id += 1
        self.callbacks[self.next_id] = callback
        return self.next_id

    def after_cancel(self, job):
        self.cancelled.append(job)
        self.callbacks.pop(job, None)


class FakePomodoroService:
    def __init__(self):
        self.started = None
        self.paused = []
        self.completed = []
        self.reset_ids = []

    def start(self, duration_seconds, work_item_id):
        self.started = (duration_seconds, work_item_id)
        return type("Session", (), {"id": "session-1", "duration_seconds": duration_seconds})()

    def pause(self, session_id):
        self.paused.append(session_id)

    def resume(self, _session_id):
        pass

    def complete(self, session_id):
        self.completed.append(session_id)

    def reset(self, session_id):
        self.reset_ids.append(session_id)


class PomodoroControllerTests(unittest.TestCase):
    def test_start_pause_resume_and_reset_manage_scheduled_job(self):
        scheduler = FakeScheduler()
        service = FakePomodoroService()
        changes = []
        controller = PomodoroHook(scheduler, service, lambda state, remaining: changes.append((state, remaining)))

        controller.start(120, "work-1")
        self.assertEqual(service.started, (120, "work-1"))
        first_job = controller.job
        controller.pause()
        self.assertIn(first_job, scheduler.cancelled)
        controller.resume()
        controller.reset()
        self.assertEqual(service.reset_ids, ["session-1"])
        self.assertEqual(changes[0], ("running", 120))
        self.assertEqual(changes[-1], ("ready", 0))
        self.assertIsNone(controller.state.session_id)


if __name__ == "__main__":
    unittest.main()
