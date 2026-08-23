/* ============================================================
   EduFinanzas - Lógica de la página de Registro
   Envía los datos al backend Flask (/api/registro).
   ============================================================ */
(function () {
    'use strict';

    const form = document.getElementById('form-registro');
    const btnDni = document.getElementById('btn-buscar-dni');
    const inputDni = document.getElementById('dni');
    const inputNombres = document.getElementById('nombres');
    const inputApellidos = document.getElementById('apellidos');
    const inputCorreo = document.getElementById('correo');
    const inputContrasena = document.getElementById('contrasena');
    const inputConfirmar = document.getElementById('confirmar-contrasena');
    const chkTerminos = document.getElementById('terminos');
    const fortalezaEl = document.getElementById('fortaleza-contrasena');

    /* ---------- Fortaleza de contraseña ---------- */
    inputContrasena.addEventListener('input', () => {
        const r = EF.validacion.validarContrasena(inputContrasena.value);
        fortalezaEl.className = 'fortaleza';
        if (inputContrasena.value) fortalezaEl.classList.add(`fortaleza--${r.nivel}`);
    });

    /* ---------- Validación en tiempo real ---------- */
    [inputDni, inputNombres, inputApellidos, inputCorreo, inputContrasena, inputConfirmar].forEach(el => {
        el.addEventListener('input', () => EF.ui.limpiarError(el.id));
        el.addEventListener('blur', validarCampo);
    });

    function validarCampo(e) {
        const el = e.target;
        const val = el.value.trim();
        switch (el.id) {
            case 'dni':
                if (val && !/^\d{8}$/.test(val)) EF.ui.mostrarError(el.id, 'El DNI debe tener 8 dígitos');
                break;
            case 'correo':
                if (val && !EF.validacion.esCorreoValido(val)) EF.ui.mostrarError(el.id, 'Correo inválido');
                break;
            case 'contrasena': {
                if (!val) break;
                const r = EF.validacion.validarContrasena(val);
                if (!r.valido) EF.ui.mostrarError(el.id, r.mensaje);
                break;
            }
            case 'confirmar-contrasena':
                if (val && val !== inputContrasena.value) EF.ui.mostrarError(el.id, 'Las contraseñas no coinciden');
                break;
            case 'nombres':
            case 'apellidos':
                if (!val) EF.ui.mostrarError(el.id, 'Campo requerido');
                break;
        }
    }

    /* ---------- Buscar DNI (simulado localmente) ---------- */
    btnDni.addEventListener('click', () => {
        const dni = inputDni.value.trim();
        if (!/^\d{8}$/.test(dni)) {
            EF.ui.mostrarError('dni', 'Ingresa 8 dígitos');
            inputDni.focus();
            return;
        }
        EF.ui.limpiarError('dni');
        EF.ui.setCargando(btnDni, true);

        // Pequeña demora para simular la consulta
        setTimeout(() => {
            try {
                const datos = EF.dni.consultar(dni);
                inputNombres.value = datos.nombres || '';
                inputApellidos.value = datos.apellidos || '';
                EF.ui.toast('Datos autocompletados (modo demo)', 'info');
                inputCorreo.focus();
            } finally {
                EF.ui.setCargando(btnDni, false);
            }
        }, 400);
    });
    inputDni.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); btnDni.click(); } });

    /* ---------- Google: marcador informativo ---------- */
    EF.ui.marcadorGoogle('google-button');

    /* ---------- Envío del formulario → POST /api/registro ---------- */
    form.addEventListener('submit', async e => {
        e.preventDefault();
        let valido = true;

        [inputDni, inputNombres, inputApellidos, inputCorreo, inputContrasena, inputConfirmar].forEach(el => {
            validarCampo({ target: el });
            if (el.classList.contains('invalido')) valido = false;
        });

        // Requeridos vacíos sin blur previo
        if (!inputNombres.value.trim()) { EF.ui.mostrarError('nombres', 'Campo requerido'); valido = false; }
        if (!inputApellidos.value.trim()) { EF.ui.mostrarError('apellidos', 'Campo requerido'); valido = false; }
        if (!inputCorreo.value.trim()) { EF.ui.mostrarError('correo', 'Campo requerido'); valido = false; }
        if (!inputContrasena.value) { EF.ui.mostrarError('contrasena', 'Campo requerido'); valido = false; }
        if (inputConfirmar.value !== inputContrasena.value) { EF.ui.mostrarError('confirmar-contrasena', 'Las contraseñas no coinciden'); valido = false; }

        if (!chkTerminos.checked) {
            EF.ui.toast('Debes aceptar los términos y condiciones', 'advertencia');
            valido = false;
        }
        if (!valido) {
            EF.ui.toast('Corrige los errores antes de continuar', 'advertencia');
            return;
        }

        const btnSubmit = form.querySelector('button[type="submit"]');
        EF.ui.setCargando(btnSubmit, true);

        try {
            await EF.sesion.registrar({
                nombre: `${inputNombres.value.trim()} ${inputApellidos.value.trim()}`.trim(),
                correo: inputCorreo.value.trim().toLowerCase(),
                contrasena: inputContrasena.value,
                dni: inputDni.value.trim()
            });
            EF.ui.toast('¡Cuenta creada correctamente!', 'exito');
            setTimeout(() => EF.ui.redireccionar('dashboard.html'), 900);
        } catch (err) {
            EF.ui.setCargando(btnSubmit, false);
            if (err.codigo === 'correo_duplicado') {
                EF.ui.mostrarError('correo', 'Este correo ya está registrado');
                EF.ui.toast('El correo ya está en uso', 'error');
            } else {
                EF.ui.toast(err.mensaje || 'No se pudo crear la cuenta', 'error');
            }
        }
    });
})();