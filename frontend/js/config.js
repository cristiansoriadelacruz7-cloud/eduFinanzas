/* ============================================================
   EduFinanzas - Configuración
   ============================================================ */

window.EF_CONFIG = {
    // El CLIENT ID de Google se obtiene automáticamente del backend
    // (GET /api/auth/google/config). Solo rellénalo aquí si quieres
    // forzar uno distinto en local:
    googleClientId: "",

    // Redirección tras login/registro exitoso
    redireccionDespuesAuth: "dashboard.html"
};