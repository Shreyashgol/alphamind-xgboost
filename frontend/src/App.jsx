import Dashboard from "./pages/Dashboard";
import Guide from "./pages/Guide";
import Navbar from "./components/Navbar";
import { Route, Routes } from "react-router-dom";

export default function App() {
  return (
    <div className="min-h-screen bg-transparent text-slate-100">
      <Navbar />
      <main className="mx-auto flex w-full max-w-7xl flex-col gap-6 px-4 py-8 sm:px-6 lg:px-8">
        <Routes>
          <Route element={<Dashboard />} path="/" />
          <Route element={<Guide />} path="/guide" />
        </Routes>
      </main>
    </div>
  );
}
