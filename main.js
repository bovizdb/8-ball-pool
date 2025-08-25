import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const yAxis = new THREE.Vector3(0, 1, 0);
const zAxis = new THREE.Vector3(0, 0, 1);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.01, 1000);
camera.position.set(0, 4, 0);
camera.rotation.x = -Math.PI/2;


const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
document.body.appendChild(renderer.domElement);


const controls = new OrbitControls(camera, renderer.domElement);

controls.target.set(0, 1, 0);
controls.maxPolarAngle = 49*Math.PI/100;
controls.minAzimuthAngle = -49*Math.PI/100;
controls.maxDistance = 8;
controls.minDistance = 1;
// controls.autoRotate = true;
controls.autoRotateSpeed = 4;
controls.update();

const light1 = new THREE.SpotLight(0xFFFFFF, 10, 2.5, 60);
const light2 = new THREE.SpotLight(0xFFFFFF, 10, 2.5, 60);
const light3 = new THREE.SpotLight(0xFFFFFF, 10, 2.5, 60);
light1.position.set(-1.2, 2, 0);
light2.position.set(0, 2, 0)
light3.position.set(1.2, 2, 0);
scene.add(light1, light2, light3);

const loader = new GLTFLoader();

let table;

loader.load('table.glb', function (glb) {
    
    table = glb.scene;
    table.position.set(0, 0, 0);
	scene.add(table);
    
}, undefined, function (error) {
    
    console.error(error);
    
});

let balls = {};
const colors = {
    "yellow": 0xFFFF00,
    "blue": 0x064CA8,
    "red": 0xFF071A,
    "purple": 0x5E3C9C,
    "orange": 0xFFA903,
    "green": 0x09BD58,
    "maroon": 0xD33329,
    "black": 0x000000
}

function fetchBalls() {
    fetch('balls.json')
        .then(response => response.json())
        .then(data => {
            balls = data;
            Object.values(balls).forEach(item => {
                loader.load(item.label+'.glb', function (glb) {
                item.x = 2*item.x/1000-1.88;
                item.y = 2*item.y/1000-0.91;
                let ball = glb.scene;
                ball.position.set(item.x, 1.00, item.y);
                ball.scale.set(0.0525, 0.0525, 0.0525);
                let rotx = Math.random()*Math.PI*2;
                let roty = Math.random()*Math.PI*2;
                let rotz = Math.random()*Math.PI*2;
                ball.rotation.set(rotx, roty, rotz);
                scene.add(ball);
                
            }, undefined, function (error) {
                console.error(error);
            });
        });
        console.log(balls);
    })
    .catch(err => console.error("Fetch error:", err));
    return new Promise(resolve => setTimeout(resolve, 500));
}

console.log(balls);

let cueRotation, cueX, cueY;

fetch('cue.txt')
    .then(response => response.text())
    .then(data => {
        [cueRotation, cueX, cueY] = data.split(' ').map(parseFloat);
        cueX = 2*cueX/1000-1.88;
        cueY = 2*cueY/1000-0.91;
    })
    .catch(err => console.error("Fetch error:", err));

// for (let i = 0; i < 16; i++) {
//     loader.load('/'+i+'.glb', function (glb) {
//         let ball = glb.scene;
//         let posx = Math.random()*3.6 - 1.8;
//         let posz = Math.random()*1.6 - 0.8;
//         ball.position.set(posx, 1.00, posz);
//         ball.scale.set(0.0525, 0.0525, 0.0525);
//         let rotx = Math.random()*Math.PI*2;
//         let roty = Math.random()*Math.PI*2;
//         let rotz = Math.random()*Math.PI*2;
//         ball.rotation.set(rotx, roty, rotz);
//         scene.add(ball);
//         balls.push(ball);

//     }, undefined, function (error) {
//         console.error(error);
//     });

// }
function loadCue() {
    loader.load('cue.glb', function (glb) {
        let cue = glb.scene;
        cue.position.set(balls[0].x, 1, balls[0].y);
        cue.rotation.set(1.7, 0, 0);
        cue.rotateOnWorldAxis(yAxis, Math.PI-cueRotation);
        scene.add(cue);

    }, undefined, function (error) {  
        console.error(error);
    });
}

function drawLine(start, end, color=0xFFFFFF) {
    const material = new THREE.MeshBasicMaterial({color: color});
    const points = [];
    points.push(start);
    points.push(end);
    const geometry = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(points), 64, 0.004, 8, false);
    const line = new THREE.Mesh(geometry, material);
    scene.add(line);
}

async function fetchLines() {
    await fetchBalls();
    loadCue();
    fetch('lines.json')
        .then(response => response.json())
        .then(data => {
            data.forEach(line => {
                let x1 = 2*line.x1/1000-1.88, y1 = 2*line.y1/1000-0.91, x2 = 2*line.x2/1000-1.88, y2 = 2*line.y2/1000-0.91;
                const start = new THREE.Vector3(x1, 1, y1);
                const end = new THREE.Vector3(x2, 1, y2);
                drawLine(start, end, line.color);
                console.log(x1, balls[0].x);
                if (Math.abs(x1 - balls[0].x) < 0.01 && Math.abs(y1 - balls[0].y) < 0.01) {
                    const sphere = new THREE.Mesh(new THREE.SphereGeometry(0.0525, 32, 32), new THREE.MeshBasicMaterial({color: line.color, opacity: 0.8, transparent: true}));
                    sphere.position.set(x2, 1, y2);
                    scene.add(sphere);
                }
            });
        })
        .catch(err => console.error("Fetch error:", err));
}

fetchLines();

document.getElementById('home-view').addEventListener('click', () => {
    camera.position.set(0, 4, 0);
});
document.getElementById('cue-view').addEventListener('click', () => {
    camera.position.set(cueX, 1.2, cueY);
});

document.addEventListener('keydown', (event) => {
    if (event.key === 'h') {
        camera.position.set(0, 4, 0);
    } else if (event.key === 'c') {
        camera.position.set(cueX, 1.2, cueY);
    }
});

let b = 0;

function animate() {
    // requestAnimationFrame(animate);
    
    if (balls.length == 16 && b == 0) {
        b = 1;
        //drawLine(balls[0].position, balls[Math.round(Math.random()*14+1)].position);
    }
    // camera.rotateOnWorldAxis(yAxis, 0.001);
	renderer.render(scene, camera);
    controls.update();
    for (let i = 0; i < balls.length; i++) {
        //balls[i].rotation.y += 0.02;
    }
}
renderer.setAnimationLoop(animate);
//animate();