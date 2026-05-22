# -*- coding: utf-8 -*-
"""
Script de automatización para estructurar y cablear todos los templates de Stitch de la Suite Enthema.
Combina diseño visual Tailwind (Stitch) con Jinja2 y llamadas a la API de FastAPI.
Inyecta la barra lateral persistente del Enthema AI Coach en todas las vistas del investigador.
"""
import os
import re

TEMPLATE_DIR = "/Users/rafaellacau/.gemini/antigravity-ide/scratch/enthema-suite/templates"

def get_standard_aside(is_fixed=True):
    aside_class = "fixed left-0 top-0 h-screen w-64 border-r border-outline-variant bg-surface-container-lowest flex flex-col py-4 z-50"
    if not is_fixed:
        aside_class = "flex flex-col h-full py-4 w-64 bg-surface-container-lowest border-r border-outline-variant shadow-sm z-50"
        
    return f"""<aside class="{aside_class}">
  <div class="px-6 mb-8 flex items-center gap-3">
    <img alt="Logo Enthema Suite" class="w-10 h-10 object-contain" src="https://lh3.googleusercontent.com/aida-public/AB6AXuAQhB_22VotrZZbL_jOLGaLeHsfqeUWPxCXbGgk1A7Ydge9sMGxnjsgi9n4Uso49AMQ9uLO4Fx_1t-KkEooVK3Tj5VYG8Diek9UboE6JUb0hJW-LWeiMcEUgA2qTXIvc9kNrF9ls8gCXxEkvyGMjumvqE5w013AYnWc9OuZLXo2lP0FIe9TXE2kgFWA0mMIeaOMe43bRjjp1mRgsQCKVlcCyZRD59PHK1tYF7w3m8U2qFNJhSeFZfoMGrJucg_brj8IWe3DTAGBkpNp"/>
    <div>
      <h1 class="font-headline-lg text-primary font-bold tracking-tight text-[18px] leading-tight">Enthema Suite</h1>
      <p class="font-label-md text-on-surface-variant text-[10px]">Precisión Técnica</p>
    </div>
  </div>
  <nav class="flex-grow space-y-1 px-4">
    <a class="flex items-center gap-3 px-3 py-3 rounded-lg transition-colors duration-200" href="/dashboard">
      <span class="material-symbols-outlined" data-icon="dashboard">dashboard</span>
      <span class="font-label-md text-label-md">Panel de Control</span>
    </a>
    <a class="flex items-center gap-3 px-3 py-3 rounded-lg transition-colors duration-200" href="/">
      <span class="material-symbols-outlined" data-icon="folder_special">folder_special</span>
      <span class="font-label-md text-label-md">Proyectos (Onboarding)</span>
    </a>
    <a class="flex items-center gap-3 px-3 py-3 rounded-lg transition-colors duration-200" href="/data-analysis">
      <span class="material-symbols-outlined" data-icon="analytics">analytics</span>
      <span class="font-label-md text-label-md">Análisis de Datos</span>
    </a>
    <a class="flex items-center gap-3 px-3 py-3 rounded-lg transition-colors duration-200" href="/modeling">
      <span class="material-symbols-outlined" data-icon="biotech">biotech</span>
      <span class="font-label-md text-label-md">Modelado Semántico</span>
    </a>
    <a class="flex items-center gap-3 px-3 py-3 rounded-lg transition-colors duration-200" href="/finance">
      <span class="material-symbols-outlined" data-icon="payments">payments</span>
      <span class="font-label-md text-label-md">Finanzas</span>
    </a>
    <a class="flex items-center gap-3 px-3 py-3 rounded-lg transition-colors duration-200" href="/reports">
      <span class="material-symbols-outlined" data-icon="description">description</span>
      <span class="font-label-md text-label-md">Informes</span>
    </a>
    <a class="flex items-center gap-3 px-3 py-3 rounded-lg transition-colors duration-200" href="/compliance">
      <span class="material-symbols-outlined" data-icon="verified_user">verified_user</span>
      <span class="font-label-md text-label-md">Cumplimiento</span>
    </a>
    <a class="flex items-center gap-3 px-3 py-3 rounded-lg transition-colors duration-200" href="/configuration">
      <span class="material-symbols-outlined" data-icon="settings">settings</span>
      <span class="font-label-md text-label-md">Configuración</span>
    </a>
    {{% if profile.user_role in ['admin', 'auditor'] %}}
    <a class="flex items-center gap-3 px-3 py-3 rounded-lg text-secondary hover:bg-secondary-container/10 border-r-4 border-secondary transition-colors duration-200" href="/admin">
      <span class="material-symbols-outlined" data-icon="shield">shield</span>
      <span class="font-label-md text-label-md font-bold">Consola Auditoría</span>
    </a>
    {{% endif %}}
  </nav>
  <div class="px-4 py-2 border-t border-outline-variant">
    <a class="flex items-center gap-3 px-3 py-3 rounded-lg text-danger hover:bg-danger/10 transition-colors duration-200 cursor-pointer" onclick="logout()">
      <span class="material-symbols-outlined" data-icon="logout">logout</span>
      <span class="font-label-md text-label-md font-bold">Cerrar Sesión</span>
    </a>
  </div>
</aside>"""

def get_standard_header():
    return """<header class="flex justify-between items-center px-6 h-16 sticky top-0 z-40 bg-surface/80 backdrop-blur-md border-b border-outline-variant">
  <div class="flex items-center w-1/3">
    <div class="relative w-full max-w-md">
      <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-[20px]" data-icon="search">search</span>
      <input class="w-full bg-surface-container-low border border-outline-variant rounded-lg pl-10 pr-4 py-2 text-body-md focus:ring-2 focus:ring-primary/20 outline-none transition-all" placeholder="Buscar parámetros, sensores o informes..." type="text"/>
    </div>
  </div>
  <div class="flex items-center gap-2">
    <button class="p-2 text-on-surface-variant hover:bg-surface-container-high rounded-full transition-all">
      <span class="material-symbols-outlined" data-icon="notifications">notifications</span>
    </button>
    <button class="p-2 text-on-surface-variant hover:bg-surface-container-high rounded-full transition-all">
      <span class="material-symbols-outlined" data-icon="settings">settings</span>
    </button>
    <div class="h-8 w-px bg-outline-variant mx-2"></div>
    <div class="flex items-center gap-3 pl-2">
      <div class="text-right">
        <p class="font-label-md text-on-surface font-bold leading-none">{{ profile.name }}</p>
        <p class="font-label-sm text-outline">{% if profile.user_role == 'investment_consultant' %}Consultor de Inversión{% else %}Investigador Principal{% endif %}</p>
      </div>
      <div class="w-8 h-8 rounded-full bg-primary-container text-white flex items-center justify-center font-bold">
        {{ profile.name[:2].upper() }}
      </div>
    </div>
  </div>
</header>"""

def get_standard_coach():
    return """<!-- Enthema AI Coach Right Sidebar -->
<aside class="fixed right-0 top-0 h-screen w-80 border-l border-outline-variant bg-surface-container-lowest flex flex-col z-40 shadow-lg text-left">
  <!-- Coach Header -->
  <div class="px-6 py-4 border-b border-outline-variant bg-surface-container-lowest/80 backdrop-blur-md flex items-center gap-3">
    <div class="w-10 h-10 rounded-full bg-primary/10 text-primary flex items-center justify-center">
      <span class="material-symbols-outlined text-[24px]">psychology</span>
    </div>
    <div>
      <h3 class="font-headline-md text-on-surface text-[15px] font-bold leading-tight text-primary">Enthema AI Coach</h3>
      <p class="font-label-sm text-outline text-[10px]">ASISTENTE CIENTÍFICO OFFLINE</p>
    </div>
  </div>

  <!-- Chat History -->
  <div id="coach-chat-history" class="flex-grow p-4 overflow-y-auto space-y-3 bg-surface-container-low/20 custom-scrollbar text-xs">
    <!-- Welcome message -->
    <div class="flex items-start gap-2 max-w-[85%] mb-2">
      <div class="w-6 h-6 rounded-full bg-primary/15 text-primary flex items-center justify-center shrink-0">
        <span class="material-symbols-outlined text-[14px]">smart_toy</span>
      </div>
      <div class="bg-surface-container border border-outline-variant/30 rounded-lg p-2.5 text-on-surface-variant leading-relaxed">
        Hola, soy su <strong>AI Coach</strong> técnico. Estoy listo para guiarle de forma segura sin costo de API ($0.00). ¿En qué área técnica o solver financiero desea profundizar hoy?
      </div>
    </div>
  </div>

  <!-- Suggestions / Quick Links -->
  <div class="px-4 py-2 bg-surface-container-low/40 border-t border-outline-variant/30">
    <p class="text-[10px] font-bold text-primary uppercase mb-1">Consultas Sugeridas</p>
    <div class="flex flex-wrap gap-1.5">
      <button onclick="sendQuickQuery('¿Cómo funciona el reactor ABM?')" class="text-[10px] px-2 py-1 bg-surface-container border border-outline-variant rounded hover:bg-primary-container/10 hover:text-primary transition-all text-left">🧬 Bio-reactor ABM</button>
      <button onclick="sendQuickQuery('¿Cómo interpreto el Solver Financiero?')" class="text-[10px] px-2 py-1 bg-surface-container border border-outline-variant rounded hover:bg-primary-container/10 hover:text-primary transition-all text-left">💸 Solver TIR/VAN</button>
      <button onclick="sendQuickQuery('¿Qué validez tiene el Sello del Acta?')" class="text-[10px] px-2 py-1 bg-surface-container border border-outline-variant rounded hover:bg-primary-container/10 hover:text-primary transition-all text-left">🛡️ Cumplimiento Legal</button>
    </div>
  </div>

  <!-- Chat Input Form -->
  <form id="coach-chat-form" class="p-4 border-t border-outline-variant bg-surface-container-lowest flex items-center gap-2">
    <input type="text" id="coach-query-input" placeholder="Pregunte algo al AI Coach..." class="flex-grow bg-surface-container-low border border-outline-variant rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-primary/20 outline-none transition-all text-on-surface" required autocomplete="off" />
    <button type="submit" class="p-2 bg-primary text-white rounded-lg hover:opacity-90 transition-all shrink-0">
      <span class="material-symbols-outlined text-[16px]">send</span>
    </button>
  </form>
</aside>"""

def get_active_nav_script():
    return """
    // Active Navigation Logic for SideNavBar
    const currentPath = window.location.pathname;
    document.querySelectorAll('aside nav a').forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || (currentPath === '/' && href === '/')) {
            link.className = "flex items-center gap-3 px-3 py-3 rounded-lg text-primary font-bold bg-primary-container/10 border-r-4 border-primary transition-all duration-150";
        } else {
            link.className = "flex items-center gap-3 px-3 py-3 rounded-lg text-on-surface-variant hover:bg-surface-container transition-colors duration-200";
        }
    });

    // Global Logout Handler
    async function logout() {
        if (confirm('¿Está seguro de que desea cerrar sesión?')) {
            try {
                const res = await fetch('/api/logout', { method: 'POST' });
                if (res.ok) {
                    window.location.href = '/login';
                } else {
                    alert('Error al cerrar sesión');
                }
            } catch (err) {
                console.error('Error al cerrar sesión:', err);
            }
        }
    }

    // AI Coach Quick Query
    function sendQuickQuery(text) {
        const input = document.getElementById('coach-query-input');
        if (input) {
            input.value = text;
            document.getElementById('coach-chat-form').dispatchEvent(new Event('submit'));
        }
    }

    // AI Coach AJAX submit handler
    document.addEventListener('DOMContentLoaded', () => {
        const chatForm = document.getElementById('coach-chat-form');
        const chatHistory = document.getElementById('coach-chat-history');
        const queryInput = document.getElementById('coach-query-input');
        
        if (chatForm && chatHistory && queryInput) {
            chatForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const query = queryInput.value.trim();
                if (!query) return;
                
                // Append User Message
                const userMsgDiv = document.createElement('div');
                userMsgDiv.className = "flex items-start gap-2 max-w-[85%] ml-auto justify-end mb-2";
                userMsgDiv.innerHTML = `
                    <div class="bg-primary text-white rounded-lg p-2.5 leading-relaxed text-right">
                        ${query}
                    </div>
                    <div class="w-6 h-6 rounded-full bg-primary text-white flex items-center justify-center shrink-0 font-bold font-label-sm text-[10px]">
                        YO
                    </div>
                `;
                chatHistory.appendChild(userMsgDiv);
                chatHistory.scrollTop = chatHistory.scrollHeight;
                
                // Clear input and show typing...
                queryInput.value = '';
                queryInput.disabled = true;
                
                const typingDiv = document.createElement('div');
                typingDiv.className = "flex items-start gap-2 max-w-[85%] typing-indicator mb-2";
                typingDiv.innerHTML = `
                    <div class="w-6 h-6 rounded-full bg-primary/15 text-primary flex items-center justify-center shrink-0">
                        <span class="material-symbols-outlined text-[14px]">smart_toy</span>
                    </div>
                    <div class="bg-surface-container border border-outline-variant/30 rounded-lg p-2.5 text-on-surface-variant leading-relaxed italic animate-pulse">
                        Analizando variables técnicas...
                    </div>
                `;
                chatHistory.appendChild(typingDiv);
                chatHistory.scrollTop = chatHistory.scrollHeight;
                
                try {
                    const res = await fetch('/api/copilot/query', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: query })
                    });
                    
                    // Remove typing indicator
                    const typing = chatHistory.querySelector('.typing-indicator');
                    if (typing) typing.remove();
                    
                    if (res.ok) {
                        const data = await res.json();
                        
                        const botMsgDiv = document.createElement('div');
                        botMsgDiv.className = "flex items-start gap-2 max-w-[85%] mb-2 animate-fade-in";
                        botMsgDiv.innerHTML = `
                            <div class="w-6 h-6 rounded-full bg-primary/15 text-primary flex items-center justify-center shrink-0">
                                <span class="material-symbols-outlined text-[14px]">smart_toy</span>
                            </div>
                            <div class="bg-surface-container border border-outline-variant/30 rounded-lg p-2.5 text-on-surface-variant leading-relaxed">
                                ${data.answer}
                            </div>
                        `;
                        chatHistory.appendChild(botMsgDiv);
                    } else {
                        const errorDiv = document.createElement('div');
                        errorDiv.className = "flex items-start gap-2 max-w-[85%] mb-2";
                        errorDiv.innerHTML = `
                            <div class="w-6 h-6 rounded-full bg-danger/15 text-danger flex items-center justify-center shrink-0">
                                <span class="material-symbols-outlined text-[14px]">error</span>
                            </div>
                            <div class="bg-danger/5 border border-danger/20 text-danger rounded-lg p-2.5 leading-relaxed">
                                Error en la conexión offline con el Coach.
                            </div>
                        `;
                        chatHistory.appendChild(errorDiv);
                    }
                } catch (err) {
                    const typing = chatHistory.querySelector('.typing-indicator');
                    if (typing) typing.remove();
                    
                    const errorDiv = document.createElement('div');
                    errorDiv.className = "flex items-start gap-2 max-w-[85%] mb-2";
                    errorDiv.innerHTML = `
                        <div class="w-6 h-6 rounded-full bg-danger/15 text-danger flex items-center justify-center shrink-0">
                            <span class="material-symbols-outlined text-[14px]">error</span>
                        </div>
                        <div class="bg-danger/5 border border-danger/20 text-danger rounded-lg p-2.5 leading-relaxed">
                            Error de red: ${err.message}
                        </div>
                    `;
                    chatHistory.appendChild(errorDiv);
                } finally {
                    queryInput.disabled = false;
                    queryInput.focus();
                    chatHistory.scrollTop = chatHistory.scrollHeight;
                }
            });
        }
    });
    """

def update_dashboard():
    path = os.path.join(TEMPLATE_DIR, "dashboard.html")
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    # Reemplazar aside y header
    html = re.sub(r'<aside.*?</aside>', get_standard_aside(is_fixed=False), html, flags=re.DOTALL)
    html = re.sub(r'<header.*?</header>', get_standard_header(), html, flags=re.DOTALL)

    # Reemplazar el contenedor principal para agregar el espacio del coach
    html = html.replace('<main class="flex-1 flex flex-col min-w-0 bg-surface overflow-hidden">', '<main class="flex-1 flex flex-col min-w-0 bg-surface overflow-hidden mr-80">')

    # Reemplazar valores de telemetría por Jinja2 placeholders
    html = html.replace('1,240.5', '<span id="temp-val">{{ reactor_temp }}</span>')
    html = html.replace('104.2', '<span id="press-val">{{ reactor_pressure }}</span>')
    html = html.replace('7.42', '<span id="ph-val">{{ reactor_ph }}</span>')
    html = html.replace('Operativo', '<span id="status-val">{{ reactor_status }}</span>')

    # Inject Coach Right Sidebar
    if "Enthema AI Coach" not in html:
        html = html.replace('</body>', get_standard_coach() + '\n</body>')

    # Script de auto-refresh de telemetría y navegación
    script_pattern = r'<script>.*?</script>\s*</body>'
    new_script = f"""<script>
        {get_active_nav_script()}

        // Auto-refresh telemetry simulation
        setInterval(async () => {{
            try {{
                const res = await fetch('/api/model/abm', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ duration_months: 12, subsidy_amount: 150000 }})
                }});
                const data = await res.json();
                if (data.status === 'success' && data.reactor_telemetry.length > 0) {{
                    const latest = data.reactor_telemetry[data.reactor_telemetry.length - 1];
                    document.getElementById('temp-val').innerText = latest.temp;
                    document.getElementById('press-val').innerText = latest.pres;
                    document.getElementById('ph-val').innerText = latest.ph;
                }}
            }} catch (err) {{
                console.warn('Error refreshing telemetry:', err);
            }}
        }}, 5000);
    </script>
</body>"""
    html = re.sub(script_pattern, new_script, html, flags=re.DOTALL)

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("dashboard.html actualizado con éxito!")

def update_data_analysis():
    path = os.path.join(TEMPLATE_DIR, "data_analysis.html")
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    # Standardize navigation and header
    html = re.sub(r'<aside.*?</aside>', get_standard_aside(is_fixed=True), html, flags=re.DOTALL)
    html = re.sub(r'<header.*?</header>', get_standard_header(), html, flags=re.DOTALL)

    # Reemplazar el contenedor principal para agregar el espacio del coach
    html = html.replace('<main class="ml-64 flex-1 min-h-screen">', '<main class="ml-64 flex-1 min-h-screen mr-80">')

    # Inject Coach Right Sidebar
    if "Enthema AI Coach" not in html:
        html = html.replace('</body>', get_standard_coach() + '\n</body>')

    # Insert forms for synthetic simulation and CSV upload in stats sidebar (col-span-4)
    target_stats_sidebar = r'<!-- Stats Sidebar -->\s*<div class="col-span-4 flex flex-col gap-gutter">'
    forms_injected = """<!-- Stats Sidebar -->
<div class="col-span-4 flex flex-col gap-gutter">
  <!-- Controles de Datos -->
  <div class="bg-surface-container-lowest border border-outline-variant rounded-xl p-6 shadow-sm space-y-4 text-left">
    <h3 class="font-headline-md text-on-surface text-[18px]">⚡ Controles de Datos</h3>
    <p class="font-body-md text-on-surface-variant">Genere datos piloto sintéticos o cargue su dataset de laboratorio.</p>
    
    <div class="space-y-3 pt-2">
      <!-- Botón Piloto -->
      <button id="btn-synthetic" class="w-full bg-primary text-white py-2.5 px-4 rounded-lg font-label-md hover:opacity-90 transition-all flex items-center justify-center gap-2">
        <span class="material-symbols-outlined text-[18px]">insights</span> Generar Datos Piloto
      </button>
      
      <!-- Cargador CSV -->
      <div class="border border-dashed border-outline-variant rounded-lg p-4 text-center space-y-2 hover:border-primary transition-all">
        <span class="material-symbols-outlined text-primary text-[28px]">cloud_upload</span>
        <p class="text-xs text-on-surface-variant">Cargar archivo de Muestras (.csv)</p>
        <input type="file" id="quantCsvFile" class="hidden" accept=".csv" />
        <button type="button" onclick="document.getElementById('quantCsvFile').click()" class="text-xs px-3 py-1 bg-surface-container border border-outline-variant rounded hover:bg-surface-container-high transition-all">Seleccionar</button>
      </div>
      <div id="dataUploadStatus" class="hidden text-xs p-2 rounded text-left"></div>
    </div>
  </div>"""
    html = re.sub(target_stats_sidebar, forms_injected, html, flags=re.DOTALL)

    # Script for scatterplot and API wiring
    script_pattern = r'<script>.*?</script>\s*</body>'
    new_script = f"""<script>
        {get_active_nav_script()}

        // Populate initial Scatter Plot and Heatmap
        const heatmap = document.getElementById('heatmap');
        const rows = 8;
        const cols = 12;
        const colors = [
            'bg-blue-100', 'bg-blue-200', 'bg-blue-300', 
            'bg-primary/40', 'bg-primary/60', 'bg-primary/80', 'bg-primary',
            'bg-danger/40', 'bg-danger/60', 'bg-danger/80'
        ];

        function rebuildHeatmap() {{
            heatmap.innerHTML = '';
            for (let i = 0; i < rows * cols; i++) {{
                const cell = document.createElement('div');
                const randomColor = colors[Math.floor(Math.random() * colors.length)];
                cell.className = `h-6 w-full rounded-[2px] heatmap-cell ${{randomColor}}`;
                heatmap.appendChild(cell);
            }}
        }}
        rebuildHeatmap();

        // Scatter plot functionality
        const dotContainer = document.getElementById('dot-container');
        const palette = ['#005bbf', '#c55500', '#005ac1', '#4d8efe'];

        function addScatterDots(count = 80) {{
            dotContainer.innerHTML = '';
            for (let i = 0; i < count; i++) {{
                const dot = document.createElement('div');
                const size = Math.random() * 8 + 4;
                const x = Math.random() * 90 + 5;
                const y = Math.random() * 90 + 5;
                const color = palette[Math.floor(Math.random() * palette.length)];
                const opacity = Math.random() * 0.5 + 0.5;

                dot.className = 'absolute molecular-dot rounded-full';
                dot.style.width = `${{size}}px`;
                dot.style.height = `${{size}}px`;
                dot.style.left = `${{x}}%`;
                dot.style.top = `${{y}}%`;
                dot.style.backgroundColor = color;
                dot.style.opacity = opacity;
                
                dotContainer.appendChild(dot);
            }}
        }}
        addScatterDots();

        // Micro-interaction: random subtle movement for dots
        setInterval(() => {{
            const dots = document.querySelectorAll('.molecular-dot');
            dots.forEach(dot => {{
                const moveX = (Math.random() - 0.5) * 4;
                const moveY = (Math.random() - 0.5) * 4;
                const currentLeft = parseFloat(dot.style.left) || 50;
                const currentTop = parseFloat(dot.style.top) || 50;
                dot.style.left = `${{currentLeft + moveX * 0.1}}%`;
                dot.style.top = `${{currentTop + moveY * 0.1}}%`;
            }});
        }}, 1500);

        // Grid lines for scatter plot
        const scatterGrid = document.getElementById('scatter-plot');
        for (let i = 0; i < 100; i++) {{
            const line = document.createElement('div');
            line.className = 'border-[0.5px] border-outline-variant/20';
            scatterGrid.appendChild(line);
        }}

        // API Wiring: Generate synthetic pilot
        document.getElementById('btn-synthetic').addEventListener('click', async () => {{
            const btn = document.getElementById('btn-synthetic');
            btn.disabled = true;
            btn.innerHTML = '<span class="material-symbols-outlined text-[18px] animate-spin">sync</span> Generando...';
            
            try {{
                const res = await fetch('/api/data/synthetic', {{ method: 'POST' }});
                const data = await res.json();
                if (data.status === 'success') {{
                    alert('🧬 Piloto autogenerado exitosamente para ' + data.quantitative.title + '\\nVariables: ' + data.quantitative.variables.map(v => v.name).join(', '));
                    addScatterDots(120);
                    rebuildHeatmap();
                }} else {{
                    alert('Error: ' + data.message);
                }}
            }} catch (err) {{
                alert('Error de conexión: ' + err.message);
            }} finally {{
                btn.disabled = false;
                btn.innerHTML = '<span class="material-symbols-outlined text-[18px]">insights</span> Generar Datos Piloto';
            }}
        }});

        // API Wiring: Upload CSV
        document.getElementById('quantCsvFile').addEventListener('change', async (e) => {{
            const file = e.target.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('file', file);

            const status = document.getElementById('dataUploadStatus');
            status.className = "block text-xs p-2 rounded bg-primary-container/10 text-primary";
            status.innerText = "Procesando dataset y winsorizando outliers...";

            try {{
                const res = await fetch('/api/data/upload', {{
                    method: 'POST',
                    body: formData
                }});
                const result = await res.json();
                if (res.ok) {{
                    status.className = "block text-xs p-2 rounded bg-success/10 text-success";
                    status.innerText = `✅ Ingesta exitosa! Registros: ${{result.total_records}}, Anomalías corregidas: ${{result.anomalies}}`;
                    addScatterDots(100);
                    rebuildHeatmap();
                }} else {{
                    status.className = "block text-xs p-2 rounded bg-danger/10 text-danger";
                    status.innerText = "Error: " + result.detail;
                }}
            }} catch (err) {{
                status.className = "block text-xs p-2 rounded bg-danger/10 text-danger";
                status.innerText = "Error de red: " + err.message;
            }}
        }});
    </script>
</body>"""
    html = re.sub(script_pattern, new_script, html, flags=re.DOTALL)

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("data_analysis.html actualizado con éxito!")

def update_semantic_modeling():
    path = os.path.join(TEMPLATE_DIR, "semantic_modeling.html")
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    # Standardize navigation and header
    html = re.sub(r'<aside.*?</aside>', get_standard_aside(is_fixed=True), html, flags=re.DOTALL)
    html = re.sub(r'<header.*?</header>', get_standard_header(), html, flags=re.DOTALL)

    # Reemplazar el contenedor principal para agregar el espacio del coach
    html = html.replace('<main class="ml-64 h-screen flex flex-col relative overflow-hidden">', '<main class="ml-64 h-screen flex flex-col relative overflow-hidden mr-80">')

    # Inject Coach Right Sidebar
    if "Enthema AI Coach" not in html:
        html = html.replace('</body>', get_standard_coach() + '\n</body>')

    # Inyectar id al botón de simulación si no está
    sim_btn_pattern = r'<button class="w-full bg-primary text-white py-3 rounded-lg font-bold font-label-md hover:opacity-90 transition-opacity flex items-center justify-center gap-2">'
    html = html.replace(sim_btn_pattern, '<button id="btn-run-simulation" class="w-full bg-primary text-white py-3 rounded-lg font-bold font-label-md hover:opacity-90 transition-opacity flex items-center justify-center gap-2">')

    # Añadir un div en el inspector-panel para volcar resultados de STEAM si no existe
    if "steam-projection-card" not in html:
        target_results_panel = r'</section>\s*<button id="btn-run-simulation"'
        results_div = """</section>
<div id="steam-projection-card" class="hidden bg-surface-container-low p-4 rounded-xl border border-outline-variant mt-4 space-y-3 text-left">
  <h4 class="font-label-md text-primary uppercase font-bold text-xs">🤖 Simulación ABM Termina</h4>
  <p id="steam-explanation" class="text-[11px] text-on-surface-variant leading-relaxed"></p>
  <div class="bg-inverse-surface text-inverse-on-surface p-3 rounded font-label-sm text-[11px] overflow-x-auto select-all">
    <pre><code id="steam-code"></code></pre>
  </div>
  <p class="text-[10px] text-outline">El script anterior puede importarse directamente en OpenSCAD para impresión 3D física.</p>
</div>
<button id="btn-run-simulation\""""
        html = html.replace(target_results_panel, results_div)

    # Script for semantic graph
    script_pattern = r'<script>.*?</script>\s*</body>'
    new_script = f"""<script>
        {get_active_nav_script()}

        function toggleInspector() {{
            const panel = document.getElementById('inspector-panel');
            if (panel.classList.contains('translate-x-0')) {{
                panel.classList.remove('translate-x-0');
                panel.classList.add('translate-x-full');
            }} else {{
                panel.classList.remove('translate-x-full');
                panel.classList.add('translate-x-0');
            }}
        }}

        // Wire simulation run
        document.getElementById('btn-run-simulation').addEventListener('click', async () => {{
            const btn = document.getElementById('btn-run-simulation');
            btn.disabled = true;
            btn.innerHTML = '<span class="material-symbols-outlined text-[18px] animate-spin">sync</span> Ejecutando ABM...';
            
            try {{
                const res = await fetch('/api/model/abm', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ duration_months: 12, subsidy_amount: 150000 }})
                }});
                const data = await res.json();
                if (data.status === 'success') {{
                    document.getElementById('steam-projection-card').classList.remove('hidden');
                    document.getElementById('steam-explanation').innerText = data.steam_projections.explanation;
                    document.getElementById('steam-code').innerText = data.steam_projections.code_snippet;
                    alert('🚀 Simulación ABM catalizada! El modelo OpenSCAD 3D ha sido generado.');
                }} else {{
                    alert('Error ejecutando simulación.');
                }}
            }} catch (err) {{
                alert('Error de conexión: ' + err.message);
            }} finally {{
                btn.disabled = false;
                btn.innerHTML = '<span class="material-symbols-outlined text-[18px]">rocket_launch</span> Ejecutar Simulación';
            }}
        }});

        // SVGs / lines motion
        document.querySelector('svg').addEventListener('mousedown', function(e) {{
            this.style.cursor = 'grabbing';
        }});
        document.querySelector('svg').addEventListener('mouseup', function(e) {{
            this.style.cursor = 'grab';
        }});
    </script>
</body>"""
    html = re.sub(script_pattern, new_script, html, flags=re.DOTALL)

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("semantic_modeling.html actualizado con éxito!")

def update_finance():
    path = os.path.join(TEMPLATE_DIR, "finance.html")
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    # Standardize navigation and header
    html = re.sub(r'<aside.*?</aside>', get_standard_aside(is_fixed=True), html, flags=re.DOTALL)
    html = re.sub(r'<header.*?</header>', get_standard_header(), html, flags=re.DOTALL)

    # Reemplazar el contenedor principal para agregar el espacio del coach
    html = html.replace('<div class="ml-64 min-h-screen flex flex-col">', '<div class="ml-64 min-h-screen flex flex-col mr-80">')

    # Inject Coach Right Sidebar
    if "Enthema AI Coach" not in html:
        html = html.replace('</body>', get_standard_coach() + '\n</body>')

    # Insert Solver Form before Gantt Chart if not exists
    if "financeSolverForm" not in html:
        gantt_chart_pattern = r'<section class="bg-surface-container-lowest border border-outline-variant rounded-xl overflow-hidden shadow-\[0_1px_3px_rgba\(60,64,67,0.12\)\]>'
        solver_form = """<!-- Solver Financiero Form -->
<section class="bg-surface-container-lowest border border-outline-variant rounded-xl p-6 shadow-[0_1px_3px_rgba(60,64,67,0.12)] space-y-6 text-left">
  <div class="border-b border-outline-variant pb-4">
    <h3 class="font-headline-md text-on-surface text-[20px] flex items-center gap-2">
      <span class="material-symbols-outlined text-primary">analytics</span> Resolver Viabilidad Financiera (Newton-Raphson)
    </h3>
    <p class="font-body-md text-on-surface-variant">Modifique el flujo de caja estimado para computar los valores de VAN y TIR dinámicamente.</p>
  </div>
  
  <form id="financeSolverForm" class="grid grid-cols-12 gap-6">
    <!-- Col 1: Tasa Descuento -->
    <div class="col-span-12 md:col-span-4 space-y-1">
      <label class="block text-xs font-label-md text-primary font-bold">TASA DE DESCUENTO (WACC)</label>
      <input type="number" step="0.01" id="discount_rate_solver" name="discount_rate" value="0.10" class="w-full bg-white border border-outline-variant rounded px-3 py-2 text-body-md text-on-surface" required />
    </div>

    <!-- Col 2: Financiamiento Objetivo -->
    <div class="col-span-12 md:col-span-4 space-y-1">
      <label class="block text-xs font-label-md text-primary font-bold">INVERSIÓN INICIAL (USD)</label>
      <input type="number" id="target_fund_solver" name="target_fund_usd" value="{{ profile.target_fund_usd }}" class="w-full bg-white border border-outline-variant rounded px-3 py-2 text-body-md text-on-surface" required />
    </div>
    
    <div class="col-span-12">
      <p class="text-xs font-label-md text-primary font-bold mb-2">FLUJOS NETOS ANUALES (INFLOWS - OUTFLOWS)</p>
      <div class="grid grid-cols-6 gap-3">
        <div>
          <label class="block text-[10px] text-outline text-center">AÑO 0 (EGRESO)</label>
          <input type="number" id="flow_0" value="-100000" class="w-full bg-white border border-outline-variant rounded px-2 py-1.5 text-center text-body-md text-on-surface" />
        </div>
        <div>
          <label class="block text-[10px] text-outline text-center">AÑO 1</label>
          <input type="number" id="flow_1" value="40000" class="w-full bg-white border border-outline-variant rounded px-2 py-1.5 text-center text-body-md text-on-surface" />
        </div>
        <div>
          <label class="block text-[10px] text-outline text-center">AÑO 2</label>
          <input type="number" id="flow_2" value="45000" class="w-full bg-white border border-outline-variant rounded px-2 py-1.5 text-center text-body-md text-on-surface" />
        </div>
        <div>
          <label class="block text-[10px] text-outline text-center">AÑO 3</label>
          <input type="number" id="flow_3" value="50000" class="w-full bg-white border border-outline-variant rounded px-2 py-1.5 text-center text-body-md text-on-surface" />
        </div>
        <div>
          <label class="block text-[10px] text-outline text-center">AÑO 4</label>
          <input type="number" id="flow_4" value="55000" class="w-full bg-white border border-outline-variant rounded px-2 py-1.5 text-center text-body-md text-on-surface" />
        </div>
        <div>
          <label class="block text-[10px] text-outline text-center">AÑO 5</label>
          <input type="number" id="flow_5" value="60000" class="w-full bg-white border border-outline-variant rounded px-2 py-1.5 text-center text-body-md text-on-surface" />
        </div>
      </div>
    </div>
    
    <div class="col-span-12 flex justify-end gap-4 pt-2">
      <button type="submit" class="px-6 py-2.5 bg-primary text-white rounded font-label-md hover:shadow transition-all flex items-center gap-2">
        <span class="material-symbols-outlined text-[18px]">calculate</span> Resolver Viabilidad
      </button>
    </div>
  </form>
  
  <!-- Glowing Result Card -->
  <div id="solverResultCard" class="hidden bg-primary-container/10 p-5 rounded-xl border border-primary/20 grid grid-cols-3 gap-6">
    <div class="text-center border-r border-outline-variant/30">
      <p class="text-xs text-on-surface-variant font-label-md uppercase">VALOR ACTUAL NETO (VAN)</p>
      <p id="solver-van" class="text-2xl font-bold text-primary">$0.00</p>
    </div>
    <div class="text-center border-r border-outline-variant/30">
      <p class="text-xs text-on-surface-variant font-label-md uppercase">TASA INTERNA RETORNO (TIR)</p>
      <p id="solver-tir" class="text-2xl font-bold text-secondary">0.00%</p>
    </div>
    <div class="text-center flex flex-col justify-center items-center">
      <p class="text-xs text-on-surface-variant font-label-md uppercase mb-1">DICTAMEN</p>
      <span id="solver-dictamen" class="px-4 py-1 text-xs font-bold rounded-full"></span>
    </div>
  </div>
</section>

<section class="bg-surface-container-lowest border border-outline-variant rounded-xl overflow-hidden shadow-[0_1px_3px_rgba(60,64,67,0.12)]">"""
        html = re.sub(gantt_chart_pattern, solver_form, html, flags=re.DOTALL)

    # Wire Solver Form via Fetch and dynamic updates
    script_pattern = r'<script>.*?</script>\s*</body>'
    new_script = f"""<script>
        {get_active_nav_script()}

        document.getElementById('financeSolverForm').addEventListener('submit', async (e) => {{
            e.preventDefault();
            const wacc = parseFloat(document.getElementById('discount_rate_solver').value) || 0.10;
            const targetFund = parseFloat(document.getElementById('target_fund_solver').value) || 2500000;
            
            // Build periods cash flows
            const flows = [
                {{ period: 0, inflow: 0.0, outflow: Math.abs(parseFloat(document.getElementById('flow_0').value)) }},
                {{ period: 1, inflow: parseFloat(document.getElementById('flow_1').value), outflow: 0.0 }},
                {{ period: 2, inflow: parseFloat(document.getElementById('flow_2').value), outflow: 0.0 }},
                {{ period: 3, inflow: parseFloat(document.getElementById('flow_3').value), outflow: 0.0 }},
                {{ period: 4, inflow: parseFloat(document.getElementById('flow_4').value), outflow: 0.0 }},
                {{ period: 5, inflow: parseFloat(document.getElementById('flow_5').value), outflow: 0.0 }}
            ];
            
            try {{
                const res = await fetch('/api/finance/solve', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        discount_rate: wacc,
                        target_fund_usd: targetFund,
                        cash_flow: flows
                    }})
                }});
                const data = await res.json();
                if (data.status === 'success') {{
                    document.getElementById('solverResultCard').classList.remove('hidden');
                    document.getElementById('solver-van').innerText = '$' + data.van.toLocaleString(undefined, {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }}) + ' USD';
                    document.getElementById('solver-tir').innerText = (data.tir * 100).toFixed(2) + '%';
                    
                    const badge = document.getElementById('solver-dictamen');
                    badge.innerText = data.dictamen;
                    if (data.dictamen.includes('VIABLE')) {{
                        badge.className = "px-4 py-1 text-xs font-bold rounded-full bg-success/20 text-success";
                    }} else {{
                        badge.className = "px-4 py-1 text-xs font-bold rounded-full bg-danger/20 text-danger";
                    }}
                }} else {{
                    alert('Error resolviendo flujos.');
                }}
            }} catch (err) {{
                alert('Error de red: ' + err.message);
            }}
        }});

        // Smooth animations on load
        document.addEventListener('DOMContentLoaded', () => {{
            const cards = document.querySelectorAll('.bg-surface-container-lowest');
            cards.forEach(card => {{
                card.addEventListener('mouseenter', () => {{
                    card.style.transform = 'translateY(-2px)';
                    card.style.transition = 'transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.2s ease';
                }});
                card.addEventListener('mouseleave', () => {{
                    card.style.transform = 'translateY(0)';
                }});
            }});
        }});
    </script>
</body>"""
    html = re.sub(script_pattern, new_script, html, flags=re.DOTALL)

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("finance.html actualizado con éxito!")

def update_reports():
    path = os.path.join(TEMPLATE_DIR, "reports.html")
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    # Standardize navigation and header
    html = re.sub(r'<aside.*?</aside>', get_standard_aside(is_fixed=True), html, flags=re.DOTALL)
    html = re.sub(r'<header.*?</header>', get_standard_header(), html, flags=re.DOTALL)

    # Reemplazar el contenedor principal para agregar el espacio del coach
    html = html.replace('<main class="ml-64 flex flex-col h-screen">', '<main class="ml-64 flex flex-col h-screen mr-80">')

    # Inject Coach Right Sidebar
    if "Enthema AI Coach" not in html:
        html = html.replace('</body>', get_standard_coach() + '\n</body>')

    # Insert compiled monograph rendering above Integrity Status if not exists
    if "mono_chapters" not in html:
        integrity_pattern = r'<!-- Audit Integrity Status -->'
        monograph_section = """<!-- Monografía Científica / Académica (Jinja2 Rendered) -->
<section class="col-span-12 bg-surface-base border border-border-subtle rounded-xl p-8 shadow-sm space-y-6 text-left">
  <div class="border-b border-outline-variant pb-4">
    <span class="px-3 py-1 bg-primary-fixed text-on-primary-fixed font-label-sm rounded-full">Revista Objetivo: {{ mono_style }}</span>
    <h3 class="font-headline-lg text-on-surface mt-2 text-xl font-bold">{{ mono_title }}</h3>
    <p class="text-xs text-on-surface-variant font-label-md uppercase">Autor Principal: {{ profile.name }} • {{ profile.institution }}</p>
  </div>
  
  <div class="space-y-6 max-h-[500px] overflow-y-auto pr-4 custom-scrollbar bg-surface-container-low/20 p-6 rounded-lg border border-outline-variant/30">
    {% for chapter in mono_chapters %}
      <article class="space-y-2">
        <h4 class="font-headline-md text-primary text-[20px] font-bold">{{ chapter.title }}</h4>
        <div class="text-body-md text-on-surface-variant leading-relaxed whitespace-pre-wrap">{{ chapter.content }}</div>
      </article>
      {% if not loop.last %}<hr class="border-outline-variant/30 my-6" />{% endif %}
    {% endfor %}
  </div>
  
  <!-- Bibliography Section -->
  <div class="border-t border-outline-variant pt-4 space-y-2">
    <h4 class="font-label-md text-primary uppercase font-bold">📚 Bibliografía y Referencias Citadas (Estilo {{ mono_style }})</h4>
    <ul class="list-disc pl-5 space-y-1 text-xs text-on-surface-variant leading-normal">
      {% for bib in mono_bibliography %}
        <li>{{ bib }}</li>
      {% endfor %}
    </ul>
  </div>
</section>

<!-- Canales de Difusión Generados -->
{% if dissemination %}
<section class="col-span-12 bg-surface-base border border-border-subtle rounded-xl p-8 shadow-sm space-y-6 text-left">
  <div class="border-b border-outline-variant pb-4">
    <h3 class="font-headline-md text-on-surface text-lg font-bold">📢 Canales de Difusión y Transferencia Tecnológica</h3>
    <p class="font-body-md text-on-surface-variant">Formatos de salida adaptados a su postura epistémica y objetivos de financiamiento.</p>
  </div>
  
  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
    <!-- Abstract / Executive Summary -->
    <div class="bg-surface-container-low p-5 rounded-lg border border-outline-variant/30 space-y-2">
      <h4 class="font-bold text-primary flex items-center gap-2">
        <span class="material-symbols-outlined">description</span> Resumen Académico / Abstract
      </h4>
      <p class="text-xs text-on-surface-variant leading-relaxed">{{ dissemination.abstract_draft or dissemination.pitch_deck_narrative or "Resumen no disponible" }}</p>
    </div>
    
    <!-- Patent Claims or Funding Call -->
    <div class="bg-surface-container-low p-5 rounded-lg border border-outline-variant/30 space-y-2">
      <h4 class="font-bold text-secondary flex items-center gap-2">
        <span class="material-symbols-outlined">gavel</span> Reivindicaciones / Pitch Comercial
      </h4>
      <p class="text-xs text-on-surface-variant leading-relaxed">{{ dissemination.patent_claims or dissemination.funding_call_matching or "Detalle no disponible" }}</p>
    </div>
  </div>
</section>
{% endif %}

<!-- Audit Integrity Status -->"""
        html = html.replace(integrity_pattern, monograph_section)

    # Script for reports page
    script_pattern = r'<script>.*?</script>\s*</body>'
    new_script = f"""<script>
        {get_active_nav_script()}

        document.querySelectorAll('button').forEach(btn => {{
            btn.addEventListener('click', function() {{
                this.classList.add('scale-95');
                setTimeout(() => this.classList.remove('scale-95'), 100);
            }});
        }});
    </script>
</body>"""
    html = re.sub(script_pattern, new_script, html, flags=re.DOTALL)

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("reports.html actualizado con éxito!")

def update_compliance():
    path = os.path.join(TEMPLATE_DIR, "compliance.html")
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    # Standardize navigation and header
    html = re.sub(r'<aside.*?</aside>', get_standard_aside(is_fixed=True), html, flags=re.DOTALL)
    html = re.sub(r'<header.*?</header>', get_standard_header(), html, flags=re.DOTALL)

    # Reemplazar el contenedor principal para agregar el espacio del coach
    html = html.replace('<main class="ml-64 pt-16 h-screen overflow-y-auto custom-scrollbar bg-background">', '<main class="ml-64 pt-16 h-screen overflow-y-auto custom-scrollbar bg-background mr-80">')

    # Inject Coach Right Sidebar
    if "Enthema AI Coach" not in html:
        html = html.replace('</body>', get_standard_coach() + '\n</body>')

    # Insert Digital Signature Form & Cloud database sync before Contextual Stats if not exists
    if "legalSignatureForm" not in html:
        contextual_stats_pattern = r'<!-- Contextual Stats Summary -->'
        compliance_modules = """<!-- Consentimiento Ético y Firma Digital del Proyecto -->
<section class="col-span-12 bg-surface-base border border-border-subtle rounded-xl p-8 shadow-sm space-y-6 text-left">
  <div class="border-b border-outline-variant pb-4">
    <h3 class="font-headline-md text-on-surface text-[20px] flex items-center gap-2">
      <span class="material-symbols-outlined text-primary">draw</span> Declaración de Consentimiento Ético y Nagoya Protocol
    </h3>
    <p class="font-body-md text-on-surface-variant">Firme electrónicamente para archivar el acta de cumplimiento en el servidor y sincronizar con la nube.</p>
  </div>
  
  <div class="grid grid-cols-12 gap-6">
    <div class="col-span-12 lg:col-span-7 space-y-4">
      <div class="bg-surface-container-low p-5 rounded-lg border border-outline-variant/30 space-y-3">
        <h4 class="font-bold text-on-surface text-sm">📜 Estatus de Cumplimiento Regulatorio</h4>
        <ul class="space-y-2 text-xs text-on-surface-variant">
          <li class="flex items-center justify-between">
            <span>Protocolo de Nagoya (Acceso a Recursos Genéticos):</span>
            <span class="px-2 py-0.5 bg-success/20 text-success rounded font-bold">{{ nagoya_protocol_badge }}</span>
          </li>
          <li class="flex items-center justify-between">
            <span>Declaración de Consentimiento CONABIOS:</span>
            <span class="px-2 py-0.5 bg-primary-container/20 text-primary rounded font-bold">{{ conabios_declaration }}</span>
          </li>
        </ul>
      </div>
      
      <!-- Formulario de Firma -->
      <form id="legalSignatureForm" class="space-y-4">
        <div class="flex items-start gap-2">
          <input type="checkbox" id="accept_terms" name="accept_terms" class="mt-1 border border-outline-variant rounded" required />
          <label for="accept_terms" class="text-xs text-on-surface-variant select-none">
            Confirmo que toda la información científica ingresada es verídica y cumple con los estándares éticos, del Protocolo de Nagoya y de conservación ecológica nacional.
          </label>
        </div>
        
        <div class="grid grid-cols-12 gap-4">
          <div class="col-span-12 md:col-span-8 space-y-1">
            <label class="block text-xs font-label-md text-primary font-bold">FIRMA ELECTRÓNICA (NOMBRE COMPLETO)</label>
            <input type="text" id="signature_name" placeholder="Ej. Dr. Aris Thorne" class="w-full bg-white border border-outline-variant rounded px-3 py-2 text-body-md text-on-surface" required />
          </div>
          
          <div class="col-span-12 md:col-span-4 flex items-end">
            <button type="submit" class="w-full py-2 px-4 bg-primary text-white font-label-md rounded hover:opacity-90 transition-all flex items-center justify-center gap-2">
              <span class="material-symbols-outlined text-[18px]">verified_user</span> Registrar Acta
            </button>
          </div>
        </div>
      </form>
    </div>
    
    <div class="col-span-12 lg:col-span-5 flex items-center justify-center">
      <!-- Success signature status widget -->
      <div id="sigResultWidget" class="hidden bg-success/5 border border-success/20 rounded-2xl p-6 text-center space-y-4 w-full">
        <div class="inline-flex w-12 h-12 rounded-full bg-success/25 items-center justify-center text-success">
          <span class="material-symbols-outlined text-3xl">verified</span>
        </div>
        <div>
          <h4 class="font-bold text-success">Acta Archivada y Sincronizada</h4>
          <p id="sig-hash" class="text-[11px] font-label-sm text-outline select-all"></p>
        </div>
        <div id="sig-qr-container" class="flex justify-center items-center p-2 bg-white rounded-lg inline-block w-28 h-28 mx-auto border border-outline-variant"></div>
      </div>
    </div>
  </div>
</section>

<!-- Base de Datos Cloud Sync (NoSQL Firestore Mock) -->
<section class="col-span-12 bg-surface-base border border-border-subtle rounded-xl p-8 shadow-sm space-y-4 text-left">
  <div class="border-b border-outline-variant pb-4">
    <h3 class="font-headline-md text-on-surface text-[18px] flex items-center gap-2 font-bold">
      <span class="material-symbols-outlined text-primary">cloud_sync</span> Historial de Base de Datos Cloud NoSQL (Firestore Sincronizada)
    </h3>
    <p class="font-body-md text-on-surface-variant">Registro inmutable de hashes científicos persistidos y replicados en la nube.</p>
  </div>
  
  <div class="overflow-x-auto">
    <table class="w-full text-left">
      <thead class="bg-surface-container-low border-b border-outline-variant text-[11px] font-label-sm uppercase tracking-wider text-on-surface-variant font-bold">
        <tr>
          <th class="px-6 py-3">Marcador Temporal</th>
          <th class="px-6 py-3">ID Registro</th>
          <th class="px-6 py-3">Proyecto / Título</th>
          <th class="px-6 py-3">Hash Cifrado</th>
          <th class="px-6 py-3">Proveedor</th>
          <th class="px-6 py-3">Estado</th>
        </tr>
      </thead>
      <tbody id="cloudRecordsTableBody" class="divide-y divide-outline-variant/30 text-xs font-body-md text-on-surface">
        {% for record in cloud_records %}
          <tr class="hover:bg-surface-container-low/50 transition-all">
            <td class="px-6 py-3 text-outline">{{ record.timestamp_utc }}</td>
            <td class="px-6 py-3 font-label-sm text-primary">{{ record._id }}</td>
            <td class="px-6 py-3 font-medium">{{ record.project_title }}</td>
            <td class="px-6 py-3 text-outline select-all">{{ record.hash_proyecto[:18] }}...</td>
            <td class="px-6 py-3 text-on-surface-variant">{{ record.connection_metadata.cloud_sync_provider }}</td>
            <td class="px-6 py-3">
              <span class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-success/15 text-success uppercase">Sincronizado</span>
            </td>
          </tr>
        {% else %}
          <tr>
            <td colspan="6" class="px-6 py-8 text-center text-on-surface-variant">Ningún acta firmada en este perfil. Firme arriba para sincronizar.</td>
          </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</section>

<!-- Contextual Stats Summary -->"""
        html = html.replace(contextual_stats_pattern, compliance_modules)

    # Script for signature submit and table update
    script_pattern = r'<script>.*?</script>\s*</body>'
    new_script = f"""<script>
        {get_active_nav_script()}

        document.getElementById('legalSignatureForm').addEventListener('submit', async (e) => {{
            e.preventDefault();
            const payload = {{
                accept_terms: document.getElementById('accept_terms').checked,
                signature_name: document.getElementById('signature_name').value
            }};

            try {{
                const res = await fetch('/api/legal/sign', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(payload)
                }});
                const data = await res.json();
                if (data.status === 'success') {{
                    // Show success widget
                    document.getElementById('sigResultWidget').classList.remove('hidden');
                    document.getElementById('sig-hash').innerText = 'HASH ACTA: ' + data.hash_proyecto;
                    document.getElementById('sig-qr-container').innerHTML = data.cloud_record.qr_svg_mock || '<svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100" fill="#f8f9fa"/><path d="M10 10h20v20H10zM70 10h20v20H70zM10 70h20v20H10zM40 40h20v20H40z" fill="#1a73e8"/></svg>';
                    
                    // Add new sync row to the table
                    const tbody = document.getElementById('cloudRecordsTableBody');
                    const record = data.cloud_record;
                    const newRow = document.createElement('tr');
                    newRow.className = "hover:bg-surface-container-low/50 transition-all font-bold bg-success/5 animate-pulse text-on-surface";
                    newRow.innerHTML = `
                        <td class="px-6 py-3 text-outline">${{record.timestamp_utc}}</td>
                        <td class="px-6 py-3 font-label-sm text-primary">${{record._id}}</td>
                        <td class="px-6 py-3 font-medium">${{record.project_title}}</td>
                        <td class="px-6 py-3 text-outline select-all">${{record.hash_proyecto.substring(0, 18)}}...</td>
                        <td class="px-6 py-3 text-on-surface-variant">${{record.connection_metadata.cloud_sync_provider}}</td>
                        <td class="px-6 py-3">
                          <span class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-success/15 text-success uppercase">Sincronizado</span>
                        </td>
                    `;
                    
                    // Clear empty row if exists
                    if (tbody.innerText.includes('Ningún acta firmada')) {{
                        tbody.innerHTML = '';
                    }}
                    tbody.prepend(newRow);
                    
                    alert('✍️ Acta ética firmada con éxito! Registro sincronizado en la base de datos Firestore Cloud Mock.');
                }} else {{
                    alert('Error guardando firma: ' + data.message);
                }}
            }} catch (err) {{
                alert('Error de red: ' + err.message);
            }}
        }});

        // Smooth animations on load
        document.addEventListener('DOMContentLoaded', () => {{
            const panels = document.querySelectorAll('section');
            panels.forEach((panel, index) => {{
                panel.style.opacity = '0';
                panel.style.transform = 'translateY(10px)';
                panel.style.transition = 'all 0.4s ease-out ' + (index * 0.1) + 's';
                setTimeout(() => {{
                    panel.style.opacity = '1';
                    panel.style.transform = 'translateY(0)';
                }}, 50);
            }});
        }});
    </script>
</body>"""
    html = re.sub(script_pattern, new_script, html, flags=re.DOTALL)

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("compliance.html actualizado con éxito!")

def update_configuration():
    path = os.path.join(TEMPLATE_DIR, "configuration.html")
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    # Standardize navigation and header
    html = re.sub(r'<aside.*?</aside>', get_standard_aside(is_fixed=True), html, flags=re.DOTALL)
    html = re.sub(r'<header.*?</header>', get_standard_header(), html, flags=re.DOTALL)

    # Reemplazar el contenedor principal para agregar el espacio del coach
    html = html.replace('<div class="ml-64 flex flex-col min-h-screen">', '<div class="ml-64 flex flex-col min-h-screen mr-80">')

    # Inject Coach Right Sidebar
    if "Enthema AI Coach" not in html:
        html = html.replace('</body>', get_standard_coach() + '\n</body>')

    # Script replacement for active nav and reset click action
    script_pattern = r'<script>.*?</script>\s*</body>'
    new_script = f"""<script>
        {get_active_nav_script()}

        // Reset click action
        document.getElementById('btn-reset').addEventListener('click', async () => {{
            if (!confirm('¿Está seguro de que desea reiniciar completamente el estado de su simulación? Se borrarán todos los perfiles cargados, bases de datos y flujos en memoria.')) {{
                return;
            }}
            
            const btn = document.getElementById('btn-reset');
            const status = document.getElementById('reset-status');
            btn.disabled = true;
            status.innerText = "Restableciendo...";
            status.className = "text-xs font-semibold text-on-surface-variant block animate-pulse";

            try {{
                const res = await fetch('/api/configuration/reset', {{ method: 'POST' }});
                const data = await res.json();
                
                if (res.ok && data.status === 'success') {{
                    status.className = "text-xs font-semibold text-success block";
                    status.innerText = "🔄 ¡Estado restablecido con éxito! Redirigiendo...";
                    setTimeout(() => {{
                        window.location.href = '/';
                    }}, 1200);
                }} else {{
                    status.className = "text-xs font-semibold text-danger block";
                    status.innerText = "Error: " + (data.detail || 'No se pudo reiniciar el estado.');
                    btn.disabled = false;
                }}
            }} catch (err) {{
                status.className = "text-xs font-semibold text-danger block";
                status.innerText = "Error de red: " + err.message;
                btn.disabled = false;
            }}
        }});
    </script>
</body>"""
    html = re.sub(script_pattern, new_script, html, flags=re.DOTALL)

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("configuration.html actualizado con éxito!")

def update_onboarding():
    path = os.path.join(TEMPLATE_DIR, "onboarding.html")
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    # Standardize navigation and header
    html = re.sub(r'<aside.*?</aside>', get_standard_aside(is_fixed=True), html, flags=re.DOTALL)
    html = re.sub(r'<header.*?</header>', get_standard_header(), html, flags=re.DOTALL)

    # Reemplazar el contenedor principal para agregar el espacio del coach
    html = html.replace('<main class="flex-grow ml-64 min-w-0">', '<main class="flex-grow ml-64 min-w-0 mr-80">')

    # Inject Coach Right Sidebar
    if "Enthema AI Coach" not in html:
        html = html.replace('</body>', get_standard_coach() + '\n</body>')

    # 3. Insertar formulario Onboarding antes de la sección Testimonios si no está
    if "profileForm" not in html:
        testimonial_pattern = r'<!-- Testimonials - Impacto Global -->'
        onboarding_form = """<!-- Onboarding Form Section -->
<section id="onboarding-form-section" class="bg-surface-container-lowest border border-outline-variant rounded-3xl p-10 lg:p-12 shadow-sm space-y-8">
  <div class="border-b border-outline-variant pb-6 text-left">
    <h2 class="font-headline-lg text-on-surface text-xl font-bold">🧬 Configuración Científica y Académica (Onboarding)</h2>
    <p class="font-body-md text-on-surface-variant">Establezca los parámetros clave de su ADN intelectual y defina la revista o patente destino para su investigación.</p>
  </div>
  
  <form id="profileForm" class="grid grid-cols-12 gap-6 text-on-surface">
    <!-- Col 1: Nombre del Investigador -->
    <div class="col-span-12 md:col-span-6 space-y-2 text-left">
      <label class="block font-label-md text-primary tracking-wide text-xs">NOMBRE COMPLETO</label>
      <input type="text" id="name" name="name" value="{{ profile.name }}" class="w-full bg-white border border-outline-variant rounded-lg px-4 py-2.5 text-body-md focus:border-2 focus:border-primary focus:ring-0 outline-none transition-all text-on-surface" required />
    </div>

    <!-- Col 2: Institución -->
    <div class="col-span-12 md:col-span-6 space-y-2 text-left">
      <label class="block font-label-md text-primary tracking-wide text-xs">INSTITUCIÓN O FIRMA CONSULTORA</label>
      <input type="text" id="institution" name="institution" value="{{ profile.institution }}" class="w-full bg-white border border-outline-variant rounded-lg px-4 py-2.5 text-body-md focus:border-2 focus:border-primary focus:ring-0 outline-none transition-all text-on-surface" required />
    </div>

    <!-- Col 3: Rol del Usuario -->
    <div class="col-span-12 md:col-span-4 space-y-2 text-left">
      <label class="block font-label-md text-primary tracking-wide text-xs">ROL DE OPERACIÓN EN LA SUITE</label>
      <select id="user_role" name="user_role" class="w-full bg-white border border-outline-variant rounded-lg px-4 py-2.5 text-body-md focus:border-2 focus:border-primary focus:ring-0 outline-none transition-all text-on-surface">
        <option value="classic_researcher" {% if profile.user_role == 'classic_researcher' %}selected{% endif %}>Investigador Clásico</option>
        <option value="investment_consultant" {% if profile.user_role == 'investment_consultant' %}selected{% endif %}>Consultor de Inversión</option>
      </select>
    </div>

    <!-- Col 4: Postura Epistémica -->
    <div class="col-span-12 md:col-span-4 space-y-2 text-left">
      <label class="block font-label-md text-primary tracking-wide text-xs">POSTURA EPISTÉMICA</label>
      <select id="epistemologic_stance" name="epistemologic_stance" class="w-full bg-white border border-outline-variant rounded-lg px-4 py-2.5 text-body-md focus:border-2 focus:border-primary focus:ring-0 outline-none transition-all text-on-surface">
        <option value="Positivista" {% if profile.epistemologic_stance == 'Positivista' %}selected{% endif %}>Positivista (Experimental/Matemático)</option>
        <option value="Constructivista" {% if profile.epistemologic_stance == 'Constructivista' %}selected{% endif %}>Constructivista (Cualitativo/Social)</option>
        <option value="Hermenéutica" {% if profile.epistemologic_stance == 'Hermenéutica' %}selected{% endif %}>Hermenéutica (Arte/Vanguardias)</option>
        <option value="Mixed_Methods" {% if profile.epistemologic_stance == 'Mixed_Methods' %}selected{% endif %}>Métodos Mixtos (Cuali-Cuanti)</option>
      </select>
    </div>

    <!-- Col 5: Fase de Madurez -->
    <div class="col-span-12 md:col-span-4 space-y-2 text-left">
      <label class="block font-label-md text-primary tracking-wide text-xs">FASE DE MADUREZ CIENTÍFICA</label>
      <select id="research_maturity_stage" name="research_maturity_stage" class="w-full bg-white border border-outline-variant rounded-lg px-4 py-2.5 text-body-md focus:border-2 focus:border-primary focus:ring-0 outline-none transition-all text-on-surface">
        <option value="Ideación" {% if profile.research_maturity_stage == 'Ideación' %}selected{% endif %}>Ideación Activa (Early-stage sin datos reales)</option>
        <option value="En Curso" {% if profile.research_maturity_stage == 'En Curso' %}selected{% endif %}>En Curso (Con recolección de muestras)</option>
        <option value="Consolidado" {% if profile.research_maturity_stage == 'Consolidado' %}selected{% endif %}>Consolidado (Dataset completo)</option>
      </select>
    </div>

    <!-- Col 6: Canal / Revista Objetivo -->
    <div class="col-span-12 md:col-span-4 space-y-2 text-left">
      <label class="block font-label-md text-primary tracking-wide text-xs">REVISTA O PATENTE OBJETIVO</label>
      <select id="target_publication_objective" name="target_publication_objective" class="w-full bg-white border border-outline-variant rounded-lg px-4 py-2.5 text-body-md focus:border-2 focus:border-primary focus:ring-0 outline-none transition-all text-on-surface">
        <option value="Nature" {% if profile.target_publication_objective == 'Nature' %}selected{% endif %}>Nature (STEM)</option>
        <option value="IEEE" {% if profile.target_publication_objective == 'IEEE' %}selected{% endif %}>IEEE (Ingeniería y Materiales)</option>
        <option value="World Development" {% if profile.target_publication_objective == 'World Development' %}selected{% endif %}>World Development (Sociales/Gini)</option>
        <option value="Leonardo" {% if profile.target_publication_objective == 'Leonardo' %}selected{% endif %}>Leonardo (Arte/Interactivos)</option>
        <option value="HBR" {% if profile.target_publication_objective == 'HBR' %}selected{% endif %}>Harvard Business Review (Negocios)</option>
        <option value="ONAPI" {% if profile.target_publication_objective == 'ONAPI' %}selected{% endif %}>ONAPI (Registro de Patentes)</option>
        <option value="ONDA" {% if profile.target_publication_objective == 'ONDA' %}selected{% endif %}>ONDA (Registro de Obras Artísticas)</option>
      </select>
    </div>

    <!-- Col 7: ORCID -->
    <div class="col-span-12 md:col-span-4 space-y-2 text-left">
      <label class="block font-label-md text-primary tracking-wide text-xs">IDENTIFICADOR CIENTÍFICO ORCID</label>
      <input type="text" id="orcid" name="orcid" value="{{ profile.orcid or '' }}" placeholder="0000-0000-0000-0000" class="w-full bg-white border border-outline-variant rounded-lg px-4 py-2.5 text-body-md focus:border-2 focus:border-primary focus:ring-0 outline-none transition-all text-on-surface" />
    </div>

    <!-- Col 8: Financiamiento Objetivo (USD) -->
    <div class="col-span-12 md:col-span-4 space-y-2 text-left">
      <label class="block font-label-md text-primary tracking-wide text-xs">FINANCIAMIENTO OBJETIVO (USD)</label>
      <input type="number" id="target_fund_usd" name="target_fund_usd" value="{{ profile.target_fund_usd }}" class="w-full bg-white border border-outline-variant rounded-lg px-4 py-2.5 text-body-md focus:border-2 focus:border-primary focus:ring-0 outline-none transition-all text-on-surface" />
    </div>

    <div class="col-span-12 flex justify-end gap-4 pt-4">
      <button type="submit" class="px-8 py-3 bg-primary text-on-primary rounded-lg font-headline-md text-body-lg hover:shadow-lg hover:bg-primary/95 transition-all flex items-center gap-2 font-bold">
        <span class="material-symbols-outlined" data-icon="save">save</span> Guardar Configuración
      </button>
    </div>
  </form>
</section>

<!-- Import Panel -->
<section class="bg-surface-container-lowest border border-outline-variant rounded-3xl p-10 lg:p-12 shadow-sm space-y-8">
  <div class="border-b border-outline-variant pb-6 text-left">
    <h2 class="font-headline-lg text-on-surface text-xl font-bold">📂 Ingesta de Historial de Investigación (Importación Pasiva)</h2>
    <p class="font-body-md text-on-surface-variant">Cargue sus notas de Obsidian (.md), reportes en formato RIS de Zotero (.ris), BibTeX (.bib) o cuadernos de Jupyter (.ipynb) para compilar su perfil científico de forma automática.</p>
  </div>
  
  <div class="border-2 border-dashed border-outline-variant rounded-2xl p-8 text-center space-y-4 hover:border-primary transition-all bg-surface-container-low/20">
    <span class="material-symbols-outlined text-[48px] text-primary" data-icon="cloud_upload">cloud_upload</span>
    <p class="font-body-md text-on-surface">Arrastre su archivo de investigación aquí o haga clic para cargarlo</p>
    <input type="file" id="academicFile" class="hidden" accept=".md,.ris,.bib,.bibtex,.ipynb" />
    <button type="button" onclick="document.getElementById('academicFile').click()" class="px-6 py-2 border border-outline-variant text-primary rounded-lg font-label-md hover:bg-surface-container transition-all">Seleccionar Archivo</button>
    <p class="font-label-sm text-outline">Formatos válidos: Markdown (.md), RIS (.ris), BibTeX (.bib), Jupyter Notebook (.ipynb)</p>
  </div>
  
  <div id="uploadStatus" class="hidden font-label-md p-4 rounded-lg text-left"></div>
</section>

<!-- Testimonials - Impacto Global -->"""
        html = html.replace(testimonial_pattern, onboarding_form)

    # 4. Actualizar Script de navegación activa y llamadas API
    script_pattern = r'<script>.*?</script>\s*</body>'
    new_script = f"""<script>
        {get_active_nav_script()}

        // Submit Profile Form
        document.getElementById('profileForm').addEventListener('submit', async (e) => {{
            e.preventDefault();
            const payload = {{
                name: document.getElementById('name').value,
                institution: document.getElementById('institution').value,
                user_role: document.getElementById('user_role').value,
                epistemologic_stance: document.getElementById('epistemologic_stance').value,
                research_maturity_stage: document.getElementById('research_maturity_stage').value,
                target_publication_objective: document.getElementById('target_publication_objective').value,
                orcid: document.getElementById('orcid').value,
                target_fund_usd: parseFloat(document.getElementById('target_fund_usd').value) || 2500000.0,
                discount_rate: 0.10
            }};

            try {{
                const response = await fetch('/api/profile', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(payload)
                }});
                const result = await response.json();
                if (result.status === 'success') {{
                    // Si la madurez es Ideación, generar pilotos automáticamente
                    if (payload.research_maturity_stage === 'Ideación') {{
                        await fetch('/api/data/synthetic', {{ method: 'POST' }});
                    }}
                    window.location.href = '/dashboard';
                }} else {{
                    alert('Error guardando perfil: ' + result.message);
                }}
            }} catch (err) {{
                alert('Error de conexión: ' + err.message);
            }}
        }});

        // File upload handling
        document.getElementById('academicFile').addEventListener('change', async (e) => {{
            const file = e.target.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('file', file);

            const statusDiv = document.getElementById('uploadStatus');
            statusDiv.className = "block font-label-md p-4 rounded-lg bg-primary-container/10 text-primary text-left";
            statusDiv.innerHTML = "Procesando archivo e integrando genoma intelectual...";

            try {{
                const response = await fetch('/api/profile/upload', {{
                    method: 'POST',
                    body: formData
                }});
                const result = await response.json();
                if (response.ok) {{
                    statusDiv.className = "block font-label-md p-4 rounded-lg bg-success/10 text-success text-left";
                    statusDiv.innerHTML = `🧬 Ingesta exitosa! Perfil extraído: ${{result.message}}. Cargando valores en el formulario...`;
                    
                    // Actualizar formulario
                    if (result.profile) {{
                        document.getElementById('name').value = result.profile.name || '';
                        document.getElementById('institution').value = result.profile.institution || '';
                        document.getElementById('user_role').value = result.profile.user_role || 'classic_researcher';
                        document.getElementById('epistemologic_stance').value = result.profile.epistemologic_stance || 'Mixed_Methods';
                        document.getElementById('research_maturity_stage').value = result.profile.research_maturity_stage || 'En Curso';
                        document.getElementById('target_publication_objective').value = result.profile.target_publication_objective || 'Nature';
                        document.getElementById('orcid').value = result.profile.orcid || '';
                        document.getElementById('target_fund_usd').value = result.profile.target_fund_usd || 2500000;
                    }}
                }} else {{
                    statusDiv.className = "block font-label-md p-4 rounded-lg bg-danger/10 text-danger text-left";
                    statusDiv.innerHTML = "Error: " + result.detail;
                }}
            }} catch (err) {{
                statusDiv.className = "block font-label-md p-4 rounded-lg bg-danger/10 text-danger text-left";
                statusDiv.innerHTML = "Error de conexión: " + err.message;
            }}
        }});
    </script>
</body>"""
    html = re.sub(script_pattern, new_script, html, flags=re.DOTALL)

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("onboarding.html (index) actualizado con éxito!")

if __name__ == "__main__":
    print("Iniciando compilación completa de todos los Stitch templates...")
    update_onboarding()
    update_dashboard()
    update_data_analysis()
    update_semantic_modeling()
    update_finance()
    update_reports()
    update_compliance()
    update_configuration()
    print("¡Todos los templates actualizados, estilizados e integrados con el Enthema AI Coach y la API REST con éxito!")
