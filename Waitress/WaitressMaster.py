class WaitressMaster:
    def __init__(self, max_waitress=3):
        self.followup_waitress = {}
        self.idle_waitress = max_waitress

    async def submit(self, request):
        waitress = None

        if request.message_id in self.followup_messages:
            waitress = self.followup_messages[request.message_id]
        elif self.idle_waitress > 0:
            self.idle_waitress -= 1
            waitress = Waitress()

        if waitress is None:
            return await None

        await waitress.pre_work.start()
        response = await waitress.start(request)

        if not response.is_completed():
            self.followup_waitress[response.followup_message_id] = waitress
            await waitress.post_work.start()
        else:
            del waitress
            self.idle_waitress += 1
