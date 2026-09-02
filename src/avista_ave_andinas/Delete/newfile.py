import folium
from folium.plugins import HeatMap

# 1. Initialize map with locked background tiles
m = folium.Map(location=[45.5236, -122.6750], zoom_start=12, tiles="OpenStreetMap", control=False)

# Get the auto-generated internal variable name of your map object
map_macro_id = m.get_name()

# 2. Define your structured data
categories = {
    "City North": {
        "Morning Traffic": [[45.530, -122.670, 1.0], [45.531, -122.672, 0.8]],
        "Evening Traffic": [[45.535, -122.675, 0.9], [45.536, -122.677, 0.7]]
    },
    "City South": {
        "Morning Traffic": [[45.510, -122.660, 1.0], [45.511, -122.662, 0.6]],
        "Noise Complaints": [[45.505, -122.665, 0.9], [45.504, -122.661, 0.5]]
    }
}

layer_mapping = {}
layer_index = 0

# 3. Create Heatmap layers and add them to the map hidden by default
for cat_name, sub_dict in categories.items():
    for heat_name, coords in sub_dict.items():
        layer_id = f"heatmap_layer_{layer_index}"
        
        heatmap_layer = folium.FeatureGroup(name=heat_name, show=False)
        HeatMap(coords, radius=25, blur=15).add_to(heatmap_layer)
        heatmap_layer.add_to(m)
        
        layer_mapping[f"{cat_name} - {heat_name}"] = {
            "id": layer_id,
            "obj_ref": heatmap_layer.get_name()
        }
        layer_index += 1

# 4. Generate the HTML code for the custom Legend
legend_html = """
<div class="custom-legend">
    <h4>Map Layers</h4>
"""

for cat_name, sub_dict in categories.items():
    legend_html += f'<div class="category-header">{cat_name}</div>'
    for heat_name in sub_dict.keys():
        key = f"{cat_name} - {heat_name}"
        layer_info = layer_mapping[key]
        
        legend_html += f"""
        <div class="layer-item">
            <input type="radio" id="{layer_info['id']}" name="global-layers" 
                   onchange="toggleGlobalLayer('{layer_info['obj_ref']}')">
            <label for="{layer_info['id']}">{heat_name}</label>
        </div>
        """
legend_html += "</div>"

# 5. Add visual styles
css_styles = """
<style>
    .custom-legend {
        position: fixed;
        top: 10px; right: 10px; z-index: 9999;
        background: white; padding: 12px 16px;
        border-radius: 8px; box-shadow: 0 0 15px rgba(0,0,0,0.2);
        font-family: Arial, sans-serif; font-size: 14px; max-width: 220px;
    }
    .custom-legend h4 { margin: 0 0 8px 0; font-size: 16px; border-bottom: 1px solid #ccc; padding-bottom: 5px;}
    .category-header { font-weight: bold; margin-top: 10px; margin-bottom: 4px; color: #333; text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px;}
    .layer-item { margin-left: 8px; margin-bottom: 4px; display: flex; align-items: center; }
    .layer-item input { margin-right: 6px; cursor: pointer; }
    .layer-item label { cursor: pointer; color: #555; }
</style>
"""

# 6. Corrected JavaScript passing the exact dynamic map object reference identifier
js_script = f"""
<script>
var totalLayers = {str([info['obj_ref'] for info in layer_mapping.values()])};

function toggleGlobalLayer(targetLayerName) {{
    var targetMap = window["{map_macro_id}"];
    
    if (targetMap) {{
        // 1. Force remove all heatmap layers from the active canvas
        totalLayers.forEach(function(layerName) {{
            var layerObj = window[layerName];
            if (layerObj && targetMap.hasLayer(layerObj)) {{
                targetMap.removeLayer(layerObj);
            }}
        }});
        
        // 2. Safely add the freshly checked radio item back to view
        var activeLayerObj = window[targetLayerName];
        if (activeLayerObj) {{
            targetMap.addLayer(activeLayerObj);
        }}
    }}
}}
</script>
"""

# 7. Inject everything directly into the DOM tree
m.get_root().html.add_child(folium.Element(css_styles + legend_html + js_script))
m.save("global_legend_fixed.html")
