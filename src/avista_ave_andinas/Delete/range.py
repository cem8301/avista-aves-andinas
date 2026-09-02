import io
import requests
#import matplot6lib.pyplot as plt
#import geopandas as gpd
#import contextily as ctx
from PIL import Image
from pygbif import species
from pygbif import occurrences as occ
#from shapely.geometry import Point

import branca
from branca.element import Element
import xyzservices.providers as xyz
from flatten_dict import flatten
import folium
from folium.plugins import TimestampedGeoJson
from folium.plugins import FeatureGroupSubGroup
from branca.element import MacroElement
from jinja2 import Template
from folium.plugins import MarkerCluster
from folium.plugins import HeatMap
from folium.plugins import GroupedLayerControl
import gpxpy.gpx
import pandas as pd
import polyline


colombia_endemics = {
"Penelope perspicax": {"common_name": "Cauca Guan", "found_on_route": True}}#,
b={"Ortalis garrula": {"common_name": "Chestnut-winged Chachalaca", "found_on_route": False},
"Ortalis columbiana": {"common_name": "Colombian Chachalaca", "found_on_route": True},
"Crax alberti": {"common_name": "Blue-billed Curassow", "found_on_route": False}, "Odontophorus hyperythrus": {"common_name": "Chestnut Wood-Quail", "found_on_route": True},
"Odontophorus strophium": {"common_name": "Gorgeted Wood-Quail", "found_on_route": False},
"Leptotila conoveri": {"common_name": "Tolima Dove", "found_on_route": True},
"Ramphomicron dorsale": {"common_name": "Black-backed Thornbill", "found_on_route": False},
"Oxypogon stuebelii": {"common_name": "Buffy Helmetcrest", "found_on_route": True},
"Oxypogon cyanolaemus": {"common_name": "Blue-bearded Helmetcrest", "found_on_route": False},
"Oxypogon guerinii": {"common_name": "Green-bearded Helmetcrest", "found_on_route": False},
"Eriocnemis isabellae": {"common_name": "Gorgeted Puffleg", "found_on_route": False},
"Eriocnemis mirabilis": {"common_name": "Colorful Puffleg", "found_on_route": False},
"Coeligena prunellei": {"common_name": "Black Inca", "found_on_route": False},
"Coeligena phalerata": {"common_name": "White-tailed Starfrontlet", "found_on_route": False},
"Coeligena orina": {"common_name": "Glittering Starfrontlet", "found_on_route": True},
"Coeligena bonapartei": {"common_name": "Golden-bellied Starfrontlet", "found_on_route": False},
"Chaetocercus astreans": {"common_name": "Santa Marta Woodstar", "found_on_route": False},
"Chlorostilbon olivaresi": {"common_name": "Chiribiquete Emerald", "found_on_route": False},
"Anthocephala floriceps": {"common_name": "Santa Marta Blossomcrown", "found_on_route": False},
"Anthocephala berlepschi": {"common_name": "Tolima Blossomcrown", "found_on_route": True},
"Campylopterus phainopeplus": {"common_name": "Santa Marta Sabrewing", "found_on_route": False},
"Saucerottia castaneiventris": {"common_name": "Chestnut-bellied Hummingbird", "found_on_route": False},
"Saucerottia cyanifrons": {"common_name": "Indigo-capped Hummingbird", "found_on_route": True},
"Chrysuronia lilliae": {"common_name": "Sapphire-bellied Hummingbird", "found_on_route": False},
"Rallus semiplumbeus": {"common_name": "Bogota Rail", "found_on_route": False},
"Megascops gilesi": {"common_name": "Santa Marta Screech-Owl", "found_on_route": False},
"Nystactes noanamae": {"common_name": "Sooty-capped Puffbird", "found_on_route": False},
"Capito hypoleucus": {"common_name": "White-mantled Barbet", "found_on_route": False},
"Picumnus granadensis": {"common_name": "Grayish Piculet", "found_on_route": True},
"Melanerpes pulcher": {"common_name": "Beautiful Woodpecker", "found_on_route": False},
"Bolborhynchus ferrugineifrons": {"common_name": "Rufous-fronted Parakeet", "found_on_route": True},
"Hapalopsittaca fuertesi": {"common_name": "Indigo-winged Parrot", "found_on_route": True},
"Forpus spengeli": {"common_name": "Turquoise-winged Parrotlet", "found_on_route": False},
"Pyrrhura viridicata": {"common_name": "Santa Marta Parakeet", "found_on_route": False},
"Pyrrhura chapmani": {"common_name": "Upper Magdalena Parakeet", "found_on_route": False},
"Pyrrhura calliptera": {"common_name": "Brown-breasted Parakeet", "found_on_route": False},
"Ognorhynchus icterotis": {"common_name": "Yellow-eared Parrot", "found_on_route": True},
"Cercomacroides parkeri": {"common_name": "Parker's Antbird", "found_on_route": True},
"Drymophila hellmayri": {"common_name": "Santa Marta Antbird", "found_on_route": False},
"Drymophila caudata": {"common_name": "East Andean Antbird", "found_on_route": False},
"Grallaria bangsi": {"common_name": "Santa Marta Antpitta", "found_on_route": False},
"Grallaria kaestneri": {"common_name": "Cundinamarca Antpitta", "found_on_route": False},
"Grallaria alticola": {"common_name": "Boyaca Antpitta", "found_on_route": False},
"Grallaria fenwickorum": {"common_name": "Urrao Antpitta", "found_on_route": False},
"Grallaria milleri": {"common_name": "Brown-banded Antpitta", "found_on_route": True},
"Grallaria alvarezi": {"common_name": "Chami Antpitta", "found_on_route": True},
"Grallaria spatiator": {"common_name": "Sierra Nevada Antpitta", "found_on_route": False},
"Scytalopus alvarezlopezi": {"common_name": "Tatamá Tapaculo", "found_on_route": True},
"Scytalopus sanctaemartae": {"common_name": "Santa Marta Tapaculo", "found_on_route": False},
"Scytalopus rodriguezi": {"common_name": "Magdalena Tapaculo", "found_on_route": False},
"Scytalopus stilesi": {"common_name": "Stiles's Tapaculo", "found_on_route": True},
"Scytalopus latebricola": {"common_name": "Brown-rumped Tapaculo", "found_on_route": False},
"Scytalopus canus": {"common_name": "Paramillo Tapaculo", "found_on_route": True},
"Clibanornis rufipectus": {"common_name": "Santa Marta Foliage-gleaner", "found_on_route": False},
"Cranioleuca hellmayri": {"common_name": "Streak-capped Spinetail", "found_on_route": False},
"Synallaxis fuscorufa": {"common_name": "Rusty-headed Spinetail", "found_on_route": False},
"Synallaxis subpudica": {"common_name": "Silvery-throated Spinetail", "found_on_route": False},
"Chloropipo flavicapilla": {"common_name": "Yellow-headed Manakin", "found_on_route": True},
"Lipaugus weberi": {"common_name": "Chestnut-capped Piha", "found_on_route": False},
"Pogonotriccus lanyoni": {"common_name": "Antioquia Bristle-tyrant", "found_on_route": False},
"Myiarchus apicalis": {"common_name": "Apical Flycatcher", "found_on_route": False},
"Myiotheretes pernix": {"common_name": "Santa Marta Bush-tyrant", "found_on_route": False},
"Vireo caribaeus": {"common_name": "San Andres Vireo", "found_on_route": False},
"Troglodytes monticola": {"common_name": "Santa Marta Wren", "found_on_route": False},
"Cistothorus apolinari": {"common_name": "Apolinar's Wren", "found_on_route": False},
"Thryophilus sernai": {"common_name": "Antioquia Wren", "found_on_route": False},
"Thryophilus nicefori": {"common_name": "Niceforo's Wren", "found_on_route": False},
"Henicorhina anachoreta": {"common_name": "Hermit Wood-Wren", "found_on_route": False},
"Henicorhina negreti": {"common_name": "Munchique Wood-Wren", "found_on_route": True},
"Euphonia concinna": {"common_name": "Velvet-fronted Euphonia", "found_on_route": True},
"Arremon basilicus": {"common_name": "Sierra Nevada Brushfinch", "found_on_route": False},
"Atlapetes albofrenatus": {"common_name": "Moustached Brushfinch", "found_on_route": False},
"Atlapetes melanocephalus": {"common_name": "Santa Marta Brushfinch", "found_on_route": False},
"Atlapetes flaviceps": {"common_name": "Yellow-headed Brushfinch", "found_on_route": True},
"Atlapetes fuscoolivaceus": {"common_name": "Dusky-headed Brushfinch", "found_on_route": False},
"Atlapetes blancae": {"common_name": "Antioquia Brushfinch", "found_on_route": False},
"Psarocolius cassini": {"common_name": "Baudo Oropendola", "found_on_route": True},
"Molothrus armenti": {"common_name": "Bronze-brown Cowbird", "found_on_route": False},
"Hypopyrrhus pyrohypogaster": {"common_name": "Red-bellied Grackle", "found_on_route": True},
"Macroagelaius subalaris": {"common_name": "Mountain Grackle", "found_on_route": False},
"Myiothlypis basilica": {"common_name": "Santa Marta Warbler", "found_on_route": False},
"Myiothlypis conspicillata": {"common_name": "White-lored Warbler", "found_on_route": False},
"Myioborus flavivertex": {"common_name": "Yellow-crowned Whitestart", "found_on_route": False},
"Myioborus chrysops": {"common_name": "Golden-fronted Whitestart", "found_on_route": True},
"Habia gutturalis": {"common_name": "Sooty Ant-Tanager", "found_on_route": False},
"Habia cristata": {"common_name": "Crested Ant-Tanager", "found_on_route": True},
"Dacnis hartlaubi": {"common_name": "Turquoise Dacnis", "found_on_route": True},
"Diglossa gloriosissima": {"common_name": "Chestnut-bellied Flowerpiercer", "found_on_route": True},
"Dubusia carrikeri": {"common_name": "Carriker's Mountain-Tanager", "found_on_route": False},
"Anisognathus melanogenys": {"common_name": "Santa Marta Mountain-Tanager", "found_on_route": False},
"Chlorochrysa nitidissima": {"common_name": "Multicolored Tanager", "found_on_route": True},
"Bangsia aureocincta": {"common_name": "Gold-ringed Tanager", "found_on_route": True},
"Bangsia melanochlamys": {"common_name": "Black-and-gold Tanager", "found_on_route": True}}


wow_birds = {
"Aglaiocercus kingii": {"common_name": "Long-tailed Sylph", "found_on_route": True},
"Semnornis ramphastinus": {"common_name": "Toucan Barbet", "found_on_route": True},
"Andigena hypoglauca": {"common_name": "Gray-breasted Mountain-Toucan", "found_on_route": True},
"Aulacorhynchus haematopygus": {"common_name": "Crimson-rumped Toucanet", "found_on_route": True},
"Pharomachrus antisianus": {"common_name": "Crested Quetzal", "found_on_route": True},
"Pipreola jucunda": {"common_name": "Orange-breasted Fruiteater", "found_on_route": True},
"Pharomachrus auriceps": {"common_name": "Golden-headed Quetzal", "found_on_route": True},
"Andigena nigrirostris": {"common_name": "Black-billed Mountain-Toucan", "found_on_route": True},
"Ensifera ensifera": {"common_name": "Sword-billed Hummingbird", "found_on_route": True},
"Rupicola peruvianus": {"common_name": "Andean Cock-of-the-rock", "found_on_route": True},
"Vultur gryphus": {"common_name": "Andean Condor", "found_on_route": True},
"Gallinago nobilis": {"common_name": "Noble Snipe", "found_on_route": True}}


m = folium.Map()
tiles_name = 'Esri.NatGeoWorldMap'
providers = xyz.flatten()
tiles = providers[tiles_name]
folium.TileLayer(
    tiles=tiles.build_url(),
    attr=tiles.html_attribution,
    name=tiles.name,
    show=False
).add_to(m)

gpx_file_path = "Avista_Aves_Andinas.gpx"
with open(gpx_file_path, "r") as gpx_file:
    gpx = gpxpy.parse(gpx_file)

points = []
for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            points.append((point.latitude, point.longitude))
            
folium.PolyLine(locations=points, color="blue", weight=4, opacity=0.8).add_to(m)



feature_group_on_route = folium.FeatureGroup(overlay=False)
feature_group_off_route = folium.FeatureGroup(overlay= False)
feature_group_wow = folium.FeatureGroup(overlay= False)

m.add_child(feature_group_on_route)
m.add_child(feature_group_off_route)
m.add_child(feature_group_wow)


found_on_route_list = []
not_on_route_list = []
wow_list = []
bird_limit = 1

first = True
for key, value in colombia_endemics.items():
    scientific_name = key
    common_name = value['common_name']
    found_on_route = value['found_on_route']
    print(common_name)
    taxon_info = species.name_backbone(scientificName=scientific_name,kingdom="animals")
    taxon_key = taxon_info.get('usage',{}).get('key')
    raw_data = occ.search(taxonKey=taxon_key, hasCoordinate=True, limit=bird_limit)
    results = raw_data["results"]
    lon_list = [obs["decimalLongitude"] for obs in results]
    lat_list = [obs["decimalLatitude"] for obs in results]
    points = list(zip(lat_list, lon_list))
    if found_on_route:
        if first:
            show = True
            first = False
        else:
            show = False
        sub_feature_group = FeatureGroupSubGroup(feature_group_on_route, name=f"{common_name}", show=show)
        found_on_route_list.append(sub_feature_group)
    else:
         sub_feature_group = FeatureGroupSubGroup(feature_group_off_route, name=f"{common_name}", show=False)
         not_on_route_list.append(sub_feature_group)
    HeatMap(points).add_to(sub_feature_group)
    m.add_child(sub_feature_group)


for key, value in wow_birds.items():
    scientific_name = key
    common_name = value['common_name']
    found_on_route = value['found_on_route']
    print(common_name)
    taxon_info = species.name_backbone(scientificName=scientific_name,kingdom="animals")
    taxon_key = taxon_info.get('usage',{}).get('key')
    raw_data = occ.search(taxonKey=taxon_key, hasCoordinate=True, limit=bird_limit)
    results = raw_data["results"]
    lon_list = [obs["decimalLongitude"] for obs in results]
    lat_list = [obs["decimalLatitude"] for obs in results]
    points = list(zip(lat_list, lon_list))
    sub_feature_group = FeatureGroupSubGroup(feature_group_wow, name=f"{common_name}", show=False)
    wow_list.append(sub_feature_group)
    HeatMap(points).add_to(sub_feature_group)
    m.add_child(sub_feature_group)




GroupedLayerControl(
    groups={
        "Found On Route": found_on_route_list,
        "Not on Route": not_on_route_list,
        'General Wow': wow_list
    },
    exclusive_groups=True,
    overlay= False,
    collapsed=True,
    position='topright'
).add_to(m)



#4. Inject Mobile-Friendly Scroll Script and CSS
mobile_scroll_inject = """
<style>
    /* Limits height and enables native scrolling */
    .leaflet-control-layers-list {
        max-height: 250px;
        overflow-y: auto;
        padding-right: 5px;
        scroll-behavior: smooth;
    }
    /* Simple styling for the phone scroll button */
    .mobile-scroll-btn {
        display: block;
        width: 100%;
        background: #0078A8;
        color: white;
        text-align: center;
        padding: 6px 0;
        margin-top: 8px;
        border-radius: 4px;
        font-size: 10px;
        font-weight: bold;
        cursor: pointer;
        border: none;
    }
    .mobile-scroll-btn:active {
        background: #005A7E;
    }
</style>

<script>
document.addEventListener("DOMContentLoaded", function() {
    // Wait for Folium to build the layer control UI
    setTimeout(function() {
        var container = document.querySelector('.leaflet-control-layers-list');
        var controlPanel = document.querySelector('.leaflet-control-layers');
        
        if (container && controlPanel) {
            // Create the tap-to-scroll button
            var btn = document.createElement('button');
            btn.className = 'mobile-scroll-btn';
            btn.innerText = '👇 Tap to Scroll Menu';
            
            // Handle the tapping behavior
            btn.onclick = function(e) {
                e.preventDefault();
                e.stopPropagation(); // Prevents map from clicking behind it
                
                // If at bottom, loop back to top. Otherwise scroll down.
                if (container.scrollTop + container.clientHeight >= container.scrollHeight - 5) {
                    container.scrollTop = 0;
                    btn.innerText = '👇 Tap to Scroll Menu';
                } else {
                    container.scrollTop += 80; // Scrolls down by 80 pixels per tap
                    if (container.scrollTop + container.clientHeight >= container.scrollHeight - 5) {
                        btn.innerText = '👆 Back to Top';
                    }
                }
            };
            
            // Append button right below the layer list
            controlPanel.appendChild(btn);
        }
    }, 500); // Short delay ensures elements exist in DOM
});
</script>
"""
m.get_root().header.add_child(Element(mobile_scroll_inject))



m.save("birds.html")
            
            

# 3. Create a MarkerCluster object and add it to the map
#marker_cluster = MarkerCluster().add_to(m)
#for point in points:
#    folium.Marker(
#        location=point,
#        icon=folium.Icon(color="purple", icon="info-sign")
#        #popup=f"Coordinates: {point}"
#    ).add_to(marker_cluster)
