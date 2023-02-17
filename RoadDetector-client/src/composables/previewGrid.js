import store from '~/store'
import mapboxgl from 'mapbox-gl';
import * as turf from '@turf/turf'
import { ElMessage } from 'element-plus'


function lat2tile(lat, zoom)  {
	return Math.floor((1 - Math.log(Math.tan(lat * Math.PI / 180) + 1 / Math.cos(lat * Math.PI / 180)) / Math.PI) / 2 * Math.pow(2, zoom))
}

function long2tile(lon, zoom) {
	return Math.floor((lon + 180) / 360 * Math.pow(2, zoom))
}

function tile2long(x, z) {
	return x / Math.pow(2, z) * 360 - 180
}
function tile2lat(y, z) {
	let n = Math.PI - 2 * Math.PI * y / Math.pow(2, z)
	return 180 / Math.PI * Math.atan(0.5 * (Math.exp(n) - Math.exp(-n)))
}

function getTileRect(x, y, zoom) {
	let c1 = new mapboxgl.LngLat(tile2long(x, zoom), tile2lat(y, zoom))
	let c2 = new mapboxgl.LngLat(tile2long(x + 1, zoom), tile2lat(y + 1, zoom))

	return new mapboxgl.LngLatBounds(c1, c2);
}

export function getGrid(zoomLevel, max_grid) {
	let bounds = getBounds()

	let rects = []
	let thisZoom = zoomLevel

	let TY = lat2tile(bounds.getNorthEast().lat, thisZoom)
	let LX = long2tile(bounds.getSouthWest().lng, thisZoom)
	let BY = lat2tile(bounds.getSouthWest().lat, thisZoom)
	let RX = long2tile(bounds.getNorthEast().lng, thisZoom)

	
	let grid_count = 0
	for(let y = TY; y <= BY; y++) {
		for(let x = LX; x <= RX; x++) {
			let rect = getTileRect(x, y, thisZoom)
			if(isTileInSelection(rect)) {
				grid_count++
				if(grid_count > max_grid){
					return null
				}
				rects.push({
					x: x,
					y: y,
					z: thisZoom,
					rect: rect,
				})
			}
		}
	}

	return rects
}

function isTileInSelection(tileRect) {
	var polygon = getPolygonByBounds(tileRect);
	var areaPolygon = store.state.draw.getAll().features[0];
	if(turf.booleanDisjoint(polygon, areaPolygon) == false) {
		return true;
	}
	return false;
}

function getPolygonByBounds(bounds) {
	var tilePolygonData = getArrayByBounds(bounds)
	var polygon = turf.polygon([tilePolygonData])
	return polygon
}

function getBounds() {
	let coordinates = store.state.draw.getAll().features[0].geometry.coordinates[0];
	
	let bounds = coordinates.reduce(function(bounds, coord) {
			return bounds.extend(coord);
		}, new mapboxgl.LngLatBounds(coordinates[0], coordinates[0]))

	return bounds;
}

function getArrayByBounds(bounds) {
	var tileArray = [
		[ bounds.getSouthWest().lng, bounds.getNorthEast().lat ],
		[ bounds.getNorthEast().lng, bounds.getNorthEast().lat ],
		[ bounds.getNorthEast().lng, bounds.getSouthWest().lat ],
		[ bounds.getSouthWest().lng, bounds.getSouthWest().lat ],
		[ bounds.getSouthWest().lng, bounds.getNorthEast().lat ],
	];

	return tileArray;
}

export function previewGrid(max_grid){
	if (store.state.draw.getAll().features.length > 0) {
		let grid = getGrid(store.state.zoom, max_grid)
		if (grid === null) {
			return null
		}
		
		removeLayer("grid-preview")
        removeSource("grid-preview")
		var pointsCollection = []
	
		for(var i in grid) {
			var feature = grid[i];
			var array = getArrayByBounds(feature.rect);
			pointsCollection.push(array);
		}
	
		store.state.map.addLayer({
			'id': "grid-preview",
			'type': 'line',
			'source': {
				'type': 'geojson',
				'data': turf.polygon(pointsCollection),
			},
			'layout': {},
			'paint': {
				"line-color": "#fa8231",
				"line-width": 3,
			}
		});
	
		return grid.length
	}
	return -1  // grid-preview layer not exists
}

export function removeLayer(layerId) {
    if (store.state.map.getLayer(layerId) !== undefined) {
        store.state.map.removeLayer(layerId)
    }
}

export function removeSource(sourceId) {
    if (store.state.map.getSource(sourceId) !== undefined) {
        store.state.map.removeSource(sourceId)
    }
}

export function previewRect(rectInfo) {
	var array = getArrayByBounds(rectInfo.rect);
	var id = "Rect-" + rectInfo.x + '-' + rectInfo.y + '-' + rectInfo.z;
	store.state.map.addLayer({
		'id': id,
		'type': 'line',
		'source': {
			'type': 'geojson',
			'data': turf.polygon([array]),
		},
		'layout': {},
		'paint': {
			"line-color": "#ff9f1a",
			"line-width": 3,
		}
	});
	return id;
}