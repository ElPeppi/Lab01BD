import api from "../../api/client";

const { data } = await api.get("/api/catalogo/libros/");

export default function Login(){

    return(<>
        {console.log("API URL:", import.meta.env.VITE_API_URL)} 
        {console.log("API Data:", data)}  
    </>);
}