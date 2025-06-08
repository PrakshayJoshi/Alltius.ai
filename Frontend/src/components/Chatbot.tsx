
import { useState, useRef, useEffect } from "react";
import { Send, Bot, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import ChatMessage from "./ChatMessage";
import TypingIndicator from "./TypingIndicator";

interface Message {
  id: string;
  text: string;
  isBot: boolean;
  timestamp: Date;
}

const Chatbot = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      text: "Hello! I'm your AI assistant. How can I help you today?",
      isBot: true,
      timestamp: new Date(),
    },
  ]);
  const [inputText, setInputText] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  // const simulateAPICall = async (userMessage: string): Promise<string> => {
  //   // Simulate API delay
  //   await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));
    
  //   // Mock responses - replace this with actual FastAPI integration
  //   const responses = [
  //     "That's an interesting question! Let me think about that for you.",
  //     "I understand what you're asking. Here's what I think about that topic.",
  //     "Thanks for sharing that with me. I'd be happy to help you with this.",
  //     "That's a great point! Let me provide you with some insights on that.",
  //     "I see what you mean. Here's my perspective on what you've asked.",
  //   ];
    
  //   return responses[Math.floor(Math.random() * responses.length)];
  // };
  
  const handleSendMessage = async () => {
  if (!inputText.trim()) return;

  const userMessage: Message = {
    id: Date.now().toString(),
    text: inputText,
    isBot: false,
    timestamp: new Date(),
  };

  setMessages((prev) => [...prev, userMessage]);
  setInputText("");
  setIsTyping(true);

  try {
    const response = await fetch("http://127.0.0.1:8001/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query: inputText }),
    });

    if (!response.ok) {
      throw new Error("Failed to fetch response from server");
    }

    const data = await response.json();

    const botMessage: Message = {
      id: (Date.now() + 1).toString(),
      text: data.answer,
      isBot: true,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, botMessage]);
  } catch (error) {
    console.error("Error calling API:", error);
    const errorMessage: Message = {
      id: (Date.now() + 1).toString(),
      text: "Sorry, I'm having trouble connecting right now. Please try again.",
      isBot: true,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, errorMessage]);
  } finally {
    setIsTyping(false);
  }
};

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen p-4">
      <div className="w-full max-w-4xl h-[80vh] bg-white/70 backdrop-blur-sm rounded-3xl shadow-2xl border border-white/20 flex flex-col animate-fade-in">
        {/* Header */}
        <div className="flex items-center gap-3 p-6 border-b border-gray-200/50 bg-gradient-to-r from-indigo-500/10 to-purple-500/10 rounded-t-3xl">
          <div className="flex items-center justify-center w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full animate-scale-in">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
              AI Assistant
            </h1>
            <p className="text-sm text-gray-600">Always here to help</p>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((message, index) => (
            <ChatMessage 
              key={message.id} 
              message={message} 
              animationDelay={index * 100}
            />
          ))}
          {isTyping && <TypingIndicator />}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-6 border-t border-gray-200/50 bg-gradient-to-r from-gray-50/50 to-white/50 rounded-b-3xl">
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <Input
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message here..."
                className="pr-12 py-3 rounded-2xl border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200 text-base"
                disabled={isTyping}
              />
            </div>
            <Button
              onClick={handleSendMessage}
              disabled={!inputText.trim() || isTyping}
              className="bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white rounded-2xl px-6 py-3 transition-all duration-200 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="w-5 h-5" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;
