import asyncio
import json
import threading
from PyQt5.QtCore import QSettings
import websockets
import traceback

from constants.stock_settings import FRAVEL_TRADER_SETTING_PATH, RESPONSE_DICT, TR_DICT

class WebSocketWorker(threading.Thread):
    def __init__(self, token, sendQ, recvQ, windowQ):
        super().__init__(daemon=True)
        self.settings = QSettings(FRAVEL_TRADER_SETTING_PATH, QSettings.IniFormat)

        if self.settings.value("trading_type", "mock") == "mock":
            self.socket_url = "wss://mockapi.kiwoom.com:10000/api/dostk/websocket"
            print(f"WebSocketWorker 모의투자 연결 : {self.socket_url}")
        else:
            self.socket_url = "wss://api.kiwoom.com:10000/api/dostk/websocket"
            print(f"WebSocketWorker 실전 연결 : {self.socket_url}")
            
        self.token = token
        self.sendQ = sendQ
        self.recvQ = recvQ
        self.windowQ = windowQ

        self.loop = None
        self.websocket = None
        self.running = True
        
        self.current_condition_seq = None # 현재 조건식 일련번호

    # ===============================
    # Thread 진입점
    # ===============================
    def run(self):
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self._main())
        except Exception:
            self._log("WebSocketWorker fatal error")
            self._log(traceback.format_exc())
        finally:
            if self.loop:
                self.loop.close()
            self._log("WebSocketWorker 종료")

    # ===============================
    # 메인 asyncio 루프
    # ===============================
    async def _main(self):
        self._log("WS 연결 시도")
        async with websockets.connect(self.socket_url) as ws:
            self.websocket = ws

            await self._login()
            await asyncio.gather(
                self._recv_loop(),
                self._send_loop(),
            )

    # ===============================
    # 로그인
    # ===============================
    async def _login(self):
        msg = {
            "trnm": "LOGIN",
            "token": self.token,
        }
        await self.websocket.send(json.dumps(msg))
        
        if self.settings.value("trading_type", "mock") == "mock":
            self._log(f"WS 모의투자 로그인 요청 : {json.dumps(msg)}")
        else:
            self._log(f"WS 실전 로그인 요청 : {json.dumps(msg)}")
        
        # 로그인 응답 대기
        raw = await self.websocket.recv()
        data = json.loads(raw)

        if data.get("return_code") != 0:
            raise RuntimeError(f"LOGIN 실패: {data}")
        
        if self.settings.value("trading_type", "mock") == "mock":
            self._log(f"WS 모의투자 로그인 성공 : {json.dumps(data)}")
        else:
            self._log(f"WS 실전 로그인 성공 : {json.dumps(data)}")

    # ===============================
    # 수신 루프 (키움 서버에서 오는 메시지)
    # ===============================
    async def _recv_loop(self):
        while self.running:
            try:
                raw = await self.websocket.recv()
                data = json.loads(raw)

                trnm = data.get("trnm")

                self._log(f"WS 수신 - {trnm}")

                if trnm == "PING":
                    await self.websocket.send(raw)
                    continue
                
                print(f"WebSocket 수신 - {data}")
                self.recvQ.put(data)

            except Exception:
                self._log("WebSocket recv error")
                self._log(traceback.format_exc())
                break

    # ===============================
    # 송신 루프 (키움 서버에 요청)
    # ===============================
    async def _send_loop(self):
        while self.running:
            try:
                msg = await self.loop.run_in_executor(None, self.sendQ.get)
                
                if msg.get("trnm") == TR_DICT["조건검색 요청 실시간"]: # CNSRREQ
                    if self.current_condition_seq is not None:
                        # 기존 조건식 해제
                        cmd = {
                            "trnm": TR_DICT["조건검색 실시간 해제"], # CNSRREQ
                            "seq" : self.current_condition_seq, # 조건검색식 일련번호
                            "search_type" : "0", # 0: 조건검색식 해제
                            "stex_tp" : "K" # K:KRX
                        }
                        await self.websocket.send(json.dumps(cmd)) # 해제 요청
                    self.current_condition_seq = msg.get("seq") # 현재 조건식 일련번호 업데이트
                
                await self.websocket.send(json.dumps(msg))

                self._log(f"WS 송신 - {json.dumps(msg)}")
                
            except Exception:
                self._log("WebSocket send error")
                self._log(traceback.format_exc())
                break

    # ===============================
    # 외부 종료 요청
    # ===============================
    def stop(self):
        self.running = False
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)

    # ===============================
    # 로그
    # ===============================
    def _log(self, msg):
        if self.windowQ:
            self.windowQ.put([RESPONSE_DICT["로그텍스트"], msg])