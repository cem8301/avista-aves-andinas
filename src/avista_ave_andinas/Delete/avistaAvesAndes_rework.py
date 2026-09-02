#!/usr/bin/env python3
import configparser
import json
from pathlib import Path

import folium
from folium.plugins import HeatMap
import gpxpy
import pandas as pd
from pygbif import occurrences as occ
from pygbif import species


class AvistaAvesAndinas:
    def __init__(self,
        config_file: str,
        limit_bird_sightings: int = 500,
        limit_output: int | None = None):
        self.pwd = Path.cwd()
        self.config = self._load_config(config_file)
        self.limit_bird_sightings = \
            limit_bird_sightings
        self.birds_dict = self._load_birds(
            limit_output)
        self.bird_locations_dict = \
            self._initialize_bird_locations()
        self.map = self._create_map()
        self.map_macro_id = self.map.get_name()
        self.layer_mapping = {}
        self.layer_index = 0
        gpx = self.config.get('path', 'gpx')
        if gpx:
            self.gpx_file_path = f'{self.pwd}/{gpx}'

    def run(self, output_name='birds'):
        self.add_gpx()
        self.get_data()
        self.add_data_layers()
        self.add_custom_legend()
        output_path = \
            self.pwd / f'{output_name}.html'
        self.map.save(output_path)
        print(f'Saved: {output_path}')
        
    def add_gpx(self):
        print('Adding gpx file to map: '
            f'{self.gpx_file_path}')
        with open(self.gpx_file_path, "r") as gpx_file:
            gpx = gpxpy.parse(gpx_file)
        points = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    points.append((
                    point.latitude, point.longitude))
                    
        folium.PolyLine(
            locations=points,
            color="blue",
            weight=4,
            opacity=0.8).add_to(self.map)
     
    def get_data(self):
        print(f'Fetching {len(self.birds_dict)} '
            'bird entries')
        for index, (key, value) in enumerate(
            self.birds_dict.items()):
            scientific_name = key
            common_name = value["common_name"]
            feature_group = value["feature_group"]
            print(f"{index}: {common_name}")
            points = self._get_bird_occurrences(
                scientific_name)
            self.bird_locations_dict[feature_group
                ][common_name] = points
            
    def add_data_layers(self):
        for cat_name, sub_dict in \
            self.bird_locations_dict.items():
            for heat_name, coords in sub_dict.items():
                layer_id = \
                    f"heatmap_layer_{self.layer_index}"
                heatmap_layer = \
                    folium.FeatureGroup(
                        name=heat_name, show=False)
                HeatMap(coords, radius=25, blur=15
                    ).add_to(heatmap_layer)
                heatmap_layer.add_to(self.map)
                self.layer_mapping[
                    f"{cat_name} - {heat_name}"] = {
                    "id": layer_id,
                    "obj_ref": heatmap_layer.get_name()
                }
                self.layer_index += 1
    
    def add_custom_legend(self):
        legend_html = self.get_custom_legend()
        css_styles = self.get_css_styles()
        js_script = self.get_js_script()
        self.map.get_root().html.add_child(
            folium.Element(
            css_styles + legend_html + js_script))               
    def get_custom_legend(self):
        legend_items = ""
        for cat_name, sub_dict in self.bird_locations_dict.items():
            legend_items += (
                f'<div class="category-header">{cat_name}</div>'
            )
            for heat_name in sub_dict.keys():
                key = f"{cat_name} - {heat_name}"
                layer_info = self.layer_mapping[key]
                legend_items += f"""
                <div class="layer-item">
                    <input
                        type="radio"
                        id="{layer_info['id']}"
                        name="global-layers"
                        onchange="toggleGlobalLayer('{layer_info['obj_ref']}')"
                    >
                    <label for="{layer_info['id']}">{heat_name}</label>
                </div>
                """
        legend_html = self._load_template(
            "legend.html")
        legend_html = legend_html.replace(
            "$legend_items",
            legend_items
        )
        return legend_html

    def get_js_script(self):
        js = self._load_template("legend.js")
        total_layers = json.dumps([
            info["obj_ref"]
            for info in self.layer_mapping.values()])
        js = js.replace("$total_layers", total_layers)
        js = js.replace("$map_macro_id",
            self.map_macro_id)
        return f"""<script>{js}</script>"""
        
    def get_css_styles(self):
        css = self._load_template("legend.css")
        return f"""<style>{css}</style>"""
    
    def _load_config(self,
        config_file: str) -> configparser.ConfigParser:
        config = configparser.ConfigParser()
        config_path = self.pwd / config_file
        if not config_path.exists():
            raise FileNotFoundError(
                f"Config file not found: {config_path}"
            )
        config.read(config_path)
        print(f"Reading config: {config_file}")
        return config
        
    def _load_birds(self,
        limit_output: int | None = None) -> dict:
        birds_csv = self.config.get(
            "path", "birds_csv")
        df = pd.read_csv(self.pwd / birds_csv)
        if limit_output:
            print(f"Limiting output: {limit_output}")
            df = df.head(limit_output)
        return (df.set_index("scientific_name")
            [["common_name", "feature_group"]]
            .to_dict(orient="index"))
        
    def _initialize_bird_locations(self):
        return {inner_dict["feature_group"]: {} 
            for inner_dict in self.birds_dict.values()
            if "feature_group" in inner_dict}
            
    def _create_map(self):
        location = json.loads(
            self.config.get('map', 'location'))
        zoom_start = self.config.getint(
            'map', 'zoom_start')
        return folium.Map(
            location=location,
            zoom_start=zoom_start,
            tiles='OpenStreetMap',
            control=False)
        
    def _get_bird_occurrences(self,
        scientific_name: str) -> list[tuple]:
        taxon_info = species.name_backbone(
            scientificName=scientific_name,
            kingdom='animals')
        taxon_key = taxon_info.get(
            'usage', {}).get('key')
        if not taxon_key:
            return []
        raw_data = occ.search(
            taxonKey=taxon_key,
            hasCoordinate=True,
            limit=self.limit_bird_sightings)
        return [(observation['decimalLatitude'],
            observation['decimalLongitude'])
            for observation in raw_data.get(
            'results', [])]
            
    def _load_template(self, filename):
        template_path = \
            self.pwd / 'templates' / filename
        with open(template_path) as file:
            return file.read()
   
if __name__ == "__main__":
    AAA = AvistaAvesAndinas(
        config_file='colombia_config.ini',
        limit_bird_sightings=1,
        limit_output=3
        )
    AAA.run(output_name='colombia_birds_test')
        