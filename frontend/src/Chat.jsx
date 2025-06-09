import React, { useState, useRef, useEffect } from "react";
import { Send, Paperclip, Link, MessageCircle, Upload, X } from "lucide-react";
import toast from "react-hot-toast";
import Logout from "./Logout";

const ChatbotApp = ({ setCurrentPage, setUser, user }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm your AI assistant. How can I help you today?",
      sender: "bot",
      timestamp: new Date(),
    },
  ]);
  const [inputText, setInputText] = useState("");
  const [doc_id, setDocId] = useState("");
  const [job_id, setJobId] = useState("");
  const [showUploadMenu, setShowUploadMenu] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = () => {
    if (!inputText.trim()) return;

    const newMessage = {
      text: inputText,
      sender: "user",
      timestamp: new Date(),
      files: uploadedFiles.length > 0 ? [...uploadedFiles] : null,
    };
    const newMessageSend = {
      message: inputText,
      doc_id: doc_id,
    };

    setMessages((prev) => [...prev, newMessage]);
    setInputText("");
    setUploadedFiles([]);

    let job_id_set = "";

    fetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(newMessageSend),
      credentials: "include",
    })
      .then((res) => {
        return res.json();
      })
      .then((res) => {
        setJobId(res?.job_id);
        job_id_set = res?.job_id;
      })
      .catch((err) => {
        console.log(err);
        toast.error("something went wrong");
      });

    // Simulate bot response
    let interval = setInterval(() => {
      fetch(`/status/${job_id_set}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
      })
        .then((res) => {
          return res.json();
        })
        .then((res) => {
          console.log(res);
          if (res?.status === "success") {
            if (res?.data.status === "completed") {
              clearInterval(interval);
              const botResponse = {
                id: Date.now() + 1,
                text: res?.data.response,
                sender: "bot",
                timestamp: new Date(),
              };
              setMessages((prev) => [...prev, botResponse]);
              setJobId("");
            }
          }
        })
        .catch((err) => {
          console.log(err);
          toast.error("something went wrong");
          clearInterval(interval);
        });
    }, 3000);
  };

  const handleFileUpload = (event) => {
    const files = Array.from(event.target.files);
    const newFiles = files.map((file) => ({
      id: Date.now() + Math.random(),
      name: file.name,
      size: file.size,
      type: "file",
    }));

    let f1 = files[0];

    const formData = new FormData();
    formData.append("file", f1);

    fetch("/upload", {
      method: "POST",
      body: formData,
      credentials: "include",
    })
      .then((res) => res.json())
      .then((res) => {
        console.log(res);
        setDocId(res?.job_id);
      })
      .catch((err) => {
        console.log(err);
        toast.error("something went wrong");
      });
    const botResponse = {
      id: Date.now() + 1,
      text: "processing file...",
      sender: "bot",
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, botResponse]);
    setShowUploadMenu(false);
  };

  const handleLinkUpload = () => {
    const url = prompt("Enter URL:");
    if (url) {
      fetch("/link", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: url }),
        credentials: "include",
      })
        .then((res) => res.json())
        .then((res) => {
          console.log(res);
          setDocId(res?.job_id);
        })
        .catch((err) => {
          console.log(err);
          toast.error("something went wrong");
        });
      const botResponse = {
        id: Date.now() + 1,
        text: "processing link...",
        sender: "bot",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, botResponse]);
    }
    setShowUploadMenu(false);
  };

  // Chat Component
  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="bg-blue-100 w-10 h-10 rounded-full flex items-center justify-center">
            <MessageCircle className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h1 className="text-xl font-semibold text-gray-800">
              AI Assistant
            </h1>
            <p className="text-sm text-gray-500">Always here to help</p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <span className="text-sm text-gray-600">Welcome, {user?.name}</span>
          <Logout
            setCurrentPage={setCurrentPage}
            setUser={setUser}
            setMessages={setMessages}
          />
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${
              message.sender === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl ${
                message.sender === "user"
                  ? "bg-blue-600 text-white"
                  : "bg-white text-gray-800 border border-gray-200"
              }`}
            >
              {message.files && (
                <div className="mb-2 space-y-1">
                  {message.files.map((file) => (
                    <div
                      key={file.id}
                      className="flex items-center space-x-2 text-xs opacity-75"
                    >
                      {file.type === "link" ? (
                        <Link className="w-3 h-3" />
                      ) : (
                        <Upload className="w-3 h-3" />
                      )}
                      <span className="truncate">{file.name}</span>
                    </div>
                  ))}
                </div>
              )}
              <p className="text-sm">{message.text}</p>
              <p
                className={`text-xs mt-1 ${
                  message.sender === "user" ? "text-blue-100" : "text-gray-500"
                }`}
              >
                {message.timestamp.toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </p>
            </div>
          </div>
        ))}
        {job_id != "" && (
          <div className={`flex justify-start`}>
            <div
              className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl bg-white text-gray-800 border border-gray-200`}
            >
              <p className="text-sm">processing...</p>
              <p className={`text-xs mt-1 text-gray-500`}>
                {new Date().toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </p>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-white border-t border-gray-200 px-6 py-4">
        <div className="flex items-center space-x-3">
          <div className="relative">
            <button
              onClick={() => setShowUploadMenu(!showUploadMenu)}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <Paperclip className="w-5 h-5" />
            </button>

            {showUploadMenu && (
              <div className="absolute bottom-full left-0 mb-2 bg-white border border-gray-200 rounded-lg shadow-lg p-2 min-w-40">
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="flex items-center space-x-2 w-full px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded"
                >
                  <Upload className="w-4 h-4" />
                  <span>Upload File</span>
                </button>
                <button
                  onClick={handleLinkUpload}
                  className="flex items-center space-x-2 w-full px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded"
                >
                  <Link className="w-4 h-4" />
                  <span>Add Link</span>
                </button>
              </div>
            )}
          </div>

          <div className="flex-1 relative">
            <input
              type="text"
              value={inputText}
              disabled={job_id != ""}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
              placeholder="Type your message..."
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none resize-none"
            />
          </div>

          <button
            onClick={handleSendMessage}
            disabled={!inputText.trim() && uploadedFiles.length === 0}
            className="p-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.doc,.docx,.txt"
        onChange={handleFileUpload}
        className="hidden"
      />
    </div>
  );
};

export default ChatbotApp;
