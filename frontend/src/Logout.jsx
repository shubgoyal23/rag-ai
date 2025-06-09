import { LogOut } from "lucide-react";
import toast from "react-hot-toast";

const Logout = ({ setCurrentPage, setUser, setMessages }) => {
  const handleLogout = () => {
    console.log("Logout");
    fetch("/logout", {
      method: "POST",
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
          setUser(null);
          setCurrentPage("login");
          setMessages([]);
        }
      })
      .catch((err) => {
        console.log(err);
        toast.error("something went wrong");
      });
  };

  return (
    <button
      onClick={handleLogout}
      className="flex items-center space-x-1 text-gray-500 hover:text-red-600 transition-colors cursor-pointer"
    >
      <LogOut className="w-4 h-4" />
      <span className="text-sm">Logout</span>
    </button>
  );
};

export default Logout;
