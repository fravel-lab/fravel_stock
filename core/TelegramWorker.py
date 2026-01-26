import asyncio
import time
import telegram
import sys

class TelegramWorker:

    # TODO 2024-11-26 Fravel Stock 텔레그램 봇
    def __init__(self, qlist):
        self.eventQ = qlist[0]
        self.windowQ = qlist[1]
        self.settingsQ = qlist[2]
        self.teleQ = qlist[3]

        self.token = "7468273764:AAGLOPP9mHSTlGYbkJ2Z1rYTvSyO_PlcUaQ"
        self.bot = telegram.Bot(token=self.token)

        # TODO 2024-12-21 windows 환경에서는 WindowsSelectorEventLoopPolicy 사용
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        else:
            asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
            
        # ✅ 이벤트 루프를 딱 한 번 생성
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        self.EventLoop()

    def EventLoop(self):
        while True:
            if not self.teleQ.empty():
                data = self.teleQ.get()
                self.SendMsg(data)
            time.sleep(0.0001)

    def SendMsg(self, msg):
        # TODO 2024-11-26 추후 str, list, df 구분하여 메시지 발송해야함
        print(f"TelegramMsg: {msg}")
       # ✅ asyncio.run() 사용 금지
        self.loop.run_until_complete(
            self.bot.send_message(
                chat_id="1237532491",
                text=str(msg)
            )
        )
