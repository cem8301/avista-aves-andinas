var totalLayers = $total_layers;

function scrollLegend(amount) {
    var container = document.getElementById('legendContainer');

    if (container) {
        container.scrollTop += amount;
    }
}

function toggleGlobalLayer(targetLayerName) {
    var targetMap = window["$map_macro_id"];

    if (targetMap) {
        totalLayers.forEach(function(layerName) {
            var layerObj = window[layerName];

            if (layerObj && targetMap.hasLayer(layerObj)) {
                targetMap.removeLayer(layerObj);
            }
        });

        var activeLayerObj = window[targetLayerName];

        if (activeLayerObj) {
            targetMap.addLayer(activeLayerObj);
        }
    }
}