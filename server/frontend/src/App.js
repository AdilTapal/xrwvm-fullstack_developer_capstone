import LoginPanel from "./components/Login/Login.jsx"
import Register from "./components/Register/Register.jsx"
import Dealers from "./components/Dealers/Dealers.jsx"
import Dealer from "./components/Dealers/Dealer.jsx"
import PostReview from "./components/Dealers/PostReview.jsx"
import { Routes, Route } from "react-router-dom";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Dealers />} />
      <Route path="/dealers" element={<Dealers />} />
      <Route path="/dealer-details/:id" element={<Dealer />} />
      <Route path="/post-review/:id" element={<PostReview />} />
      <Route path="/login" element={<LoginPanel />} />
      <Route path="/register" element={<Register />} />
    </Routes>
  );
}
export default App;
