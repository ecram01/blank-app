import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, Rectangle, FancyBboxPatch
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Foundation Layout Tool",
    page_icon="🏗️",
    layout="wide"
)

# Title and description
st.title("🏗️ Offshore Wind Foundation Layout Tool")
st.markdown("*Interactive design tool for internal foundation component placement*")

# Initialize session state for storing layouts
if 'layouts' not in st.session_state:
    st.session_state.layouts = []
if 'current_layout' not in st.session_state:
    st.session_state.current_layout = {
        'name': 'Layout 1',
        'tendons': [],
        'grout_connections': [],
        'access_shafts': []
    }

# Sidebar - Component Library
st.sidebar.header("📦 Component Library")

component_type = st.sidebar.selectbox(
    "Add Component",
    ["Prestressing Tendon", "Grout Connection", "Access Shaft"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("Foundation Parameters")

foundation_diameter = st.sidebar.slider("Foundation Diameter (m)", 5.0, 15.0, 10.0, 0.5)
wall_thickness = st.sidebar.slider("Wall Thickness (m)", 0.3, 1.5, 0.8, 0.1)

st.sidebar.markdown("---")

# Component placement controls
st.sidebar.subheader(f"Place {component_type}")

if component_type == "Prestressing Tendon":
    placement_mode = st.sidebar.radio("Placement Mode", ["Circular Pattern", "Manual"])
    
    if placement_mode == "Circular Pattern":
        num_tendons = st.sidebar.number_input("Number of Tendons", 4, 24, 8, 1)
        radius = st.sidebar.slider("Radius from Center (m)", 2.0, foundation_diameter/2 - 1.0, 4.0, 0.5)
        tendon_diameter = st.sidebar.slider("Tendon Diameter (mm)", 100, 300, 150, 10)
        
        if st.sidebar.button("Generate Circular Pattern"):
            st.session_state.current_layout['tendons'] = []
            angles = np.linspace(0, 2*np.pi, num_tendons, endpoint=False)
            for i, angle in enumerate(angles):
                x = radius * np.cos(angle)
                y = radius * np.sin(angle)
                st.session_state.current_layout['tendons'].append({
                    'id': i,
                    'x': x,
                    'y': y,
                    'diameter': tendon_diameter,
                    'type': 'vertical'
                })
            st.success(f"✓ Added {num_tendons} tendons in circular pattern")
    
    else:  # Manual placement
        manual_x = st.sidebar.slider("X Position (m)", -foundation_diameter/2, foundation_diameter/2, 0.0, 0.1)
        manual_y = st.sidebar.slider("Y Position (m)", -foundation_diameter/2, foundation_diameter/2, 0.0, 0.1)
        tendon_diameter = st.sidebar.slider("Tendon Diameter (mm)", 100, 300, 150, 10)
        
        if st.sidebar.button("Add Tendon"):
            st.session_state.current_layout['tendons'].append({
                'id': len(st.session_state.current_layout['tendons']),
                'x': manual_x,
                'y': manual_y,
                'diameter': tendon_diameter,
                'type': 'vertical'
            })
            st.success("✓ Tendon added")

elif component_type == "Grout Connection":
    grout_x = st.sidebar.slider("X Position (m)", -foundation_diameter/2, foundation_diameter/2, 0.0, 0.1)
    grout_y = st.sidebar.slider("Y Position (m)", -foundation_diameter/2, foundation_diameter/2, 2.0, 0.1)
    grout_diameter = st.sidebar.slider("Connection Diameter (mm)", 200, 600, 400, 50)
    
    if st.sidebar.button("Add Grout Connection"):
        st.session_state.current_layout['grout_connections'].append({
            'id': len(st.session_state.current_layout['grout_connections']),
            'x': grout_x,
            'y': grout_y,
            'diameter': grout_diameter
        })
        st.success("✓ Grout connection added")

elif component_type == "Access Shaft":
    shaft_x = st.sidebar.slider("X Position (m)", -foundation_diameter/2, foundation_diameter/2, 0.0, 0.1)
    shaft_y = st.sidebar.slider("Y Position (m)", -foundation_diameter/2, foundation_diameter/2, -3.0, 0.1)
    shaft_diameter = st.sidebar.slider("Shaft Diameter (m)", 0.8, 2.0, 1.2, 0.1)
    
    if st.sidebar.button("Add Access Shaft"):
        st.session_state.current_layout['access_shafts'].append({
            'id': len(st.session_state.current_layout['access_shafts']),
            'x': shaft_x,
            'y': shaft_y,
            'diameter': shaft_diameter
        })
        st.success("✓ Access shaft added")

# Clear button
st.sidebar.markdown("---")
if st.sidebar.button("🗑️ Clear All Components"):
    st.session_state.current_layout['tendons'] = []
    st.session_state.current_layout['grout_connections'] = []
    st.session_state.current_layout['access_shafts'] = []
    st.rerun()

# Main area - Layout Visualization
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Foundation Cross-Section")
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_xlim(-foundation_diameter/2 - 1, foundation_diameter/2 + 1)
    ax.set_ylim(-foundation_diameter/2 - 1, foundation_diameter/2 + 1)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('X (meters)', fontsize=12)
    ax.set_ylabel('Y (meters)', fontsize=12)
    
    # Draw foundation outer circle
    outer_circle = Circle((0, 0), foundation_diameter/2, fill=False, 
                          edgecolor='#2C3E50', linewidth=3, label='Foundation Outer')
    ax.add_patch(outer_circle)
    
    # Draw foundation inner circle
    inner_circle = Circle((0, 0), foundation_diameter/2 - wall_thickness, 
                          fill=False, edgecolor='#2C3E50', linewidth=2, 
                          linestyle='--', label='Foundation Inner')
    ax.add_patch(inner_circle)
    
    # Draw tendons
    for tendon in st.session_state.current_layout['tendons']:
        tendon_circle = Circle((tendon['x'], tendon['y']), tendon['diameter']/1000/2,
                              color='#E74C3C', alpha=0.7, edgecolor='#C0392B', linewidth=2,
                              label='Tendon' if tendon['id'] == 0 else '')
        ax.add_patch(tendon_circle)
        ax.text(tendon['x'], tendon['y'], f"T{tendon['id']}", 
               ha='center', va='center', fontsize=8, color='white', weight='bold')
    
    # Draw grout connections
    for grout in st.session_state.current_layout['grout_connections']:
        grout_circle = Circle((grout['x'], grout['y']), grout['diameter']/1000/2,
                             color='#3498DB', alpha=0.6, edgecolor='#2980B9', linewidth=2,
                             label='Grout' if grout['id'] == 0 else '')
        ax.add_patch(grout_circle)
        ax.text(grout['x'], grout['y'], f"G{grout['id']}", 
               ha='center', va='center', fontsize=8, color='white', weight='bold')
    
    # Draw access shafts
    for shaft in st.session_state.current_layout['access_shafts']:
        shaft_circle = Circle((shaft['x'], shaft['y']), shaft['diameter']/2,
                             color='#2ECC71', alpha=0.5, edgecolor='#27AE60', linewidth=2,
                             label='Access Shaft' if shaft['id'] == 0 else '')
        ax.add_patch(shaft_circle)
        ax.text(shaft['x'], shaft['y'], f"A{shaft['id']}", 
               ha='center', va='center', fontsize=10, color='white', weight='bold')
    
    # Add center point
    ax.plot(0, 0, 'ko', markersize=8, label='Center')
    
    # Legend
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        # Remove duplicate labels
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), loc='upper right', fontsize=10)
    
    st.pyplot(fig)

with col2:
    st.subheader("Engineering Analysis")
    
    # Component count
    st.metric("Total Tendons", len(st.session_state.current_layout['tendons']))
    st.metric("Grout Connections", len(st.session_state.current_layout['grout_connections']))
    st.metric("Access Shafts", len(st.session_state.current_layout['access_shafts']))
    
    st.markdown("---")
    st.subheader("Constraint Validation")
    
    # Run validation checks
    violations = []
    warnings = []
    
    # Check 1: Components inside foundation
    for tendon in st.session_state.current_layout['tendons']:
        distance = np.sqrt(tendon['x']**2 + tendon['y']**2)
        if distance + tendon['diameter']/1000/2 > foundation_diameter/2 - wall_thickness:
            violations.append(f"Tendon T{tendon['id']} too close to wall")
    
    # Check 2: Minimum clearance between tendons
    min_clearance = 0.3  # meters
    tendons = st.session_state.current_layout['tendons']
    for i, t1 in enumerate(tendons):
        for j, t2 in enumerate(tendons[i+1:], i+1):
            dist = np.sqrt((t1['x']-t2['x'])**2 + (t1['y']-t2['y'])**2)
            min_dist = (t1['diameter'] + t2['diameter'])/1000/2 + min_clearance
            if dist < min_dist:
                violations.append(f"Tendons T{i} and T{j} too close ({dist:.2f}m < {min_dist:.2f}m)")
    
    # Check 3: Grout connection clearance
    for grout in st.session_state.current_layout['grout_connections']:
        for tendon in tendons:
            dist = np.sqrt((grout['x']-tendon['x'])**2 + (grout['y']-tendon['y'])**2)
            min_dist = grout['diameter']/1000/2 + tendon['diameter']/1000/2 + 0.2
            if dist < min_dist:
                warnings.append(f"Grout G{grout['id']} near Tendon T{tendon['id']}")
    
    # Display validation results
    if len(violations) == 0 and len(warnings) == 0:
        st.success("✓ All constraints satisfied")
    else:
        if violations:
            st.error(f"❌ {len(violations)} Constraint Violations:")
            for v in violations:
                st.write(f"• {v}")
        if warnings:
            st.warning(f"⚠️ {len(warnings)} Warnings:")
            for w in warnings:
                st.write(f"• {w}")
    
    st.markdown("---")
    st.subheader("Estimates")
    
    # Simple cost estimation
    tendon_count = len(tendons)
    steel_per_tendon = 150  # kg
    total_steel = tendon_count * steel_per_tendon
    steel_cost_per_kg = 3.50  # USD
    
    st.metric("Total Steel", f"{total_steel} kg")
    st.metric("Steel Cost", f"${total_steel * steel_cost_per_kg:,.0f}")
    
    # Construction complexity score (1-10)
    complexity = min(10, 2 + tendon_count * 0.3 + len(st.session_state.current_layout['grout_connections']) * 0.5)
    st.metric("Complexity Score", f"{complexity:.1f}/10")

# Bottom section - Layout management
st.markdown("---")
st.subheader("Layout Management")

col_a, col_b, col_c = st.columns(3)

with col_a:
    layout_name = st.text_input("Layout Name", value=st.session_state.current_layout['name'])
    st.session_state.current_layout['name'] = layout_name

with col_b:
    if st.button("💾 Save Layout"):
        layout_copy = {
            'name': layout_name,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'tendons': st.session_state.current_layout['tendons'].copy(),
            'grout_connections': st.session_state.current_layout['grout_connections'].copy(),
            'access_shafts': st.session_state.current_layout['access_shafts'].copy(),
            'foundation_diameter': foundation_diameter,
            'wall_thickness': wall_thickness
        }
        st.session_state.layouts.append(layout_copy)
        st.success(f"✓ Layout '{layout_name}' saved!")

with col_c:
    # Export to CSV
    if len(st.session_state.current_layout['tendons']) > 0:
        df_tendons = pd.DataFrame(st.session_state.current_layout['tendons'])
        csv = df_tendons.to_csv(index=False)
        st.download_button(
            label="📥 Export Tendons CSV",
            data=csv,
            file_name=f"{layout_name}_tendons.csv",
            mime="text/csv"
        )

# Show saved layouts
if len(st.session_state.layouts) > 0:
    st.markdown("---")
    st.subheader("Saved Layouts")
    
    for i, layout in enumerate(st.session_state.layouts):
        with st.expander(f"{layout['name']} - {layout['timestamp']}"):
            col1, col2, col3 = st.columns(3)
            col1.metric("Tendons", len(layout['tendons']))
            col2.metric("Grout Connections", len(layout['grout_connections']))
            col3.metric("Access Shafts", len(layout['access_shafts']))
            
            if st.button(f"Load Layout {i}", key=f"load_{i}"):
                st.session_state.current_layout = {
                    'name': layout['name'] + " (copy)",
                    'tendons': layout['tendons'].copy(),
                    'grout_connections': layout['grout_connections'].copy(),
                    'access_shafts': layout['access_shafts'].copy()
                }
                st.rerun()

# Footer
st.markdown("---")
st.caption("Offshore Wind Foundation Layout Tool | Built with Streamlit")
