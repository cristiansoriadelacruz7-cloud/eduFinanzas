/* ============================================================
   EduFinanzas - Reportes · Tema oscuro "Deep Teal"
   Consume /api/reportes del backend
   ============================================================ */
(function () {
    'use strict';

    const $ = id => document.getElementById(id);
    const COLOR_ACENTO = '#07b2af';
    const COLOR_SUAVE = '#93abb3';

    /* ---------- Iconos de línea ---------- */
    const svg = p =>
        `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${p}</svg>`;

    const ICONOS = {
        comida: svg('<circle cx="12" cy="13" r="8"/><path d="M12 9v4l2.5 2.5"/><path d="M9 2h6"/>'),
        transporte: svg('<rect x="4" y="4" width="16" height="12" rx="3"/><path d="M4 10h16"/><circle cx="8.5" cy="18" r="1.5"/><circle cx="15.5" cy="18" r="1.5"/>'),
        estudios: svg('<path d="M2 6s2.5-2 6-2 6 2 6 2v14s-2.5-2-6-2-6 2-6 2z"/><path d="M14 6s2.5-2 6-2"/><path d="M14 6v14"/>'),
        entretenimiento: svg('<rect x="3" y="5" width="18" height="14" rx="3"/><path d="M8 5v14M16 5v14M3 10h18M3 14h18"/>'),
        hogar: svg('<path d="M3 11l9-8 9 8"/><path d="M5 9v11h14V9"/>'),
        salud: svg('<path d="M12 21C7 16.5 3 13.2 3 8.9 3 6.2 5.2 4 7.9 4c1.7 0 3.2.8 4.1 2.1C12.9 4.8 14.4 4 16.1 4 18.8 4 21 6.2 21 8.9c0 4.3-4 7.6-9 12.1z"/>'),
        compras: svg('<path d="M6 7h12l-1.2 12.2a2 2 0 01-2 1.8H9.2a2 2 0 01-2-1.8z"/><path d="M9 10V6a3 3 0 016 0v4"/>'),
        dinero: svg('<rect x="2" y="6" width="20" height="12" rx="3"/><circle cx="12" cy="12" r="2.5"/><path d="M6 12h.01M18 12h.01"/>')
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
        return ICONOS.dinero;
    }

    /* ---------- Resumen ---------- */
    function pintarResumen(r) {
        $('repIngresos').textContent = EF.formato.moneda(r.total_ingresos);
        $('repGastos').textContent = EF.formato.moneda(r.total_gastos);
        const ahorroEl = $('repAhorro');
        ahorroEl.textContent = (r.ahorro_total < 0 ? '−' : '') + EF.formato.moneda(Math.abs(r.ahorro_total));
        ahorroEl.style.color = r.ahorro_total >= 0 ? '#fff' : 'var(--c-error)';

        const nota = $('notaAhorro');
        if (!r.total_ingresos && !r.total_gastos) {
            nota.textContent = 'Registra tus primeros movimientos para ver tu evolución.';
        } else if (r.ahorro_total >= 0) {
            const tasa = r.total_ingresos ? Math.round(r.ahorro_total / r.total_ingresos * 100) : 0;
            nota.textContent = `Has ahorrado el ${tasa}% de tus ingresos.`;
        } else {
            nota.textContent = 'Estás gastando más de lo que recibes.';
        }
    }

    /* ---------- Registro de gráficas: destruir antes de reutilizar canvas ---------- */
    const graficosActivos = {};

    function crearChart(canvasId, config) {
        if (typeof Chart === 'undefined') return;
        const canvas = $(canvasId);
        if (!canvas) return;
        if (graficosActivos[canvasId]) {
            graficosActivos[canvasId].destroy();
            delete graficosActivos[canvasId];
        }
        graficosActivos[canvasId] = new Chart(canvas, config);
    }

    /* ---------- Barras mensuales ---------- */
    function pintarBarrasMensuales(porMes) {
        if (typeof Chart === 'undefined' || !$('graficoMensual')) return;
        Chart.defaults.font.family = "'Poppins', system-ui, sans-serif";
        Chart.defaults.color = COLOR_SUAVE;

        crearChart('graficoMensual', {
            type: 'bar',
            data: {
                labels: porMes.map(m => m.mes),
                datasets: [
                    { label: 'Ingresos', data: porMes.map(m => m.ingresos), backgroundColor: COLOR_ACENTO, borderRadius: 8, maxBarThickness: 34 },
                    { label: 'Gastos', data: porMes.map(m => m.gastos), backgroundColor: '#f87171', borderRadius: 8, maxBarThickness: 34 }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { grid: { display: false }, border: { display: false } },
                    y: { beginAtZero: true, grid: { color: 'rgba(228,237,244,0.07)' }, border: { display: false } }
                },
                plugins: {
                    legend: { position: 'bottom', labels: { usePointStyle: true, boxWidth: 8, padding: 16 } },
                    tooltip: {
                        backgroundColor: '#11323c',
                        titleColor: '#fff',
                        bodyColor: '#e4edf4',
                        padding: 10,
                        cornerRadius: 10,
                        callbacks: { label: ctx => ` ${ctx.dataset.label}: ${EF.formato.moneda(ctx.parsed.y)}` }
                    }
                }
            }
        });
    }

    /* ---------- Categorías ---------- */
    function pintarCategorias(categorias) {
        const ul = $('listaCategorias');
        ul.innerHTML = '';

        const totalGastos = categorias.reduce((a, c) => a + c.monto, 0);
        if (!categorias.length || !totalGastos) {
            ul.innerHTML = '<li class="estado-vacio"><p>Sin gastos registrados todavía.</p></li>';
            return;
        }

        if (typeof Chart !== 'undefined') {
            crearChart('graficoCategorias', {
                type: 'doughnut',
                data: {
                    labels: categorias.map(c => c.nombre),
                    datasets: [{
                        data: categorias.map(c => c.monto),
                        backgroundColor: categorias.map(c => c.color || '#94A3B8'),
                        borderColor: '#0c232a',
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
                                    const pct = Math.round(ctx.parsed / totalGastos * 100);
                                    return ` ${ctx.label}: ${EF.formato.moneda(ctx.parsed)} (${pct}%)`;
                                }
                            }
                        }
                    }
                }
            });
        }

        categorias.forEach(c => {
            const pct = Math.round(c.monto / totalGastos * 100);
            const li = document.createElement('li');
            li.innerHTML =
                `<span class="leyenda__icono">${iconoCategoria(c.nombre)}</span>` +
                `<span class="leyenda__nombre">${c.nombre}</span>` +
                `<span class="leyenda__pct">${pct}%</span>`;
            ul.appendChild(li);
        });
    }

    async function inicializar() {
        try {
            const r = await EF.api('/api/reportes');
            pintarResumen(r);
            pintarBarrasMensuales(r.por_mes);
            pintarCategorias(r.categorias);
        } catch (err) {
            if (err.codigo === 'sin_sesion' || err.estado === 401) {
                window.location.href = 'login.html';
                return;
            }
            EF.ui.toast(err.mensaje || 'No se pudieron cargar los reportes', 'error');
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
