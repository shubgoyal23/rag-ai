import { useEffect, useState } from "react";
import LoginPage from "./Login";
import RegisterPage from "./Register";
import ChatPage from "./Chat";

function App() {
  const [currentPage, setCurrentPage] = useState("login");
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetch("/user", {
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
        if (res.success) {
          setUser(res.data);
          setCurrentPage("chat");
        }
      })
      .catch((err) => {
        console.log(err);
        toast.error("Invalid email or password");
      });
  }, []);
  if (currentPage === "login")
    return <LoginPage setCurrentPage={setCurrentPage} setUser={setUser} />;
  if (currentPage === "register")
    return <RegisterPage setCurrentPage={setCurrentPage} setUser={setUser} />;
  if (currentPage === "chat")
    return <ChatPage setCurrentPage={setCurrentPage} setUser={setUser} user={user} />;
}

export default App;
