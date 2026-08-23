/* ============================================================
   EduFinanzas - Núcleo del frontend
   Conecta con el backend Flask (/api/...) usando fetch + cookies.
   ============================================================ */
(function () {
    'use strict';

    /* ---------- Cliente API ---------- */
    async function api(ruta, opciones = {}) {
        const config = {
            method: opciones.metodo || 'GET',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin'
        };
        if (opciones.datos !== undefined) config.body = JSON.stringify(opciones.datos);

        let respuesta;
        try {
            respuesta = await fetch(ruta, config);
        } catch {
            throw { codigo: 'sin_conexion', mensaje: 'No hay conexión con el servidor' };
        }

        let datos = null;
        try { datos = await respuesta.json(); } catch { /* respuesta vacía */ }

        if (!respuesta.ok || (datos && datos.ok === false)) {
            const codigo = (datos && datos.error) || 'http_' + respuesta.status;
            throw {
                codigo,
                estado: respuesta.status,
                mensaje: (datos && datos.error) || ('Error HTTP ' + respuesta.status)
            };
        }
        return datos;
    }

    /* ---------- Sesión (vía API, cookie de Flask) ---------- */
    async function iniciarSesion(correo, contrasena) {
        const r = await api('/api/login', { metodo: 'POST', datos: { correo, contrasena } });
        return r.usuario;
    }

    async function registrar(datos) {
        const r = await api('/api/registro', { metodo: 'POST', datos });
        return r.usuario;
    }

    async function cerrarSesion() {
        try { await api('/api/logout', { metodo: 'POST' }); } catch { /* ignorar */ }
    }

    async function usuarioActual() {
        try {
            const r = await api('/api/sesion');
            return r.usuario;
        } catch {
            return null;
        }
    }

    /* ---------- Validaciones locales ---------- */
    function esCorreoValido(correo) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correo);
    }
    function validarContrasena(pass) {
        if (pass.length < 6) return { valido: false, mensaje: 'Mínimo 6 caracteres' };
        let score = 0;
        if (/[a-z]/.test(pass)) score++;
        if (/[A-Z]/.test(pass)) score++;
        if (/[0-9]/.test(pass)) score++;
        if (/[^a-zA-Z0-9]/.test(pass)) score++;
        let nivel = 'debil';
        if (score >= 3) nivel = 'fuerte';
        else if (score >= 2) nivel = 'media';
        return { valido: true, nivel, score };
    }

    /* ---------- DNI (simulación local determinista, sin API externa) ---------- */
    function consultarDni(numero) {
        const dni = String(numero).trim();
        if (!/^\d{8}$/.test(dni)) throw { codigo: 'formato', mensaje: 'El DNI debe tener 8 dígitos' };

        const ultimo = parseInt(dni.slice(-1), 10);
        const nombres = ultimo % 2 === 0 ? 'Carlos Antonio' : 'Maria Fernanda';
        const paterno = ultimo % 2 === 0 ? 'Gomez' : 'Ruiz';

        const prefijo = parseInt(dni.slice(0, 3), 10) % 100;
        let materno = 'Perez';
        if (prefijo < 33) materno = 'Fernandez';
        else if (prefijo < 66) materno = 'Lopez';

        return normalizarRespuestaDni({ nombres, apellidoPaterno: paterno, apellidoMaterno: materno });
    }

    function normalizarRespuestaDni(d) {
        const nombres = (d.nombres || '').trim();
        const apellidos = [(d.apellidoPaterno || '').trim(), (d.apellidoMaterno || '').trim()]
            .filter(Boolean).join(' ');
        return { nombres: capitalizar(nombres), apellidos: capitalizar(apellidos) };
    }

    function capitalizar(str) {
        return str.toLowerCase().replace(/\b\w/g, c => c.toUpperCase());
    }

    /* ---------- Formato ---------- */
    const _fmt = new Intl.NumberFormat('es-PE', { style: 'currency', currency: 'PEN' });
    function moneda(n) { return _fmt.format(Number(n) || 0); }

    /* ---------- UI Helpers ---------- */
    function toast(mensaje, tipo = 'info') {
        let contenedor = document.querySelector('.toast-contenedor');
        if (!contenedor) {
            contenedor = document.createElement('div');
            contenedor.className = 'toast-contenedor';
            document.body.appendChild(contenedor);
        }
        const el = document.createElement('div');
        el.className = `toast toast--${tipo}`;
        const iconos = { exito: '✅', error: '❌', advertencia: '⚠️', info: 'ℹ️' };
        el.innerHTML = `<span>${iconos[tipo] || iconos.info}</span><span>${mensaje}</span>`;
        contenedor.appendChild(el);
        setTimeout(() => { el.remove(); }, 4000);
    }

    function mostrarError(campoId, mensaje) {
        const input = document.getElementById(campoId);
        const contenedor = input?.closest('.campo');
        if (!contenedor) return;
        input.classList.add('invalido');
        let errorEl = contenedor.querySelector('.campo__error');
        if (!errorEl) {
            errorEl = document.createElement('div');
            errorEl.className = 'campo__error';
            errorEl.setAttribute('role', 'alert');
            contenedor.appendChild(errorEl);
        }
        errorEl.textContent = '⚠ ' + mensaje;
    }

    function limpiarError(campoId) {
        const input = document.getElementById(campoId);
        const contenedor = input?.closest('.campo');
        if (!contenedor) return;
        input.classList.remove('invalido');
        const errorEl = contenedor.querySelector('.campo__error');
        if (errorEl) errorEl.remove();
    }

    function setCargando(btn, cargando) {
        if (cargando) btn.classList.add('cargando'); else btn.classList.remove('cargando');
        btn.disabled = cargando;
    }

    function redireccionar(url) { window.location.href = url; }

    /* Placeholder visual para "Continuar con Google" */
    function marcadorGoogle(contenedorId) {
        const c = document.getElementById(contenedorId);
        if (!c) return;
        c.innerHTML = `
            <button type="button" class="btn btn--secundario auth__google__btn" disabled
                    title="Disponible próximamente">
                Continuar con Google (próximamente)
            </button>`;
    }

    /* ---------- API pública ---------- */
    window.EF = {
        api,
        sesion: { iniciarSesion, registrar, cerrarSesion, usuarioActual },
        validacion: { esCorreoValido, validarContrasena },
        dni: { consultar: consultarDni },
        formato: { moneda },
        ui: { toast, mostrarError, limpiarError, setCargando, redireccionar, marcadorGoogle }
    };
})();