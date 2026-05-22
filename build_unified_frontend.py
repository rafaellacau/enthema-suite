# -*- coding: utf-8 -*-
"""
Script de automatización para estructurar los templates de Stitch
"""
import os
import re

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

def update_onboarding():
    path = os.path.join(TEMPLATE_DIR, "onboarding.html")
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Reemplazar el Header del Investigador
    header_pattern = r'<div class="text-right">\s*<p class="font-label-md text-on-surface font-bold leading-none">Dr\. Aris Thorne</p>\s*<p class="font-label-sm text-outline">Investigador Principal</p>\s*</div>'
    new_header = """<div class="text-right">
<p class="font-label-md text-on-surface font-bold leading-none">{{ profile.name }}</p>
<p class="font-label-sm text-outline">{% if profile.user_role == 'investment_consultant' %}Consultor de Inversión{% else %}Investigador Principal{% endif %}</p>
</div>"""
    html = re.sub(header_pattern, new_header, html)

    # 2. Reemplazar enlaces del Sidebar
    nav_pattern = r'<nav class="flex-grow space-y-1 px-4">.*?</nav>'
    new_nav = """<nav class="flex-grow space-y-1 px-4">
<a class="flex items-center gap-3 px-3 py-3 rounded-lg transition-all duration-150" href="/dashboard">
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
<span class="font-label-md text-label-md">Modelado</span>
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
</nav>"""
    html = re.sub(nav_pattern, new_nav, html, flags=re.DOTALL)

    # 3. Insertar formulario Onboarding antes de la sección Testimonios
    testimonial_pattern = r'<!-- Testimonials - Impacto Global -->'
    onboarding_form = """<!-- Onboarding Form Section -->
<section id="onboarding-form-section" class="bg-surface-container-lowest border border-outline-variant rounded-3xl p-10 lg:p-12 shadow-sm space-y-8">
  <div class="border-b border-outline-variant pb-6">
    <h2 class="font-headline-lg text-on-surface">🧬 Configuración Científica y Académica (Onboarding)</h2>
    <p class="font-body-md text-on-surface-variant">Establezca los parámetros clave de su ADN intelectual y defina la revista o patente destino para su investigación.</p>
  </div>
  
  <form id="profileForm" class="grid grid-cols-12 gap-6">
    <!-- Col 1: Nombre del Investigador -->
    <div class="col-span-12 md:col-span-6 space-y-2 text-left">
      <label class="block font-label-md text-primary tracking-wide text-xs">NOMBRE COMPLETO</label>
      <input type="text" id="name" name="name" value="{{ profile.name }}" class="w-full bg-white border border-outline-variant rounded-lg px-4 py-2.5 text-body-md focus:border-2 focus:border-primary focus:ring-0 outline-none transition-all" required />
    </div>

    <!-- Col 2: Institución -->
    <div class="col-span-12 md:col-span-6 space-y-2 text-left">
      <label class="block font-label-md text-primary tracking-wide text-xs">INSTITUCIÓN O FIRMA CONSULTORA</label>
      <input type="text" id="institution" name="institution" value="{{ profile.institution }}" class="w-full bg-white border border-outline-variant rounded-lg px-4 py-2.5 text-body-md focus:border-2 focus:border-primary focus:ring-0 outline-none transition-all" required />
    </div>

    <!-- Col 3: Rol del Usuario -->
    <div class="col-span-12 md:col-span-4 space-y-2 text-left">
      <label class="block font-label-md text-primary tracking-wide text-xs">ROL DE OPERACIÓN EN LA SUITE</label>
      <select id="user_role" name="user_role" class="w-full bg-white border border-outline-variant rounded-lg px-4 py-2.5 text-body-md focus:border-2 focus:border-primary focus:ring-0 outline-none transition-all">
        <option value="classic_researcher" {% if profile.user_role == 'classic_researcher' %}selected{% endif %}>Investigador Clásico</option>
        <option value="investment_consultant" {% if profile.user_role == 'investment_consultant' %}selected{% endif %}>Consultor de Inversión</option>
      </select>
    </div>

    <!-- Col 4: Postura Epistémica -->
    <div class="col-span-12 md:col-span-4 space-y-2 text-left">
      <label class="block font-label-md text-primary tracking-wide text-xs">POSTURA EPISTÉMICA</label>
      <select id="epistemologic_stance" name="epistemologic_stance" class="w-full bg-white border border-outline-variant rounded-lg px-4 py-2.5 text-body-md focus:border-2 focus:border-primary focus:ring-0 outline-none transition-all">
        <option value="Positivista" {% if profile.epistemologic_stance == 'Positivista' %}selected{% endif %}>Positivista (Experimental/Matemático)</option>
        <option value="Constructivista" {% if profile.epistemologic_stance == 'Constructivista' %}selected{% endif %}>Constructivista (Cualitativo/Social)</option>
        <option value="Hermenéutica" {% if profile.epistemologic_stance == 'Hermenéutica' %}selected{% endif %}>Hermenéutica (Arte/Vanguardias)</option>
        <option value="Mixed_Methods" {% if profile.epistemologic_stance == 'Mixed_Methods' %}selected{% endif %}>Métodos Mixtos (Cuali-Cuanti)</option>
      </select>
    </div>

    <!-- Col 5: Fase de Madurez -->
    <div class="col-span-12 md:col-span-4 space-y-2 text-left">
      <label class="block font-label-md text-primary tracking-wide text-xs">FASE DE MADUREZ CIENTÍFICA</label>
      <select id="research_maturity_stage" name="research_maturity_stage" class="w-full bg-white border border-outline-variant rounded-lg px-4 py-2.5 text-body-md focus:border-2 focus:border-primary focus:ring-0 outline-none transition-all">
        <option value="Ideación" {% if profile.research_maturity_stage == 'Ideación' %}selected{% endif %}>Ideación Activa (Early-stage sin datos reales)</option>
        <option value="En Curso" {% if profile.research_maturity_stage == 'En Curso' %}selected{% endif %}>En Curso (Con recolección de muestras)</option>
        <option value="Consolidado" {% if profile.research_maturity_stage == 'Consolidado' %}selected{% endif %}>Consolidado (Dataset completo)</option>
      </select>
    </div>

    <!-- Col 6: Canal / Revista Objetivo -->
    <div class="col-span-12 md:col-span-4 space-y-2 text-left">
      <label class="block font-label-md text-primary tracking-wide text-xs">REVISTA O PATENTE OBJETIVO</label>
      <select id="target_publication_objective" name="target_publication_objective" class="w-full bg-white border border-outline-variant rounded-lg px-4 py-2.5 text-body-md focus:border-2 focus:border-primary focus:ring-0 outline-none transition-all">
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
      <input type="text" id="orcid" name="orcid" value="{{ profile.orcid or '' }}" placeholder="0000-0000-0000-0000" class="w-full bg-white border border-outline-variant rounded-lg px-4 py-2.5 text-body-md focus:border-2 focus:border-primary focus:ring-0 outline-none transition-all" />
    </div>

    <!-- Col 8: Financiamiento Objetivo (USD) -->
    <div class="col-span-12 md:col-span-4 space-y-2 text-left">
      <label class="block font-label-md text-primary tracking-wide text-xs">FINANCIAMIENTO OBJETIVO (USD)</label>
      <input type="number" id="target_fund_usd" name="target_fund_usd" value="{{ profile.target_fund_usd }}" class="w-full bg-white border border-outline-variant rounded-lg px-4 py-2.5 text-body-md focus:border-2 focus:border-primary focus:ring-0 outline-none transition-all" />
    </div>

    <div class="col-span-12 flex justify-end gap-4 pt-4">
      <button type="submit" class="px-8 py-3 bg-primary text-on-primary rounded-lg font-headline-md text-body-lg hover:shadow-lg hover:bg-primary/95 transition-all flex items-center gap-2">
        <span class="material-symbols-outlined" data-icon="save">save</span> Guardar Configuración
      </button>
    </div>
  </form>
</section>

<!-- Import Panel -->
<section class="bg-surface-container-lowest border border-outline-variant rounded-3xl p-10 lg:p-12 shadow-sm space-y-8">
  <div class="border-b border-outline-variant pb-6 text-left">
    <h2 class="font-headline-lg text-on-surface">📂 Ingesta de Historial de Investigación (Importación Pasiva)</h2>
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
    new_script = """<script>
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

        // Submit Profile Form
        document.getElementById('profileForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                name: document.getElementById('name').value,
                institution: document.getElementById('institution').value,
                user_role: document.getElementById('user_role').value,
                epistemologic_stance: document.getElementById('epistemologic_stance').value,
                research_maturity_stage: document.getElementById('research_maturity_stage').value,
                target_publication_objective: document.getElementById('target_publication_objective').value,
                orcid: document.getElementById('orcid').value,
                target_fund_usd: parseFloat(document.getElementById('target_fund_usd').value) || 2500000.0,
                discount_rate: 0.10
            };

            try {
                const response = await fetch('/api/profile', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const result = await response.json();
                if (result.status === 'success') {
                    // Si la madurez es Ideación, generar pilotos automáticamente
                    if (payload.research_maturity_stage === 'Ideación') {
                        await fetch('/api/data/synthetic', { method: 'POST' });
                    }
                    window.location.href = '/dashboard';
                } else {
                    alert('Error guardando perfil: ' + result.message);
                }
            } catch (err) {
                alert('Error de conexión: ' + err.message);
            }
        });

        // File upload handling
        document.getElementById('academicFile').addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('file', file);

            const statusDiv = document.getElementById('uploadStatus');
            statusDiv.className = "block font-label-md p-4 rounded-lg bg-primary-container/10 text-primary text-left";
            statusDiv.innerHTML = "Procesando archivo e integrando genoma intelectual...";

            try {
                const response = await fetch('/api/profile/upload', {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();
                if (response.ok) {
                    statusDiv.className = "block font-label-md p-4 rounded-lg bg-success/10 text-success text-left";
                    statusDiv.innerHTML = `🧬 Ingesta exitosa! Perfil extraído: ${result.message}. Cargando valores en el formulario...`;
                    
                    // Actualizar formulario
                    if (result.profile) {
                        document.getElementById('name').value = result.profile.name || '';
                        document.getElementById('institution').value = result.profile.institution || '';
                        document.getElementById('user_role').value = result.profile.user_role || 'classic_researcher';
                        document.getElementById('epistemologic_stance').value = result.profile.epistemologic_stance || 'Mixed_Methods';
                        document.getElementById('research_maturity_stage').value = result.profile.research_maturity_stage || 'En Curso';
                        document.getElementById('target_publication_objective').value = result.profile.target_publication_objective || 'Nature';
                        document.getElementById('orcid').value = result.profile.orcid || '';
                        document.getElementById('target_fund_usd').value = result.profile.target_fund_usd || 2500000;
                    }
                } else {
                    statusDiv.className = "block font-label-md p-4 rounded-lg bg-danger/10 text-danger text-left";
                    statusDiv.innerHTML = "Error: " + result.detail;
                }
            } catch (err) {
                statusDiv.className = "block font-label-md p-4 rounded-lg bg-danger/10 text-danger text-left";
                statusDiv.innerHTML = "Error de conexión: " + err.message;
            }
        });
    </script>
</body>"""
    html = re.sub(script_pattern, new_script, html, flags=re.DOTALL)

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("onboarding.html actualizado con éxito!")

if __name__ == "__main__":
    update_onboarding()
