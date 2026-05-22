import networkx as nx
import plotly.graph_objects as go
from typing import List, Tuple
from .models import ResearcherProfile, ConsortiumProfile

class SemanticGraphEngine:
    """
    Motor de Grafos Semánticos basado en NetworkX y Plotly.
    Construye, fusiona y visualiza la red conceptual colectiva de los investigadores,
    detectando sinergias y vacíos estructurales.
    """
    
    @staticmethod
    def build_consortium_graph(consortium: ConsortiumProfile) -> Tuple[nx.Graph, List[str], List[str]]:
        """
        Toma un consorcio de investigadores, realiza la fusión de sus grafos conceptuales
        y calcula las sinergias (nodos compartidos) y los vacíos (nodos desconectados).
        Retorna (Grafo, Nodos_Sinergias, Nodos_Vacios).
        """
        G = nx.Graph()
        
        # 1. Inyectar nodos de los investigadores y sus palabras clave
        concept_owners = {}
        for member in consortium.members:
            G.add_node(member.name, type="researcher", size=30, color="#1f6feb")
            for kw in member.local_keywords:
                clean_kw = kw.strip().capitalize()
                G.add_node(clean_kw, type="concept", size=15, color="#3fb950")
                G.add_edge(member.name, clean_kw, weight=1.0)
                
                if clean_kw not in concept_owners:
                    concept_owners[clean_kw] = []
                concept_owners[clean_kw].append(member.name)
                
        # 2. Agregar enlaces semánticos automáticos entre conceptos según temas afines
        concepts = [n for n, attr in G.nodes(data=True) if attr.get("type") == "concept"]
        
        # Heurísticas de puentes semánticos comunes (conectar conceptos relacionados)
        semantic_bridges = [
            ("Sargazo", "Metales_pesados"),
            ("Sargazo", "Biofertilizante"),
            ("Biofertilizante", "Metales_pesados"),
            ("Inflación", "Pyme"),
            ("Crédito", "Pyme"),
            ("Crédito", "Inflación"),
            ("Prótesis_falanges", "Simulación"),
            ("Prótesis_falanges", "Biomecánica")
        ]
        
        for c1, c2 in semantic_bridges:
            c1_cap, c2_cap = c1.capitalize(), c2.capitalize()
            if G.has_node(c1_cap) and G.has_node(c2_cap):
                G.add_edge(c1_cap, c2_cap, weight=0.5)
                
        # 3. Calcular sinergias (conceptos en los que coinciden más de 1 investigador)
        synergies = [concept for concept, owners in concept_owners.items() if len(owners) > 1]
        
        # 4. Calcular vacíos estructurales del consorcio
        all_concepts_lower = [c.lower() for c in concepts]
        gaps = []
        
        # Heurísticas de vacíos en base al foco y la convocatoria
        if "sargazo" in all_concepts_lower:
            if "toxicidad" not in all_concepts_lower and "metales_pesados" in all_concepts_lower:
                gaps.append("ToxicidadSuelo (Falta experto en Bioética o Agronomía)")
            if "comercial" not in all_concepts_lower:
                gaps.append("TransferenciaComercial (Falta Gestor o Consultor)")
                
        if "inflación" in all_concepts_lower:
            if "econometría" not in all_concepts_lower:
                gaps.append("ModeladoEconométrico (Falta experto cuantitativo)")
                
        if "prótesis_falanges" in all_concepts_lower:
            if "cirugía" not in all_concepts_lower:
                gaps.append("ValidaciónClínica (Falta cirujano de mano en el equipo)")

        return G, synergies, gaps

    @staticmethod
    def draw_plotly_network(G: nx.Graph, theme: str = "google") -> go.Figure:
        """
        Dibuja un gráfico interactivo premium con Plotly a partir de la red NetworkX.
        Utiliza una jerarquía visual de tres capas (Investigadores, Sinergias y Conceptos)
        con colores de alta gama al estilo Google Material Design y tipografía impecable.
        Soporta temas de estilo dinámico ("google" vs "cyberpunk").
        """
        if len(G.nodes) == 0:
            fig = go.Figure()
            fig.update_layout(
                title=dict(
                    text="Sin nodos cargados. Configura un consorcio para ver el grafo semántico.",
                    font=dict(family="'Space Grotesk', sans-serif", size=14, color="#94a3b8")
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
            return fig

        # Spring layout con una distribución más abierta y espaciosa
        pos = nx.spring_layout(G, k=0.55, iterations=60, seed=42)
        
        # 1. Trazar aristas con un color gris suave semitransparente
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
        edge_color = 'rgba(95, 99, 104, 0.15)' if theme == "google" else 'rgba(203, 213, 225, 0.4)'
        edge_width = 1.0 if theme == "google" else 1.5
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=edge_width, color=edge_color),
            hoverinfo='none',
            mode='lines'
        )
        
        # Calcular sinergias localmente para colorear
        concept_owners = {}
        for u, v in G.edges():
            researcher = None
            concept = None
            if G.nodes[u].get("type") == "researcher":
                researcher, concept = u, v
            elif G.nodes[v].get("type") == "researcher":
                researcher, concept = v, u
            
            if researcher and concept:
                if concept not in concept_owners:
                    concept_owners[concept] = []
                concept_owners[concept].append(researcher)
        
        synergies = [c for c, owners in concept_owners.items() if len(owners) > 1]

        # 2. Organizar nodos en 3 trazas distintas para un control estético perfecto
        # Capa A: Investigadores
        res_x, res_y, res_text, res_hover = [], [], [], []
        # Capa B: Sinergias (Conceptos compartidos)
        syn_x, syn_y, syn_text, syn_hover = [], [], [], []
        # Capa C: Conceptos individuales
        con_x, con_y, con_text, con_hover = [], [], [], []

        for node in G.nodes():
            x, y = pos[node]
            node_type = G.nodes[node].get("type", "concept")
            
            if node_type == "researcher":
                res_x.append(x)
                res_y.append(y)
                res_text.append(f"<b>{node}</b>")
                deg = G.degree(node)
                res_hover.append(f"👤 <b>Investigador:</b> {node}<br>⚡ Conexiones en Red: {deg} conceptos")
            elif node in synergies:
                syn_x.append(x)
                syn_y.append(y)
                syn_text.append(node)
                owners_list = ", ".join(concept_owners[node])
                syn_hover.append(f"🔥 <b>Sinergia Colectiva:</b> {node}<br>💡 Compartido por: {owners_list}")
            else:
                con_x.append(x)
                con_y.append(y)
                con_text.append(node)
                con_hover.append(f"🌱 <b>Concepto Clave:</b> {node}")

        # Trazador para Investigadores (Círculos grandes azul Google con borde blanco)
        res_text_color = "#202124" if theme == "google" else "#ffffff"
        res_line_color = "#bdc1c6" if theme == "google" else "#ffffff"
        res_trace = go.Scatter(
            x=res_x, y=res_y,
            mode='markers+text',
            hoverinfo='text',
            text=res_text,
            hovertext=res_hover,
            textposition="top center",
            textfont=dict(family="'Space Grotesk', sans-serif", size=11, color=res_text_color),
            marker=dict(
                color='#1a73e8',  # Google Blue
                size=32,
                line=dict(width=3, color=res_line_color),
                shadow=dict(color='rgba(0,0,0,0.15)' if theme == "google" else 'rgba(0,0,0,0.3)', width=5, x=0, y=2)
            )
        )

        # Trazador para Sinergias (Círculos medianos ámbar vibrante con borde blanco)
        syn_text_color = "#b06000" if theme == "google" else "#fcd34d"
        syn_line_color = "#bdc1c6" if theme == "google" else "#ffffff"
        syn_trace = go.Scatter(
            x=syn_x, y=syn_y,
            mode='markers+text',
            hoverinfo='text',
            text=syn_text,
            hovertext=syn_hover,
            textposition="bottom center",
            textfont=dict(family="'Space Grotesk', sans-serif", size=10, color=syn_text_color),
            marker=dict(
                color='#f9ab00',  # Google Amber
                size=22,
                line=dict(width=2.5, color=syn_line_color),
                shadow=dict(color='rgba(0,0,0,0.1)' if theme == "google" else 'rgba(0,0,0,0.2)', width=4, x=0, y=1)
            )
        )

        # Trazador para Conceptos Individuales (Círculos pequeños menta suave con borde blanco)
        con_text_color = "#5f6368" if theme == "google" else "#cbd5e1"
        con_line_color = "#bdc1c6" if theme == "google" else "#ffffff"
        con_trace = go.Scatter(
            x=con_x, y=con_y,
            mode='markers+text',
            hoverinfo='text',
            text=con_text,
            hovertext=con_hover,
            textposition="bottom center",
            textfont=dict(family="'Outfit', sans-serif", size=9, color=con_text_color),
            marker=dict(
                color='#34a853',  # Google Emerald/Mint
                size=14,
                line=dict(width=2, color=con_line_color)
            )
        )

        # 3. Construir la figura Plotly con espacio amplio y estética moderna
        fig = go.Figure(
            data=[edge_trace, con_trace, syn_trace, res_trace],
            layout=go.Layout(
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=20, r=20, t=20),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                dragmode='pan'
            )
        )
        return fig

