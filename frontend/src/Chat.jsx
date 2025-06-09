import React, { useState, useRef, useEffect } from "react";
import {
   Send,
   Paperclip,
   Link,
   User,
   Lock,
   Mail,
   MessageCircle,
   Upload,
   X,
   Plus,
   LogOut,
} from "lucide-react";
import toast from "react-hot-toast";

const ChatbotApp = () => {
   const [currentPage, setCurrentPage] = useState("login");
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
   const [user, setUser] = useState(null);
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

      fetch("http://localhost:8000/chat", {
         method: "POST",
         headers: {
            "Content-Type": "application/json",
         },
         body: JSON.stringify(newMessageSend),
      })
         .then((res) => {
            return res.json();
         })
         .then((res) => {
            if (res.success) {
               toast.success("Logged in successfully");
            }
         })
         .catch((err) => {
            console.log(err);
            toast.error("Invalid email or password");
         });

      // Simulate bot response
      setTimeout(() => {
         const botResponse = {
            id: Date.now() + 1,
            text: "I've received your message. How else can I assist you?",
            sender: "bot",
            timestamp: new Date(),
         };
         setMessages((prev) => [...prev, botResponse]);
      }, 1000);
   };

   const handleFileUpload = (event) => {
      const files = Array.from(event.target.files);
      const newFiles = files.map((file) => ({
         id: Date.now() + Math.random(),
         name: file.name,
         size: file.size,
         type: "file",
      }));
      setUploadedFiles((prev) => [...prev, ...newFiles]);
      setShowUploadMenu(false);
   };

   const handleLinkUpload = () => {
      const url = prompt("Enter URL:");
      if (url) {
         const linkFile = {
            id: Date.now(),
            name: url,
            type: "link",
         };
         setUploadedFiles((prev) => [...prev, linkFile]);
      }
      setShowUploadMenu(false);
   };

   const removeUploadedFile = (id) => {
      setUploadedFiles((prev) => prev.filter((file) => file.id !== id));
   };

   const handleLogin = async (email, password) => {
      fetch("http://localhost:8000/login", {
         method: "POST",
         headers: {
            "Content-Type": "application/json",
         },
         body: JSON.stringify({ email, password }),
      })
         .then((res) => {
            return res.json();
         })
         .then((res) => {
            if (res.success) {
               setUser({ email: res.data.email, name: res.data.name });
               setCurrentPage("chat");
               toast.success("Logged in successfully");
            }
         })
         .catch((err) => {
            console.log(err);
            toast.error("Invalid email or password");
         });
   };

   const handleRegister = async (email, password, name) => {
      fetch("http://localhost:8000/register", {
         method: "POST",
         headers: {
            "Content-Type": "application/json",
         },
         body: JSON.stringify({ email, password, name }),
      })
         .then((res) => {
            return res.json();
         })
         .then((res) => {
            if (res.success) {
               setUser({ email, name });
               setCurrentPage("login");
               toast.success("Registered successfully");
            }
         })
         .catch((err) => {
            console.log(err);
            toast.error("Invalid email or password");
         });
   };

   const handleLogout = () => {
      fetch("http://localhost:8000/logout", {
         method: "POST",
         headers: {
            "Content-Type": "application/json",
         },
      })
         .then((res) => {
            return res.json();
         })
         .then((res) => {
            if (res.success) {
               setUser(null);
               setCurrentPage("login");
               setMessages([
                  {
                     id: 1,
                     text: "Hello! I'm your AI assistant. How can I help you today?",
                     sender: "bot",
                     timestamp: new Date(),
                  },
               ]);
            }
         })
         .catch((err) => {
            console.log(err);
            toast.error("Invalid email or password");
         });
   };

   const formatFileSize = (bytes) => {
      if (bytes === 0) return "0 Bytes";
      const k = 1024;
      const sizes = ["Bytes", "KB", "MB", "GB"];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
   };

   // Login Component
   const LoginPage = () => {
      const [email, setEmail] = useState("");
      const [password, setPassword] = useState("");

      return (
         <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">
               <div className="text-center mb-8">
                  <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                     <MessageCircle className="w-8 h-8 text-blue-600" />
                  </div>
                  <h1 className="text-3xl font-bold text-gray-800 mb-2">
                     Welcome Back
                  </h1>
                  <p className="text-gray-600">Sign in to continue chatting</p>
               </div>

               <div className="space-y-6">
                  <div>
                     <label className="block text-sm font-medium text-gray-700 mb-2">
                        Email
                     </label>
                     <div className="relative">
                        <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                        <input
                           type="email"
                           value={email}
                           onChange={(e) => setEmail(e.target.value)}
                           className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
                           placeholder="Enter your email"
                           required
                        />
                     </div>
                  </div>

                  <div>
                     <label className="block text-sm font-medium text-gray-700 mb-2">
                        Password
                     </label>
                     <div className="relative">
                        <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                        <input
                           type="password"
                           value={password}
                           onChange={(e) => setPassword(e.target.value)}
                           className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
                           placeholder="Enter your password"
                           required
                        />
                     </div>
                  </div>

                  <button
                     onClick={() => handleLogin(email, password)}
                     type="button"
                     className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
                  >
                     Sign In
                  </button>
               </div>

               <div className="mt-6 text-center">
                  <p className="text-gray-600">
                     Don't have an account?{" "}
                     <button
                        onClick={() => setCurrentPage("register")}
                        className="text-blue-600 hover:underline font-semibold"
                     >
                        Sign up
                     </button>
                  </p>
               </div>
            </div>
         </div>
      );
   };

   // Register Component
   const RegisterPage = () => {
      const [email, setEmail] = useState("");
      const [password, setPassword] = useState("");
      const [name, setName] = useState("");
      const [confirmPassword, setConfirmPassword] = useState("");

      return (
         <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">
               <div className="text-center mb-8">
                  <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                     <User className="w-8 h-8 text-green-600" />
                  </div>
                  <h1 className="text-3xl font-bold text-gray-800 mb-2">
                     Create Account
                  </h1>
                  <p className="text-gray-600">Join us and start chatting</p>
               </div>

               <div className="space-y-6">
                  <div>
                     <label className="block text-sm font-medium text-gray-700 mb-2">
                        Full Name
                     </label>
                     <div className="relative">
                        <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                        <input
                           type="text"
                           value={name}
                           onChange={(e) => setName(e.target.value)}
                           className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition-all"
                           placeholder="Enter your full name"
                           required
                        />
                     </div>
                  </div>

                  <div>
                     <label className="block text-sm font-medium text-gray-700 mb-2">
                        Email
                     </label>
                     <div className="relative">
                        <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                        <input
                           type="email"
                           value={email}
                           onChange={(e) => setEmail(e.target.value)}
                           className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition-all"
                           placeholder="Enter your email"
                           required
                        />
                     </div>
                  </div>

                  <div>
                     <label className="block text-sm font-medium text-gray-700 mb-2">
                        Password
                     </label>
                     <div className="relative">
                        <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                        <input
                           type="password"
                           value={password}
                           onChange={(e) => setPassword(e.target.value)}
                           className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition-all"
                           placeholder="Create a password"
                           required
                        />
                     </div>
                  </div>

                  <div>
                     <label className="block text-sm font-medium text-gray-700 mb-2">
                        Confirm Password
                     </label>
                     <div className="relative">
                        <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                        <input
                           type="password"
                           value={confirmPassword}
                           onChange={(e) => setConfirmPassword(e.target.value)}
                           className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition-all"
                           placeholder="Confirm your password"
                           required
                        />
                     </div>
                  </div>

                  <button
                     onClick={() => {
                        if (password === confirmPassword) {
                           handleRegister(email, password, name);
                        } else {
                           alert("Passwords do not match");
                        }
                     }}
                     type="button"
                     className="w-full bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors"
                  >
                     Create Account
                  </button>
               </div>

               <div className="mt-6 text-center">
                  <p className="text-gray-600">
                     Already have an account?{" "}
                     <button
                        onClick={() => setCurrentPage("login")}
                        className="text-green-600 hover:underline font-semibold"
                     >
                        Sign in
                     </button>
                  </p>
               </div>
            </div>
         </div>
      );
   };

   // Chat Component
   const ChatPage = () => (
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
               <span className="text-sm text-gray-600">
                  Welcome, {user?.name}
               </span>
               <button
                  onClick={handleLogout}
                  className="flex items-center space-x-1 text-gray-500 hover:text-red-600 transition-colors"
               >
                  <LogOut className="w-4 h-4" />
                  <span className="text-sm">Logout</span>
               </button>
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
                           message.sender === "user"
                              ? "text-blue-100"
                              : "text-gray-500"
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
            <div ref={messagesEndRef} />
         </div>

         {/* Upload Preview */}
         {uploadedFiles.length > 0 && (
            <div className="px-6 py-2 bg-gray-100 border-t border-gray-200">
               <div className="flex flex-wrap gap-2">
                  {uploadedFiles.map((file) => (
                     <div
                        key={file.id}
                        className="flex items-center space-x-2 bg-white px-3 py-2 rounded-lg border text-sm"
                     >
                        {file.type === "link" ? (
                           <Link className="w-4 h-4 text-blue-500" />
                        ) : (
                           <Upload className="w-4 h-4 text-green-500" />
                        )}
                        <span className="truncate max-w-32">{file.name}</span>
                        {file.size && (
                           <span className="text-gray-500">
                              ({formatFileSize(file.size)})
                           </span>
                        )}
                        <button
                           onClick={() => removeUploadedFile(file.id)}
                           className="text-red-500 hover:text-red-700"
                        >
                           <X className="w-4 h-4" />
                        </button>
                     </div>
                  ))}
               </div>
            </div>
         )}

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
                     onChange={(e) => setInputText(e.target.value)}
                     onKeyPress={(e) =>
                        e.key === "Enter" && handleSendMessage()
                     }
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
            multiple
            onChange={handleFileUpload}
            className="hidden"
         />
      </div>
   );

   // Main App Render
   if (currentPage === "login") return <LoginPage />;
   if (currentPage === "register") return <RegisterPage />;
   if (currentPage === "chat") return <ChatPage />;
};

export default ChatbotApp;
