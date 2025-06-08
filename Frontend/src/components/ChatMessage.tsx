
import { Bot, User } from "lucide-react";

interface Message {
  id: string;
  text: string;
  isBot: boolean;
  timestamp: Date;
}

interface ChatMessageProps {
  message: Message;
  animationDelay?: number;
}

const ChatMessage = ({ message, animationDelay = 0 }: ChatMessageProps) => {
  return (
    <div
      className={`flex items-start gap-3 animate-fade-in ${
        message.isBot ? "flex-row" : "flex-row-reverse"
      }`}
      style={{ animationDelay: `${animationDelay}ms` }}
    >
      {/* Avatar */}
      <div
        className={`flex items-center justify-center w-10 h-10 rounded-full flex-shrink-0 animate-scale-in ${
          message.isBot
            ? "bg-gradient-to-br from-indigo-500 to-purple-600"
            : "bg-gradient-to-br from-emerald-500 to-teal-600"
        }`}
        style={{ animationDelay: `${animationDelay + 100}ms` }}
      >
        {message.isBot ? (
          <Bot className="w-5 h-5 text-white" />
        ) : (
          <User className="w-5 h-5 text-white" />
        )}
      </div>

      {/* Message Bubble */}
      <div
        className={`max-w-[70%] rounded-2xl px-4 py-3 shadow-sm animate-scale-in ${
          message.isBot
            ? "bg-white/80 text-gray-800 border border-gray-200/50"
            : "bg-gradient-to-r from-indigo-500 to-purple-600 text-white"
        }`}
        style={{ animationDelay: `${animationDelay + 200}ms` }}
      >
        <p className="text-sm leading-relaxed whitespace-pre-wrap">
          {message.text}
        </p>
        <div
          className={`text-xs mt-2 opacity-70 ${
            message.isBot ? "text-gray-500" : "text-white/80"
          }`}
        >
          {message.timestamp.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
