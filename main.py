import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from google import genai

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# জেমিনি ক্লায়েন্ট ইনিশিয়ালাইজ করা
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


class CommandRequest(BaseModel):
    command: str

# রুট ইউআরএল-এ ভিজিট করলেই সুন্দর জারভিস ইন্টারফেস ওপেন হবে
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html lang="bn">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>JARVIS - AI Assistant</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #0d1117; color: #c9d1d9; text-align: center; padding-top: 40px; margin: 0; }
            .container { max-width: 90%; width: 450px; margin: auto; background: #161b22; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,255,255,0.2); }
            h1 { color: #58a6ff; font-size: 24px; margin-bottom: 5px; }
            p { color: #8b949e; font-size: 14px; }
            input { width: 90%; padding: 12px; border-radius: 6px; border: 1px solid #30363d; background: #0d1117; color: white; font-size: 16px; margin-top: 15px; margin-bottom: 15px; outline: none; }
            button { background-color: #238636; color: white; border: none; padding: 12px 20px; font-size: 16px; border-radius: 6px; cursor: pointer; width: 95%; font-weight: bold; }
            button:hover { background-color: #2ea043; }
            #output { margin-top: 20px; text-align: left; background: #010409; padding: 15px; border-radius: 6px; min-height: 100px; border: 1px solid #30363d; font-size: 15px; line-height: 1.5; word-break: break-word; color: #f0f6fc; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>JARVIS SYSTEM</h1>
            <p>আপনার ব্যক্তিগত এআই অ্যাসিস্ট্যান্ট</p>
            <input type="text" id="userInput" placeholder="এখানে আপনার কমান্ড লিখুন..." onkeypress="if(event.key === 'Enter') sendCommand()">
            <br>
            <button onclick="sendCommand()">കমান্ড পাঠান</button>
            
            <h3>রেসপন্স:</h3>
            <div id="output">সিস্টেম প্রস্তুত...</div>
        </div>

        <script>
            async function sendCommand() {
                const commandText = document.getElementById('userInput').value;
                if (!commandText) return;

                document.getElementById('output').innerText = "প্রসেস হচ্ছে...";

                try {
                    const response = await fetch('/api/command', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ command: commandText })
                    });
                    const data = await response.json();
                    document.getElementById('output').innerText = data.response;
                    
                    // ভয়েসে উত্তর শুনিয়ে দেওয়া
                    let speech = new SpeechSynthesisUtterance(data.response);
                    speech.lang = 'bn-BD';
                    window.speechSynthesis.speak(speech);

                } catch (err) {
                    document.getElementById('output').innerText = "ত্রুটি ঘটেছে: " + err;
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/api/command")
async def process_command(req: CommandRequest):
    try:
        prompt = (
            "তুমি জারভিস (Jarvis), আয়রনম্যানের অত্যন্ত বুদ্ধিমান ও বিশ্বস্ত এআই অ্যাসিস্ট্যান্ট। "
            "ইউজারের কমান্ড বা প্রশ্নের অত্যন্ত সংক্ষিপ্ত, পেশাদার এবং কাজের উপযোগী উত্তর দাও। "
            f"ইউজারের কমান্ড: {req.command}"
        )
        
        response = client.models.generate_content(
    model='gemini-2.0-flash',
    contents=prompt,
)

return {"status": "success", "response": response.text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 7860)))
