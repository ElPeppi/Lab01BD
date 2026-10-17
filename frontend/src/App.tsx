import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Catalogo from "./pages/catalogo/Catalogo";
import Prestamos from "./pages/prestamos/Prestamos";
import Login from "./pages/login/Login";
import Dashboard from "./pages/dashboard/Dashboard";

export default function App() {

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />}/>

        <Route element={<Layout />}>
          <Route path="/catalogo" element={<Catalogo />} />
          <Route path="/prestamos" element={<Prestamos />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}