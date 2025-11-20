from dotenv import load_dotenv
from livekit import agents
from livekit.agents import Agent, AgentSession
from livekit.agents.llm import LLM, ChatChunk, ChoiceDelta
from livekit.plugins import deepgram, silero, elevenlabs
import os
import asyncio
import websockets
from contextlib import asynccontextmanager

load_dotenv(".env")

# -----------------------------
# 🔹 Custom WebSocket-based LLM
# -----------------------------
class WebSocketLLM(LLM):
    def __init__(self, url: str):
        super().__init__()
        self.url = url

    @asynccontextmanager
    async def chat(self, chat_ctx, **kwargs):
        async def gen():
            try:
                # Get user message
                user_msg = ""
                # if hasattr(chat_ctx, 'messages') and chat_ctx.items:
                    # user_msg = chat_ctx.messages[-1].content
                all_messages = chat_ctx.items
                # if all_messages:
                mesg = all_messages[-1]
                user_msg = mesg.content

                if isinstance(user_msg, list):
                    user_msg = " ".join(str(part) for part in user_msg)
                
                user_msg = user_msg.strip() if user_msg else "Hi"
                print(f"[DEBUG] Sending to WebSocket: {user_msg}")

                # Get WebSocket response
                async with websockets.connect(self.url) as ws:
                    await ws.send(user_msg)
                    reply = await ws.recv()
                    print(f"[WebSocket] Reply: {reply}")

                    # ✅ SIMPLE: Just yield the whole response as one chunk
                    yield ChatChunk(
                        id="ws-chunk",
                        delta=ChoiceDelta(role="assistant", content=reply)
                    )
                    
            except Exception as e:
                print(f"[ERROR] {e}")
                import traceback
                traceback.print_exc()
                
        yield gen()


# -----------------------------
# 🔹 Assistant & Entry Point
# -----------------------------
class Assistant(Agent):
    def __init__(self):
        super().__init__(instructions="You are a helpful and friendly voice assistant.")


async def entrypoint(ctx: agents.JobContext):
    websocket_llm = WebSocketLLM(
        url=os.getenv("WS_SERVER_URL", "ws://127.0.0.1:8080/ws")
    )

    session = AgentSession(
        stt=deepgram.STT(model="nova-2", language="en"),
        llm=websocket_llm,
        tts=elevenlabs.TTS(
            **{
                k: v
                for k, v in {
                    "voice_id": os.getenv("ELEVENLABS_VOICE_ID"),
                    "model": os.getenv("ELEVENLABS_TTS_MODEL"),
                    "api_key": os.getenv("ELEVENLABS_API_KEY"),
                }.items()
                if v
            },
            streaming_latency=int(os.getenv("ELEVENLABS_STREAMING_LATENCY", "0")),
        ),
        vad=silero.VAD.load(),
    )

    await session.start(room=ctx.room, agent=Assistant())
    await session.say("Hi there! How can I help you today?")


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))