import { useState, useContext } from "react";
import { AuthContext } from "../auth/AuthContext";

export default function Dashboard() {
  const { token } = useContext(AuthContext);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const send = async () => {
    const response = await fetch(
      `${import.meta.env.VITE_API_URL}/chat-stream`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, message: input })
      }
    );

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    let assistantText = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      assistantText += chunk;

      setMessages(prev => [
        ...prev.filter(m => m.role !== "streaming"),
        { role: "streaming", content: assistantText }
      ]);
    }

    setMessages(prev => [
      ...prev.filter(m => m.role !== "streaming"),
      { role: "assistant", content: assistantText }
    ]);

    setInput("");
  };

  return (
    <div className="min-h-screen bg-black text-white flex flex-col justify-center items-center p-6">
      <div className="w-full max-w-3xl space-y-4">
        {messages.map((m, i) => (
          <div key={i} className="whitespace-pre-wrap">
            {m.content}
          </div>
        ))}

        <div className="flex mt-6">
          <input
            className="flex-1 bg-gray-800 p-3 rounded-l"
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button
            onClick={send}
            className="bg-blue-600 px-6 rounded-r"
          >
            ⌲
          </button>
        </div>
      </div>
    </div>
  );
}