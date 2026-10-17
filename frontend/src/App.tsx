import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import RutaProtegida from "./auth/RutaProtegida";
import Login from "./pages/login/Login";
import Catalogo from "./pages/catalogo/Catalogo";
import Prestamos from "./pages/prestamos/Prestamos";
import Dashboard from "./pages/dashboard/Dashboard";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<Login />} />

        <Route element={<RutaProtegida />}>
          <Route element={<Layout />}>
            <Route path="/catalogo" element={<Catalogo />} />
            <Route path="/prestamos" element={<Prestamos />} />
            <Route element={<RutaProtegida tipos={["empleado"]} />}>
              <Route path="/dashboard" element={<Dashboard />} />
            </Route>
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}