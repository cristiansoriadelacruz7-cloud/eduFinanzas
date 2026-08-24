/* ============================================================
   EduFinanzas - Dashboard · Tema oscuro "Deep Teal"
   Consume /api/dashboard y /api/reportes (sparklines)
   ============================================================ */
(function () {
    'use strict';

    const $ = id => document.getElementById(id);
    const COLOR_ACENTO = '#07b2af';
    const COLOR_TARJETA = '#0c232a';
    const COLOR_SUAVE = '#93abb3';

    /* ---------- Iconos de línea (estilo uniforme) ---------- */
    const svg = (path, sw = 1.8) =>
        `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${path}</svg>`;

    const ICONOS = {
        comida: svg('<circle cx="12" cy="13" r="8"/><path d="M12 9v4l2.5 2.5"/><path d="M9 2h6"/>'),
        transporte: svg('<rect x="4" y="4" width="16" height="12" rx="3"/><path d="M4 10h16"/><circle cx="8.5" cy="18" r="1.5"/><circle cx="15.5" cy="18" r="1.5"/>'),
        estudios: svg('<path d="M2 6s2.5-2 6-2 6 2 6 2v14s-2.5-2-6-2-6 2-6 2z"/><path d="M14 6s2.5-2 6-2"/><path d="M14 6v14"/>'),
        entretenimiento: svg('<rect x="3" y="5" width="18" height="14" rx="3"/><path d="M8 5v14M16 5v14M3 10h18M3 14h18"/>'),
        hogar: svg('<path d="M3 11l9-8 9 8"/><path d="M5 9v11h14V9"/>'),
        salud: svg('<path d="M12 21C7 16.5 3 13.2 3 8.9 3 6.2 5.2 4 7.9 4c1.7 0 3.2.8 4.1 2.1C12.9 4.8 14.4 4 16.1 4 18.8 4 21 6.2 21 8.9c0 4.3-4 7.6-9 12.1z"/>'),
        compras: svg('<path d="M6 7h12l-1.2 12.2a2 2 0 01-2 1.8H9.2a2 2 0 01-2-1.8z"/><path d="M9 10V6a3 3 0 016 0v4"/>'),
        ocio: svg('<circle cx="12" cy="12" r="9"/><path d="M12 8v4l2.5 2.5"/>'),
        dinero: svg('<rect x="2" y="6" width="20" height="12" rx="3"/><circle cx="12" cy="12" r="2.5"/><path d="M6 12h.01M18 12h.01"/>'),
        flechaIngreso: svg('<path d="M17 7L7 17"/><path d="M8 7h9v9"/>'),
        flechaGasto: svg('<path d="M7 7l10 10"/><path d="M17 8v9h-9"/>'),
        laptop: svg('<rect x="4" y="5" width="16" height="11" rx="2"/><path d="M2 19h20"/>'),
        bici: svg('<circle cx="5.5" cy="17.5" r="3.5"/><circle cx="18.5" cy="17.5" r="3.5"/><path d="M5.5 17.5L9 8h4l5.5 9.5M9 8L15 8"/>'),
        casa: svg('<path d="M3 11l9-8 9 8"/><path d="M5 9v11h14V9"/>'),
        carro: svg('<path d="M5 11l1.5-4.5A2 2 0 018.4 5h7.2a2 2 0 011.9 1.5L19 11"/><rect x="3" y="11" width="18" height="6" rx="2"/><circle cx="7.5" cy="17" r="1.5"/><circle cx="16.5" cy="17" r="1.5"/>'),
        viaje: svg('<path d="M17.8 19.2L16 11l3.5-3.5a2.1 2.1 0 00-3-3L13 8 4.8 6.2a.5.5 0 00-.5.8l4.2 4.2-2 3.4-2.3.6a.5.5 0 00-.2.9l2.4 2.4a.5.5 0 00.9-.2l.6-2.3 3.4-2 4.2 4.2a.5.5 0 00.8-.5z"/>'),
        meta: svg('<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>')
    };

    function iconoCategoria(nombre) {
        const n = (nombre || '').toLowerCase();
        if (/aliment|comida|almuerzo|desayuno|cena|snack/.test(n)) return ICONOS.comida;
        if (/transport|pasaje|bus|movilidad/.test(n)) return ICONOS.transporte;
        if (/estudi|libro|univers|curso|matric/.test(n)) return ICONOS.estudios;
        if (/entreten|cine|juego|pelicul|salida/.test(n)) return ICONOS.entretenimiento;
        if (/hogar|alquiler|renta|luz|agua/.test(n)) return ICONOS.hogar;
        if (/salud|farmacia|medic/.test(n)) return ICONOS.salud;
        if (/compra|ropa|tienda/.test(n)) return ICONOS.compras;
        if (/ocio|diversion/.test(n)) return ICONOS.ocio;
        if (/sueldo|beca|ingreso|pago|bono|venta/.test(n)) return ICONOS.dinero;
        return ICONOS.dinero;
    }

    function iconoMeta(nombre) {
        const n = (nombre || '').toLowerCase();
        if (/laptop|computadora|pc|notebook/.test(n)) return ICONOS.laptop;
        if (/bici|bicicleta/.test(n)) return ICONOS.bici;
        if (/casa|departamento|cuarto/.test(n)) return ICONOS.casa;
        if (/carro|auto|moto/.test(n)) return ICONOS.carro;
        if (/viaje|tour|vacacion/.test(n)) return ICONOS.viaje;
        return ICONOS.meta;
    }

    /* ---------- Saludo ---------- */
    function saludar(nombre) {
        const hora = new Date().getHours();
        let texto = 'Buenas noches';
        if (hora < 12) texto = 'Buenos días';
        else if (hora < 19) texto = 'Buenas tardes';
        const primerNombre = (nombre || '').split(' ')[0];
        $('saludo').textContent = `${texto}${primerNombre ? ', ' + primerNombre : ''} 👋`;
    }

    /* ---------- Sparklines ---------- */
    function renderSpark(canvasId, valores, color) {
        const canvas = $(canvasId);
        if (!canvas || typeof Chart === 'undefined' || valores.length < 2) return;
        const ctx = canvas.getContext('2d');
        const gradiente = ctx.createLinearGradient(0, 0, 0, 48);
        gradiente.addColorStop(0, color + '55');
        gradiente.addColorStop(1, color + '00');

        new Chart(canvas, {
            type: 'line',
            data: {
                labels: valores.map((_, i) => i),
                datasets: [{
                    data: valores,
                    borderColor: color,
                    backgroundColor: gradiente,
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: 0.45,
                    fill: true
                }]
            },
            options: {
                responsive: false,
                maintainAspectRatio: false,
                plugins: { legend: { display: false }, tooltip: { enabled: false } },
                scales: { x: { display: false }, y: { display: false } },
                animation: { duration: 600 }
            }
        });
    }

    /* ---------- Gráfico doughnut de gastos ---------- */
    function pintarDoughnut(categorias) {
        if (typeof Chart === 'undefined') return;
        Chart.defaults.font.family = "'Poppins', system-ui, sans-serif";
        Chart.defaults.color = COLOR_SUAVE;

        new Chart($('graficoGastos'), {
            type: 'doughnut',
            data: {
                labels: categorias.map(c => c.nombre),
                datasets: [{
                    data: categorias.map(c => c.monto),
                    backgroundColor: categorias.map(c => c.color || '#94A3B8'),
                    borderColor: COLOR_TARJETA,
                    borderWidth: 4,
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '72%',
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#11323c',
                        titleColor: '#fff',
                        bodyColor: '#e4edf4',
                        padding: 10,
                        cornerRadius: 10,
                        callbacks: {
                            label: ctx => {
                                const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                                const pct = total ? Math.round(ctx.parsed / total * 100) : 0;
                                return ` ${EF.formato.moneda(ctx.parsed)} (${pct}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    function pintarLeyenda(categorias) {
        const ul = $('leyendaGastos');
        ul.innerHTML = '';
        categorias.forEach(c => {
            const li = document.createElement('li');
            li.innerHTML =
                `<span class="leyenda__icono">${iconoCategoria(c.nombre)}</span>` +
                `<span class="leyenda__nombre">${c.nombre}</span>` +
                `<span class="leyenda__pct">${c.porcentaje}%</span>`;
            ul.appendChild(li);
        });
    }

    /* ---------- Metas ---------- */
    function pintarMetas(metas) {
        const ul = $('listaMetas');
        ul.innerHTML = '';
        if (!metas.length) {
            ul.innerHTML = `
                <li class="estado-vacio">
                    <div class="estado-vacio__icono" aria-hidden="true">🎯</div>
                    <p>Aún no tienes metas de ahorro.</p>
                </li>`;
            return;
        }
        metas.forEach(m => {
            const li = document.createElement('li');
            li.className = 'meta';
            li.dataset.id = m.id;
            const faltante = Math.max(m.monto_objetivo - m.monto_actual, 0);
            li.innerHTML = `
                <span class="meta__icono">${iconoMeta(m.nombre)}</span>
                <span class="meta__nombre">${m.nombre}</span>
                <div class="meta__barra barra"><div class="barra__fill" style="width:${m.progreso}%"></div></div>
                <span class="meta__pct">${m.progreso}%</span>
                <div class="meta__montos">
                    <span>${EF.formato.moneda(m.monto_actual)} / ${EF.formato.moneda(m.monto_objetivo)}</span>
                    <span>${faltante > 0 ? 'Faltan ' + EF.formato.moneda(faltante) : '¡Completada!'}</span>
                </div>
                <div class="meta-acciones">
                    <button type="button" data-accion="aportar">＋ Aportar</button>
                    <button type="button" data-accion="eliminar" title="Eliminar meta">Eliminar</button>
                </div>`;
            ul.appendChild(li);
        });
    }

    async function accionMeta(e) {
        const boton = e.target.closest('button[data-accion]');
        if (!boton) return;
        const id = boton.closest('.meta').dataset.id;
        if (boton.dataset.accion === 'aportar') {
            const monto = await EF.ui.pedirNumero('Aportar a la meta', '¿Cuánto deseas aportar? (S/)');
            if (monto === null) return;
            try {
                await EF.api(`/api/metas/${id}/aportar`, { metodo: 'PUT', datos: { monto } });
                EF.ui.toast('Aporte registrado 🎯', 'exito');
                inicializar();
            } catch (err) { EF.ui.toast(err.mensaje || 'No se pudo aportar', 'error'); }
        } else {
            const ok = await EF.ui.confirmar('Eliminar meta', 'Esta acción no se puede deshacer.');
            if (!ok) return;
            try {
                await EF.api(`/api/metas/${id}`, { metodo: 'DELETE' });
                EF.ui.toast('Meta eliminada', 'info');
                inicializar();
            } catch (err) { EF.ui.toast(err.mensaje || 'No se pudo eliminar', 'error'); }
        }
    }

    /* ---------- Últimos movimientos ---------- */
    const MOVS_POR_PAGINA = 4;
    let movsTodas = [];
    let paginaMovs = 0;

    function formatearFecha(iso) {
        try {
            return new Date(iso + 'T12:00:00').toLocaleDateString('es-PE', { day: '2-digit', month: 'short' });
        } catch { return iso; }
    }

    function pintarMovimientos(movimientos) {
        movsTodas = movimientos || [];
        paginaMovs = 0;
        pintarPaginaMovs();
    }

    function totalPaginasMovs() {
        return Math.max(1, Math.ceil(movsTodas.length / MOVS_POR_PAGINA));
    }

    function irAPagina(delta) {
        if (movsTodas.length <= MOVS_POR_PAGINA) return;
        const total = totalPaginasMovs();
        paginaMovs = (paginaMovs + delta + total) % total; // cicla entre páginas
        pintarPaginaMovs();
    }

    function pintarPaginaMovs() {
        const ol = $('listaMovimientos');
        const inicio = paginaMovs * MOVS_POR_PAGINA;
        const visibles = movsTodas.slice(inicio, inicio + MOVS_POR_PAGINA);

        ol.innerHTML = '';
        if (!visibles.length) {
            ol.innerHTML = '<li class="estado-vacio"><p>No hay movimientos todavía.</p></li>';
            pintarDots();
            return;
        }
        visibles.forEach(m => {
            const esIngreso = m.tipo === 'ingreso';
            const li = document.createElement('li');
            li.className = 'mov ' + (esIngreso ? 'mov--ingreso' : 'mov--gasto');
            li.dataset.id = m.id;
            li.dataset.tipo = m.tipo;
            const nombreCat = m.categoria || (esIngreso ? 'Ingreso' : 'Gasto');
            li.innerHTML = `
                <span class="mov__icono">${esIngreso ? ICONOS.flechaIngreso : iconoCategoria(nombreCat)}</span>
                <span class="mov__info">
                    <span class="mov__desc">${m.descripcion || nombreCat}</span>
                    <span class="mov__meta">${nombreCat} · ${formatearFecha(m.fecha)}</span>
                </span>
                <span class="mov__monto">${esIngreso ? '+' : '−'} ${EF.formato.moneda(m.monto)}</span>
                <button type="button" class="mov__borrar" data-accion="eliminar-mov"
                        title="Eliminar movimiento" aria-label="Eliminar ${m.descripcion || nombreCat}">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 7h16"/><path d="M10 11v6M14 11v6"/><path d="M6 7l1 13a2 2 0 002 2h6a2 2 0 002-2l1-13"/><path d="M9 7V5a2 2 0 012-2h2a2 2 0 012 2v2"/></svg>
                </button>`;
            ol.appendChild(li);
        });
        pintarDots();
    }

    function pintarDots() {
        const cont = $('pagDots');
        if (!cont) return;
        const total = movsTodas.length ? totalPaginasMovs() : 1;
        cont.classList.toggle('paginacion--oculta', total <= 1);

        cont.innerHTML = '';
        for (let i = 0; i < total; i++) {
            const dot = document.createElement('button');
            dot.type = 'button';
            dot.className = 'dot' + (i === paginaMovs ? ' dot--activo' : '');
            dot.setAttribute('aria-label', `Página ${i + 1} de ${total}`);
            dot.addEventListener('click', () => {
                paginaMovs = i;
                pintarPaginaMovs();
            });
            cont.appendChild(dot);
        }

        // Ocultar flechas si no hay nada que paginar
        const izq = $('flechaIzq'), der = $('flechaDer');
        const multiple = total > 1;
        if (izq) izq.style.display = multiple ? '' : 'none';
        if (der) der.style.display = multiple ? '' : 'none';
    }

    async function eliminarMovimiento(e) {
        const boton = e.target.closest('button[data-accion="eliminar-mov"]');
        if (!boton) return;
        const fila = boton.closest('.mov');
        const id = fila.dataset.id;
        const tipo = fila.dataset.tipo;
        const ok = await EF.ui.confirmar('Eliminar movimiento', 'Esta acción no se puede deshacer.');
        if (!ok) return;

        boton.disabled = true;
        try {
            await EF.api(tipo === 'ingreso' ? `/api/ingresos/${id}` : `/api/gastos/${id}`, { metodo: 'DELETE' });
            EF.ui.toast('Movimiento eliminado', 'info');
            inicializar();
        } catch (err) {
            boton.disabled = false;
            if (err.codigo === 'sin_sesion' || err.estado === 401) { window.location.href = 'login.html'; return; }
            EF.ui.toast(err.mensaje || 'No se pudo eliminar el movimiento', 'error');
        }
    }

    /* ---------- Presupuesto diario ---------- */
    function pintarPresupuesto(d) {
        $('cardPresupuesto').textContent = EF.formato.moneda(d.limite_diario);
        $('fuenteLimite').textContent = d.fuente_limite === 'personalizado'
            ? 'personalizado' : 'automático';

        // Línea de tiempo del mes
        const hoy = new Date();
        const diasDelMes = new Date(hoy.getFullYear(), hoy.getMonth() + 1, 0).getDate();
        $('diasRestantesHero').textContent = d.dias_restantes;
        $('diasRestantes').textContent = d.dias_restantes;
        $('diaActual').textContent = hoy.getDate();
        $('diasDelMes').textContent = `${diasDelMes} días`;
        $('barraMes').style.width = Math.round(hoy.getDate() / diasDelMes * 100) + '%';

        // Estado
        const pill = $('estadoPresupuesto');
        const gastado = d.gastado_hoy || 0;
        const limite = d.limite_diario || 0;
        if (gastado > limite && limite >= 0 && gastado > 0) {
            const exceso = gastado - limite;
            pill.className = 'pill-estado pill-estado--excedido';
            pill.innerHTML = `⚠️ Superaste tu límite diario en <b>&nbsp;${EF.formato.moneda(exceso)}</b>` +
                `<br>Gastaste ${EF.formato.moneda(gastado)} de ${EF.formato.moneda(limite)}.`;
        } else if (limite > 0 && gastado / limite > 0.8) {
            pill.className = 'pill-estado pill-estado--alerta';
            pill.innerHTML = `⏳ Te queda <b>&nbsp;${EF.formato.moneda(limite - gastado)}</b> de tu presupuesto diario.` +
                `<br>Has usado el ${Math.round(gastado / limite * 100)}% de tu límite.`;
        } else {
            pill.className = 'pill-estado pill-estado--ok';
            pill.innerHTML = `✅ Te queda <b>&nbsp;${EF.formato.moneda(limite - gastado)}</b> para gastar hoy.` +
                `<br>Límite: ${EF.formato.moneda(limite)} · Gastado hoy: ${EF.formato.moneda(gastado)}.`;
        }
    }

    /* ---------- Modal nueva meta ---------- */
    // El CSS controla la visibilidad con la clase .abierto (opacity/visibility);
    // el atributo hidden se mantiene como respaldo de accesibilidad.
    function abrirModal() {
        const modal = $('modalMeta');
        modal.hidden = false;
        requestAnimationFrame(() => modal.classList.add('abierto'));
        $('metaNombre').focus();
    }
    function cerrarModal() {
        const modal = $('modalMeta');
        modal.classList.remove('abierto');
        setTimeout(() => { modal.hidden = true; }, 220);
        document.getElementById('form-meta').reset();
    }

    async function crearMeta(e) {
        e.preventDefault();
        EF.ui.limpiarError('metaNombre');
        EF.ui.limpiarError('metaObjetivo');
        const nombre = $('metaNombre').value.trim();
        const objetivo = parseFloat($('metaObjetivo').value);
        let valido = true;
        if (!nombre) { EF.ui.mostrarError('metaNombre', 'Campo requerido'); valido = false; }
        if (!objetivo || objetivo <= 0) { EF.ui.mostrarError('metaObjetivo', 'Monto mayor a 0'); valido = false; }
        if (!valido) return;

        const btn = e.target.querySelector('button[type="submit"]');
        EF.ui.setCargando(btn, true);
        try {
            await EF.api('/api/metas', {
                metodo: 'POST',
                datos: {
                    nombre,
                    monto_objetivo: objetivo,
                    monto_inicial: parseFloat($('metaInicial').value) || 0,
                    fecha_limite: $('metaFecha').value || undefined
                }
            });
            cerrarModal();
            EF.ui.toast('Meta creada 🎯', 'exito');
            inicializar();
        } catch (err) {
            EF.ui.setCargando(btn, false);
            if (err.codigo === 'sin_sesion' || err.estado === 401) { window.location.href = 'login.html'; return; }
            EF.ui.toast(err.mensaje || 'No se pudo crear la meta', 'error');
        }
    }

    /* ---------- Modal presupuesto ---------- */
    function abrirModalPresupuesto() {
        const modal = $('modalPresupuesto');
        modal.hidden = false;
        requestAnimationFrame(() => modal.classList.add('abierto'));
        $('presupMonto').value = '';
        EF.api('/api/presupuesto').then(p => {
            if (p.fuente === 'personalizado') $('presupMonto').value = p.presupuesto_guardado;
        }).catch(() => {});
        $('presupMonto').focus();
    }
    function cerrarModalPresupuesto() {
        const modal = $('modalPresupuesto');
        modal.classList.remove('abierto');
        setTimeout(() => { modal.hidden = true; }, 220);
    }

    async function guardarPresupuesto(monto) {
        try {
            const r = await EF.api('/api/presupuesto', { metodo: 'PUT', datos: monto === null ? {} : { monto } });
            EF.ui.toast(r.fuente === 'personalizado'
                ? `Presupuesto diario fijado en ${EF.formato.moneda(r.limite_diario)}`
                : 'Volverás al cálculo automático', 'exito');
            cerrarModalPresupuesto();
            inicializar();
        } catch (err) {
            if (err.codigo === 'sin_sesion' || err.estado === 401) { window.location.href = 'login.html'; return; }
            EF.ui.toast(err.mensaje || 'No se pudo guardar', 'error');
        }
    }

    /* ---------- Cerrar sesión ---------- */
    async function salir() {
        await EF.sesion.cerrarSesion();
        window.location.href = 'login.html';
    }

    /* ---------- Inicialización ---------- */
    // Registra eventos de forma independiente: si falta un elemento
    // (p. ej. mezcla de caché vieja), los demás botones siguen funcionando.
    function on(id, evento, fn) {
        const el = $(id);
        if (el) el.addEventListener(evento, fn);
    }

    async function inicializar() {
        on('btnLogout', 'click', salir);
        on('btnNuevaMeta', 'click', abrirModal);
        on('btnCerrarModal', 'click', cerrarModal);
        on('modalMeta', 'click', e => { if (e.target === e.currentTarget) cerrarModal(); });
        on('form-meta', 'submit', crearMeta);
        on('listaMetas', 'click', accionMeta);
        on('listaMovimientos', 'click', eliminarMovimiento);
        on('flechaIzq', 'click', () => irAPagina(-1));
        on('flechaDer', 'click', () => irAPagina(1));

        on('btnEditarPresupuesto', 'click', abrirModalPresupuesto);
        on('btnCerrarModalPresupuesto', 'click', cerrarModalPresupuesto);
        on('modalPresupuesto', 'click', e => { if (e.target === e.currentTarget) cerrarModalPresupuesto(); });
        on('btnPresupAuto', 'click', () => guardarPresupuesto(null));
        on('form-presupuesto', 'submit', e => {
            e.preventDefault();
            const valor = $('presupMonto').value.trim();
            if (!valor) {
                EF.ui.toast('Ingresa un monto o usa el botón "Usar automático"', 'advertencia');
                return;
            }
            const monto = parseFloat(valor);
            if (!monto || monto <= 0) { EF.ui.toast('El monto debe ser mayor a 0', 'advertencia'); return; }
            guardarPresupuesto(monto);
        });

        try {
            const [d, rep] = await Promise.all([
                EF.api('/api/dashboard'),
                EF.api('/api/reportes').catch(() => null)
            ]);

            saludar(d.usuario?.nombre);

            // Tarjetas resumen
            $('montoDisponible').textContent = EF.formato.moneda(d.disponible);
            $('miniIngresos').textContent = EF.formato.moneda(d.total_ingresos_mes);
            $('miniGastos').textContent = EF.formato.moneda(d.total_gastos_mes);

            // Sparklines con evolución mensual (reportes)
            if (rep && Array.isArray(rep.por_mes) && rep.por_mes.length) {
                const meses = rep.por_mes;
                renderSpark('sparkBalance', meses.map(m => m.ingresos - m.gastos), COLOR_ACENTO);
                renderSpark('sparkIngresos', meses.map(m => m.ingresos), COLOR_ACENTO);
                renderSpark('sparkGastos', meses.map(m => m.gastos), '#f87171');
            }

            // Paneles
            pintarLeyenda(d.categorias);
            pintarDoughnut(d.categorias);
            pintarMetas(d.metas);
            pintarMovimientos(d.movimientos);
            pintarPresupuesto(d);
        } catch (err) {
            console.error('[dashboard] fallo al cargar:', err);
            if (err.codigo === 'sin_sesion' || err.estado === 401) {
                window.location.href = 'login.html';
                return;
            }
            EF.ui.toast(err.detalle || err.mensaje || 'No se pudo cargar el dashboard', 'error');
        }
    }

    // Ejecutar aunque el documento ya haya terminado de cargar (bfcache, timing)
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', inicializar);
    } else {
        inicializar();
    }

    // Al volver con "atrás" el navegador restaura la página vieja: recargar datos
    window.addEventListener('pageshow', e => { if (e.persisted) inicializar(); });
})();
