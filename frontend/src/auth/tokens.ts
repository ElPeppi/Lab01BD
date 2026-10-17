const ACCESS = "access_token";
const REFRESH = "refresh_token";

export const tokens = {

    getAccess: () => localStorage.getItem(ACCESS),
    getRefresh: () => localStorage.getItem(REFRESH),
    set: (access: string, refresh?: string) => {
        localStorage.setItem(ACCESS, access);

        if (refresh) localStorage.setItem(REFRESH, refresh);

    },
    clear: () => {
        localStorage.removeItem(ACCESS);
        localStorage.removeItem(REFRESH);
        localStorage.removeItem("perfil");
    },
};