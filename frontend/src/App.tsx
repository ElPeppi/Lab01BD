import { lazy } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import RutaProtegida from "./auth/RutaProtegida";
import Login from "./pages/login/Login";

// Cada pantalla se descarga solo cuando se abre (code splitting): el login carga más rápido
// y un estudiante nunca descarga las pantallas del personal.
const Catalogo = lazy(() => import("./pages/catalogo/Catalogo"));
const Prestamos = lazy(() => import("./pages/prestamos/Prestamos"));
const Dashboard = lazy(() => import("./pages/dashboard/Dashboard"));
const Ejemplares = lazy(() => import("./pages/ejemplares/Ejemplares"));
const Devoluciones = lazy(() => import("./pages/devoluciones/Devoluciones"));

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
              <Route path="/ejemplares" element={<Ejemplares />} />
              <Route path="/devoluciones" element={<Devoluciones />} />
            </Route>
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}