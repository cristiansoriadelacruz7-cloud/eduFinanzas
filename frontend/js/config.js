/* ============================================================
   EduFinanzas - Configuración (modo ficticio)
   ============================================================ */

window.EF_CONFIG = {
    // Modo: 'ficticio' - todos los datos son simulados localmente
    // Sin APIs externas: DNI, Google, etc.
    // Perfecto para demo/local sin necesidad de tokens ni servidores
    modo: 'ficticio',

    // Estos valores son irrelevantes en modo ficticio
    dniApiToken: "",
    googleClientId: "",

    // Redirección tras login/registro exitoso
    redireccionDespuesAuth: "dashboard.html"
};